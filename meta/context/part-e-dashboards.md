# Part E — Dashboards & Management Reporting (Part 13)

**Last verified:** 2026-09-07 (Financial Dashboard added) · **Owner:** Branch/Department Manager, Executive Management (roles, not yet named people)

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

## Claims Dashboard

Bullet text: "open vs. closed claims, outstanding claims value, claims
ageing, loss ratio by client/line/insurer." A NEW endpoint, `GET
/dashboards/claims`, gated by the already-pre-seeded `dashboard.claims.view`
(its first real consumer, same shape as Policy Dashboard's own
`dashboard.policy.view`).

**Every one of this bullet's four metrics is a CURRENT-STATE noun, not a
period-scoped event** — unlike Sales/Policy Dashboards, there is no "claims
opened this period" phrasing anywhere. So Claims Dashboard carries NO
`periodStart`/`periodEnd` range at all; every metric is a live snapshot.
Part E's own cross-cutting rule still demands "filterable by... time
period," so a single `asOf` REFERENCE-DATE override is exposed instead of a
range (the #33 AR ageing report's own shape) — the honest reading of "time
period" for a dashboard whose every metric is a point-in-time snapshot
rather than a range-scoped count. `asOf` narrows which claims are
considered (`createdAt < asOf-exclusive-upper-bound`) but classifies each by
its CURRENT `Claim.status`, not the status it held as of that date — a
documented limitation (full reconstruction would need to walk
`ClaimStatusHistory`), the same shape as the AR ageing report's own "a
receipt means paid in full" simplification.

**"Open vs. closed"**: `CLOSED` is the ONLY terminal `ClaimStatus`
(`WORKFLOW_TRANSITIONS.Claim` — reachable only via `DECLINED -> CLOSED` or
`SETTLED -> CLOSED`), so "open" is simply "status != CLOSED."

**"Outstanding claims value"** sums, over every OPEN claim, the more precise
figure once known: `Settlement.netSettlement` when a settlement already
exists (a claim can be `SETTLED` but not yet `CLOSED`), else
`Claim.estimatedLoss` — the same "netSettlement is the ground truth once
available" precedent `computeLossRatio` itself uses for `periodClaims`.

**"Claims ageing"** buckets each open claim by whole days between
`Claim.createdAt` (the NOTIFIED moment) and `asOf`. Unlike
`AR_AGEING_BUCKET_KEYS` (which has a `current`/"not yet due" bucket), an
open claim starts ageing from day zero, so the new `CLAIMS_AGEING_BUCKET_
KEYS` begin at `d0_30` (then `d31_60`/`d61_90`/`d90_plus`) — the same 30/60/
90 boundary spirit, adapted since there is no "not yet due" state for an
already-open claim.

**"Loss ratio by client/line/insurer" needed a genuine schema-adjacent
widening**: Process 30's own `LOSS_RATIO_GROUP_BY` only carried `['customer',
'policy', 'line']` — no insurer dimension. Widened it to add `'insurer'`
(and `AnalyticsPolicyLike`/`AnalyticsPolicyRow` to carry `insurerId`/
`insurerName`) rather than writing a Claims-Dashboard-local copy, since a
groupBy union is exactly the kind of thing meant to grow. **This is a real,
free capability upgrade to the pre-existing `GET /claims-analytics/
loss-ratio?groupBy=` endpoint too** — its DTO validates against the same
constant, so `groupBy=insurer` now works there as well, with zero code
changes to that controller/service. The three breakdowns (`lossRatioByClient
`/`lossRatioByLine`/`lossRatioByInsurer`) are the SAME pre-existing, all-time
`buildLossRatioBreakdown` pure function called three times over one fetched
policy set — the #62 Portfolio Analysis "several breakdowns in one response"
shape. Reused via a direct import of a PURE function — one step lighter than
#63 Profitability Analysis's own repository-injection precedent (no DI
wiring at all needed for a pure function). `computeLossRatio`'s own
documented "all-time" scope is untouched, so `asOf` never affects it.

**`LossRatioRepository` is reused the #63 way**: `ClaimsDashboardModule`
provides its own `LossRatioRepository` instance directly (`imports: []`, no
`LossRatioModule` wiring) — the same class independently instantiated in two
modules' own `providers` arrays, both wrapping the singleton `PrismaService`,
exactly like `ProfitabilityPolicyRepository` is shared between
`FinanceModule` and `ProfitabilityAnalysisModule`.

Filter applicability: `branchId` (-> `Policy.placedByUserId` via the `Claim
-> Policy` relation), `insuranceLine`, and `insurerId` all scope every
metric uniformly — every one of this dashboard's reads ultimately goes
through a `Claim`'s owning `Policy`, so (like Policy Dashboard, unlike Sales
Dashboard) there is no per-metric carve-out to document.

Audited as a sensitive READ (`isSensitiveDataAccess: true` unconditionally,
since `Claim` is HIGHLY_CONFIDENTIAL by default) — the snapshot records
counts only, never `Cancellation`-style free text (there is none on this
dashboard) nor individual claim references.

**Test-isolation note**: unlike Sales/Policy Dashboards (isolated by a
distinctive historical PERIOD window), Claims Dashboard's own `createdAt <
asOf` scope has NO lower bound, so a date window alone cannot isolate one
e2e test's figures from `db-test`'s cumulative history. Its own e2e spec
isolates instead via a freshly-created, uniquely-named `Insurer` row and the
`insurerId` filter — every fixture claim is placed through a policy with
that insurer, so filtering the dashboard read by that same `insurerId`
returns exactly (and only) that test's own rows, safe for exact-equality
assertions.

### Where the code lives (Claims Dashboard)

- `apps/api/src/modules/management-reporting/claims-dashboard.
  {config,service,controller,module}.ts` +
  `repositories/claims-dashboard.repository.ts`.
- Widened: `modules/loss-ratio/loss-ratio.config.ts` (`LOSS_RATIO_GROUP_BY`
  + `AnalyticsPolicyLike`) and `repositories/loss-ratio.repository.ts`
  (`AnalyticsPolicyRow` + `loadPoliciesForAnalytics` scope).
- `apps/web/app/(app)/dashboards/claims/page.tsx` +
  `lib/management-reporting/claims-dashboard-api.ts`.

No migration, no new permission.

## Financial Dashboard

Bullet text: "receivables and ageing, payables to insurers, commission
income and outstanding commission, profitability by client segment/line."

**This is neither a fresh build nor a pure "verify, don't build" outcome —
a third, in-between shape.** Backlog #40 (`FinancialReportService.summary()`,
`GET /financial-report/summary`) already computes every one of these four
sections verbatim — its own doc comment quotes this exact Part E bullet.
But #40's own `FinancialReportQueryDto` says outright: "No line / insurer /
branch filters here — those are a Part E dashboard refinement." That is the
ONE genuine gap between #40 and Part E's cross-cutting "filterable by
branch/line/insurer/period" rule, and this dashboard supplies it.

**Reused #40's own PURE builders via direct import** —
`buildReceivablesAgeing` / `buildInsurerPayables` / `buildCommissionRollup` /
`buildProfitability`, all untouched — rather than re-deriving a single line
of bucket/rollup/`netPosition` math. The Claims Dashboard "reuse a pure
function directly" precedent, applied to four functions in one module
instead of one. `GET /dashboards/financial`'s own `financial-dashboard.
config.ts` is almost entirely a composition function, not new business
logic.

**Widened the THREE repositories that feed those builders** with optional
`insuranceLine`/`insurerId`/`ownerUserIds` scope params — all additive, so
no existing caller's call site changed:
- `InvoiceRepository.loadOutstandingReceivables` (#33) — narrowed via the
  invoice's OPTIONAL `policy` relation (`Invoice.policyId` is nullable), so
  an invoice with NO linked policy is excluded whenever any of the three is
  given — a filter on the underlying policy cannot include a receivable
  with no policy to check it against.
- `InvoiceRepository.loadInsurerObligations` (#34) — `insurerId` already
  existed; added `insuranceLine`/`ownerUserIds` the same way, via the
  policy relation (guaranteed present on this query already).
- `InvoiceRepository.loadInsurerRemittances` (#34) — **deliberately NOT
  widened** beyond its existing `insurerId`. A `Remittance` is a lump
  payment against one insurer with no `Policy` relation of its own
  (it can cover many invoices/lines/branches in one payment), so
  `insuranceLine`/`branchId` genuinely cannot narrow it — a real "not
  applicable" case, the Sales Dashboard "filter applicability is real, not
  uniform" discipline, not a shortcut.
- `FinancialReportRepository.loadCommissionRollupEntries` (#40) — added all
  three (no existing filter at all before).
- `ProfitabilityPolicyRepository.loadWrittenPolicies` (#40/#63, a SHARED
  repository) — added an optional trailing `scope` param; `#63`
  Profitability Analysis's own call site is untouched and re-confirmed
  green.

