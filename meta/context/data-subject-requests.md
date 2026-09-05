# Data Subject Request Management (M04)

**Last verified:** 2026-09-05 · **Owner:** DPO (role, not yet a named person)

## What this is

M04 (`meta/context/pcms-privacy-modules.md`) governs the Access / Correction / Deletion /
Objection request workflow a data subject can raise under PDPL — intake, identity
verification, working the request, a statutory SLA per request type, and closure with a
mandatory second-DPO sign-off. `ibms-app`'s Prisma schema has modeled
`DataSubjectRequest` since the initial domain-model migration; the first real writer
landed 2026-09-05 (backlog Part D, bundled under Process **#52 Data Protection
Compliance**). It is the second of Part D's nine systems to be built, after M03 (Consent
Management, `meta/context/consent-management.md`) — the two now share
`apps/api/src/modules/pdpl/`.

## The shapes

```
DataSubjectRequest
  customerId: string?              # exactly one of customerId / insuredPersonId
  insuredPersonId: string?         # (service-level 422, not a DB CHECK — the ConsentRecord shape)
  type: DsrType                    # ACCESS | CORRECTION | DELETION | OBJECTION
  status: DsrStatus                # RECEIVED -> IDENTITY_VERIFIED -> IN_PROGRESS ->
                                    # {FULFILLED | PARTIALLY_FULFILLED | REJECTED} -> CLOSED
                                    # (REJECTED also reachable straight from RECEIVED /
                                    # IDENTITY_VERIFIED — WORKFLOW_TRANSITIONS.DataSubjectRequest)
  receivedAt: DateTime             # ALWAYS new Date() at create() — never caller-suppliable
  identityVerifiedAt: DateTime?
  slaDueAt: DateTime                # SlaTimerService.computeDueAt at create time
  accessExtensionAppliedAt: DateTime?  # ACCESS-only, +15 business days, write-once
  extensionReason: string?
  retentionScheduleReference: string?       # required for a partially-fulfilled DELETION
  partialFulfilmentJustification: string?
  processedByUserId: string?       # the MAKER — stamped by fulfil/partiallyFulfil/reject
  closedByUserId: string?          # the CHECKER — must differ from processedByUserId
  rejectionReason: string?
  noOpenRetentionHoldConfirmedAt: DateTime?  # DELETION-only staff attestation, persisted
                                              # at fulfil() time — see "not obvious" below
  closedAt: DateTime?
  dpoHandlerUserId: string?

SlaTimer (entityType: 'DataSubjectRequest')
  workflowName: 'dsr_access_deletion'        # ACCESS, DELETION — 15 business days
  workflowName: 'dsr_correction_objection'   # CORRECTION, OBJECTION — 10 business days
  both: 2 escalation stages — DPO at T-3 business days, General Manager at the due date
  itself (SLA_REGISTRY, pdpl-sla-timers.md) — 2 SlaTimer rows per DSR, not 1
```

`WORKFLOW_TRANSITIONS.DataSubjectRequest` and `SLA_REGISTRY`'s two DSR entries both
pre-existed (A.6/A.8 backlog infrastructure) — this module is their first real consumer.

## The rules that aren't obvious

- **Closure needs sign-off from a DIFFERENT DPO officer than whoever processed the
  request** — `processedByUserId` (stamped by whichever of `fulfil` / `partiallyFulfil` /
  `reject` drove the terminal outcome) vs. `closedByUserId`, enforced by
  `assertDifferentActors` AND the `DataSubjectRequest_closure_maker_checker_distinct` DB
  CHECK (mirrors `Complaint_closure_maker_checker_distinct`). Both `dsr.handle` and
  `dsr.close` are DPO-only permissions, so this segregates between two distinct DPO
  officers, not between roles — `meta/lex/maker-checker-segregation.md`'s "Covered
  actions" table names this ("DPO officer who processes a DSR" / "a different DPO officer
  who closes it"). **This lex row didn't exist until this build** — the brain `CLAUDE.md`
  "Mandatory rules" summary already said "DSR closure" was covered, but the lex file's own
  table was silent on it; fixed alongside this file, a documentation gap the build itself
  surfaced, not a new rule.
