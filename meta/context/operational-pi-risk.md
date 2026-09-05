# Operational & Professional Indemnity Risk (Process 53-54)

**Last verified:** 2026-09-05 · **Owner:** Compliance Officer (role, not yet a named person)

## What this is

Backlog Part C #53-54 has two checkboxes: "A generic risk register covering the six
categories the source explicitly names: operational/cyber/financial/compliance/
reputational (`RiskRegisterItem.riskType`) — Professional Indemnity gets its own, deeper
table" and "Track the broker's own Professional Indemnity policy (coverage limit, expiry,
claims history) — a broker without valid PI cover is itself a licensing breach." Three
models, all pre-existing "core schema" (Part 5/7.1) — genuinely no migration, no seed
change; `risk-register.manage` (`[COMPLIANCE_OFFICER, BRANCH_DEPARTMENT_MANAGER]`) and
`pi-policy.manage` (`[COMPLIANCE_OFFICER]`) were both pre-seeded ahead of time.

`RiskRegisterService`/`PiPolicyService`/`PiRiskEventService`
(`apps/api/src/modules/compliance-risk/`) extend `ComplianceRiskModule` (opened by #48).
`ProfessionalIndemnityRiskEvent` already had a real writer before this landing:
`PolicyCheckingRepository.recordChecking` (Process 20) auto-logs one, in the same
`$transaction` as the `PolicyChecking` row, the moment a coverage discrepancy is found —
this process gives those rows their first read surface, not their first writer.

## The shapes

```
RiskRegisterItem                            # unlimited rows, no PI category
  id: uuid
  riskType: operational|cyber|financial|compliance|reputational   # NOT professional_indemnity
  description: string
  mitigationAction: string?
  status: "open" | "closed"                 # @default("open") — plain string, no engine
  loggedAt: DateTime                        # backdatable (parseHistoricalInstant)
  closedAt: DateTime?

ProfessionalIndemnityPolicy                 # NOT a singleton — a renewal is a NEW row
  id: uuid
  insurerName: string
  coverageLimit: Decimal(18,3)              # JOD, money-decimal-jod.md
  expiresAt: DateTime
  claimsHistorySummary: string?
  # "current" = findFirst({ orderBy: [{expiresAt:'desc'},{id:'desc'}] })
  # — the id tiebreak is load-bearing, see @code-reviewer findings below

ProfessionalIndemnityRiskEvent              # unlimited rows, two writers
  id: uuid
  piPolicyId: string?                       # FK, nullable — null if no PI policy on file
  sourcePolicyCheckingId: string?           # set ONLY by the Process 20 auto-link
  description: string
  mitigationAction: string?
  loggedAt: DateTime
```

## The rules that aren't obvious

- **`ProfessionalIndemnityPolicy` is deliberately NOT a fixed-id singleton, unlike
  `BrokerLicense` (Process 51)** — the model has no `issuedAt`/period-start field to define
  a validity window with, so there is no way to express "this row's coverage window is
  currently in force" other than by comparing `expiresAt` values across every row; a
  renewal is therefore a brand-new row (preserving `claimsHistorySummary` per period,
  since a PAST policy's claims experience is itself a fact worth keeping, not something a
  renewal should overwrite) and "current" is simply the row that expires furthest in the
  future. This definition — `findFirst({ orderBy: { expiresAt: 'desc' } })` — pre-dates
  this process: `PolicyCheckingRepository.findLatestPiPolicyId` (Process 20/54's
  discrepancy auto-link) already needed it before `PiPolicyRepository` existed to give it
  a home. This process promotes that query into `PiPolicyRepository.findCurrent()` and has
  `PolicyCheckingRepository` delegate to it instead of carrying its own copy — one
  definition of "current," not two that could drift apart.
- **The `orderBy`'s secondary `id: 'desc'` tiebreak is load-bearing, not decorative** — a
  `@code-reviewer` BLOCKER on the first pass. `CreatePiPolicyDto.expiresAt` goes through
  `parseCalendarDate`, so any plain date (the expected input shape) normalizes to an exact
  UTC midnight — two officers entering the same calendar-year renewal date, a genuine
  multi-insurer PI tower with layers expiring the same day, or an accidental duplicate
  submission (no uniqueness guard exists on this table) all tie to the millisecond, and a
  bare `orderBy: { expiresAt: 'desc' }` gives Postgres no tiebreak, so which tied row wins
  is DB-implementation-defined and can differ between `GET /pi-policy/current`, `list()`'s
  `isCurrent` flag, and the Policy Checking auto-link — three different answers to "which
  PI record is authoritative right now," for a control whose own backlog framing calls a
  gap here a licensing breach.
- **A DELETION-style "which category" exclusion**: `RISK_REGISTER_TYPES` is exactly the
  five non-PI categories — `professional_indemnity` is not a legal `riskType` value at
  all, enforced by `@IsIn` on the DTO. The source names SIX categories total; PI gets its
  own two-model deep-dive instead of a seventh generic register row.
- **The PI risk event audit trail must NOT re-embed the coverage-figure diff a sibling
  audit row already excludes** — a `@code-reviewer` MAJOR. For an auto-logged event
  (`sourcePolicyCheckingId` set), `description` is built by `piRiskEventDescription()`
  (`policy-checking.config.ts`), which names the exact requested-vs-issued coverage
  amounts and the policy number — the SAME content `policyCheckingAuditSnapshot`
  deliberately keeps out of the `PolicyChecking` row's own audit trail
  (`ibms-brain/meta/lex/sensitive-data-handling.md` — "metadata not body," #12-19's
  precedent). `piRiskEventAuditSnapshot` redacts `description` to a placeholder for any
  row where `sourcePolicyCheckingId !== null`; a MANUAL entry's `description` (Compliance's
  own narrative, never derived from a coverage diff) stays verbatim, the
  `BrokerLicense.scopeOfAuthorization` reasoning. `mitigationAction` is never redacted
  either way — it is always fresh text a human wrote afterward, not derived content.
