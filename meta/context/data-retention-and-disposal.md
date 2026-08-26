# Data retention & secure disposal (M06)

**Last verified:** 2026-08-26 · **Owner:** DPO (role, not yet a named person)

## What this is

M06 (`meta/context/pcms-privacy-modules.md`) governs how long every record category is
kept and how it's destroyed once retention expires: a per-category schedule
(`RetentionScheduleItem`), a dual-control destruction workflow (`DisposalBatch` +
`CertificateOfDestruction`), and an exclusion mechanism for records under active
litigation/investigation hold (`LegalHold`). `ibms-app`'s Prisma schema has modeled all
four entities since the initial domain-model migration; the first real caller landed
2026-08-26 when `AuditLogEntry` (Part 10.3) got a seeded schedule row and a
`getRetentionCutoffDate()` reader — see "Where the code lives" below.

## The shapes

```
RetentionScheduleItem
  recordCategory: string              # e.g. "AuditLogEntry" — free text, no enum
  retentionPeriodMonths: int
  legalBasis: string?                 # should cite PRIV-STD-03 / the specific CBJ or AML
                                       # article — see "not obvious" below for the catch
  confirmedByLegalCounselAt: DateTime?  # null = draft/unconfirmed, do not treat as authoritative

DisposalBatch
  status: NOMINATED → MANAGER_APPROVED → DPO_APPROVED → EXECUTED → CLOSED
  nominatedByUserId    # maker — Department Manager
  dpoApprovedByUserId  # checker — MUST differ from nominatedByUserId
  certificateOfDestruction: CertificateOfDestruction?  # required before status can be CLOSED

LegalHold
  scope, reason, placedAt, nextReviewDueAt (6-month SLA), releasedAt?
```

## The rules that aren't obvious

- **`RetentionScheduleItem.recordCategory` has no unique constraint** — it's a free-text
  field, not an enum, and nothing in the schema stops two rows for the same category. Any
  seed/admin code that writes to this table must find-then-create/update by
  `recordCategory` itself (see `packages/db/prisma/seed.ts`'s `ensureRetentionSchedule()`),
  not assume a Prisma `upsert` is available.
- **Engineering has never been handed the actual retention-period table.** `PRIV-STD-03`
  (cited in `pcms-privacy-modules.md`'s M06 row) is where the real per-category retention
  periods live — this brain does not restate them, on purpose, per `meta/CLAUDE.md`'s
  meta-structure rule 5. But as of this writing, **no engineering session has actually been
  given that table's contents.** The A.4 engineering backlog's "log-retention policy = the
  longer of CBJ, AML, and PDPL record-keeping requirements" is a *principle*, not a citation
  — it names three regulatory regimes without a number attached to any of them.
- **Consequence:** `ibms-app`'s first `RetentionScheduleItem` row (`recordCategory:
  "AuditLogEntry"`, seeded in `packages/db/prisma/seed-data/retention-schedule.ts`) is an
  engineering-invented draft — 120 months (10 years), reasoned from generic AML-minimum
  (~5yr, FATF Recommendation 11 / Jordan AML/CFT Law No. 46/2007 as amended) vs. typical
  CBJ/insurance-broker practice (~10yr) in comparable regimes, with `confirmedByLegalCounselAt`
  left `null`. **Do not treat that number, or any future one seeded the same way, as a real
  citation.** The fix is someone with access to `PRIV-STD-03` (DPO/Compliance/Legal)
  supplying the actual table — at that point this file should gain a real "The retention
  table" section (category → months → `PRIV-STD-03` section reference) and the seed data
  should be updated to match, with `confirmedByLegalCounselAt` finally set.
- **A `DisposalBatch` cannot reach `Closed` without a `CertificateOfDestruction` attached**,
  and destruction is always dual-control (Department Manager nominates, DPO approves,
  `dpoApprovedByUserId != nominatedByUserId`) — already stated in `pcms-privacy-modules.md`,
  repeated here because it's the mechanism a retention-expiry job would eventually have to
  drive.
- **Retention informs disposal eligibility; it does not execute disposal.** Nothing in
  `ibms-app` today turns "past its retention cutoff" into an actual `DisposalBatch` —
  `AuditService.getRetentionCutoffDate()` only answers "what's the cutoff date," and
  `AuditLogEntry` is additionally immutable at the DB layer (a Postgres trigger added in the
  same change — see `meta/lex/sensitive-data-handling.md`'s sibling concern and
  `packages/db/prisma/migrations/20260826083942_add_audit_log_entry_immutability_trigger/`),
  so any future disposal-execution path for it would need a deliberate, dual-control,
  documented bypass of that trigger — not a queued DELETE.

## Where the code lives

- `packages/db/prisma/schema.prisma` — `RetentionScheduleItem`, `DisposalBatch`,
  `LegalHold`, `CertificateOfDestruction` models (search "PART 6.2").
- `packages/db/prisma/seed-data/retention-schedule.ts` + `seed.ts`'s
  `ensureRetentionSchedule()` — the only seed data today, one draft row for `AuditLogEntry`.
- `apps/api/src/modules/audit/audit.service.ts`'s `getRetentionCutoffDate()` — the only
  reader today.

## Out of scope for this file

The M04 rule that a Deletion DSR with an open retention flag can't close as "fully
fulfilled" — `meta/context/pcms-privacy-modules.md`. The `AuditLogEntry` immutability
trigger itself and Part 10.3 audit-trail requirements generally — a future
`meta/context/audit-trail.md` would be the right home if this grows past what fits here.
The M06 dual-control disposal-execution workflow's actual approval/controller code — none
exists yet in `ibms-app`.