- **A DELETION request cannot be marked fully FULFILLED without an explicit staff
  attestation that no retention hold applies** (`confirmNoOpenRetentionHold: true` on the
  fulfil request) — Retention & Disposal (M06, `RetentionScheduleItem`/`LegalHold`) is not
  built yet, so this is deliberately a staff attestation, not an automated check against
  real retention data; an automated check today would always trivially pass, the exact
  #48 `third_party_payment_source`-dormancy mistake this build was reasoned against
  repeating (`meta/context/transaction-monitoring.md`). The attestation is **persisted**
  (`noOpenRetentionHoldConfirmedAt`, stamped in the same write as `processedByUserId`) and
  carried into the UPDATE audit snapshot — a `@code-reviewer` MAJOR on the first pass
  validated the flag in memory and then discarded it, leaving no record of which DPO
  officer attested it. If a retention hold DOES apply, use `partially-fulfil` instead —
  the request's status stays `PARTIALLY_FULFILLED` permanently; there is no path back to
  `FULFILLED` for a DELETION once a hold has been recorded.
- **The one +15-business-day extension is ACCESS-only**, additive to the *existing*
  `slaDueAt` (not restarted from `now()`), and write-once
  (`accessExtensionAppliedAt IS NULL` in the repository guard, re-asserted alongside
  `status IN (RECEIVED, IDENTITY_VERIFIED, IN_PROGRESS)` — a `@code-reviewer` BLOCKER on
  the first pass had only the write-once guard, not the status re-assertion, so a DSR that
  concluded between the service's read and the repository's write could still have its
  deadline silently re-based and a fresh pair of `SlaTimer` rows opened against an
  already-closed-out request). DELETION's own retention-flag mechanism
  (`partially-fulfil`) is the tool for "we cannot finish on time because data must be
  retained" — the model does not offer DELETION an extension too.