- **Auto-resolving a manual risk event to `findCurrent()` when `piPolicyId` is omitted
  never silently ignores a lapsed result** — a `@code-reviewer` MINOR. Rather than adding
  an `isCurrentlyLapsed` field to every future read of `PiRiskEventView` (which would need
  either an N+1 lookup per event or a bulk-fetch on every `list()` call for a fact that is
  only ever true at the moment of creation), the signal is durable in two lighter-weight
  places instead: a `logger.warn` for immediate ops visibility, and
  `linkedPolicyWasLapsedAtLogTime` in the CREATE audit row's `afterValue`, so the fact
  survives even after the PI policy is eventually renewed and no longer reads as lapsed.
- **`recordClaimsHistory` (`POST /pi-policy/:id/claims-history`) has no optimistic-
  concurrency guard, and can target ANY historical row, not just the current one** —
  accepted deliberately (documented explicitly in `pi-policy.service.ts`'s own comment
  after a `@code-reviewer` MINOR asked for the reasoning to be stated, not left implicit):
  the model has no `updatedAt`/version column to build a real guard from without a
  migration this checkbox doesn't call for, the `pi-policy.manage` user pool is small and
  single-role, and every write still produces its own accurate `UPDATE` audit row — so a
  concurrent edit's content is never unrecoverable, only the live column's value is
  momentarily contested. The exact `BrokerLicense.scopeOfAuthorization` trust level.
- **`RiskRegisterItem`, `ProfessionalIndemnityPolicy`, and `ProfessionalIndemnityRiskEvent`
  carry no `DataClassification` field** — a `@code-reviewer` MINOR, NOT fixed in this pass
  (unlike #49's BLOCKER 4 for `WatchlistEntry`, which added one): this predates the PR (no
  migration lands here at all), and properly resolving it would mean widening three
  pre-existing models rather than the narrow, checkbox-scoped work this process asks for.
  Flagged as a real open question, not resolved by analogy to `BrokerLicense.
  scopeOfAuthorization` any further than it already has been:
  `ProfessionalIndemnityPolicy.claimsHistorySummary` and an auto-logged risk event's
  underlying coverage-figure content plausibly name identifiable customers and settlement
  amounts, closer in profile to `TransactionMonitoringAlert.detailText`
  (`HIGHLY_CONFIDENTIAL`) than to a bare authorization-scope label. A real PCMS/
  `PRIV-STD-02` determination is needed here, not another engineering guess — file a
  `/brain-gap` the day someone actually makes that call, per `meta/designs/2026-08-pcms-
  source-of-truth.md`.

