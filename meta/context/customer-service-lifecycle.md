# Customer service lifecycle

**Last verified:** 2026-09-04 · **Owner:** shouq

## What this is

Domain E, Processes 41–46: the post-sale customer touchpoints — service
requests (certificates / copies / changes, #41), complaints (#42), the
cross-module SLA dashboard (#43), consent-gated customer communication (#44),
feedback (#45) and retention (#46). Source:
`IBMS_Full_Scope_Context_Document.docx` Part 3.8. SLA mechanics are
`meta/lex/pdpl-sla-timers.md` + the generic `SlaTimer` engine
(`apps/api/src/modules/sla/`); consent is a PCMS concern —
`meta/context/pcms-privacy-modules.md` (M03).

**#41 (Customer Requests), #42 (Complaints Management), #43 (SLA Management),
#44 (Customer Communication) and #45 (Customer Feedback) are built.** #46 is not
started — see root `README.md` § Scope status.

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

## SLA Management (Process 43)

*(All `ibms-app` product decisions filed via `/brain-gap` at Part C #43 — the
backlog line is one sentence: "a monitoring dashboard over `SlaTimer` across
every module", no checkboxes. Like #40 Financial Reporting, #43 is the
**backend** for a Part E-style dashboard.)*

- **A read-only view — it creates and resolves nothing.** New module
  `apps/api/src/modules/sla-dashboard/`, kept **separate from `SlaModule`**
  (which owns the generic `SlaTimerService` engine + the 15-minute
  `SlaTimerScheduler` escalation sweep — backlog A.8). `sla-dashboard` only
  reads `SlaTimer` rows and aggregates them, the way `loss-ratio` is a
  separate module from the workflow it reports on. **No migration, no seed
  change** — `sla-dashboard.view`
  (`[COMPLIANCE_OFFICER, BRANCH_DEPARTMENT_MANAGER, EXECUTIVE_MANAGEMENT,
  EXTERNAL_AUDITOR]`) was seeded in `a440c1b`. **No maker/checker.**
- **Built ahead of its data source.** Only 3 registry workflows create timers
  today (`quarterly_access_review`, `service_request_fulfilment` #41,
  `complaint_resolution` #42); the dashboard is written to show **every**
  `SLA_REGISTRY` workflow as `startTimer` call sites land (the #8 / #10
  shape).
- **Endpoints** (both `sla-dashboard.view`, book-wide, computed at request
  `now`, capped `SLA_DASHBOARD_TIMER_LIMIT = 5000` with a `logger.warn` on
  truncation — the #30 / #33 / #40 in-memory-aggregation pattern):
  - **`GET /sla-dashboard/summary`** → `{ generatedAt, dueSoonWindow, totals,
    byWorkflow[], byEntityType[], byEscalationTarget[] }`.
  - **`GET /sla-dashboard/timers?state=&entityType=&workflowName=`** → the
    per-timer drill-down list, worst-first (state severity, then oldest
    `dueAt`, then `id`). `workflowName` is matched as a **prefix** (a base name
    catches its `::stage` rows). Default when `state` is omitted: the `open`
    group.
- **Six mutually-exclusive leaf states**, evaluated per timer at `now`
  (`classifyTimer`, `sla-dashboard.config.ts`), precedence in this order:
  `resolved_on_time` (`resolvedAt <= dueAt`) · `resolved_late`
  (`resolvedAt > dueAt`, even by 1 ms) · `escalated` (`resolvedAt == null &&
  escalatedAt != null` — always implies past due, the sweep only escalates
  overdue rows) · `breached` (`resolvedAt == null && escalatedAt == null &&
  dueAt <= now`) · `due_soon` (`… && dueAt <= now + SLA_DASHBOARD_DUE_SOON_WINDOW`)
  · `on_track` (everything else). Named **groups** the `?state=` filter also
  accepts: `open` = the four unresolved states · `open_breached` =
  breached + escalated · `at_risk` = due_soon + breached + escalated ·
  `resolved` = both resolved states.
- **`SLA_DASHBOARD_DUE_SOON_WINDOW = { value: 3, unit: 'calendarDays' }` is a
  dashboard lookahead heuristic, NOT an SLA registry value.** It only decides
  which bucket a still-open timer is *shown* in — it never changes a deadline,
  an escalation, or a `SlaTimer` row — so it is **outside** `pdpl-sla-timers.md`'s
  rule that any registry value must be sourced from a PRIV-SOP / PRIV-STD. It
  is drafted; tune it freely. Same drafted status as #41's 5-business-day
  figure and the #40 `netPosition` metric.
- **Counts are per timer *row*.** A workflow with N escalation stages (only the
  two DSR types, and neither is wired yet) produces N `SlaTimer` rows per
  entity, distinguished by a `::stage` suffix on `workflowName`
  (`SlaTimerService.stageWorkflowName`). `buildSlaDashboardSummary` groups
  `byWorkflow` on the **base** name (`baseWorkflowName()` strips the suffix) so
  all DSR-access stages roll into one `dsr_access_deletion` row, and each group
  carries `entityCount` (distinct `entityId`) alongside `total` so the reader
  sees "8 rows across 5 DSRs". `oldestOverdueDays` per group = the max
  `now − dueAt` across its breached + escalated rows.
- **`breachRate`** (`totals`, a fixed-4dp string) =
  `(resolvedLate + breached + escalated) / (resolvedLate + breached +
  escalated + resolvedOnTime)` — i.e. over timers that have **reached a
  timeliness verdict**; a still-comfortably-open `on_track` / `due_soon` timer
  does not dilute it. `"0.0000"` when the denominator is 0.
- **Registry lookups are non-throwing here.** A persisted `SlaTimer.workflowName`
  could name a workflow since renamed or removed from `SLA_REGISTRY`, so #43
  added **`findSlaRegistryEntry(name): SlaRegistryEntry | undefined`**
  (`sla-registry.config.ts`) — the throwing `getSlaRegistryEntry` is for call
  sites that control the name. On a miss the dashboard falls back to
  `{ label: rawName, entityType: timer.entityType, drafted: false,
  configuredDuration: null }`. `drafted` = the registry `citation` starts
  `"DRAFT"` (the #41 / #42 / KYC rows).
- **Best-effort `READ` audit row per read** (`entityType: 'SlaDashboard'`,
  `entityId: 'summary' | 'timers'`, `afterValue` = counts + `generatedAt` +
  the filter set only — **never an `entityId`, an entity reference, or a
  name**). `isSensitiveDataAccess` is set when the loaded timer set contains a
  row whose `entityType` is in `SLA_DASHBOARD_SENSITIVE_ENTITY_TYPES`
  (`DataSubjectRequest`, `IncidentReport`, `Complaint`, `KYCRecord`, `Claim`,
  `LegalHold`) — the existence of a DSR / incident / complaint timer is itself
  Confidential context (`sensitive-data-handling.md`). This mirrors #30 Claims
  Analytics / #40 Financial Reporting; contrast #33 / #34 (Confidential-tier
  AR/AP reads, not audited). A failed audit write is logged and swallowed — it
  never breaks the read.
- All aggregation is **pure and unit-tested** in `sla-dashboard.config.ts`
  (`classifyTimer`, `baseWorkflowName`, `buildSlaTimerRows`,
  `buildSlaDashboardSummary`, `deriveSlaTimerRow`, `hasSensitiveEntityType`) —
  the `finance.config.ts` split. The service (`sla-dashboard.service.ts`) only
  loads rows (`repositories/sla-dashboard.repository.ts`) and writes the audit;
  the repo read is `orderBy: { dueAt: 'asc' }` so a truncated load keeps the
  most urgent rows.
- `apps/web/` gains an **"SLA dashboard"** screen
  (`app/(app)/sla-dashboard/page.tsx` + `lib/sla/sla-dashboard-api.ts` + an
  `AppNav` entry) — summary stat cards + a breach-rate %, a `byWorkflow` table
  (label · entity type · configured SLA · per-state counts · oldest-overdue · a
  "drafted" marker), a `byEntityType` table, and a `state`-`<select>` + a
  timers table from `/timers`.
- **Deferred**: no historical SLA-performance trend — the dashboard is a live
  "right now" view, no `asOf`, no over-time series; the `dueSoonWindow` is a
  drafted heuristic; in-memory aggregation capped at 5000 rows (push into the
  query when the timer table outgrows it); no per-workflow drill-through page;
  no CSV / export; no notifications (the dashboard reads the same rows the
  nightly `SlaTimerScheduler` sweep already escalates — it does not add a
  second alerting path); no de-duplication of a multi-stage workflow's rows to
  one logical item (`entityCount` is the current mitigation).

## Customer Communication (Process 44)

*(All `ibms-app` product decisions filed via `/brain-gap` at Part C #44 — the
backlog line is one checkbox: "Respect the customer's recorded channel and
language, and check consent status (`ConsentRecord`) before any marketing
send". Part 3.8 adds nothing else.)*

- **The model pre-existed and is shared with Process 12.** `CommunicationLog`
  already carried the Process-44 columns (`channel`, `templateId`,
  `languageUsed`, `direction @default(OUTBOUND)`, `subject`, `body`,
  `respectedConsent @default(true)`, `sentAt`, `loggedByUserId`) alongside the
  Part C #12 RFQ-correspondence columns (`rfqId`, `rfqInsurerId`). The
  `communication.send` perm
  (`[SALES_RELATIONSHIP_OFFICER, PLACEMENT_TECHNICAL_OFFICER, CLAIMS_OFFICER,
  FINANCE_COLLECTIONS_OFFICER]`) was seeded in `a440c1b`. **DISCRIMINATOR:
  `rfqId IS NULL` == a Process-44 customer-communication row; `rfqId IS NOT
  NULL` == a #12 RFQ-correspondence row.** Every Process-44 read filters
  `rfqId: null`, so a #12 row never surfaces through `/communications` (and a
  #12 id 404s on `GET /communications/:id`).
- **Migration `20260904120000` (43rd) only WIDENS** — no new table, **no seed
  change** (149 perms). `Customer.preferredContactChannel InteractionChannel?`
  (nullable — the recorded channel preference, the parallel to the existing
  `Customer.languagePreference`, which is where "recorded language" already
  lives; also added to `CreateCustomerDto`, `CustomerService.toMasked` / `list`
  and `CustomerRepository`). `CommunicationLog.isMarketing Boolean
  @default(false)` and `CommunicationLog.consentRecordId String?` (nullable FK →
  `ConsentRecord`, `ON DELETE SET NULL`). `@@index([customerId])` → composite
  `@@index([customerId, sentAt])` (the "this customer's comms, newest first"
  read), plus `@@index([consentRecordId])`.
- **`CommunicationLog` is NOT a `WorkflowTransitionService` entity and has NO
  maker/checker** — a factual send log, create + read only, the `Interaction`
  #10 / RFQ-correspondence #12 shape. No `SlaTimer` (Process 44 has no SLA; the
  `consent_withdrawal` M03 timer is a separate concern — reflecting a
  withdrawal in the register — that #44 only *reads*).
- **New module code lives in `apps/api/src/modules/customer-service/`**
  (`communication.config.ts` pure core, `.service.ts`, `.controller.ts`,
  `dto/create-communication.dto.ts`, `dto/list-communications-query.dto.ts`) +
  `repositories/communication.repository.ts`, wired into
  `CustomerServiceModule` (the third controller alongside #41 / #42).
- **Endpoints** (all `communication.send`):
  - **`POST /communications`** — `{ customerId, body (mandatory), channel?,
    languageUsed?, isMarketing?, templateId?, subject?, sentAt? }`. Creates a
    row at `direction: OUTBOUND`, `respectedConsent: true`. 404 unknown
    customer.
  - **`GET /communications?customerId=&channel=&isMarketing=&direction=`** —
    the book-wide Process-44 list (`rfqId IS NULL`), newest-first (`sentAt`
    then `createdAt`), capped `COMMUNICATION_READ_LIMIT = 5000` (`logger.warn`
    on truncation).
  - **`GET /communications/consent-status?customerId=`** — a pre-compose
    check: `{ customerId, marketing: { allowed, reason, consentRecordId } }`.
    Declared **before** `:id` in the controller so the literal path wins. 400
    if `customerId` is omitted, 404 unknown.
  - **`GET /communications/:id`** — one Process-44 row; a #12 / unknown id →
    404.
- **"Respect the customer's recorded channel and language"** — both are
  **derived, not an input**, the #28 / #31 / #38 "computed when derivable"
  rule (`resolveChannel` / `resolveLanguage`, pure). Omit → taken from the
  customer record. Supply a value that **disagrees** with the recorded one →
  **422**. `languageUsed` always resolves (`Customer.languagePreference` has a
  value); `channel` becomes a **required input** (422 if also omitted) when
  the customer has no `preferredContactChannel` on record — **and also when the
  recorded value is outside `COMMUNICATION_CHANNELS`** (the field is the full
  `InteractionChannel` enum, so a `MEETING` / `VISIT` preference is treated as
  "no usable preference" — the caller must name an outbound channel; otherwise
  the send would be logged with a nonsensical channel, or every explicit
  channel would 422). There is deliberately no per-message language override.
- **The marketing-consent gate** (`evaluateMarketingConsent`, pure) — only
  when `isMarketing: true`. The repository loads the customer's `ConsentRecord`
  rows where `purpose = 'MARKETING' OR isMarketing = true` (`PRIV-SOP-04` keeps
  the two as separate controls; either identifies a marketing-consent row).
  **Fail-safe rule:** a send is allowed only if there is an *active grant*
  (`granted === true && withdrawnAt === null`) **and no withdrawal event is at
  least as recent as the newest active grant** ("effective time" =
  `grantedAt ?? createdAt` for a grant, `withdrawnAt` for a withdrawal). A
  fresh grant after an earlier withdrawal is a valid re-opt-in (the new grant
  is more recent); a withdrawal recorded after — or at the same instant as —
  the newest active grant blocks, **even when it sits on a different (older)
  record** (PDPL: any ambiguity about whether consent still stands is a "no").
  The exact multi-record precedence is **drafted pending a pinned `PRIV-SOP-04`
  section** (like the drafted SLA figures); single grant / withdraw on one
  record is unambiguous. On allow, the active grant's id is stamped onto
  `CommunicationLog.consentRecordId`. Otherwise the send is **BLOCKED with a
  422** (`reason` ∈ `no_record` / `not_granted` / `withdrawn`), **no
  `CommunicationLog` row is written** (PDPL: no marketing without consent — a
  blocked send did not happen), and a **best-effort `REJECT` audit row**
  records the attempt (`entityType: 'CommunicationLog'`, `entityId: 'blocked'`,
  `afterValue` = `customerId` + `channel` +
  `blocked: 'marketing_consent_<reason>'` + `consentRecordId` — **no subject /
  body**). A non-marketing (service / transactional) send never touches the
  consent table — `respectedConsent` stays `true` (contractual necessity, no
  consent needed) and `consentRecordId` is null. **The gate is a read-then-write
  with no DB constraint** tying the consent read to the `CommunicationLog`
  insert — tolerable only because this is a *log*, not a sender (delivery is
  deferred); a real email / SMS dispatch MUST re-check consent at send time.
- **`subject` / `body` carry the shared `NO_FULL_ACCOUNT_NUMBER` guard**
  (`common/dto.util.ts`, same as #41 / #42) and are **Confidential-tier free
  text** — returned unmasked but **never in an audit row**. The best-effort
  `CREATE` audit `afterValue` is structural metadata only (`channel`,
  `templateId`, `languageUsed`, `direction`, `isMarketing`, `respectedConsent`,
  `consentRecordId`, `sentAt`) — the #12 `RfqCommunication` / CRM `Interaction`
  precedent (channel + when, not the body). Reads are **not** audited
  (Confidential tier — the #33 / #34 / #41 precedent; contrast the #30 / #40 /
  #43 aggregate reads). **Open `PRIV-SOP-04` check**: `/communications/consent-status`
  returns a named data subject's marketing-consent posture — if PRIV-SOP-04 /
  Part 10.3 treats a consent-status lookup as a loggable read of consent data,
  it should audit; no lex mandates it today.
- **`sentAt` is backdatable** via `parseHistoricalInstant` (the #10 / #12
  helper — an offset-less datetime or a future instant → 422); default now().
- **No maker/checker** — logging a send is single-actor cross-functional work
  (`communication.send` is granted to four roles for exactly that reason, the
  #10 `interaction.log` shape).
- **Deferred**: no real delivery integration — this is a *log*, not a sender
  (no email/SMS gateway, no bounce/read tracking; **the consent-gate
  read-then-write TOCTOU is only acceptable because of this — a real dispatch
  must re-check consent at send time inside a guard**); the multi-record
  consent precedence is drafted pending a pinned `PRIV-SOP-04` section;
  `isMarketing` is a caller-asserted boolean, not derived from `templateId`;
  one consent check covers all marketing (no per-campaign / per-purpose
  granularity beyond MARKETING); `INBOUND` Process-44 rows can be created
  directly in the DB but the `POST` endpoint only writes `OUTBOUND`; no
  `CommunicationLog` → CRM 360° timeline wiring (#10 `buildCustomerTimeline`
  still merges only interactions / policies / claims / complaints); no
  template library / render step (`templateId` is a free string); no bulk /
  campaign send; no `Customer` update endpoint, so `preferredContactChannel`
  is set only at customer creation (and a non-outbound value there just means
  every send to that customer must name a channel).

## Customer Feedback (Process 45)

*(All `ibms-app` product decisions filed via `/brain-gap` at Part C #45 — the
backlog line is a title only, no checkboxes: "Customer Feedback —
`CustomerFeedback`". Part 3.8 names the model's own doc comment: "satisfaction
feedback post-issuance, post-claim, post-renewal".)*

- **The model pre-existed and needed NO widening.** `CustomerFeedback` (Part 4
  core schema) already had every field a satisfaction-survey log needs:
  `customerId`, `context` (a plain string), `score` (`Int?`), `comments`
  (`String?`), `submittedAt`. **No migration.** `feedback.log`
  (`[SALES_RELATIONSHIP_OFFICER]`) was seeded in `a440c1b` — **no seed change**
  (149 perms). There is **no separate read permission** — `feedback.log` covers
  create *and* read, the #41 / #44 shape (contrast CRM's `interaction.log` /
  `customer.360-view.read` split, which exists because `interaction.log` is
  granted to six cross-functional roles).
- **Not a `WorkflowTransitionService` entity, no maker/checker, no `SlaTimer`**
  — a factual log, create + read only. The closest precedent is `Interaction`
  (#10), not #41 / #42 / #44: feedback has no status, no derived fields, no
  cross-entity validation at all beyond the customer existing.
- New module code lives in `apps/api/src/modules/customer-service/`
  (`feedback.{config,service,controller}.ts` + `dto/create-feedback.dto.ts` +
  `dto/list-feedback-query.dto.ts`) + `repositories/feedback.repository.ts`,
  wired as the **4th `CustomerServiceModule` controller**.
- **`context`** is restricted to the three values the model's own doc comment
  names — `post_issuance` / `post_claim` / `post_renewal`
  (`FEEDBACK_CONTEXTS`, `isFeedbackContext`) — a fourth touchpoint is a
  `/brain-gap`, not a silent DTO relaxation.
- **`score`** is optional, bounded `1`–`5` (`FEEDBACK_SCORE_MIN` /
  `FEEDBACK_SCORE_MAX`). **DRAFTED / UNSOURCED** — Part 3.8 names no scale; a
  5-point CSAT is the common convention, same drafted status as
  `CLAIM_LARGE_THRESHOLD_JOD` (#23) and the #41 / #42 SLA figures. Replace with
  a sourced figure if a CX / Compliance SOP supplies one.
- **Endpoints** (all `feedback.log`): `POST /feedback` — `{ customerId,
  context, score?, comments?, submittedAt? }`; 404 unknown customer.
  `GET /feedback?customerId=&context=` — the book-wide list, newest first by
  `submittedAt`, capped `FEEDBACK_READ_LIMIT = 5000`. `GET /feedback/:id`.
  `submittedAt` is backdatable via `parseHistoricalInstant` (the #10 / #12 /
  #44 helper — an offset-less datetime or a future instant → 422; default
  now()), for logging a response captured after the fact (verbally on a call,
  on a paper form).
- **`comments` carries NO `NO_FULL_ACCOUNT_NUMBER` guard**, unlike #41 / #42 /
  #44's free-text fields — a deliberate divergence, not an oversight. That
  guard exists for a field sitting *next to a masked-data path* (a "change my
  bank account" service request, a premium-dispute complaint) where a customer
  could plausibly paste a full account/card number expecting it to be acted
  on. Feedback `comments` is a satisfaction survey's open-text box — the CRM
  `Interaction.summary` shape (`log-interaction.dto.ts` carries no such guard
  either), not the #41/#42/#44 shape. If a future Domain E item finds this
  wrong, extend the guard here too — the constant is centralized in
  `common/dto.util.ts` either way.
- **`comments` is deliberately excluded from the `CREATE` audit `afterValue`**
  — `afterValue` = ids + `context` + `score` + `submittedAt` only. This follows
  the CRM `Interaction.summary` precedent (`crm.service.ts` `logInteraction`
  logs channel/`occurredAt`, never `summary`), not #41 (`detail`) / #42
  (`issue`/`resolution`), which DO log their free text verbatim. The reasoning:
  feedback `comments` is the customer's own subjective reflection — closer in
  kind to a private relationship-log note than to an operational "what was
  done / why" business-action record, so the more conservative precedent wins.
- **No ownership-based read gating.** `feedback.log` is single-role
  (`SALES_RELATIONSHIP_OFFICER`) and is the sole gate on both write and read —
  book-wide, not filtered by `Customer.ownerUserId` (the #41 / #42 / #44
  shape; CRM's ownership check exists only because `customer.360-view.read` is
  a *separate*, broader-granted read permission).
- Audit: best-effort `CREATE CustomerFeedback` only (ids + `context` + `score`
  + `submittedAt`, never `comments`). Reads are not audited (Confidential
  tier — the #33 / #34 / #41 / #44 precedent).
- **Deferred**: no link from a feedback row to the specific triggering
  `Policy` / `Claim` / `RenewalCase` — `context` is a label, not a foreign key,
  so "which claim was this post-claim survey about" is not queryable (adding
  that would be a migration + per-context FK validation, out of scope for a
  no-checkbox backlog line); the 1–5 score scale is drafted; no automatic
  survey trigger (a #23-style "on claim closure, prompt for feedback" flow is
  not built — logging is always a manual `POST`); no duplicate-response
  detection (a customer can submit feedback for the same context repeatedly);
  no aggregation / CSAT-dashboard reporting (the #40 / #43 "backend for a Part
  E dashboard" shape is not repeated here — reads are a plain filtered list).
