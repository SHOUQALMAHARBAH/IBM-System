# Profitability Analysis (Process 63)

**Last verified:** 2026-09-14 · **Owner:** Executive Management, Finance /
Collections (roles, not yet named people)

## What this is

Backlog Part C #63, the sixth Domain G item — "Profitability Analysis:
commission income vs. cost-to-serve per segment/line." Like #62, there is no
new model, migration, or scheduler — a pure, on-demand, current-state read.
Unlike #62, this process reuses the SAME written-policy data #40's
`FinancialReportService` already loads, reduced into a genuinely different
metric.

## Why this isn't a duplicate of #40's `netPosition`

`FinancialReportService` (#40) already has a "profitability by client
segment / line" section: `netPosition = premiumWritten - claimsPaid -
commissionEarned` — an underwriting-result view of the INSURER's side of the
book (`ibms-app` root `README.md`, Part C #40 entry). The backlog's own
phrase for #63 — "commission income vs. cost-to-serve" — asks a different
question: **is the commission the BROKER earns on this book enough to cover
what it costs the broker to service it?** That is `netProfitability =
commissionIncome - costToServe`, not `premiumWritten - claimsPaid -
commissionEarned`. Both read the identical raw policy/claims/commission
data; they reduce it differently, for different audiences (#40 is an
insurer-side underwriting view; #63 is a broker-margin view).

- **`commissionIncomeJod`** — Σ (`commissionAmount - commissionReversedAmount`)
  per group, the IDENTICAL net-of-clawback calculation #40's `commissionEarned`
  already uses. NOT #58/#61's deliberately-gross "no netting" simplification —
  this process needs the precise figure since it IS the metric, not a
  supporting context field.
- **`costToServeJod`** — Σ net settlement of the group's SETTLED / CLOSED
  claims. **A documented scoped interpretation, not a true operational
  cost**: no operational-expense / staff-time / overhead tracking model
  exists anywhere in this schema (Domain H / backlog #66, Human Resources,
  is not built) — claims-settlement payout is the one real cost-shaped
  figure attributable to a line/segment anywhere in the schema, so it stands
  in as the closest available signal for "what it costs to service this
  book." This is the SAME `claimsPaid` figure #40's `netPosition` already
  computes.
- **`netProfitabilityJod`** = `commissionIncomeJod - costToServeJod`. Can be
  negative (a segment costing more in claims churn than it earns in
  commission).

Grouped by `insuranceLine` and `customerType` ("segment") ONLY — the backlog
names exactly these two dimensions, unlike #62's four (no insurer, no
geography). Rows sort worst-first (most-negative `netProfitabilityJod`), the
#40 `groupProfitability` sort convention.

## The reuse pattern: promoting a repository, not a pure function

#61/#62 each promoted a small PURE utility function (`previousUtcMonthRange`,
`formatMoneySum`) from one module's config file to `common/` once a second
consumer needed it. #63 needed the same PATTERN applied to something bigger:
a non-trivial Prisma QUERY (`loadProfitabilityPolicies` — a `findMany`
joining `Policy` -> `Customer`/`Claim`/`Settlement`/`CommissionLedgerEntry`),
not a pure function.

`ProfitabilityPolicyRow` and the loader method were extracted out of
`FinancialReportRepository` (#40) into a new standalone file,
`repositories/profitability-policy.repository.ts` (`ProfitabilityPolicyRepository.
loadWrittenPolicies(limit)`), and `financial-report.service.ts` was updated
to inject the new repository directly. `finance.config.ts` re-exports the
`ProfitabilityPolicyRow` type so its existing imports keep working
unchanged — the same "original file re-exports the promoted symbol"
courtesy #61/#62 established.

**Module wiring stayed zero-coupling**: `ProfitabilityPolicyRepository` is
provided independently in BOTH `FinanceModule`'s and
`ProfitabilityAnalysisModule`'s own `providers` arrays — the SAME class,
two separate instances, both wrapping the singleton `PrismaService`. No
`imports`/`exports` wiring was added to either module. This keeps
`kpi-dashboard.md`'s "no cross-module SERVICE dependency" precedent intact
even while sharing the underlying QUERY — a NestJS provider shared this way
costs nothing at the module-graph level (`repositories/` in this codebase
has always been a shared top-level folder, not nested per-module; this is
the first time two DIFFERENT modules provide the exact same repository
class independently rather than one importing/exporting it to the other).

## Permission — a real deviation from #58-62's pattern

`profitability-analysis.view` (`packages/db/prisma/seed-data/permissions.ts`)
grants `[EXECUTIVE_MANAGEMENT, FINANCE_COLLECTIONS_OFFICER]` — **NOT**
`BRANCH_DEPARTMENT_MANAGER`, unlike every #58-62 Domain G permission. Already
pre-seeded — zero seed change, the #60/#62 "third Domain G process needing
no seed change" precedent. `EXTERNAL_AUDITOR` deliberately excluded, the #57
lesson.

## Sensitive-data audit

The `costToServe` figure aggregates HIGHLY_CONFIDENTIAL `Claim` settlement
data whenever a settled claim contributed — `ProfitabilityAnalysisService`
flags `isSensitiveDataAccess: summary.totals.claimCount > 0` on its
best-effort READ audit row, the exact #40 `recordReadBestEffort` rule.

## Where the code lives

- `apps/api/src/modules/management-reporting/profitability-analysis.
  {config,service,controller,module}.ts` — no scheduler, no dedicated
  process-specific repository (unlike #58-62, which each have their own).
- `apps/api/src/repositories/profitability-policy.repository.ts` — shared
  with `FinanceModule` (#40).
- `apps/web/app/(app)/profitability-analysis/page.tsx` +
  `lib/management-reporting/profitability-analysis-api.ts`.

## Out of scope for this file

Executive Management Reporting (#64) and Strategic Planning export (#65) —
the remaining Domain G processes, not yet built. A true operational
cost-to-serve model (staff time, overhead, claims-handling effort) — would
require Domain H / backlog #66 (HR) or a new expense-tracking model neither
of which exist; `costToServeJod` stays a documented claims-payout proxy
until one does.
