# Insurer Performance (Process 60)

**Last verified:** 2026-09-11 · **Owner:** Branch/Department Manager, Executive
Management (roles, not yet named people)

## What this is

Backlog Part C #60, the third item in Domain G (Management) — "Insurer
Performance — `InsurerPerformanceScore`: a periodic job computing the score
from quote-response speed/claims service/price/service quality." Unlike #58
and #59, **`InsurerPerformanceScore` and `InsurerSlaAgreement` already exist
in the core schema** (Part 13) — this process is their first real consumer.
Both had zero readers/writers anywhere in this codebase before this landing.

## The four dimensions, and why each metric was picked

The backlog names four dimensions but no metric per dimension. Each was
mapped to an existing, cleanly-attributable signal rather than inventing a
new one:

- **Quote-response speed** (`quoteResponseScore`) — the average days between
  `RFQInsurer.sentAt` and `RFQInsurer.respondedAt` for rows RESPONDED TO in
  the period (`respondedAt` is only ever stamped on `QUOTED`/`DECLINED` —
  `rfq.service.ts`'s own `transitionInsurer`; `NO_RESPONSE` always leaves it
  null), scored against `InsurerSlaAgreement` (`slaType: 'quote_response'`,
  the insurer's own agreed `targetDays`) if one exists, else the same 9-day
  default `RFQ.followUpThresholdDays` already uses (backlog Part C #11) —
  never an unrelated invented number.
- **Claims service** (`claimsServiceScore`) — the proportion of claims
  notified in the period (`Claim.createdAt`, via `Claim.policy.insurerId`)
  that never had a `ClaimFollowUpAlert` raised — Process 27's own definition
  of "the insurer went non-responsive on this claim." A clean, purely
  insurer-attributed binary signal; no continuous "time to insurer action"
  timestamp exists anywhere in the schema to measure against
  `InsurerSlaAgreement`'s `claim_handling` type instead, so that SLA type
  stays unconsumed by this process (a documented, deliberate gap, not an
  oversight).
- **Price** (`priceScore`) — for each of this insurer's CURRENT-version
  `Quotation`s received in the period, its premium vs. the average of every
  OTHER insurer's current quote on the SAME `rfqId` (only RFQs with a real
  competing quote are comparable — a sole bidder contributes nothing here).
  Cheaper-than-average scores above 100 capped at 100 (being cheaper than
  the field is never "more than perfect"). This touches `Quotation.premium`
  (a `MONEY_DECIMAL_FIELDS` column, `money-decimal-jod.md`) — the whole
  calculation stays in `Prisma.Decimal` via `money.util.ts`'s `sumMoney`/
  `toMoney`, never a raw JS float division of two premiums.
- **Service quality** (`serviceQualityScore`) — the average of
  `ComparisonMatrixRow.serviceScore`, the EXISTING optional 0-100 subjective
  score a Placement Officer can supply when building a Quote Comparison
  (Process 14). That column's own doc comment says outright: "there is no
  Insurer-scoring module yet" — this process is exactly that module. Scoped
  by `ComparisonMatrix.builtAt` falling in the period. Sparse by design (the
  column is optional) — most periods for most insurers will have none.

## The neutral-default fallback

Any dimension with **no computable data** for an insurer's period (no RFQ
sent, no claims notified, no comparable quotes, no subjective score
supplied) gets `NEUTRAL_SCORE = 50.00`, not 0 (which would read as "performed
badly" on no evidence) or 100 (which would read as "performed perfectly" on
no evidence). This is uniform across all four dimensions — one rule, not a
bespoke per-dimension fallback — and it is the reason **every insurer gets a
score every period**, including one with zero activity at all.

## Why the manual trigger recomputes ONE insurer, not "everybody"

