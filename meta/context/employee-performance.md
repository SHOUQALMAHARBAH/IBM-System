# Employee Performance (Process 61)

**Last verified:** 2026-09-12 · **Owner:** Branch/Department Manager, Executive
Management (roles, not yet named people)

## What this is

Backlog Part C #61, the fourth Domain G item — "Employee Performance —
`EmployeePerformanceRecord`: a periodic job: new clients/premium/commission/
renewal rate/cross-sell rate." Like #60, `EmployeePerformanceRecord` already
exists in the core schema (Part 13) with zero prior readers/writers — this
process is its first real consumer, alongside two OTHER dormant pieces:
`Employee` itself (Domain H / backlog #66, Human Resources, is not built —
no application code has ever created an `Employee` row) and `User.employeeId`
(the FK that would link a login account to one — no writer sets it either).

## Resolving "employee" to something scoreable

Every business signal this process needs (`Lead.ownerUserId`,
`Prospect.salesOwnerUserId`, `Policy.placedByUserId`, `Customer.ownerUserId`)
is keyed by **`User.id`**, not `Employee.id`. `EmployeePerformanceService`
resolves `Employee -> User` via `User.employeeId` before computing anything;
an employee with no linked `User` account has nothing to compute (404 on the
manual trigger, silently skipped by the scheduler's batch — there is no
partial record for someone with zero attributable activity because there is
no `userId` to query with in the first place).

## The five metrics, and why each was picked

- **`newClients`** (always a real number, 0 when there is no activity) —
  `Customer` rows created in the period, attributable via
  `Customer.prospectId -> Prospect.salesOwnerUserId` (the
  `SalesPerformanceService`/#59 precedent). A Customer onboarded with no
  Prospect at all is not attributable to anyone — the same documented gap
  #59 already established for `Customer.prospectId` being optional.
- **`premiumWritten`** (always a real amount, 0.000 when there is no
  activity) — `SUM(Policy.issuedPremium)` for policies this employee PLACED
  (`Policy.placedByUserId`), issued, with `Policy.createdAt` in the period.
  Unlike #59's caution about premium attribution (which was specifically
  about crediting a SALES OFFICER — unreliable, since `placedByUserId` names
  the PLACEMENT officer, a different role), attributing premium to WHOEVER
  PLACED the policy is a clean, direct, single-hop relationship — #61 scores
  employees generically, not sales officers specifically, so this dimension
  works here where it didn't for #59. `Policy` carries no dedicated "issued
  at" timestamp (the `PLACEMENT_CONFIRMED -> ISSUED` transition only lives
  in `AuditLogEntry`), so `createdAt` (when placement was recorded) is the
  period anchor instead — a documented simplification, not an oversight.
- **`commissionEarned`** (always a real amount) — `SUM(CommissionLedgerEntry.
  amount)` on policies this employee placed, `CommissionLedgerEntry.
  createdAt` in the period. A plain gross figure, no netting against
  `reversedAmount` — the `kpi-dashboard.md` `commissionThisMonthJod`
  precedent, kept consistent here.