## `@code-reviewer` findings (resolved)

Mandatory (a shared repository refactor touching a maker/checker-adjacent module, plus a
new derived-"current" resolution over money/PII-adjacent data) → CHANGES REQUESTED →
resolved: **1 BLOCKER** (the `findCurrent()` tiebreak above — fixed with a secondary
`id: 'desc'` sort key on both `findCurrent()` and `findMany()`) **+ 1 MAJOR** (the audit
redaction above) **+ 2 MINORs** (the lapsed-policy signal above; the claims-history
concurrency trust level made explicit) **+ 1 deferred MINOR** (the classification-field
gap above, documented not fixed) **+ 1 NIT** (`findCurrent()` selects the full row where
the pre-existing inline query only selected `id` — accepted, the table is tiny). The
review also explicitly verified the `PolicyCheckingRepository` refactor: behaviorally
identical to the pre-existing inline query, DI wiring correct in both `PolicyModule` and
`ComplianceRiskModule` (the `BrokerLicenseRepository` duplication-over-cross-import
shape), and the existing discrepancy-to-PI-risk-event auto-link
(`apps/api/test/policy.e2e-spec.ts`) unaffected.

A genuine cross-run test-monotonicity bug was also found and fixed while verifying the
tiebreak fix: `apps/api/test/operational-pi-risk.e2e-spec.ts`'s own `nextFarFuture()`
helper (needed because "current" resolution is book-wide with no per-test scoping
possible, and db-test is cumulative across runs) originally grew its offset by a whole
extra DAY per call within a run — which broke cross-run monotonicity, since a later
position in an earlier (buggy) run could still out-rank an earlier position in a later run
when the wall-clock gap between runs was under a day (always true in practice). Fixed by
keeping the base offset FIXED and letting only `Date.now()` (which strictly increases
between any two runs) plus a single-digit millisecond counter (same-run tiebreak only)
determine ordering.

## Where the code lives

- `packages/db/prisma/schema.prisma` — `RiskRegisterItem`, `ProfessionalIndemnityPolicy`,
  `ProfessionalIndemnityRiskEvent` (search "PROCESSES 47-57").
- `apps/api/src/modules/compliance-risk/` —
  `risk-register.{config,service,controller}.ts`,
  `pi-policy.{config,service,controller}.ts`, `pi-risk-event.{config,service,controller}.ts`.
- `apps/api/src/repositories/risk-register.repository.ts`, `pi-policy.repository.ts`,
  `pi-risk-event.repository.ts`.
- `apps/api/src/repositories/policy-checking.repository.ts` — `findLatestPiPolicyId` now
  delegates to `PiPolicyRepository.findCurrent()`.
- `apps/api/src/modules/policy/policy.module.ts` — provides `PiPolicyRepository` directly
  (the `BrokerLicenseRepository` shape), for `PolicyCheckingRepository`'s one narrow read.
- `apps/web/app/(app)/operational-pi-risk/page.tsx` — one screen, three sections.

## Out of scope for this file

An actual automated block on new business for lapsed PI cover — the backlog checkbox says
"track," not "block" (contrast #51's explicit "automatically block new business issuance"
wording); building that gate would be a separate, deliberate product decision. Retention/
disposal of PI risk data. Domain F's other processes — see
`meta/context/transaction-monitoring.md` (#48), `sanctions-pep-screening.md` (#49), and
`regulatory-compliance.md` (#51) for the sibling "Out of scope" lists.
