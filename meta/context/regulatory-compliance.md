# Regulatory Compliance (Process 51)

**Last verified:** 2026-09-05 · **Owner:** Compliance Officer (role, not yet a named person)

## What this is

Backlog Part C #51 has two checkboxes: "Automatically block new business issuance once
the license lapses" and "A compliance calendar of regulatory obligations with owner, due
date, and evidence-of-submission tracking." Two independent resources, both under
Part 7.1: the broker's own CBJ license (`BrokerLicense`), and a compliance calendar
(`ComplianceCalendarItem`). Both pre-existed as bare "core schema" models — genuinely no
migration, no seed change; `license.manage` / `compliance-calendar.manage`
(both `[COMPLIANCE_OFFICER]`) were pre-seeded ahead of time.

`BrokerLicenseService`/`ComplianceCalendarService` (`apps/api/src/modules/compliance-risk/`)
extend `ComplianceRiskModule` (opened by #48). `BrokerLicenseRepository` is ALSO provided
directly by `PolicyModule` — `PolicyService.place()` is the enforcement point for the
first checkbox.

## The shapes

```
BrokerLicense                              # a SINGLETON — one row, fixed id
  id: "the-broker-license"                 # BROKER_LICENSE_SINGLETON_ID, never a UUID
  licenseNumber: string
  scopeOfAuthorization: string?
  issuedAt: DateTime?
  expiresAt: DateTime
  status: "active" | "lapsed"              # @default("active")

ComplianceCalendarItem                     # one row per obligation-instance, unlimited rows
  id: uuid
  obligationName: string
  ownerUserId: string                      # a User id, validated to exist
  dueDate: DateTime
  evidenceOfSubmissionRef: string?         # null until recordSubmission
  submittedAt: DateTime?                   # null until recordSubmission — write-once
```

`isBrokerLicenseCurrentlyLapsed(license, now)` (`broker-license.config.ts`) — the ONE
place "is this license lapsed right now" is computed: `status === 'lapsed' || expiresAt
<= now`. Used identically by `PolicyService.assertLicenseNotLapsed` (the gate) and
`BrokerLicenseService`'s view (`isCurrentlyLapsed`) — no `BrokerLicenseSweepScheduler`
exists to keep a stored flag in sync, because there is nothing for one to do: the check
is a live recompute wherever it's needed, always correct the instant `expiresAt` passes.

## The rules that aren't obvious

- **`BrokerLicense` is a true singleton — one row, ever, at a fixed id
  (`BROKER_LICENSE_SINGLETON_ID = 'the-broker-license'`)**, not a `findFirst()` guess over
  an unconstrained table. "The broker's own CBJ license status" (the model's own doc
  comment) is singular by nature — a broker holds exactly one current license — so rather
  than a migration adding a partial-unique/singleton DB constraint for a resource
  Compliance creates once and only ever updates afterward (an infrequent, deliberate,
  human action — not a concurrent-write hotspot, the M03 "exactly-one-owner is app-level,
  not a DB CHECK" reasoning), the row is simply always created under that fixed id.
  `POST /broker-license` 409s if it already exists; `POST /broker-license/renew` 404s if
  it doesn't yet.
- **No `BrokerLicenseSweepScheduler` exists, deliberately** — see
  `isBrokerLicenseCurrentlyLapsed` above. This is the direct, generalized lesson from
  #16's `@code-reviewer` MAJOR ("a control that fires only when a human/sweep configured
  data in the right order first is procedural, not structural"): `PolicyService.place()`'s
  block must be correct the INSTANT `expiresAt` passes, not only after some future nightly
  sweep has had a chance to flip a stored column. Every OTHER "goes stale over time"
  backlog item in this codebase (KYC periodic review, retention, transaction monitoring,
  watchlist sync) DOES have a scheduler — #51 is the one place that doesn't, and that is
  correct, not a gap.
- **An unconfigured `BrokerLicense` (no row at all) is NOT treated as lapsed — it is
  explicitly "not blocked."** This is load-bearing, not an oversight: dozens of existing
  policy/endorsement/claim/finance e2e and unit tests place a `Policy` without ever
  configuring a license, and this system is built for an already-operating, already-
  licensed brokerage. Treating "unconfigured" the same as "lapsed" would fail every one
  of those tests for a condition none of them are testing. `PolicyService.
  assertLicenseNotLapsed` returns immediately on `findCurrent() === null`.
- **The gate is scoped to `PolicyService.place()` ONLY** — the moment a NEW `Policy` is
  created (today, every `Policy` is "new business"; the renewal module, Part 3.9, isn't
  built). It is checked FIRST, before any other placement precondition (the client-decision
  ACCEPT check, the duplicate-policy check) — the cheapest, most fail-fast gate, and
  logically prior to everything else. `recordIssuance` (completing an ALREADY-placed
  policy's paperwork) is deliberately NOT gated — blocking that would strand legitimately
  in-flight business placed before the lapse, which is out of scope for "block new
  business issuance."
- **`status: 'lapsed'` is a genuinely separate signal from `expiresAt` having passed** —
  `POST /broker-license/mark-lapsed` lets Compliance flag the license lapsed AHEAD of its
  calendar expiry (e.g. a CBJ suspension), independent of the date. `renew` always resets
  `status` back to `'active'` — a fresh license period supersedes any prior manual lapse.
  There is no "un-suspend without a renewal" path — deliberately: only a genuine renewal
  with updated license particulars reactivates business, not a bare status flip.
- **`ComplianceCalendarItem` submission is write-once, not idempotent-on-repeat** — unlike
  `RetentionCase.close` (#46), a second `record-submission` call 409s rather than silently
  succeeding, because silently accepting it would let a later call overwrite the first
  evidence reference with no audit trail of the original. `submittedAt` defaults to now,
  backdatable via `parseHistoricalInstant` (rejects a future instant — a submission record
  is a record of something that already happened).
- **A recurring obligation is a NEW row per cycle, not a recurrence field on one row** —
  the bare schema has nothing to express a recurrence rule with, and the backlog doesn't
  ask for one; this is the same per-instance shape `ServiceRequest` (#41) and
  `RetentionCase` (#46) use. `isOverdue` (`submittedAt === null && dueDate < now`) is a
  pure, derived dashboard convenience, not itself a tracked `SlaTimer` deadline — the
  backlog names no single statutory turnaround for the calendar entries themselves (each
  underlying filing has its own CBJ deadline, which IS the `dueDate` — there's no second,
  separate SLA on top of it to track).
- **`parseCalendarDate` moved to `common/calendar-date.util.ts`** (was local to
  `policy.config.ts`, already a de facto shared utility via `endorsement.service.ts`'s
  cross-module import) — #51 is its third consumer (`issuedAt`/`expiresAt`/`dueDate`, all
  MAY be future dates, unlike `parseHistoricalInstant`). `policy.config.ts` re-exports it
  so existing imports keep working unchanged.

## `@code-reviewer` findings (resolved) — read this before touching the license gate again

The first pass shipped without any of these. All three are now fixed; this section exists
because each is a mistake an agent re-implementing a similar "singleton create-once
resource" or "a global-state e2e test" elsewhere in this codebase is likely to repeat.

- **MAJOR — a pre-check alone does not make a singleton create race-safe.**
  `BrokerLicenseService.create()`'s `findCurrent() === null` check passes for two
  concurrent `POST /broker-license` calls before either has written the row. The fixed-id
  `@id` primary key on `BrokerLicense.id` still stops a second row from ever being
  created — the data-integrity invariant itself always held — but without a `catch` on
  `repo.create()`, the loser's P2002 (`Prisma.PrismaClientKnownRequestError`, code
  `P2002`) surfaced as an unhandled 500 instead of the same 409 a sequential caller gets.
  **Fixed**: wrap `repo.create()` in the identical `isUniqueViolation` catch-and-rethrow
  `ConflictException` pattern every other create-once resource in this codebase already
  uses (`policy.service.ts`, `watchlist-sync.service.ts`, and roughly a dozen others). The
  lesson generalizes: **a pre-check-then-write is never sufficient on its own for "at most
  one" — the write itself must also handle losing the race**, even when (as here) the
  underlying data integrity was never actually at risk. `race-safe-invariants.md` already
  says this for a `findMany().find()` check-then-act; this is the same shape one layer
  closer to the database.
- **MAJOR — an e2e test that mutates a real, shared, non-test-scoped singleton needs its
  own restore verified, not just attempted.** `test/regulatory-compliance.e2e-spec.ts` and
  the license-gate test appended to `test/policy.e2e-spec.ts` are the first e2e specs in
  this codebase to touch a genuinely global row (`BrokerLicense`'s fixed-id singleton) —
  every other fixture is scoped by a unique generated id. Both rely on restoring the
  license to `active` + a far-future `expiresAt` before the file ends
  (`vitest-e2e.config.ts`'s `fileParallelism: false` makes "restored before this file
  ends" sufficient for every file that runs afterward). The first pass's restore check
  only verified `isCurrentlyLapsed` when the renew call itself returned 201 — missing the
  more likely failure (renew returning a non-201: a transient hiccup, an expired token, a
  real regression), which would have silently left the singleton lapsed with **no
  signal**, cascading into confusing, unrelated 422s across every later e2e file that
  places a `Policy`. **Fixed**: assert the renew call's status unconditionally, not just
  when it happens to be 201. Fixing this surfaced a second issue — the original shape put
  the restore-and-throw logic inside a `finally` block, which ESLint's `no-unsafe-finally`
  correctly flags: a `throw` inside `finally` silently swallows whatever the `try` block
  itself threw. **Fixed**: restructured to capture the test body's own error into a local
  variable via `catch`, run the restore unconditionally *after* the try/catch (not inside
  a `finally`), and rethrow whichever failed (preferring the test body's own error when
  both fail, since it usually has the more specific cause).
- **MAJOR — the What's New / brain-gap documentation obligation is part of "done," not an
  afterthought.** This file existed only as an untracked, unpushed file in the `ibms-brain`
  submodule at review time, and neither `CLAUDE.md` had a dated row for this landing —
  breaking the "`/brain-gap` filed + pushed" pattern every prior landing note in this brain
  documents. `ibms-brain/meta/lex/workspace-updates.md` governs this directly (its rule is
  cross-referenced by `ibms-app/CLAUDE.md`'s own What's New table footer). Fixed by this
  documentation pass itself, committed and pushed in the same batch as the code fixes —
  not a separate, later commit.

## Where the code lives

- `packages/db/prisma/schema.prisma` — `BrokerLicense`, `ComplianceCalendarItem` (search
  "PROCESSES 47-57").
- `apps/api/src/common/calendar-date.util.ts` — `parseCalendarDate` (promoted here this
  process; `policy.config.ts` re-exports it).
- `apps/api/src/modules/compliance-risk/` — `broker-license.{config,service,controller}.ts`,
  `compliance-calendar.{config,service,controller}.ts`.
- `apps/api/src/repositories/broker-license.repository.ts`,
  `compliance-calendar.repository.ts`.
- `apps/api/src/modules/policy/policy.service.ts` — `assertLicenseNotLapsed` (called first
  in `place`).
- `apps/web/app/(app)/regulatory-compliance/page.tsx` — one screen, two sections.

## Out of scope for this file

Building an actual CBJ-integration license-status feed (the record is entered manually by
Compliance, not pulled from a regulator API — no such feed is known to exist). Any
recurrence/reminder mechanism for the compliance calendar beyond the plain `dueDate` +
derived `isOverdue`. Renewal-history tracking for `BrokerLicense` (a renewal overwrites the
singleton in place; the `AuditLogEntry` UPDATE trail is the only history). Domain F's other
processes — see `meta/context/transaction-monitoring.md` (#48) / `sanctions-pep-screening.md`
(#49) for the "Out of scope" list covering #50/#52-57 (#50 Conflict of Interest needs no
separate build — covered under #16, `meta/context/policy-lifecycle.md`).
