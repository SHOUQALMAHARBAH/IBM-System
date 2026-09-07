# Part E — Dashboards & Management Reporting (Part 13)

**Last verified:** 2026-09-07 (Policy Dashboard added) · **Owner:** Branch/Department Manager, Executive Management (roles, not yet named people)

## What this is

The backlog's Part E header cross-references Domain G's own **Process #64,
"Executive Management Reporting"**, whose entire one-liner reads "Part E
below" — Part E IS Process #64's full detail, not six unrelated processes.
Six named dashboards: Sales, Policy, Claims, Financial, Compliance, and
Insurer & Employee Performance, plus a cross-cutting rule ("every dashboard
filterable by branch/line of business/insurer/time period, and renderable
in either language").

**The permission grid was pre-seeded for exactly this** — `dashboard.sales.
view`, `dashboard.policy.view`, `dashboard.claims.view`, `dashboard.
financial.view`, `dashboard.compliance.view` (the five department
dashboards), `insurer-performance.view` + `employee-performance.view` (the
sixth, already-built as backlog #60/#61), and `dashboard.executive.view`
(#64's own top-level code, for a future cross-department rollup screen —
see `ibms-brain/meta/context/kpi-dashboard.md`, which flagged all of this
ahead of time: "#59–65 are all pre-seeded permissions with their own future
model/scheduler work"). Worked one dashboard at a time, per the user's
established Part D pacing default (an explicit "finish everything" request
is a one-time override, not the norm — see `feedback_backlog_pacing`).

## Sales Dashboard

Bullet text: "new leads and conversion rate, premium written (new vs.
renewal), commission income, cross-sell/up-sell opportunity conversion."

**`dashboard.sales.view` is ALREADY consumed by backlog #59's own `GET
/sales-performance`** (quota-vs-actual `newProspects` tracking against a
`SalesTarget`) — that endpoint is untouched. This is a SEPARATE, broader
endpoint, `GET /dashboards/sales`, sharing the same permission code on
purpose: both are genuinely "the sales dashboard" from an access-control
point of view, and #59's own module doc comment already anticipated a
sibling consumer for this code. A NEW NestJS module
(`SalesDashboardModule`), not an extension of `SalesPerformanceModule` —
the metric sets are genuinely different (Lead/Prospect quota-tracking vs.
premium/commission/cross-sell/up-sell), and conflating them under one
endpoint would mean two different backlog items writing to one payload.

**Filter applicability is real, not uniform** — the cross-cutting "every
dashboard filterable by branch/line/insurer/period" rule is honored
per-metric ONLY where the dimension exists on the underlying model, not
force-fit everywhere:
- `branchId` (resolved to the concrete `User.branchId` set, the #59
  precedent) scopes leads (`Lead.ownerUserId`) and premium/commission
  (`Policy.placedByUserId`) — NOT cross-sell/up-sell, which are
  system-detected against a `Customer` with no officer-ownership concept
  at all.
- `insuranceLine` scopes premium/commission (`Policy.insuranceLine`) AND
  cross-sell (`CrossSellOpportunity.gapLine` IS itself a line) — NOT leads
  (no line yet) or up-sell (a Sum-Insured gap, not a line dimension).
- `insurerId` scopes only premium/commission (`Policy.insurerId`) —
  nothing pre-placement has an insurer yet.
- `period` (default: the previous UTC calendar month, the all-or-none
  #60/#61 `resolvePeriodFromDto` shape — 422 on a partial override) applies
  to every metric via its own date field.

**"Premium written (new vs. renewal)"** splits on `Opportunity.isRenewal`
— a real boolean ALREADY on the schema, discovered by checking rather than
assuming a "new vs. renewal" distinction would need new modeling. Computed
via two separate `Policy.aggregate()` calls with a relation filter
(`opportunity: { isRenewal: true/false }`) — a genuine DB-side sum, never a
capped `findMany` reduced in JS. The two sums are combined into a total
using `addMoney()`/`formatMoney()` (a real `Prisma.Decimal` add), never by
parsing formatted money strings back into JS floating-point numbers — the
"never use floating point for money" rule applies even to a two-number sum
that looks trivial.

**Conversion rate is 0%, not NaN/undefined, for an empty cohort** —
`computeConversionRatePercent()` short-circuits `totalCount === 0` before
dividing, the same discipline #59's own `computeAchievementPercent` needed
a caller-side null-target guard for.

No migration, no new permission, no cross-module service dependency
(reads `Lead`/`Policy`/`Opportunity`/`CommissionLedgerEntry`/
`CrossSellOpportunity`/`UpSellRecommendation` directly — the #58 KPI
Dashboard / #62 Portfolio Analysis shape).

## Where the code lives (Sales Dashboard)

- `apps/api/src/modules/management-reporting/sales-dashboard.
  {config,service,controller,module}.ts` +
  `repositories/sales-dashboard.repository.ts`.
- `apps/web/app/(app)/dashboards/sales/page.tsx` +
  `lib/management-reporting/sales-dashboard-api.ts`.

## Policy Dashboard

Bullet text: "active policies, expiring policies (renewal window), new
policies issued, cancelled policies and cancellation reasons." A NEW
endpoint, `GET /dashboards/policy`, gated by the already-pre-seeded
`dashboard.policy.view` (its first real consumer — unlike `dashboard.sales.
view`, no earlier backlog item had touched this code yet).

**Two of the four metrics are a LIVE snapshot as of `now`; two are
period-scoped — a deliberate asymmetry, not an inconsistency to fix.**
"Active policies" and "expiring policies" describe CURRENT STATE (what's
true right now, ignoring the period filter entirely) — a `periodLabel`
override changes nothing about them. "New policies issued" and "cancelled
policies" describe an EVENT that happened WITHIN a period, so they're
scoped by `periodStart`/`periodEnd` like every other Part E metric. Both
kinds coexist on one dashboard because the backlog bullet itself mixes a
snapshot phrase ("active policies") with historical-event phrases ("new
policies issued... cancelled policies") in the same sentence.

**"Expiring policies (renewal window)" reuses `RenewalCase.leadTimeDays`'s
own existing default (90 days)** as `DEFAULT_RENEWAL_WINDOW_DAYS`, rather
than inventing an unrelated figure — keeping two related "how far ahead do
we look for a renewal" concepts numerically aligned. Exposed as a
caller-overridable `renewalWindowDays` query param (`@Type(() => Number)` +
`@IsInt() @Min(1)`, confirmed to coerce correctly under the api's global
`ValidationPipe({transform: true})`) since the backlog names no fixed
window. Computed as `Policy.count({status: 'ACTIVE', expiryDate: {gte: now,
lt: now + windowDays}})`.

**"New policies issued" reuses the KPI Dashboard's own `issuedPremium is
not null` test** for "issued" (not `status`, which can move on past
issuance) — `Policy.count({issuedPremium: {not: null}, createdAt: {gte:
periodStart, lt: periodEnd}})`.

**"Cancelled policies and cancellation reasons" uses `Endorsement.appliedAt`
— NOT `Cancellation.createdAt` — as the period-scoping date**, confirmed by
reading `EndorsementService.apply()`'s cancellation branch directly: the
`Policy.status -> CANCELLED` transition fires at the exact moment
`Endorsement.appliedAt` is stamped, right after the cancellation's financial
terms (`Cancellation.reason`/`basis`/`returnPremium`) were already recorded
earlier in the endorsement lifecycle. `Cancellation.createdAt` reflects only
when the cancellation was REQUESTED, which can predate the period in which
it actually took effect. **`reason` (free text) is returned as a capped,
ordered `findMany` list (`CANCELLED_POLICIES_READ_LIMIT = 200`), never a
`groupBy`** — the #62 Portfolio Analysis "don't group free text" precedent,
since grouping would silently fragment near-duplicate wording.

Filter applicability: `branchId` (-> `Policy.placedByUserId`),
`insuranceLine`, and `insurerId` all scope every one of the four metrics
uniformly (unlike the Sales Dashboard, every Policy Dashboard metric reads
the same `Policy` table, so there's no per-metric carve-out to document).
`period` scopes only the two event-based metrics, per the live-vs-period
split above.

The audit READ snapshot records counts only (`cancelledPoliciesCount`, not
the `cancelledPolicies` array itself) — `Cancellation.reason` is free text a
staff member wrote about a client's stated reason for leaving, kept out of
the audit trail on the same "counts, not raw content" discipline DSR's own
audit snapshots use.

### Where the code lives (Policy Dashboard)

- `apps/api/src/modules/management-reporting/policy-dashboard.
  {config,service,controller,module}.ts` +
  `repositories/policy-dashboard.repository.ts`.
- `apps/web/app/(app)/dashboards/policy/page.tsx` +
  `lib/management-reporting/policy-dashboard-api.ts`.

No migration, no new permission, no cross-module service dependency (reads
`Policy`/`Endorsement`/`Cancellation` directly).

## Out of scope for this file

Claims/Financial/Compliance dashboards and the Insurer & Employee
Performance verification — each a separate pass, to be added to this same
file as they land (the `data-retention-and-disposal.md` "grow one file per
completed sub-system" shape, since all six are one backlog item, Process
#64). The `dashboard.executive.view` cross-department rollup screen itself
— not yet built. `#59`'s own `SalesTarget` quota-tracking design —
`ibms-brain/meta/context/sales-performance.md`.
