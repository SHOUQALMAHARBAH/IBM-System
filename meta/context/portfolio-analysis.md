# Portfolio Analysis (Process 62)

**Last verified:** 2026-09-13 · **Owner:** Branch/Department Manager, Executive
Management (roles, not yet named people)

## What this is

Backlog Part C #62, the fifth Domain G item — "Portfolio Analysis: a query by
line/insurer/client segment/geography." Unlike #59-61 (each introducing or
consuming a dedicated periodic-snapshot model), #62 has no model of its own
at all — it is a pure, on-demand, current-state read over `Policy` and its
joined tables. There is no scheduler, no migration, and no new permission:
the lightest Domain G process built so far.

## Resolving "line/insurer/client segment/geography" to real fields

The backlog names four breakdown dimensions with no fields. Each was mapped
to the cleanest existing signal:

- **line** → `Policy.insuranceLine` (a display-ready string already).
- **insurer** → `Policy.insurerId`, resolved to `Insurer.name`.
- **client segment** → `Customer.customerType` (`CORPORATE`/`INDIVIDUAL`) —
  the only clean, existing 2-value segment field anywhere on `Customer`.
- **geography** → `Branch.name`, resolved via the customer-owning Sales
  Officer's `Customer.ownerUserId -> User.branchId -> Branch.name` — the
  ONLY structured, low-cardinality location-like field anywhere in this
  schema. `Customer.registeredAddress` and `RiskProfile.siteLabel` are both
  free text and unusable for a clean group-by. This is the broker's own
  operational geography (which branch serviced the customer), not the
  customer's physical address.

Every breakdown scopes to the same inclusion rule `kpi-dashboard.md`'s
`totalIssuedPremiumJod` already uses: `issuedPremium IS NOT NULL` (only
ISSUED policies count toward "the portfolio"), with no further date
scoping — a portfolio is a current-state snapshot, not a periodic figure
like #60/#61.

## The groupBy-vs-findMany+reduce split

`insuranceLine`/`insurerId` live directly on `Policy`, so `byLine`/`byInsurer`
are genuine DB-side `groupBy` calls (the #58 shape — no read-limit needed,
since a `groupBy` result size never scales with row count).

`Customer.customerType` and the resolved branch name both require crossing a
relation Prisma's `groupBy` **cannot** cross (it can only group by columns on
the model being queried). `byClientSegment`/`byGeography` are instead a
capped `findMany` (`PORTFOLIO_ANALYSIS_READ_LIMIT = 5000`, the
`SLA_DASHBOARD_TIMER_LIMIT` shape/value) reduced in pure JS —
`PortfolioAnalysisRepository.findPoliciesForCrossTableGrouping` loads
`issuedPremium` + the customer's `customerType`/`ownerUserId`, and
`portfolio-analysis.config.ts`'s `reduceByClientSegment`/`reduceByGeography`
do the grouping — the `SlaDashboardRepository`/`InternalControlsService`
"load + reduce + read-limit + truncation warning" shape, not #58/#60's pure
DB-aggregate shape. `PortfolioAnalysisService.warnIfTruncated` logs when the
cap is hit, naming exactly which two figures are partial.

An owner with no `branchId` on file resolves to `UNASSIGNED_GEOGRAPHY_LABEL`
(`'Unassigned'`) rather than being silently dropped from the breakdown.

## Composition and audit

`PortfolioAnalysisService.summary()` fires the three top-level queries
(`groupByLine`, `groupByInsurerId`, `findPoliciesForCrossTableGrouping`) via
`Promise.all` — the #56 concurrency lesson applied from the first draft, not
rediscovered via a timing failure. Insurer-name and branch-name resolution
happen afterward (each needs the ids from the query it resolves). A
best-effort `READ` audit row is written after the read completes
(`entityType: 'PortfolioAnalysis'`, `entityId: 'summary'`) — an audit write
failure never fails the read itself, the established `safeAudit` pattern.

## A shared utility promoted, not duplicated

`formatMoneySum` (formats a `Prisma.Decimal | null` aggregate sum, `null` ->
`'0.000'`) moved from `kpi-dashboard.config.ts` to `common/money.util.ts`
once this process needed the identical helper — `kpi-dashboard.config.ts`
re-exports it so its existing imports keep working unchanged. The same
promotion #61 did for `previousUtcMonthRange`/`PeriodWindow` (moved from
`insurer-performance.config.ts` to `common/period.util.ts`) — a helper used
by a second consumer belongs in `common/`, not duplicated.

## Permission

`portfolio-analysis.view` (`[BRANCH_DEPARTMENT_MANAGER,
EXECUTIVE_MANAGEMENT]`) was already pre-seeded ahead of time — the #60
"one Domain G process needing zero seed change" precedent repeated. Gates
the single `GET /portfolio-analysis` route. `EXTERNAL_AUDITOR` deliberately
excluded, the #57 lesson (their scope is logs/documents/workflow history,
not live business content).

## Where the code lives

- `apps/api/src/modules/management-reporting/portfolio-analysis.
  {config,service,controller,module}.ts` — no scheduler, unlike #59-61.
- `apps/api/src/repositories/portfolio-analysis.repository.ts`.
- `apps/api/src/common/money.util.ts` (`formatMoneySum`, shared with #58).
- `apps/web/app/(app)/portfolio-analysis/page.tsx` +
  `lib/management-reporting/portfolio-analysis-api.ts`.

## Out of scope for this file

Profitability Analysis (backlog #63) and Planning/Export (#64-65) — the
remaining Domain G processes, not yet built. `Customer.registeredAddress` as
a real free-text geography breakdown — deliberately not attempted; would
need a proper address-parsing/normalization step this process does not do.
