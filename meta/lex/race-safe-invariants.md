# Lex: Race-Safe Invariants

**Enforcement level: mandatory — no exceptions.**

## Rule

Enforce every "at most one", "exactly one", "only once", or "no duplicate"
invariant at the write itself — with a **database constraint** (a `UNIQUE`
index, a partial `UNIQUE` index, or a `CHECK`) or a **status-conditional
write** (`updateMany({ where: { id, status: <the value just read> }, ... })`
whose zero-row result is turned into a `ConflictException`). Never enforce
such an invariant with a read-then-decide-then-write: a `findFirst` /
`findMany().find(...)` / `count()` check followed by an unconditional
`create()` or `update()` is not an invariant — two requests interleaved
between the read and the write both pass the check and both proceed. A
descriptive pre-check that returns a friendly 409 before the constraint
fires is allowed, but only *in addition to* the constraint that actually
holds the line, never instead of it.

**A status-conditional `updateMany` must re-assert in its `where` *every*
field the caller validated against between the read and the write — not only
the status.** If the service loaded a row, checked `assertDifferentActors`
against its `requestedByUserId`, and is about to copy its `amount` into
another column, then `requestedByUserId` and `amount` belong in the `where`
next to `status`. A concurrent write that changed one of them must land zero
rows → `ConflictException`, not (a) proceed on a stale value it already read,
or (b) fall through to a DB `CHECK` / `UNIQUE` violation surfaced as a 500.
The zero-row → 409 path is the single clean outcome for *any* interleaving,
which is only true if the `where` pins everything the decision depended on.

## What triggers this rule

- Introducing or depending on a "one live row per parent" / "one active X" /
  "can only happen once" / "no two rows with the same natural key" rule
  (e.g. one live `InsuranceProgram` per `RiskProfile`; a `Lead` converted to
  a `Prospect` at most once; one open `KYCRecord` per `Customer`; one
  current `Quotation` version).
- Any `create()` / `createMany()` preceded by an existence or uniqueness
  `find*` / `count` on the same key, with no `@@unique`, raw
  `CREATE UNIQUE INDEX`, or `CHECK` in `packages/db/prisma/` backing it.
- Any "has this already happened?" guard before a state change that is not a
  status-conditional `updateMany` (calling
  `WorkflowTransitionService.transition()`, which already does this, is
  compliant).
- Batch / sweep jobs that "skip rows already processed" by reading a set
  then writing each — the write must re-assert the condition (`updateMany`
  with the not-yet-processed predicate in the `where`), not trust the
  earlier read.
- An approval / second-approve / override-approve write that reads a row,
  runs guards against several of its columns (`assertDifferentActors` on a
  maker id, an amount bound, a status check), then persists a decision — the
  status-conditional `updateMany` must carry **all** of those columns in its
  `where`, not just `status`, so a concurrent edit to any of them is a clean
  409 rather than a stale write or a `CHECK`-constraint 500.

## What does NOT trigger this rule

- A pre-check kept **alongside** the DB constraint purely to return a
  specific 4xx with a helpful message before the constraint is hit.
- Read-only queries, list endpoints, analytics, and serializers.
- An invariant already enforced by `WorkflowTransitionService.transition()`
  (status-conditional write + zero-row → `ConflictException`) — calling it
  is the compliant path, not a violation.
- A one-time data migration backfilling historical rows, called out
  explicitly in the migration.
- A genuinely single-writer path protected by an external lock that is
  documented at the call site (none exist in `ibms-app` today).

## How it is enforced

**Review gate:** `@code-reviewer` must flag, as a `MAJOR` citing this file,
any `create` / `update` on a PR under `apps/api/` whose only guard against
duplication or double-action is a preceding `find*` / `count` on the same
key with no matching constraint in `packages/db/prisma/schema.prisma` or a
raw-SQL migration. Greppable anti-pattern: a `findMany` / `findFirst` /
`count` result feeding an `if` that gates a `create` / `update` on the same
entity.

## Rationale

Two independent occurrences in Domain A before this was written down. Part C
#2 (Prospect conversion): a `Lead` could be converted twice, orphaning it —
fixed in `b57a380` by leaning on the terminal `CONVERTED_TO_PROSPECT` status
and `transition()`'s conditional write. Part C #7 (`InsuranceProgram`
assembly): `@code-reviewer` caught a
`findMany().find(p => p.status !== 'SUPERSEDED')` pre-check gating an
unconditional `create()` — two concurrent `POST`s under Postgres READ
COMMITTED both read "no live program" and both insert, producing two live
programs for one `RiskProfile`; rated `BLOCKER`. The fix pattern was already
in the codebase (`WorkflowTransitionService`'s
`updateMany({ where: { id, status } })` + zero-row → conflict; the
maker/checker `CHECK` constraints; the `AuditLogEntry` immutability trigger)
— it just wasn't a rule, so each new module re-derived it or missed it.

The "re-assert *every* validated field, not just status" clause was added
after `ibms-app` Part C #35 (Commission Calculation): `recordOverrideApproval`
gated its `updateMany` on `status` / `isManualOverride` /
`overrideApprovedByUserId IS NULL` but not on the `overrideRequestedByUserId`
that `assertDifferentActors` had just checked, nor the `overrideAmount` it was
about to copy into `amount`. A concurrent `raiseOverride` between the load and
the write could either surface the DB `CHECK` as a 500 (if the racing raiser
was the approver) or copy a now-stale amount into `amount` while
`overrideAmount` held a newer value. `@code-reviewer` flagged it MINOR;
adding the two columns to the `where` turned both interleavings into the
existing zero-row → 409 path.