- **`renewalRatePercent`** (`null` when nothing to rate, a real 0-100
  otherwise) — of this employee's placed policies' `RenewalCase`s TRIGGERED
  in the period that reached a terminal outcome (`RENEWED`, `LAPSED`, or
  `CANCELLED` — `IN_PROGRESS` etc. are excluded, still open, no outcome
  decided yet), the proportion `RENEWED`. **`RenewalCase` has no writer
  anywhere in this codebase today** — the renewal module isn't built (this
  brain's own workspace-updates history: "Domain C's remaining edges... wait
  on the renewal / reporting modules") — so this will genuinely return
  `null` for every employee until that module lands. Implemented anyway,
  forward-compatible (the #48/#56 dormant-feature precedent), and PROVEN
  correct in the e2e suite by seeding `RenewalCase` rows directly via Prisma
  (the #56 "plant a row bypassing the normal write path to prove the query
  logic itself is right" precedent).
- **`crossSellRatePercent`** (`null` when nothing to rate) — of
  `CrossSellOpportunity` rows for customers this employee OWNS
  (`Customer.ownerUserId`), DETECTED in the period, that have been RESOLVED
  (`CONVERTED` or `DISMISSED` — a still-`OPEN` one is excluded, no outcome
  yet), the proportion `CONVERTED`. Unlike renewal, Cross-Sell (#8) is a
  real, fully working process with genuine conversions — this dimension
  produces real, non-null data today.

## Why the two rate fields are `null`, not `0`, with no denominator

`EmployeePerformanceRecord.renewalRatePercent`/`crossSellRatePercent` are
**nullable columns by the schema's own original design** — unlike #60's
`InsurerPerformanceScore` (whose four score columns are NOT nullable, which
is why #60 needed a `NEUTRAL_SCORE = 50.00` fallback), #61 can express "no
outcomes existed to rate this period" as a genuine `null`, distinct from a
computed `0%` ("outcomes existed and none succeeded"). `ratePercentOrNull`
is the one place this rule lives — no per-metric special-casing elsewhere.
`newClients`/`premiumWritten`/`commissionEarned` never need this distinction:
a count or a sum always has a well-defined zero, so those three are always a
real number, never null, even with zero activity.

## The #60 lesson applied proactively, not rediscovered

`POST /employee-performance/compute` requires `employeeId` from the FIRST
draft — #60 discovered mid-build that an unscoped "recompute everybody"
manual trigger breaks against a large, e2e-fixture-bloated table (`Insurer`
had accumulated 2,726 rows in this session's shared `db-test`). `Employee`
has the same accumulation risk over time, so this process started with the
`up-sell-recommendations/detect` / `insurer-performance/compute` shape
already in place: the manual trigger names one employee;
`EmployeePerformanceService.computeRecords` (every linked employee) is
called ONLY by `EmployeePerformanceScheduler`, in `COMPUTE_CONCURRENCY = 20`
bounded chunks via `Promise.allSettled`, never through the HTTP layer.

## Upsert, not append

`@@unique([employeeId, periodLabel])` (migration
`20260912120000_add_employee_performance_record_unique`) — both columns
always non-null, the `InsurerPerformanceScore` shape (not `SalesTarget`'s
partial-index one) — makes a recompute UPSERT the existing row.

## Permission

`employee-performance.view` (`[BRANCH_DEPARTMENT_MANAGER,
EXECUTIVE_MANAGEMENT]`) — already pre-seeded — gates every route, including
the manual compute trigger. No new permission was needed, the #60
`insurer-performance.view` precedent (the same audience who views the report
is trusted to trigger an on-demand recompute of it).

## A shared utility promoted, not duplicated

`previousUtcMonthRange`/`PeriodWindow` moved from `insurer-performance.
config.ts` to `common/period.util.ts` once this process needed the identical
calculation — `insurer-performance.config.ts` re-exports both so its
existing imports keep working unchanged (the `calendar-date.util.ts`/
`policy.config.ts` promotion precedent).

## Where the code lives

- `apps/api/src/modules/management-reporting/employee-performance.
  {config,service,controller,module,scheduler}.ts` + `dto/`.
- `apps/api/src/repositories/employee-performance.repository.ts`.
- `apps/api/src/common/period.util.ts` (shared with #60).
- `apps/web/app/(app)/employee-performance/page.tsx` +
  `lib/management-reporting/employee-performance-api.ts`.

## Out of scope for this file

Domain H / backlog #66 (Human Resources) — a real `POST /employees` /
employee-onboarding flow, and whatever links a new hire's `User` account to
their `Employee` record, is a separate, not-yet-built process. The renewal
module (Domain C's remaining edge) — the day it exists and starts writing
real `RenewalCase` rows, `renewalRatePercent` starts producing real numbers
with no further change needed here.