The first draft exposed `POST /insurer-performance/compute` with no
`insurerId` — recompute every insurer in the book, mirroring the batch
`computeScores` the scheduler itself runs. **This broke immediately against
the shared `db-test` database**: this session's `Insurer` table had
accumulated **2,726 rows** from months of e2e fixtures across every other
module's spec files, and iterating every one of them (several Prisma queries
each) timed out a 30-second e2e test with "Engine is not yet connected"
errors — a real connection-pool-pressure symptom, not a flaky assertion.

The fix was **not** a test-only workaround — it's the correct API shape,
matching a precedent already in this codebase:
`POST /up-sell-recommendations/detect` takes a **mandatory** `customerId`
(`DetectUpSellDto.customerId`) — there is no "detect for everyone" HTTP
route; only `UpSellDetectionScheduler` iterates the whole book, internally,
on its own cadence. `InsurerPerformanceController.compute` now follows the
same shape: `ComputeInsurerPerformanceDto.insurerId` is required, and
`InsurerPerformanceService.computeScores` (the all-insurers batch) is
**never called from the controller** — only from
`InsurerPerformanceScheduler`. A manual trigger recomputing "everybody" was
never a real requirement; it was accidental scope picked up by mirroring the
scheduler's own batch method too literally.

`computeScores` itself was ALSO changed from a naive sequential loop to
**bounded-concurrency chunks** (`COMPUTE_CONCURRENCY = 20`, `Promise.
allSettled` per chunk) — the #56 lesson (fire independent queries
concurrently) taken one step further: fully sequential doesn't scale to a
large book, but fully unbounded `Promise.all` over thousands of insurers
would open thousands of simultaneous connections and make the pool pressure
WORSE, not better. Bounded chunks is the shape a real periodic job over an
unknown-but-growing table should have had from the start.

## Period resolution

Monthly, not nightly like every other sweep in this codebase — an insurer's
performance over a few hours is meaningless noise. `POST /compute` with no
period fields scores the UTC calendar month that just ended
(`previousUtcMonthRange`); supplying `periodLabel`+`periodStart`+`periodEnd`
together recomputes an explicit window (a backfill, or an e2e test that
can't wait on a real calendar month) — any OTHER combination (some but not
all three) is a 422. `InsurerPerformanceScheduler` runs at 06:00 UTC on the
1st of each month, clear of the 02:00-05:00 daily sweeps already scheduled.

## Upsert, not append

`@@unique([insurerId, periodLabel])` (migration
`20260911120000_add_insurer_performance_score_unique`) — a recompute for the
same insurer+period UPSERTS the existing row (new `computedAt`) rather than
accumulating a stray duplicate snapshot. Unlike `SalesTarget`'s owner-xor-
branch shape, both columns here are always non-null, so this is a plain
composite unique index — no partial-index NULL gotcha to work around.

## Permission

`insurer-performance.view` (`[BRANCH_DEPARTMENT_MANAGER,
EXECUTIVE_MANAGEMENT]`) — already pre-seeded ahead of #59-65 — gates every
route, including the manual compute trigger. **No new permission was needed
for this process**, unlike #58 (`kpi-dashboard.view`) and #59
(`sales-target.manage`), each of which needed exactly one new permission —
the `internal-controls.audit` "Run audit now" precedent: the same audience
who views a report is trusted to trigger an on-demand recompute of it.

## Where the code lives

- `apps/api/src/modules/management-reporting/insurer-performance.
  {config,service,controller,module,scheduler}.ts` + `dto/`.
- `apps/api/src/repositories/insurer-performance.repository.ts`.
- `apps/web/app/(app)/insurer-performance/page.tsx` +
  `lib/management-reporting/insurer-performance-api.ts`.

## Out of scope for this file

#61's `EmployeePerformanceRecord` (a periodic job with its own model, not
touched here). Reconciling a subjective `serviceScore` average against an
objective dimension if they're ever weighted into one combined figure — the
backlog names four SEPARATE scores, not one blended index, and this process
kept them separate. `InsurerSlaAgreement`'s `response_time`/
`policy_issuance` SLA types remain unconsumed by any process.