**Every section is current-state, like Claims Dashboard — no period
range**, mirrored exactly from #40's own pre-existing design (not a new
choice): receivables/payables are point-in-time at a single `asOf`
reference date; commission/profitability have no date dimension at all
(the commission ledger and `Policy.issuedPremium` are not time-versioned).
`asOf` therefore scopes ONLY receivables/payables.

**`dashboard.financial.view`'s role grant (`[FINANCE, MANAGER, EXEC]`) is a
strict SUBSET of `financial-report.view`'s (`+ EXTERNAL_AUDITOR`)** — so
there was no practical access gap to close via the Notices "also accepts
consent.manage" `RequirePermissions`-widening trick (confirmed by mapping
each seed-file role alias: `FINANCE = FINANCE_COLLECTIONS_OFFICER`,
`MANAGER = BRANCH_DEPARTMENT_MANAGER`, `EXEC = EXECUTIVE_MANAGEMENT`).
Kept as its own dedicated Part E permission on a genuinely separate route
instead — this endpoint's needs (branch/line/insurer filtering) really do
differ from #40's, unlike Notices' two identical-need callers.

### Where the code lives (Financial Dashboard)

- `apps/api/src/modules/management-reporting/financial-dashboard.
  {config,service,controller,module}.ts` +
  `repositories/financial-dashboard.repository.ts` (just
  `findUserIdsInBranch` — every other repository is reused directly, the
  #63 "share the repository, not the service" shape: `InvoiceRepository`,
  `FinancialReportRepository`, `ProfitabilityPolicyRepository` are each
  independently re-provided in `FinancialDashboardModule`'s own `providers`
  array, zero `imports`/`exports` wiring to `FinanceModule`).
- Widened: `repositories/invoice.repository.ts`,
  `repositories/financial-report.repository.ts`,
  `repositories/profitability-policy.repository.ts`.
- `apps/web/app/(app)/dashboards/financial/page.tsx` +
  `lib/management-reporting/financial-dashboard-api.ts`.

No migration, no new permission.

## Out of scope for this file

The Compliance Dashboard and the Insurer & Employee Performance
verification — each a separate pass, to be added to this same file as they
land (the `data-retention-and-disposal.md` "grow one file per completed
sub-system" shape, since all six are one backlog item, Process #64). The
`dashboard.executive.view` cross-department rollup screen itself — not yet
built. `#59`'s own `SalesTarget` quota-tracking design —
`ibms-brain/meta/context/sales-performance.md`.
