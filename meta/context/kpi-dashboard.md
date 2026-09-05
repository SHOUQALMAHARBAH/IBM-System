# General KPI Dashboard (Process 58)

**Last verified:** 2026-09-09 · **Owner:** Branch/Department Manager, Executive Management (roles, not yet named people)

## What this is

Backlog Part C #58 — the first item in Domain G (Management, #58–65) — is a
one-liner with no named model: "General KPI dashboard: aggregate queries
across every module above." It opens the whole Domain G narrative (#59–65
are all pre-seeded permissions with their own future model/scheduler work —
see "What's pre-seeded but not yet consumed" below).

## The scoping decision this process made

The backlog names no metric list and no model. Rather than trying to
represent every conceivable KPI across eight domains, this process
deliberately picked a **curated, low-risk set**: one plain `count` or
`groupBy`-count per domain already built, plus three money sums whose
definition is unambiguous enough not to risk silently duplicating (and
getting subtly wrong) business logic another process already owns:

- **Sales/CRM**: `totalCustomers` (a plain count), `leadsByStatus` /
  `prospectsByStatus` / `opportunitiesByStatus` (`groupBy` counts).
- **Policy**: `policiesByStatus` (`groupBy`), `totalIssuedPremiumJod`
  (`aggregate` sum of `Policy.issuedPremium` — null before issuance, so this
  only ever sums real issued premium).
- **Claims**: `claimsByStatus` (`groupBy`).
- **Finance**: `outstandingInvoicedJod` (sum of `Invoice.totalAmount` where
  `status = 'INVOICED'` — the SAME "outstanding" definition #33's
  accounts-receivable ageing report already uses), `invoicesByStatus`
  (`groupBy`), `commissionThisMonthJod` (sum of `CommissionLedgerEntry.
  amount` created since the 1st of the current UTC month — no netting/
  clawback logic, a plain gross figure).
- **Customer Service**: `complaintsByStatus` (`groupBy`),
  `openServiceRequests` (a plain filtered count, `status IN ('open',
  'in_progress')`).
- **Compliance & Risk**: `openRiskRegisterItems` / `openIncidents` /
  `openInternalAuditFindings` (three plain filtered counts).

**Deliberately NOT attempted**: "outstanding payables owed to insurers."
#34's insurer-accounts-payable definition nets out the broker's own
commission deduction — reproducing that correctly here would mean either
duplicating #34's business logic (a second place that could drift out of
sync) or getting it subtly wrong. A general KPI glance doesn't need that
precision; the real, precise figure lives at `GET /insurer-accounting/
payables` (#34) and the consolidated `GET /financial-report` (#40).

## Why this reads every table directly — no cross-module service calls

`FinancialReportService` (#40) already composes almost exactly this kind of
finance summary (`receivables.outstandingTotal`, `payables.
outstandingAmount`, a commission roll-up, profitability). It would have
been possible to inject `FinancialReportService`/`SlaDashboardService`/
`ClaimsAnalyticsService` into this new module and pull a few fields from
each. **This was deliberately NOT done**, for two reasons:

1. **No precedent for it anywhere in this codebase.** Every prior
   cross-cutting reporting module (`SlaDashboardModule` #43,
   `InternalControlsModule` #56, `AuditTrailModule` #57) reads its
   underlying tables DIRECTLY via its own repository — none of them calls
   into another domain's service to get a number. Following that pattern
   here keeps this module consistent with the rest of the codebase rather
   than introducing a new, one-off "compose other dashboards' services"
   shape.
2. **It would have needed modifying two unrelated modules' `exports`
   arrays** (`FinanceModule` currently exports only `InvoiceRepository`;
   `SlaDashboardModule` exports nothing at all) just to make this one new
   module possible — a wider blast radius than a self-contained new
   repository needs.

`KpiDashboardRepository` therefore has **zero dependency on any other
domain's service** — only `PrismaService`. Every method is a genuine
DB-side `count`/`groupBy`/`aggregate` call, never a `findMany` reduced in
JS — so unlike `SlaDashboardRepository`/`InternalControlsService` (which
load rows into memory and are capped with a truncation warning), **there is
no read-limit concept here at all**: the result size of a `count`/`groupBy`/
`aggregate` call is always small regardless of how many underlying rows
exist.

## The concurrency lesson applied from the start

#56's own build discovered, via an e2e timeout, that firing many
independent read queries sequentially against this session's long-lived
`db-test` database is measurably slow. This process applied that lesson
from the first draft rather than rediscovering it: all fifteen queries in
`KpiDashboardService.summary()` run inside one `Promise.all`, not a
sequential loop.

## Permission

`kpi-dashboard.view` (`[BRANCH_DEPARTMENT_MANAGER, EXECUTIVE_MANAGEMENT]`)
is a genuinely NEW permission — unlike #59–65's permissions (see below),
this one was not pre-seeded ahead of time. `EXTERNAL_AUDITOR` is
deliberately excluded: #57 already established that the External Auditor's
scope is "logs, documents, workflow history" (Part 5.1), not live business
KPI content — a general KPI dashboard showing premium/commission/pipeline
figures is squarely business content, not an audit trail.

## What's pre-seeded but not yet consumed (Domain G, #59–65)

The FULL Domain G permission grid was seeded ahead of time, the same "seed
before the code" pattern this whole Part C effort has followed since Part
B: `dashboard.sales.view` (#59), `dashboard.policy.view` /
`dashboard.claims.view` / `dashboard.financial.view` /
`dashboard.compliance.view` (five separate department dashboards — the
"six management dashboards" the root `README.md` names, the sixth being
Insurer/Employee Performance below), `insurer-performance.view` (#60, needs
a new `InsurerPerformanceScore` model + a periodic job),
`employee-performance.view` (#61, needs a new `EmployeePerformanceRecord`
model + a periodic job), `dashboard.executive.view` (#64 — "Executive
Management Reporting," explicitly deferred to "Part E below" in the
backlog's own text — this is NOT the same permission as `kpi-dashboard.
view`, and #58 does not attempt to satisfy #64), `portfolio-analysis.view`
(#62), `profitability-analysis.view` (#63 — already partly covered by
`FinancialReportService`'s own `profitability` section from #40, may need
only a dedicated read surface rather than new aggregation logic when
picked up), `planning-export.generate` (#65).

## Where the code lives

- `apps/api/src/modules/management-reporting/kpi-dashboard.
  {config,service,controller,module}.ts`.
- `apps/api/src/repositories/kpi-dashboard.repository.ts`.
- `apps/web/app/(app)/kpi-dashboard/page.tsx` +
  `lib/management-reporting/kpi-dashboard-api.ts`.

## Out of scope for this file

Any of #59–65's own dedicated dashboards, models, or periodic jobs — each
is a separate backlog item with its own permission already seeded, to be
picked up in its own pass. Reconciling this dashboard's simplified finance
figures with #40's more precise ones if they're ever shown side by side —
they answer different questions (a fast glance vs. a full report) and are
not meant to reconcile to the fils.
