# Strategic Planning Inputs (Process 65)

**Last verified:** 2026-09-15 · **Owner:** Executive Management (role, not
yet a named person)

## What this is

Backlog Part C #65 — "Strategic Planning Inputs: export portfolio/market
data for planning cycles." The last Domain G item built (#64, Executive
Management Reporting, is deliberately not built yet). No new model,
migration, or scheduler. Composes TWO already-built reports:

- **portfolio** — the SAME four breakdowns #62 (`PortfolioAnalysisService.
  summary()`) already computes: byLine/byInsurer/byClientSegment/
  byGeography, a current-state book snapshot with no period.
- **market** — every insurer's `InsurerPerformanceScore` (#60) for ONE
  period — quote-response speed/claims service/price/service quality, the
  closest existing signal for "the state of the market this broker places
  business with."

This is the first genuinely new capability shape in this codebase: an
**export**, not a dashboard read. No file/CSV/download precedent existed
anywhere before this process — the response stays a plain JSON payload
(the established convention every other report in this codebase already
uses); "export" means composing a structured snapshot for an external
planning tool to consume, not producing a downloadable file.

## The universal cross-module rule, applied to TWO repositories at once

This codebase has a single, load-bearing, zero-exception architectural
rule verified by inspecting every cross-module `import` in `apps/api/src/
modules/`: **a module that needs another domain's data imports that
module's REPOSITORY export, never its SERVICE.** `CustomerModule` exports
only `CustomerRepository` (never `CustomerService`); `PolicyModule`/
`RecommendationModule` (imported into `FinanceModule`) export only their
repositories too. #63 extended this to a repository SHARED, provided
independently in two modules with zero `imports`/`exports` wiring between
them (`ProfitabilityPolicyRepository`).

#65 needed the SAME treatment for TWO repositories at once —
`PortfolioAnalysisRepository` (#62) and `InsurerPerformanceRepository`
(#60) — both provided independently in `PlanningExportModule`'s own
`providers` array, with ZERO changes to `PortfolioAnalysisModule` or
`InsurerPerformanceModule`. `PlanningExportService` reuses their exported
PURE derivation functions directly (`deriveLineOrInsurerBreakdown`,
`reduceByClientSegment`, `reduceByGeography` from `portfolio-analysis.
config.ts`; `deriveInsurerPerformanceScoreView` from `insurer-performance.
config.ts`) — the actual reduction logic is never duplicated, only the
thin `Promise.all` + name-resolution orchestration glue every composing
report in this codebase (e.g. #40's own `FinancialReportService.
summary()`) already repeats for itself. Injecting `PortfolioAnalysisService`/
`InsurerPerformanceService` directly was considered and rejected — it would
have been the FIRST exception to a rule with zero exceptions elsewhere in
65 built processes.

## Permission — the narrowest Domain G grant

`planning-export.generate` (`packages/db/prisma/seed-data/permissions.ts`)
grants `[EXECUTIVE_MANAGEMENT]` ONLY — no `BRANCH_DEPARTMENT_MANAGER`
(unlike #58-62), no `FINANCE_COLLECTIONS_OFFICER` (unlike #63's own
deviation). Already pre-seeded — zero seed change. `EXTERNAL_AUDITOR`
deliberately excluded, the #57 lesson.

A POST route (`POST /planning-export`), not a GET, even though it is a
pure read with no persisted side effect of its own — the permission's own
verb ("generate") matches the `internal-controls.view` "Run audit now"
button shape (a GET gated by a `.view`-suffixed permission, but presented
as an action the user triggers) more than the plain auto-loading `.view`
dashboards #58-63 use.

## The first real writer of `AuditAction.EXPORT`

`AuditAction.EXPORT` has existed in the core schema's enum since before
this session's work began, and `AuditAnomalyDetectionService.evaluate()`
(Part 10.3) has ALREADY been checking for it — `checkBulkExport` fires
whenever an `AuditLogEntry` with `action: 'EXPORT'` is written, flagging a
`BULK_EXPORT` `AccessAnomalyAlert` if one user exceeds
`BULK_EXPORT_THRESHOLD` EXPORT actions in `BULK_EXPORT_WINDOW_MINUTES`.
No process before #65 had ever written an `EXPORT` audit row — this is
the first. `AuditService.record()` calls `anomalyDetection.evaluate()`
automatically after every write, so `PlanningExportService`'s own
`safeAudit` call needed NO extra wiring to activate this dormant detector
— the same "dormant, forward-compatible feature, proven by its first real
writer" pattern as #48/#56/#60/#61's own findings.

## Period semantics

`portfolio` has no period concept (always the current book, matching #62).
`market` scopes to ONE `periodLabel`, defaulting to the previous UTC
calendar month when omitted — `resolvePeriodLabel` reuses `common/
period.util.ts`'s `previousUtcMonthRange`, the #60/#61 default now shared
by a third consumer.

## Where the code lives

- `apps/api/src/modules/management-reporting/planning-export.
  {config,service,controller,module}.ts` — no scheduler, no dedicated
  process-specific repository (the #63 shape, extended to two shared
  repositories).
- `apps/web/app/(app)/planning-export/page.tsx` +
  `lib/management-reporting/planning-export-api.ts` — a form-triggered
  generate action, not an auto-loading dashboard (the #60/#61 "compute
  now" form shape, since this is a POST action, not a GET read).

## Out of scope for this file

Executive Management Reporting (#64) — deliberately built AFTER #65 in
this session's own build order (the user's own pacing), still not started.
An actual downloadable file format (CSV/XLSX) for this export — the
backlog says "export," but every other report in this codebase is a JSON
API response, and #65 kept that convention rather than introducing the
first file-download capability with no other precedent to anchor it.