- **Re-basing the SLA timer on extension is START-then-resolve, not the naive
  resolve-then-start** — `SlaTimerService` has no "update dueAt" method, only
  `startTimer`/`resolve`, and the old and new timer rows share the same `workflowName`
  (the DSR's type never changes on extension), so `resolve()`'s own `startsWith` match
  would otherwise also catch rows `startTimer()` just created. Fixed (a `@code-reviewer`
  MAJOR) by capturing a `rebaseCutoff` timestamp before either call, starting the new pair
  first, and only calling `resolve()` — now with a `createdBefore: rebaseCutoff` filter —
  if the start succeeded. This ordering makes every partial-failure outcome the SAFER of
  the two possible bad states: if `startTimer` itself fails, `resolve` is skipped and the
  pre-extension timer(s) stay open (a false-EARLY escalation on the now-superseded
  deadline a human can dismiss, not a silent gap with zero timer coverage); if `startTimer`
  succeeds but the follow-up `resolve` fails, the old rows simply stay open alongside the
  new ones (a harmless, human-visible duplicate). `SlaTimerService.resolve()`'s
  `createdBefore` parameter (an optional `createdAt: { lt: ... }` filter) was added for
  exactly this caller — every other `resolve()` call site (terminal transitions, M03)
  omits it and keeps the ordinary "resolve everything open" behavior.
- **`receivedAt` is never caller-suppliable** — always `new Date()` at `create()` time,
  unlike the #10/#12/#44/#45 `parseHistoricalInstant`-backdatable convention. This
  guarantees only that staff cannot BACKDATE a late log to disguise it as a prompt one —
  it does NOT, by itself, guarantee the backlog's "logged the same business day" intent,
  since nothing stops staff from receiving a DSR by phone on Monday and not calling
  `POST /dsr` until Friday (`receivedAt` then honestly, if unhelpfully, shows Friday).
  Closing that residual gap would need an operational logging-SLA control outside this
  code, not a field — don't oversell what the non-backdatable design actually proves.
- **DSR reads ARE audited** (`isSensitiveDataAccess: true` on both `get()` and `list()`)
  — a deliberate departure from the Confidential-tier no-read-audit precedent used by
  sibling Domain E/PDPL items (#33/#34/#41/#44/#45/#46/#51). A DSR is a data subject's own
  direct exercise of a PDPL right — closer in kind to `Claim`/`TransactionMonitoringAlert`
  (both audited every read) than to those. `list()`'s audit row uses `entityId: 'list'`
  and `afterValue: { count }`, the exact `TransactionMonitoringService.list()` shape.
- **Every status-changing engine call is race-safe against a genuinely concurrent
  double-call, not just a sequential retry** — `verifyIdentity`, `start`, `fulfil`,
  `partiallyFulfil`, `reject`, and `close` all catch the engine's own 0-row
  `ConflictException`, reload, and return the current state idempotently if it already
  matches the caller's intent (rethrowing otherwise, e.g. `partiallyFulfil`/`reject` with
  a genuinely different payload than what won the race). The first pass only did this for
  `start()`; a `@code-reviewer` MINOR flagged the inconsistency and it was applied
  uniformly across all six.

## Where the code lives

- `packages/db/prisma/schema.prisma` — `DataSubjectRequest`, `DsrType`, `DsrStatus`
  (search "Part 4.1" / "Process 52/M04").
- `packages/db/prisma/migrations/20260905120000_add_dsr_widening/` — adds
  `processedByUserId` / `closedByUserId` / `rejectionReason` /
  `noOpenRetentionHoldConfirmedAt`, the `DataSubjectRequest_closure_maker_checker_distinct`
  CHECK, and three list-filter indexes. Every other field pre-existed.
- `apps/api/src/modules/pdpl/` — `dsr.config.ts` (pure: SLA-workflow routing, the
  extension math, view/audit-snapshot builders), `dsr.service.ts`, `dsr.controller.ts`,
  `dto/`.
- `apps/api/src/repositories/dsr.repository.ts` — owns the writes, including the two
  status-conditional guards (`recordHandlerAssignment`, `applyExtension`).
- `apps/api/src/modules/sla/sla-timer.service.ts` — `ResolveSlaTimerParams.createdBefore`,
  added for this module's extension re-basing (see "not obvious" above).
- `apps/api/src/modules/sla/sla-registry.config.ts` — `dsr_access_deletion` /
  `dsr_correction_objection`, both pre-existing before this module.
- `apps/web/app/(app)/dsr/page.tsx` + `apps/web/lib/pdpl/dsr-api.ts`.

## `@code-reviewer` findings (resolved)

Mandatory (a new `WorkflowTransitionService` entity + a new maker/checker pair +
Highly-Confidential-adjacent PDPL rights data) → CHANGES REQUESTED → resolved: **1
BLOCKER** (the extension's write-once guard needed the `status` re-assertion above — a
same-shape gap `race-safe-invariants.md` already documents for a status-conditional
`updateMany`, missed on the first pass here) + **2 MAJORs** (the non-atomic SLA re-basing
ordering above; the unpersisted-and-unaudited `confirmNoOpenRetentionHold` attestation
above) + **2 MINORs** (the race-safe idempotent-retry pattern applied inconsistently
across the six status-changing methods; the `DSR_RECEIVED_AT_IS_ALWAYS_NOW` comment
overclaiming what the non-backdatable design actually guarantees — softened, not changed).

## Out of scope for this file

The other seven Part D / PCMS systems still unbuilt — M05 (access governance —
partially covered by `roles-and-segregation-of-duties.md`), M06 (Retention & Disposal —
`data-retention-and-disposal.md`), M07 (Vendor Risk), M08 (Data Sharing), M09 (Incident &
Breach), M10 (DPIA), the privacy-notice / RoPA requirements, and the DPO Workspace
dashboard. `pcms-privacy-modules.md` is the M01-M12 map; a future module gets its own
file here the same way this one did.
