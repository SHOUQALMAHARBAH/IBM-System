# AML/CFT Transaction Monitoring (Process 48)

**Last verified:** 2026-09-04 · **Owner:** Compliance Officer (role, not yet a named person)

## What this is

Part 7.2 (source context document) names AML/CFT transaction monitoring: watch for
unusual payment patterns — unusually large premium payments, frequent
cancellations/refunds, third-party premium payment sources — and escalate to
suspicious activity where warranted, with record-keeping for the regulator-mandated
period. `ibms-app`'s Prisma schema has modeled `TransactionMonitoringAlert` since the
initial domain-model migration; the first real writer landed 2026-09-04 (backlog Part C
#48, Domain F — Compliance & Risk). It is the first Domain F process to be built.
`ScreeningResult` (Process 47/49, sanctions/PEP/AML screening at KYC) is a sibling model
the backlog line also names, but #48 does not touch it — screening is Part C #3-4's
concern entirely (see "Out of scope" below).

Backlog #47 (KYC) needed no separate build before this — the backlog's own line reads
"#47 KYC — fully covered under #3–4", and that was verified against the built code
(`apps/api/src/modules/customer/`) the same day, immediately before #48 landed.

## The shapes

```
TransactionMonitoringAlert
  customerId: string?                    # nullable — not every alert traces to one
                                          # customer, though today all four automated
                                          # patterns do
  patternType: string                    # large_premium_payment | frequent_cancellations
                                          # | frequent_refunds | third_party_payment_source
                                          # | other
  detailText: string?                    # NO_FULL_ACCOUNT_NUMBER-guarded; NEVER in an
                                          # audit row (see "not obvious")
  sourceEntityType: string?              # 'Receipt', for the two event-scoped patterns
  sourceEntityId: string?                # the triggering Receipt's id; NULL for the two
                                          # aggregate patterns — see the unique-index note
  detectedAt: DateTime                   # @default(now())
  escalatedToSuspiciousActivity: bool    # step 1 of the escalation path
  escalatedAt: DateTime?
  reportedToAuthorityAt: DateTime?       # step 2 — the actual filing; record-keeping
                                          # evidence (see "not obvious")
  status: string                         # 'open' | 'closed' — NOT a WorkflowTransitionService
                                          # entity, no closedAt column
  classification: DataClassification     # @default(HIGHLY_CONFIDENTIAL)

  @@unique([patternType, sourceEntityId])              # event-scoped dedup
  # + a hand-authored partial UNIQUE (migration 20260904130000, not in schema.prisma —
  #   Prisma can't express the WHERE): ("customerId","patternType")
  #   WHERE status='open' AND "sourceEntityId" IS NULL   # aggregate-pattern dedup
```

Permissions (seeded ahead of the code, `a440c1b`, module `compliance-risk`, both
`[COMPLIANCE_OFFICER]` only): `aml.monitor` (log / detect / read / close) and
`aml.escalate` (the two-step suspicious-activity path). Kept as two permissions even
though they grant to the same single role today — the seed clearly means to separate
them, and a future role split (e.g. a junior analyst who monitors but cannot escalate)
should not need a schema change.

## The rules that aren't obvious

- **Detection reads existing Finance/Endorsement data — it is not a new business
  process.** `large_premium_payment` and `third_party_payment_source` are both scanned
  off every `Receipt` (Process 32 — an *actual collected payment*; a raised-but-unpaid
  `Invoice` is deliberately not a "payment" for this purpose), not `Invoice`.
  `frequent_cancellations` / `frequent_refunds` scan `Cancellation` / `Refund` (Process
  22/37) — neither carries its own `customerId`, so the sweep reaches it via
  `Endorsement.policy.customerId`.
- **All four thresholds are DRAFTED / UNSOURCED** — same status as
  `CLAIM_LARGE_THRESHOLD_JOD` (#23) and the #41/#42/#46 SLA figures: a large-premium
  threshold of 15,000 JOD (`AML_LARGE_PREMIUM_THRESHOLD_JOD`), and a frequent-pattern
  window of 90 calendar days / count of 3 for both cancellations and refunds. Part 7.2
  names the patterns, not figures. Do not cite these as Compliance-sourced until a real
  CBJ AML figure is identified — same treatment `kyc-aml-sla-timers.md` gives its own
  draft numbers.
- **A `Receipt` with no recorded `PaymentChannel` cannot be classified as
  third-party-sourced, and is silently skipped, not flagged.** `PaymentChannel` linkage
  on a `Receipt` is optional (#38) — a cash payment or one with no channel on file is a
  genuine detection gap, not a false negative this module claims to close.
- **The two race-safe invariants are different shapes, on purpose**
  (`race-safe-invariants.md`). The event-scoped patterns get a plain
  `@@unique([patternType, sourceEntityId])` — Postgres treats every `NULL`
  `sourceEntityId` as distinct from every other `NULL`, so this constraint is silently
  inert for the two aggregate patterns (which never set `sourceEntityId`) while still
  stopping the sweep from re-alerting the same `Receipt` forever. The aggregate
  patterns get their own hand-authored partial `UNIQUE ("customerId","patternType")
  WHERE status='open' AND "sourceEntityId" IS NULL` — the `UpSellRecommendation` /
  `ClaimFollowUpAlert` shape: at most one *open* alert per customer/pattern at a time,
  but a fresh one can open again once the prior one is closed and the pattern recurs.
  Both are backed by a service-level pre-check (readable, not the real guard) plus a
  `P2002` catch mapped to `skippedExisting` (never `failed`) for the genuine race.
- **Duplicate alerts are not treated as a hard business-integrity risk here** — unlike a
  double refund or a double policy issuance, an extra monitoring alert is harmless (a
  compliance officer sees two rows for the same thing, dismisses one); the false
  positive from a duplicate is far cheaper than a false negative from suppressing a real
  signal. This is why the pre-check is a best-effort convenience and the unique indexes
  exist to stop unbounded pile-up on repeated sweeps, not to enforce a strict business
  rule the way `Refund` / `Settlement` maker-checker constraints do.
- **The suspicious-activity escalation path is two separate steps, deliberately
  mirroring M03's consent-withdrawal request/confirm shape** (`consent-management.md`):
  `POST /transaction-monitoring-alerts/:id/escalate` records the internal decision;
  `POST .../:id/report-to-authority` records that the report was actually filed with
  the competent authority, and requires `escalate` to have run first (422 otherwise —
  a report with no internal escalation decision behind it is not this flow's shape).
  Both are idempotent. The reason for two calls instead of one: an internal escalation
  that was never followed by an actual filing is a materially different fact from one
  that was, and collapsing them into one atomic call would make that distinction
  unrecoverable.
- **Record-keeping is satisfied by the row's own immutability, not a tracked
  deadline.** No delete endpoint exists anywhere on this model — the row plus its
  `CREATE`/`UPDATE` `AuditLogEntry` rows *is* the regulator-mandated record. The actual
  retention **period** (how long that record must be kept) is undocumented — no CBJ AML
  source figure has been identified — and is **not** built as a tracked `SlaTimer`
  deadline the way `kyc-aml-sla-timers.md`'s two figures are, because there is (yet) no
  purge/disposal mechanism anywhere in this codebase to guard against (the same honest
  gap `data-retention-and-disposal.md` documents for PDPL retention schedules — M06
  execution is not built either). If a real retention-period source document surfaces,
  or a disposal mechanism gets built, this is the file to update, and it likely becomes
  a proper lex entry once there is something to enforce (`meta/` structure rule 3: a
  file belongs in `lex/` only once its "How it is enforced" section can be filled in).
- **`detailText` is guarded but excluded from every audit row** — the
  `NO_FULL_ACCOUNT_NUMBER` guard (`common/dto.util.ts`) applies to the input (it can
  name a payment counterparty), but the audit `afterValue` never carries it — the #44
  `subject`/`body` / #45 `comments` precedent, reinforced here by the model's own
  default `classification: HIGHLY_CONFIDENTIAL` ("names payment sources/counterparties,
  AML-sensitive" — the schema's own comment).
- **Not a `WorkflowTransitionService` entity, no maker/checker.** `status` is a plain
  `open`/`closed` string (no `closedAt` column either — unlike `RetentionCase` — so the
  `UPDATE` audit row's `occurredAt` is the closure timestamp of record).
  `maker-checker-segregation.md`'s explicit list (KYC, policy checking, refunds,
  disposal, DSR closure) does not name this process, and `aml.escalate` is a
  single-role grant with no paired approver permission in the seed — the #42
  `complaint.escalate` shape, not the #23-28 claim-settlement dual-approver shape.

## Where the code lives

- `packages/db/prisma/schema.prisma` — `TransactionMonitoringAlert` (search "Part 7.2").
- `packages/db/prisma/migrations/20260904130000_add_transaction_monitoring/` — the
  widening migration + both unique indexes (the partial one is hand-authored raw SQL,
  not expressible via `@@unique` in `schema.prisma`).
- `apps/api/src/modules/compliance-risk/` — `transaction-monitoring.config.ts` (pure:
  classifiers, thresholds, view/audit-snapshot builders), `transaction-monitoring.
  service.ts` (the sweep + the escalation path), `transaction-monitoring.controller.ts`,
  `transaction-monitoring-sweep.scheduler.ts` (nightly, 09:00 UTC — after the 08:00
  `RetentionSweepScheduler`), `dto/`.
- `apps/api/src/repositories/transaction-monitoring-alert.repository.ts` — owns the
  writes, plus the cross-module reads the sweep needs (`Receipt`/`Cancellation`/
  `Refund`, none of which belong to this module).
- `apps/web/app/(app)/transaction-monitoring/page.tsx` +
  `apps/web/lib/compliance-risk/transaction-monitoring-api.ts`.
- `apps/api/src/modules/customer/` — `KycService`/`ScreeningService`, which is where
  Process 47 (KYC) actually lives; #48 does not touch it.

## Out of scope for this file

The rest of Domain F: #49 (recurring sanctions/PEP batch screening beyond #3-4's
existing monthly re-screen — see `apps/api/src/modules/customer/screening-batch.
scheduler.ts`, which already re-screens monthly and may be the same mechanism #49
ultimately points at), #50 (the broker's own regulatory license record), #51 (the
compliance calendar), #52 (data protection compliance — already the umbrella backlog
process bundling Part D / PCMS, see `pcms-privacy-modules.md`), #53 (the operational/
cyber/financial/compliance/reputational risk register), #54 (Professional Indemnity —
`ProfessionalIndemnityRiskEvent` already has a real writer via Process 20's discrepancy
path), #55 (incident/breach management), #56 (internal audit), #57 — none of these are
built yet. A future Domain F process gets its own file here, or a section in this one if
it shares enough shape with transaction monitoring (unlikely — the others are mostly
governance registers, not detection sweeps).
