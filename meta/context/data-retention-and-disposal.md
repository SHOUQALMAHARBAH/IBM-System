# Data retention & secure disposal (M06)

**Last verified:** 2026-09-07 · **Owner:** DPO (role, not yet a named person)

## What this is

M06 (`meta/context/pcms-privacy-modules.md`) governs how long every record category is
kept and how it's destroyed once retention expires: a per-category schedule
(`RetentionScheduleItem`), a dual-control destruction workflow (`DisposalBatch` +
`CertificateOfDestruction`), and an exclusion mechanism for records under active
litigation/investigation hold (`LegalHold`). All four entities existed in the Prisma
schema since the initial domain-model migration; `AuditLogEntry` got a seeded schedule
row and a `getRetentionCutoffDate()` reader on 2026-08-26, but nothing before this build
ever wrote a `LegalHold` or `DisposalBatch` row, or let anyone add a SECOND
`RetentionScheduleItem`. This build (backlog Part D §5.1, Process #52, worked as item #3
of the user's 9-item Part D checklist, after Consent/M03 and DSR/M04) is that first real
CRUD across all three.

## The shapes (current)

```
RetentionScheduleItem
  recordCategory: string @unique          # widened from a bare string this build — see
                                           # "The rules that aren't obvious"
  retentionPeriodMonths: int
  legalBasis: string?                     # should cite PRIV-STD-03 / the specific CBJ or AML
                                           # article — see "not obvious" below for the catch
  confirmedByLegalCounselAt: DateTime?    # null = draft/unconfirmed; a one-time legal act,
                                           # not a toggle — 422s if already confirmed

LegalHold
  scope, reason, placedAt, nextReviewDueAt (6-month SLA), releasedAt?
  retentionScheduleItemId: string?        # NEW this build — a hold now OPTIONALLY names the
                                           # RetentionScheduleItem category it excludes from
                                           # disposal; null means the hold exists but isn't
                                           # wired to a disposal-eligibility check yet

DisposalBatch
  status: NOMINATED → MANAGER_APPROVED → DPO_APPROVED → EXECUTED → CLOSED
  nominatedByUserId    # maker — Department Manager (or any retention.dispose.nominate holder)
  dpoApprovedByUserId  # checker — MUST differ from nominatedByUserId (DB CHECK constraint)
  method: string?      # set at EXECUTED — one of the 3 DISPOSAL_METHODS
  certificateOfDestruction: CertificateOfDestruction?  # required before status can be CLOSED
```

## The rules that aren't obvious

- **`RetentionScheduleItem.recordCategory` now has a real `@unique` constraint** — the
  2026-08-26 gap this file flagged ("nothing in the schema stops two rows for the same
  category") is closed. Migration `20260914120000_add_retention_disposal_widening` adds
  the constraint; `seed.ts`'s `ensureRetentionSchedule()` was simplified from a hand-rolled
  find-then-create/update to a real Prisma `upsert` now that the constraint exists.
  `RetentionScheduleService.create()` still handles a duplicate-category race as an
  ordinary Prisma `P2002` → 409, the `rfq.service.ts` `isUniqueViolation` shape — never a
  pre-check-then-write race.
- **Engineering still has never been handed the actual retention-period table.**
  `PRIV-STD-03` is where the real per-category retention periods live; this build does not
  invent any more draft figures than the one already-flagged `AuditLogEntry` row (120
  months, unconfirmed). What this build DOES add is the CRUD itself — `POST
  /retention-schedule`, `PATCH /retention-schedule/:id`, `POST
  /retention-schedule/:id/confirm` — gated by a NEW permission, `retention-schedule.manage`
  (`[COMPLIANCE_OFFICER, DATA_PROTECTION_OFFICER]`). **No "Legal Counsel" role exists among
  the 11 seeded `RoleName` values** — the backlog's own phrase "needs Legal Counsel
  confirmation as a pending input" is therefore attested by the closest standing
  compliance-adjacent roles, a real, documented limitation of this RBAC model, not a design
  choice to route around Legal Counsel. `update()` refuses to edit an already-confirmed row
  (422 — "add a new item instead"); `confirm()` is a status-conditional `updateMany`
  re-asserting `confirmedByLegalCounselAt: null` in the `where` (0 rows → re-check: already
  confirmed is a 422, a genuine concurrent race is a 409).
- **`DisposalBatch`'s "dual-control approval (Department Manager then DPO — two different
  users)" checkbox wording only actually enforces the SECOND half.** There is no
  `managerApprovedByUserId` column — only a timestamp, `managerApprovedAt` — and the DB
  `CHECK` constraint (`DisposalBatch_maker_checker_distinct`, pre-existing since migration
  `20260826091424`) compares only `dpoApprovedByUserId` against `nominatedByUserId`.
  `MANAGER_APPROVED` is therefore a self-transition checkpoint reachable by the nominating
  manager or any other `retention.dispose.nominate` holder — the REAL two-different-humans
  enforcement is specifically nominate-vs-DPO-approve, backed by both
  `assertDifferentActors()` (app layer, a `ForbiddenException`) and the DB `CHECK`.
- **Legal-Hold exclusion is re-derived from LIVE data at every dual-control step, not
  cached from nomination time** — `DisposalBatchService`'s private
  `assertNoActiveLegalHold(retentionScheduleItemId)` runs again at `nominate()`,
  `managerApprove()`, AND `dpoApprove()` (a no-op if the batch has no
  `retentionScheduleItemId`), because a hold can be placed on the category between any two
  approval steps. This is the same "re-derive the approval gate from live data" discipline
  `#16` (Broker Recommendation) established — a hold placed after nomination but before DPO
  approval still blocks execution (422), it does not silently sail through on a stale check.
- **A `DisposalBatch` cannot reach `CLOSED` without a `CertificateOfDestruction`
  attached** (422 otherwise — the literal "no closing without a Certificate of Destruction"
  requirement), and `issueCertificate()` requires status EXECUTED or CLOSED (422 before
  that) with a real DB `@unique` on `disposalBatchId` backing duplicate detection (P2002 →
  409).
- **Retention informs disposal eligibility; it still does not execute disposal against
  any OTHER table's rows.** `DisposalBatchService.execute()` is a staff ATTESTATION — a
  status stamp to `EXECUTED` plus a `method` field naming an external destruction process
  (`certified_secure_wipe_nist_800_88` / `physical_destruction` / `certified_shredding`) —
  never a live `DELETE` against the records the schedule item actually describes. This
  deliberately avoids the significant complexity of bypassing `AuditLogEntry`'s immutability
  trigger (still the ONE dormant-model precedent for what a real disposal-execution path
  would eventually need — see `meta/lex/sensitive-data-handling.md`) and matches this file's
  own pre-existing framing verbatim: the workflow records/approves the destruction DECISION
  and attests it happened; it is not a data-deletion engine.
- **`LegalHold.recordReview()` uses start-then-resolve SLA re-basing**, the pattern
  `data-subject-requests.md`'s `applyExtension` established: `slaTimer.startTimer()` for the
  new 6-month review window runs BEFORE `slaTimer.resolve({..., createdBefore: <cutoff
  captured before either call>})` closes the old one — never the reverse. Resolve-then-start
  risks ending with ZERO open timers if start fails after resolve succeeds (a silent SLA
  coverage gap); start-then-resolve leaves an extra open timer on partial failure instead, a
  safer failure mode. `release()` is idempotent and permanently resolves the timer (no
  re-basing).

## Where the code lives

- `packages/db/prisma/schema.prisma` — `RetentionScheduleItem` (search "PART 6.2"),
  `DisposalBatch`, `LegalHold`, `CertificateOfDestruction` models; migration
  `20260914120000_add_retention_disposal_widening` for this build's widening.
- `apps/api/src/modules/pdpl/retention-schedule.{config,service,controller}.ts` +
  `apps/api/src/repositories/retention-schedule.repository.ts` — the schedule CRUD.
- `apps/api/src/modules/pdpl/legal-hold.{config,service,controller}.ts` +
  `apps/api/src/repositories/legal-hold.repository.ts` — place/review/release, the
  `hasActiveHold()` exclusion check `DisposalBatchService` calls directly (same-module
  injection, not a cross-module coupling violation).
- `apps/api/src/modules/pdpl/disposal-batch.{config,service,controller}.ts` +
  `apps/api/src/repositories/disposal-batch.repository.ts` — the dual-control
  nominate→manager-approve→dpo-approve→execute→certificate→close workflow.
- `apps/web/app/(app)/retention-disposal/page.tsx` + `apps/web/lib/pdpl/retention-disposal-api.ts`
  — a combined 3-section screen (schedule / holds / batches), each section gated by its own
  permission.
- `apps/api/test/retention-disposal.e2e-spec.ts` — the full lifecycle walk, including the
  Legal-Hold-exclusion re-check at every dual-control step.

## Out of scope for this file

The M04 rule that a Deletion DSR with an open retention flag can't close as "fully
fulfilled" — `meta/context/pcms-privacy-modules.md`. The `AuditLogEntry` immutability
trigger itself and Part 10.3 audit-trail requirements generally — a future
`meta/context/audit-trail.md` would be the right home if this grows past what fits here.
An automated retention-expiry sweep that turns "past its cutoff" into an actual
`DisposalBatch` nomination — nothing in `ibms-app` does this yet; every `DisposalBatch`
today is manually nominated.
