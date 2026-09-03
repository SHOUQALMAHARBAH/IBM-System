# Customer service lifecycle

**Last verified:** 2026-09-03 · **Owner:** shouq

## What this is

Domain E, Processes 41–46: the post-sale customer touchpoints — service
requests (certificates / copies / changes, #41), complaints (#42), the
cross-module SLA dashboard (#43), consent-gated customer communication (#44),
feedback (#45) and retention (#46). Source:
`IBMS_Full_Scope_Context_Document.docx` Part 3.8. SLA mechanics are
`meta/lex/pdpl-sla-timers.md` + the generic `SlaTimer` engine
(`apps/api/src/modules/sla/`); consent is a PCMS concern —
`meta/context/pcms-privacy-modules.md` (M03).

**#41 (Customer Requests) and #42 (Complaints Management) are built.** #43–46
are not started — see root `README.md` § Scope status.

## The shapes

```
ServiceRequest                      # #41 — certificates / copies / changes
  customerId: string                # required; validated to exist
  policyId: string?                 # the policy the request is about; if set, MUST belong to customerId (422 mismatch, 404 unknown)
  requestType: string               # certificate | copy | change | other
  detail: string?                   # free text — what specifically is requested; Confidential business note, NO_FULL_ACCOUNT_NUMBER guard (see below)
  status: string                    # open → in_progress → {fulfilled | cancelled}   -- PLAIN STRING, not a WorkflowTransition entity
  slaTimerId: string? @unique       # linked to the ONE generic SlaTimer row (service_request_fulfilment); best-effort
  raisedByUserId / assignedToUserId / fulfilledByUserId : string?   # service-desk ownership trail (bare scalars, AuditLogEntry is authoritative)
  outcomeNote: string?              # what was done (fulfil) / why cancelled — mandatory at closure, logged verbatim, NO_FULL_ACCOUNT_NUMBER guard
  createdAt / closedAt : DateTime

Complaint                          # #42 — a customer complaint (Part 3.8)
  customerId: string                # required; validated to exist
  claimId: string?                  # the claim under dispute; if set, MUST belong to customerId (422 mismatch, 404 unknown)
  policyId: string?                 # the policy concerned; same ownership check
  issue: string                     # free text — mandatory; Confidential business note, NO_FULL_ACCOUNT_NUMBER guard
  category: string?                 # denied_claim | delayed_issuance | premium_dispute | unanswered_claim | other
  responsibleEmployeeUserId: string?   # the handler (set at log or via /assign)
  status: ComplaintStatus           # LOGGED → ASSIGNED → IN_PROGRESS → {RESOLVED | ESCALATED}, ESCALATED → {IN_PROGRESS | RESOLVED}, RESOLVED → CLOSED   -- a WorkflowTransitionService entity (WORKFLOW_TRANSITIONS.Complaint)
  slaTimerId: string? @unique       # the ONE generic SlaTimer row (complaint_resolution); best-effort
  resolution: string?               # mandatory at /resolve — logged verbatim, NO_FULL_ACCOUNT_NUMBER guard
  resolvedByUserId / resolvedAt     # who moved it to RESOLVED + when — the MAKER for the closure sign-off
  closureApprovedByUserId: string?  # the MANAGER who closed it — MUST differ from resolvedByUserId (CHECK + assertDifferentActors)
  closedAt: DateTime?
ComplaintAction                     # append-only { actionText (verbatim, guarded), takenByUserId, takenAt }
EscalationRecord                    # { escalatedTo (management | regulator | dispute_resolution_committee), escalatedByUserId, reason?, escalatedAt }

SlaTimer (generic, polymorphic — apps/api/src/modules/sla/)
  entityType: 'ServiceRequest'      # #41's timer row
  workflowName: 'service_request_fulfilment'   # a SLA_REGISTRY entry — DRAFTED, see below
  dueAt: DateTime                   # createdAt + 5 business days (SlaTimerService.computeDueAt)
  escalatedAt: DateTime?            # flipped by the nightly SlaTimerScheduler sweep once dueAt passes and not resolved
  escalatedTo: 'BRANCH_DEPARTMENT_MANAGER'   # set at startTimer time, not at escalation time
  resolvedAt: DateTime?            # stamped on fulfil / cancel (SlaTimerService.resolve, best-effort)
  ---
  entityType: 'Complaint'          # #42's timer row
  workflowName: 'complaint_resolution'   # a SLA_REGISTRY entry — DRAFTED 10 business days
  resolvedAt                       # stamped when the complaint reaches RESOLVED **or** ESCALATED (internal clock stops)
```

Endpoints (`ibms-app`), all `service-request.manage`
(`[SALES_RELATIONSHIP_OFFICER, BRANCH_DEPARTMENT_MANAGER]`):
`POST /service-requests` (create at `open`, starts the SLA timer);
`POST /service-requests/:id/assign` (`{ assignedToUserId }` — while
`open`|`in_progress`); `POST /service-requests/:id/start`
(`open → in_progress`, idempotent); `POST /service-requests/:id/fulfil` /
`.../cancel` (`{ outcomeNote }` mandatory — `{open|in_progress} → terminal`,
stamps `closedAt` + (fulfil) `fulfilledByUserId`, resolves the SLA timer);
`GET /service-requests?customerId=&status=&assignedToUserId=`;
`GET /service-requests/:id`.

Endpoints (#42): `POST /complaints` (`complaint.log` —
`[SALES_RELATIONSHIP_OFFICER, CLAIMS_OFFICER, FINANCE_COLLECTIONS_OFFICER,
COMPLIANCE_OFFICER, BRANCH_DEPARTMENT_MANAGER]`; create at `LOGGED`, starts the
SLA timer); `.../:id/assign` (`{ responsibleEmployeeUserId }` — from `LOGGED`
this also drives `→ ASSIGNED`; from `ASSIGNED`|`IN_PROGRESS`|`ESCALATED` a plain
re-assign); `.../:id/start` (`{ASSIGNED | ESCALATED} → IN_PROGRESS`, idempotent);
`.../:id/actions` (`{ actionText }` — appends a `ComplaintAction` while not
`CLOSED`); `.../:id/resolve` (`{ resolution }` mandatory verbatim —
`{IN_PROGRESS | ESCALATED} → RESOLVED`, stamps `resolvedByUserId`; same-note
re-resolve → 200, different → 409); `.../:id/escalate` (`complaint.escalate` —
`[BRANCH_DEPARTMENT_MANAGER, COMPLIANCE_OFFICER]`; `{ escalatedTo?, reason? }` —
`IN_PROGRESS → ESCALATED` + an `EscalationRecord`, resolves the SLA timer);
`.../:id/close` (`complaint.close` — `[BRANCH_DEPARTMENT_MANAGER]`;
`RESOLVED → CLOSED`, **mandatory supervisor sign-off** — 403 if the closer
resolved it); `GET /complaints?customerId=&status=&claimId=&responsibleEmployeeUserId=`
+ `/:id`.

## Customer Requests (Process 41)

*(All `ibms-app` product decisions filed via `/brain-gap` at Part C #41 — Part
3.8 says only "handle certificate / copy / change requests with SLA
tracking".)*

- **The model pre-existed; #41 widens it.** `ServiceRequest` +
  `slaTimerId @unique` + the `service-request.manage` perm were already in the
  schema / seed. Migration `20260903160000` (41st) adds `policyId` (nullable
  FK, `ON DELETE SET NULL`), `detail`, `raisedByUserId` / `assignedToUserId` /
  `fulfilledByUserId`, `outcomeNote`, and `@@index([customerId])` (this
  customer's requests) / `@@index([status, createdAt])` (the "open queue" read
  — status filter + newest-first order) / `@@index([assignedToUserId])` (the
  "my queue" read). **No seed change.**
- **`ServiceRequest.status` is a PLAIN STRING** — NOT a
  `WorkflowTransitionService` entity (the `CommissionLedgerEntry.status` /
  `ReconciliationException.status` pattern). Legal moves live in
  `service-request.config.ts`'s `SERVICE_REQUEST_TRANSITIONS`
  (`open: [in_progress, fulfilled, cancelled]`, `in_progress: [fulfilled,
  cancelled]`, `fulfilled: []`, `cancelled: []` — a request may be fulfilled
  on the spot without a `start`), validated by `isServiceRequestTransition` +
  a service `assertTransition`; every move is a **status-conditional
  `updateMany`** (0 rows → reload → idempotent-or-409, `race-safe-invariants.md`).
- **The SLA timer is the generic `SlaTimerService` engine** — a NEW
  `SLA_REGISTRY` entry `service_request_fulfilment` (`entityType:
  'ServiceRequest'`, `5 businessDays`, one escalation stage to
  `BRANCH_DEPARTMENT_MANAGER`). **The 5-business-day figure is DRAFTED /
  UNSOURCED** — a customer-service-request turnaround is a published
  service-standard / contractual courtesy target, **not a PDPL statutory SLA**,
  and Part 3.8 names no number. `pdpl-sla-timers.md` § "What does NOT trigger
  this rule" says internal courtesy targets are ordinary KPIs — but the
  backlog line explicitly names `SlaTimer`, so #41 tracks it as a real timer
  (with an escalation sweep), not merely a KPI. The registry `citation` marks
  it DRAFT/UNSOURCED, like the two KYC rows; replace with a sourced figure when
  a broker service charter / SOP supplies one. Same drafted status as
  `CLAIM_LARGE_THRESHOLD_JOD` (#23), the #27 follow-up thresholds, the #40
  `netPosition` metric.
- **The timer is started BEST-EFFORT at create** (the A.8 /
  `AccessRecertificationService.startCycle` precedent — the request is already
  committed; a timer-bookkeeping failure must not roll it back or hide that
  the request was logged). `SlaTimerService.startTimer` creates the polymorphic
  `SlaTimer` row(s) keyed by `entityType`/`entityId`; #41 then does a
  best-effort `updateMany({ where: { id, slaTimerId: null }, data: {
  slaTimerId } })` to populate `ServiceRequest.slaTimerId @unique` (the schema
  intends a direct 1:1 link — `SlaTimer.serviceRequest` back-relation — unlike
  `AccessRecertificationCycle` which has no `slaTimerId` column). If the attach
  fails the timer still exists and the nightly sweep still escalates it
  polymorphically; the view's `sla` block would just be null. On fulfil /
  cancel, `SlaTimerService.resolve` flips `resolvedAt` on the timer row
  (best-effort — a closed request whose timer stays open self-heals: the sweep
  escalates it once, harmless).
- **The view carries an `sla` block** (`deriveServiceRequestView`) — `dueAt` /
  `escalatedAt` / `escalatedTo` / `resolvedAt` + a computed **`breached`**
  (`resolvedAt === null && dueAt <= now`), so the UI can show "overdue" before
  the nightly sweep has actually stamped `escalatedAt`.
- **`policyId` (optional) must belong to `customerId`** — a **422** on a
  cross-customer policy, **404** on an unknown one. `assignedToUserId` (on
  create or assign) is validated to exist (**404**).
- **`outcomeNote` is mandatory on fulfil / cancel** (`@MinLength(3)` /
  `@MaxLength(2000)`), logged **verbatim** in the `UPDATE` audit row (a
  business note — what was done / why cancelled — not personal data; the #35
  `overrideReason` / #39 `resolutionNote` precedent). `fulfil` idempotency:
  same note → 200, different → **409**; the other terminal state → **422**.
- **`detail` / `outcomeNote` carry a `NO_FULL_ACCOUNT_NUMBER` input guard**
  (`service-request.config.ts` — `@Matches(/^(?!.*\d{9,})[\s\S]*$/)`, rejecting
  a run of 9+ consecutive digits with a message pointing at Process 38's
  `PaymentChannel`). Both fields are returned unmasked in every list row and
  stored verbatim in the audit `afterValue` — Confidential tier, fine for a
  business note, but a `change` request ("update my bank account to …") is
  exactly where a user would paste a full account / card number, which is
  Highly Confidential (`sensitive-data-handling.md` — a free-text field next to
  a masked-data path must not be its capture point). A payment-method change is
  recorded through an approved `PaymentChannel` (#38, `accountLast4` only), not
  typed here.
- **No maker/checker** — a service-desk request is single-actor Sales /
  Manager work (`maker-checker-segregation.md` — the maker/checker surfaces are
  KYC / policy checking / refunds / disposal / DSR closure; #41 is none). #42
  Complaints DOES get a mandatory supervisor sign-off (a different backlog
  line).
- Audit: `CREATE ServiceRequest` (ids + type + `detail` + status +
  `assignedToUserId`), `UPDATE` on assign / start / fulfil / cancel (new status
  + who + `outcomeNote` verbatim + `closedAt`); plus the `SlaTimer` engine's
  own `CREATE` / `UPDATE` / `SLA_ESCALATED` rows. Book-wide reads (capped
  `SERVICE_REQUEST_READ_LIMIT = 5000`, `logger.warn` on truncation).
- **Deferred**: no `ServiceRequest` → `Document` link (a fulfilled certificate
  request should attach the generated PDF — a #25-style `Document` pointer, not
  built); no per-`requestType` SLA (one 5-day default for all four types); no
  customer-facing portal / self-service; the SLA figure is drafted; no
  re-open path (a `fulfilled` / `cancelled` request is terminal); no bulk
  actions.

## Complaints Management (Process 42)

*(All `ibms-app` product decisions filed via `/brain-gap` at Part C #42 — Part
3.8 asks for: log the complaint (date / customer / issue / responsible
employee / SLA), link it to a claim on dispute; a mandatory supervisor
sign-off before closure; an escalation path to the Insurance Dispute
Resolution Committee when unresolved internally.)*

- **The models pre-existed; #42 widens them.** `Complaint` /
  `ComplaintAction` / `EscalationRecord`, the `ComplaintStatus` enum,
  `Complaint.slaTimerId @unique`, the `WORKFLOW_TRANSITIONS.Complaint` map, and
  the `complaint.log` / `complaint.close` / `complaint.escalate` permissions
  were all already in the schema / seed. Migration `20260903170000` (42nd) adds
  `Complaint.resolvedByUserId` / `resolvedAt`,
  `EscalationRecord.escalatedByUserId`, the
  `Complaint_closure_maker_checker_distinct` CHECK, and four indexes
  (`Complaint` `@@index([status, createdAt])` replacing the bare
  `@@index([status])`, `@@index([claimId])`,
  `@@index([responsibleEmployeeUserId])`; `@@index([complaintId])` on both
  child tables). **No seed change.**
- **`Complaint.status` IS a `WorkflowTransitionService` entity** (unlike Process
  41's plain-string `ServiceRequest`). `WORKFLOW_TRANSITIONS.Complaint`:
  `LOGGED → [ASSIGNED]`, `ASSIGNED → [IN_PROGRESS]`,
  `IN_PROGRESS → [RESOLVED, ESCALATED]`, `ESCALATED → [IN_PROGRESS, RESOLVED]`,
  `RESOLVED → [CLOSED]`, `CLOSED → []`. Every move goes through
  `WorkflowTransitionService.transition` — never a bare `.status =`. The one
  non-transition status-conditional write is `recordAssignee` (sets
  `responsibleEmployeeUserId` while `ASSIGNED`|`IN_PROGRESS`|`ESCALATED`, no
  status change). **Only `CLOSED` is terminal** — `RESOLVED` is
  "awaiting the sign-off".
- **The SLA timer is the generic `SlaTimerService` engine** — a NEW
  `SLA_REGISTRY` entry `complaint_resolution` (`entityType: 'Complaint'`,
  `10 businessDays`, one escalation stage to `BRANCH_DEPARTMENT_MANAGER`).
  **The 10-business-day figure is DRAFTED / UNSOURCED** — a complaint-resolution
  turnaround is a CBJ insurance conduct-of-business matter (the CBJ Insurance
  Dispute Resolution Committee that `EscalationRecord` routes to is a real CBJ
  mechanism), **not a PDPL statutory SLA**, and Part 3.8 names no figure. Same
  drafted status / `citation` treatment as `service_request_fulfilment` (#41)
  and the two KYC rows; replace with a sourced figure when a CBJ
  complaint-handling instruction or a broker SOP supplies one. Started
  **best-effort at create** (the A.8 precedent), then a best-effort
  `attachSlaTimer` for the 1:1 `slaTimerId`. `SlaTimerService.resolve` (best-
  effort) flips `resolvedAt` when the complaint reaches **`RESOLVED` OR
  `ESCALATED`** — escalation stops the internal-resolution clock. The view's
  `sla` block carries a computed `breached` (same as #41).
- **`claimId` (optional) must belong to `customerId`** — a **422** on a
  cross-customer claim, **404** on an unknown one (same for `policyId`). This is
  "link it to a claim on dispute". `responsibleEmployeeUserId` (on create or
  assign) is validated to exist (**404**).
- **Mandatory supervisor sign-off before closure** (`maker-checker-segregation.md`
  / Part 5.2). `close` (`complaint.close` / **MANAGER only**) drives
  `RESOLVED → CLOSED` and stamps `closureApprovedByUserId`. The **maker** is
  `resolvedByUserId` (whoever drove `→ RESOLVED`); `assertDifferentActors`
  rejects a self-close with **403**, and the
  `Complaint_closure_maker_checker_distinct` CHECK is the DB backstop.
  `resolvedByUserId` is write-once (RESOLVED is not re-enterable) so a
  pre-check is race-safe. Added to `maker-checker.util.ts`'s covered-pairs
  table.
- **Escalation** (`escalate` — `complaint.escalate` / **MANAGER, COMPLIANCE**):
  `IN_PROGRESS → ESCALATED` + an `EscalationRecord` (`escalatedTo` ∈
  `{management, regulator, dispute_resolution_committee}`, **default
  `dispute_resolution_committee`** — the backlog's named target). The
  `EscalationRecord` write + the SLA resolve run in the engine's `sideEffect`
  (best-effort — logged, not thrown, like every other `sideEffect` in the
  codebase; on the rare DB blip that drops the record the engine's `TRANSITION`
  audit row is the authoritative "it was escalated" fact). A re-`escalate` while
  already `ESCALATED` is a **plain idempotent no-op** — there is deliberately
  NO count-then-create "self-heal" (that is the race `race-safe-invariants.md`
  forbids, and a `UNIQUE` backstop is wrong because
  `ESCALATED → IN_PROGRESS → ESCALATED` is a legal loop that SHOULD mint a
  second record). From `ESCALATED` the complaint can return to `IN_PROGRESS`
  (`start`) or be `resolve`d directly (committee ruling implemented).
- **`issue` / `resolution` / `ComplaintAction.actionText` / `EscalationRecord.reason`
  carry the shared `NO_FULL_ACCOUNT_NUMBER` guard** (`common/dto.util.ts`, moved
  there from `service-request.config.ts` at this review) — a premium-dispute
  complaint is a plausible place for a customer to paste a full card / account
  number.
- Audit: best-effort `CREATE Complaint` (ids + issue + category + status),
  `UPDATE Complaint` on assign / start / resolve / close (new status + who +
  `responsibleEmployeeUserId` + `resolution` verbatim + `closureApprovedByUserId`
  + `closedAt`), best-effort `CREATE ComplaintAction` / `CREATE EscalationRecord`
  (text verbatim), plus the engine's own `TRANSITION` rows and the `SlaTimer`
  engine's `CREATE` / `SLA_ESCALATED`. Book-wide reads (capped
  `COMPLAINT_READ_LIMIT = 5000`).
- **Deferred**: one 10-day SLA for all categories (no per-category target); the
  SLA figure is drafted; no re-open of a `CLOSED` complaint; escalation does
  not restart the SLA clock on a return-to-handling; no customer-facing
  portal; no automatic escalation sweep to the committee (the nightly sweep
  escalates the SLA timer to the internal manager only — the committee route
  is a manual `complaint.escalate`); no link from a complaint to a generated
  acknowledgement / final-response `Document`.
