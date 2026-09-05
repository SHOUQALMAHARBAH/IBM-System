# Internal Controls — Self-Approval Audit (Process 56)

**Last verified:** 2026-09-07 · **Owner:** Compliance / Executive Management / External Auditor (roles, not yet named people)

## What this is

Backlog Part C #56 is a one-liner, not a checkbox list: "Internal Controls
(Maker/Checker) — fully covered in Part A.5, plus a periodic audit report
scanning for any possible self-approval cases." Part A.5 (`common/maker-
checker.util.ts`'s `assertDifferentActors` + a DB `CHECK` constraint per pair)
was verified intact — this process's only NEW work is the second half: the
report. It lives in its own module, `apps/api/src/modules/internal-controls/`
(`internal-controls.{config,service,controller}.ts` +
`internal-controls-audit.scheduler.ts`), the `SlaDashboardModule` shape — it
aggregates data across many other modules' tables, it owns none of them, so
it stays separate rather than folding into `compliance-risk`.

## The registry

`internal-controls.config.ts`'s `MAKER_CHECKER_REGISTRY` is the single source
of truth — one entry per DB `CHECK` constraint added across five migrations
(`20260826091424`, `20260827120000`, `20260903170000`, `20260905120000`,
`20260906120000`). **15 same-table entries**, plus **one cross-table pair
handled separately** (`POLICY_CHECKING_ISSUER_PAIR`) — 16 total:

| Entity | Maker | Checker | DB CHECK |
|---|---|---|---|
| KYCRecord | createdByUserId | approvedByUserId | yes |
| PolicyChecking | placedByUserId | checkedByUserId | yes |
| Refund | raisedByUserId | approvedByUserId | yes |
| DisposalBatch (dormant — M06) | nominatedByUserId | dpoApprovedByUserId | yes |
| DataSharingApproval (dormant — M08) | requestedByUserId | approvedByUserId | yes |
| DataProcessingAgreement (dormant — M07) | assessedByUserId | dpoApprovedByUserId | yes |
| Settlement | approvedByUserId | secondApproverUserId | yes |
| CommissionLedgerEntry | overrideRequestedByUserId | overrideApprovedByUserId | yes |
| Recommendation | draftedByUserId | approvedByUserId | yes |
| AccessRecertificationItem | subjectUserId | reviewerUserId | yes |
| NeedsAssessment (×2 rows) | createdByUserId | reviewedByUserId / approvedByUserId | yes (2 constraints) |
| Complaint | resolvedByUserId | closureApprovedByUserId | yes |
| DataSubjectRequest | processedByUserId | closedByUserId | yes |
| IncidentReport | classifiedByDpoUserId | seniorManagementCoSignUserId | yes |
| **PolicyChecking → Policy (cross-table)** | **Policy.issuedByUserId** | **PolicyChecking.checkedByUserId** | **no — cannot be** |

**`DisposalBatch`/`DataSharingApproval`/`DataProcessingAgreement` are
dormant** — no application code writes to them yet (M06/M07/M08 are not
built; see root `README.md`'s Part D gaps). Kept in the registry and scanned
anyway (the #48 `third_party_payment_source` dormant-classifier precedent) —
the day those modules land, this report already covers them with no further
change.

## The one pair no DB CHECK can express

`policy-lifecycle.md` had flagged an open question before this process
existed: `PolicyCheckingService.check()` enforces `checkedByUserId !=
issuedByUserId` app-side (`assertDifferentActors`) as a "stricter-than-lex
belt," but the `PolicyChecking_maker_checker_distinct` CHECK only covers
`checkedByUserId != placedByUserId` — should the CHECK extend to
`issuedByUserId` too? **Answer, settled here: it structurally cannot.** A
Postgres `CHECK` constraint can only compare columns on the SAME row of the
SAME table. `checkedByUserId` lives on `PolicyChecking`; `issuedByUserId`
lives on the PARENT `Policy` row. There is no single-table constraint that
can express this pair. Two ways to close a cross-table invariant like this
structurally would be a trigger (this codebase already has one precedent —
the `AuditLogEntry` immutability trigger) or a denormalized copy of
`issuedByUserId` onto `PolicyChecking` kept in sync — both are real options
but out of scope for "a periodic audit report." Instead: **this scan IS the
compensating control** for this one pair — it is the ONLY defense-in-depth
backstop beyond the app-level guard, for exactly this reason. If a bug or a
raw-SQL write ever bypasses `assertDifferentActors` for this pair
specifically, the DB will not stop it — this report is what catches it, on
its next run at the latest.

`classifyCrossTableRows` (`internal-controls.config.ts`) is the twin of
`classifyPairRows` reached through the `policy` relation instead of a second
column on the same row — same condition (both sides set, both equal), same
shape violation record.

## How the scan runs

`InternalControlsService.runSelfApprovalAudit(actorUserId)`:

1. Fires all 16 pair-scans **concurrently** (`Promise.all`) — NOT
   sequentially. This was a real, measured fix, not a style preference: a
   16-round-trip sequential scan against this session's own long-lived,
   cumulative `db-test` database timed out a 30-second e2e test; running
   the same 16 queries concurrently brought it under 12 seconds.
2. Each same-table pair: `findMany` with **no `where` filter** — every row
   is fetched (capped at `INTERNAL_CONTROLS_SCAN_LIMIT = 20000`,
   `truncated: true` if hit), and null-checking happens in the pure
   `classifyPairRows` function instead of the query. This is deliberate:
   `AccessRecertificationItem.reviewerUserId` is NOT NULL while every other
   checker field IS nullable, and trusting each model's generated Prisma
   filter type to accept `{ not: null }` identically across 15 different
   models (behind an `unknown` cast that already bypasses TypeScript's own
   per-model checking) was judged a real runtime risk not worth taking for
   a report that can just fetch a bit more and filter in JS instead — these
   are workflow/approval tables, not transactional ledgers, so an unfiltered
   scan is cheap.
3. A best-effort `READ` `AuditLogEntry` row is always written
   (`entityType: 'InternalControlsAuditReport'`, counts only — never a user
   id) — the `SlaDashboardService` "prove someone looked" precedent.
4. **If any violation is found** (should be zero in ordinary operation —
   see below): logged at `ERROR`, and one `CREATE`
   `InternalControlsViolation` `AuditLogEntry` row is written per violation
   (entity/field/user ids) — no new model; `AuditLogEntry`'s own
   polymorphism is the record, the #48 `TransactionMonitoringAlert`
   record-keeping choice repeated.

`InternalControlsAuditScheduler` runs the identical scan nightly at 10:00
UTC (after the 09:00 transaction-monitoring sweep), resolving the
`system@ibms.internal` account — the same scheduler shape every other nightly
sweep in this codebase uses. `GET /internal-controls/self-approval-audit`
(`internal-controls.audit` — `[COMPLIANCE_OFFICER, EXECUTIVE_MANAGEMENT,
EXTERNAL_AUDITOR]`, a genuinely NEW permission, not pre-seeded ahead of time
the way #55's four were) runs the same scan on demand.

## Why a clean run is the expected outcome, not a surprise

Every one of the 15 same-table pairs is already backed by a DB `CHECK` — a
self-approval on any of them should be structurally impossible regardless of
which code path writes the row. This report exists as **independent
verification**, not detection of an expected-to-occur condition: an auditor
should not have to trust "the code has a guard," they should be able to see
"we scanned, and found none." The e2e proof of genuine detection therefore
had to target the ONE pair without a DB backstop (see above) — every
same-table pair was proven correct via the config's pure-function unit
tests instead (a mocked row with `maker === checker` is correctly flagged;
Postgres itself would reject that same row in reality).

## `@code-reviewer` findings (resolved)

Not run as a separate mandatory pass distinct from the build itself for this
process (a read-only reporting tool, no new workflow/approval logic, no
financial calculation, no Confidential/Highly-Confidential write path) — the
one correctness issue caught and fixed during the build itself, before
review, was the concurrency fix in "How the scan runs" step 1 above (found
via the e2e test's own timeout, not a review comment).

## Where the code lives

- `apps/api/src/modules/internal-controls/` — `internal-controls.
  {config,service,controller}.ts`, `internal-controls-audit.scheduler.ts`,
  `internal-controls.module.ts`.
- `packages/db/prisma/seed-data/permissions.ts` — `internal-controls.audit`.
- `apps/web/app/(app)/internal-controls/page.tsx` +
  `lib/internal-controls/internal-controls-api.ts`.

## Out of scope for this file

Closing the `PolicyChecking`/`Policy` cross-table gap with a real DB-level
mechanism (a trigger, or denormalizing `issuedByUserId` onto
`PolicyChecking`) — a real, deliberate follow-up decision, not done here.
Any NEW maker/checker pair added after this process ships needs a
`MAKER_CHECKER_REGISTRY` entry added by hand — this scan does not discover
pairs automatically from the schema. `#57` (Internal Audit —
`InternalAuditFinding`, the External Auditor's time-boxed access) is a
separate, not-yet-built process — this report does not feed it, and finding
a violation here does NOT create an `InternalAuditFinding` row.
