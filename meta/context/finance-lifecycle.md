# Finance lifecycle

**Last verified:** 2026-09-03 · **Owner:** shouq

## What this is

The path premium money takes once a policy is bound: billing the client
(Invoice), collecting it (Receipt), reconciling and remitting to the insurer
(Remittance), the commission ledger, and the accounting/ageing reads. Domain D,
Processes 31–40. Source: `IBMS_Full_Scope_Context_Document.docx` Part 3.6.
Policy placement/issuance/endorsement is `meta/context/policy-lifecycle.md`;
claims payouts are `meta/context/claims-lifecycle.md`.

**Processes 31 (Premium Billing), 32 (Collection), 33 (Client Accounting),
34 (Insurer Accounting), 35 (Commission Calculation) and 36 (Commission
Reconciliation)** are built in `ibms-app` so far — the rest of this file will
grow as #37–40 land.

## The shapes

```
Invoice
  policyId: string?                      # required by #31's DTO; nullable in schema for later non-policy invoices
  customerId: string                     # DERIVED from the policy — never a client input
  invoiceType: string                    # 'new_business_premium' (#31) | 'endorsement_adjustment' | 'renewal_premium'
  premiumAmount: Decimal(18,3)           # carried from Policy.issuedPremium
  taxAmount: Decimal(18,3)               # Finance input
  feesAmount: Decimal(18,3)              # Finance input, default 0
  commissionDeducted: Decimal(18,3)      # premiumAmount x commissionRatePercent, computed
  totalAmount: Decimal(18,3)             # ALWAYS premiumAmount + taxAmount + feesAmount − commissionDeducted, computed
  currency: string                       # carried from the policy
  dueDate: DateTime
  status: InvoiceStatus                  # INVOICED (#31 creates here) → COLLECTED → RECONCILED → REMITTED, + EXCEPTION_RAISED/RESOLVED (#32/#39)

Invoice is a WorkflowTransitionService entity (WORKFLOW_TRANSITIONS.Invoice).
#31 CREATES it at the schema @default(INVOICED) — no status write. #32 drives
every subsequent hop through the engine.

Receipt        n..1 Invoice   # #32 records exactly one, for the full total
  amount: Decimal(18,3)       # MUST equal Invoice.totalAmount
  method: string?             # bank_transfer | cheque | card | cash
  receivedAt: DateTime
Remittance      1..1 Receipt  # receiptId @unique
  insurerId: string           # from Policy.insurerId
  amount: Decimal(18,3)       # ALWAYS premiumAmount − commissionDeducted, computed
  remittedAt: DateTime?
ClientFundsLedgerEntry  n..1 Customer   # Part 7.3 — one per money movement
  amount / direction ('in' on receipt, 'out' on remittance)
  reference: string           # 'invoice:<id>' pointer, never free text
```

Endpoints (`ibms-app`): `POST /invoices` (`invoice.create` / Finance);
`POST /invoices/:id/receipt` + `POST /invoices/:id/reconcile`
(`receipt.record` / Finance); `POST /invoices/:id/remittance`
(`remittance.record` / Finance); `GET /invoices?policyId=|customerId=` and
`GET /invoices/:id` (`client-accounting.read` / Finance, Manager, Exec,
Auditor); `GET /client-accounting/ageing?customerId=|asOf=`
(`client-accounting.read`) — the #33 AR / ageing report;
`GET /insurer-accounting/payables?insurerId=|asOf=`
(`insurer-accounting.read`) — the #34 AP / remittance-obligations report.

## The rules that aren't obvious

*(All of Process 31 below is `ibms-app` product decisions filed via `/brain-gap`
at Part C #31 — Part 3.6 says "premium + tax + fees, net of commission, with a
due date" and nothing more precise.)*

- **`premiumAmount` is carried from `Policy.issuedPremium`, never an input.** A
  policy with no `issuedPremium` yet (not issued past Process 19) → **422**; you
  cannot bill a premium that has not been bound. Same "carried, never re-typed"
  rule as #28's `estimatedLoss`.
- **`commissionDeducted` is auto-derived** — `premiumAmount × commissionRatePercent`,
  where the rate is the one the policy was **placed at**:
  `Recommendation.recommendedQuotation.commissionRatePercent` for the policy's
  Opportunity (the same lookup #22's `commissionRateFor` uses). A policy whose
  quotation captured **no** rate cannot be billed net of commission → **422**
  ("capture the rate on the quotation first"). It is not a client input and not
  a stored `Policy` field. When Process 35 (`CommissionAgreement`) is built it
  will supply this rate from the governed table instead of the quotation.
- **`totalAmount` is ALWAYS `premiumAmount + taxAmount + feesAmount −
  commissionDeducted`, computed server-side** (`addMoney` then `subtractMoney`,
  every step through `money.util.ts`). The DTO does **not** accept a
  `totalAmount` field — a caller-supplied total is what lets the figures
  silently disagree (the #28 `netSettlement` lesson).
- **`taxAmount` and `feesAmount` are the only money inputs.** There is no
  governed premium-tax-rate table yet (Jordan's insurance premium levy is not
  encoded anywhere in the system), so Finance supplies the applicable tax per
  invoice. Both are bounded `0 ≤ x ≤ premiumAmount` (a tax or fee larger than
  the premium is a data-entry error). `feesAmount` defaults to `0`.
- **`dueDate` is a required calendar date (`YYYY-MM-DD`)**, today or later, at
  most `INVOICE_MAX_DUE_DAYS_AHEAD` (365, drafted) days ahead. No computed
  default — payment terms vary by client, and a default would drift the
  write-once idempotency check.
- **At most one new-business premium invoice per policy** — a partial
  `UNIQUE ("policyId") WHERE "invoiceType" = 'new_business_premium'` (migration
  `20260902210000`, raw SQL — Prisma can't express a predicate `UNIQUE`), so a
  double-submit cannot bill the client's premium twice
  (`meta/lex/race-safe-invariants.md`). Endorsement / renewal premium invoices
  carry a different `invoiceType` and are **not** constrained. Write-once, #24/
  #28-style: a byte-identical re-`POST` (all five figures + `dueDate` compared)
  returns the existing invoice; any different figure is a **409**; a concurrent
  create hits the index → `P2002` → 409.
- **No maker/checker.** Raising a bill is single-actor Finance work
  (`meta/lex/maker-checker-segregation.md` § "what does NOT trigger this rule").
  The second actor in Finance is at refund approval (#22/#37) and manual
  commission override (#35) — not here.
- **The read is book-wide.** `invoice.create` / `client-accounting.read` are
  Finance / cross-book reporting permissions, so there is no per-owner
  visibility filter (same as `claims-analytics.view`). `GET /invoices` with no
  `policyId`/`customerId` scope is a **400** — a book-wide invoice dump is
  Process 33's ageing report, not this endpoint.
- Audit: one `CREATE Invoice` row — ids + all five figures as fixed 3dp strings
  + the commission rate applied + the due date, no free text (an invoice
  carries none). Reads are not audited (an invoice total is Confidential, not
  Highly Confidential — same tier as `Policy` premium, which #18–21 also do not
  audit on read).

### Collection (Process 32)

*(All `ibms-app` product decisions filed via `/brain-gap` at Part C #32 — Part
3.6 says only "the full Invoice → Collection → Receipt → Reconciliation →
Remittance cycle".)*

- **Every `Invoice` status move goes through `WorkflowTransitionService
  .transition`** — `INVOICED → COLLECTED` (receipt), `COLLECTED → RECONCILED`
  (reconcile), `RECONCILED → REMITTED` (remittance), one hop per endpoint,
  matching `WORKFLOW_TRANSITIONS.Invoice`. The status-conditional `updateMany`
  in the engine is the "one receipt / one remittance per invoice" race gate —
  there is no separate `@unique` on `Receipt.invoiceId` and none is needed.
  The `Receipt` / `Remittance` / `ClientFundsLedgerEntry` artefacts are written
  **after** the transition commits (the #24 `register` pattern): a lost race
  reloads and resumes/409s; a crash between the transition and the artefact
  (`COLLECTED` with no `Receipt`) is a re-entry that writes only the artefact.
- **#32 supports one full-payment receipt per invoice.** `Receipt.amount`
  **must equal `Invoice.totalAmount` exactly** (`compareMoney === 0`) — a
  partial or over payment is a **422**. This is the `money-decimal-jod.md`
  "a reconciliation mismatch is raised as an exception, never silently written
  off" rule applied at the door: the variance / investigation path is Process
  39 (`ReconciliationException`), not a silent short-collect here. Partial
  payments (multiple receipts summing to the total) are a deferred refinement.
- **Reconcile re-derives from the live rows.** `sumMoney(receipts) ===
  totalAmount` is recomputed from the loaded `Receipt` rows at the reconcile
  call — never a stored snapshot (the #16 "re-check the gate at the decision
  point" rule). A mismatch is a 422; an already-`RECONCILED` / `REMITTED`
  invoice is an idempotent 200.
- **The remittance is `premiumAmount − commissionDeducted`, computed server-
  side** (`subtractMoney`, `>= 0` since #31 bounds commission ≤ premium). Tax
  and fees stay with the broker (to the tax authority / retained — out of #32
  scope). `insurerId` comes from `Policy.insurerId`; a non-policy invoice
  (`policyId IS NULL`) → 422. The figures are fully deterministic, so a
  re-`POST` is an idempotent no-op — a stored `Remittance` whose amount /
  insurer disagrees is a **409** (never a silent resume). `Remittance.receiptId
  @unique` + `P2002` → 409 backstops a concurrent create.
- **Client-money segregation (Part 7.3).** Every collection books an `in`
  `ClientFundsLedgerEntry` and every remittance an `out` one, each written in
  the **same `$transaction`** as its `Receipt` / `Remittance` (a deliberate
  local exception to the no-`$transaction` convention, same rationale as
  `PolicyRepository.createIssuanceArtifacts`), so a crash can never leave a
  money movement with no matching ledger row. `reference` is an `invoice:<id>`
  pointer.
- **No maker/checker.** Recording a receipt / reconciling / remitting are
  Finance/Collections single-actor duties (`roles-and-segregation-of-duties.md`
  — the Finance maker/checker pair is refunds / write-offs, #22/#37). Moving
  client money out to an insurer is mechanical and non-discretionary
  (`premium − commission`), not an approval.
- Audit: a `CREATE` row for each of `Receipt` / `Remittance` /
  `ClientFundsLedgerEntry` — ids + the amount as a fixed 3dp string + method /
  insurer / direction, no free text; plus the engine's `TRANSITION` rows
  (exactly three across the full cycle). Best-effort (`safeAudit`) — the money
  write has already committed.

### Client Accounting (Process 33)

*(All `ibms-app` product decisions filed via `/brain-gap` at Part C #33 — Part
3.6 says only "an accounts-receivable / ageing report per customer".)*

- **`GET /client-accounting/ageing?customerId=&asOf=`**
  (`client-accounting.read`) returns the AR / ageing report — one row per
  customer with an outstanding balance, each split into `current` / `d1_30` /
  `d31_60` / `d61_90` / `d90_plus` buckets, plus a `totals` row pooling every
  outstanding invoice in scope. **Computed on the fly — no stored aggregate
  table** (the same shape as #30 Claims Analytics; the unscoped `GET /invoices`
  400 message points here).
- **"Outstanding" is structural: an `Invoice` with no collection `Receipt`.**
  #32 records exactly one `Receipt` per invoice for the full total, so a
  receipt means paid in full — there is no partial-payment state to prorate (a
  deferred #32 refinement). An `EXCEPTION_RAISED` invoice with no receipt still
  reads as outstanding (correct — still owed); the #32 crash seam (status
  `COLLECTED`, no `Receipt`) reads as outstanding until the re-entry heals it.
- **`asOf` is the ageing reference date** — a bare `YYYY-MM-DD`, today or
  earlier (a future `asOf` → 422), default today. It is **point-in-time
  correct for the outstanding *set*** with no history table: the query filters
  `Invoice.createdAt < asOf+1d` (did it exist yet) and requires
  `Receipt.receivedAt < asOf+1d` to be `none` (was it still unpaid then) — and
  `Invoice.dueDate` is write-once at #31, so nothing else needs
  reconstructing. An invoice paid between `asOf` and now correctly still shows
  as outstanding-as-at-`asOf`.
- **Buckets are the textbook 30 / 60 / 90-day bands — drafted / unsourced.**
  `<= 0` days overdue is `current`, then 1–30 / 31–60 / 61–90 / over 90
  (`ageingBucketFor`, over `daysOverdue(dueDate, asOf)` on whole UTC calendar
  days). Same drafted status as `INVOICE_MAX_DUE_DAYS_AHEAD` (#31),
  `CLAIM_LARGE_THRESHOLD_JOD` (#23), the #27 follow-up thresholds and the #29
  loss-ratio "period".
- **Book-wide** — `client-accounting.read` is a Finance / cross-book reporting
  perm (`[FINANCE_COLLECTIONS_OFFICER, BRANCH_DEPARTMENT_MANAGER,
  EXECUTIVE_MANAGEMENT, EXTERNAL_AUDITOR]`); no per-owner filter, the optional
  `customerId` just narrows to one client. Rows ordered **worst-first**
  (largest days-overdue, then largest outstanding balance, then customer name
  in a fixed `en` locale). Capped at `AR_AGEING_INVOICE_LIMIT = 5000` (the #30
  `ANALYTICS_POLICY_LIMIT` precedent — `logger.warn` on truncation).
- **No maker/checker** (a read). **Not audit-logged** — an invoice total is
  Confidential, not Highly Confidential: the #31 decision (`GET /invoices` is
  likewise not audited, same tier as the `Policy` premium read). Contrast the
  #30 breakdown, which aggregates HIGHLY_CONFIDENTIAL `Claim` rows and so
  writes a `READ` row.
- Every figure is pooled through `sumMoney` (`money.util.ts`) — a bucket total
  or an `outstandingTotal` is a sum of the invoice totals, never a re-derived
  or averaged figure. No migration, no seed change (`client-accounting.read`
  pre-existed).

### Insurer Accounting (Process 34)

*(All `ibms-app` product decisions filed via `/brain-gap` at Part C #34 — Part
3.6 says only "accounts-payable / remittance obligations per insurer".)*

- **`GET /insurer-accounting/payables?insurerId=&asOf=`**
  (`insurer-accounting.read`) returns the AP report — one row per insurer with
  `outstandingAmount` (what the broker owes it right now), `remittedAmount`
  (paid to date), the counts, and `oldestDaysOutstanding` (how long the oldest
  unremitted obligation has sat), plus a `totals` row. The insurer-side mirror
  of #33; **computed on the fly, no stored aggregate**.
- **The obligation arises at collection, is discharged by the `Remittance`.**
  An **outstanding** obligation is a *collected-but-not-yet-remitted* invoice —
  a `Receipt` exists (the client paid) but no `Remittance` has been recorded
  (#32's `RECONCILED → REMITTED` hop hasn't run). The broker is holding client
  money that belongs to the insurer (Part 7.3). It is **not** read from a
  `Remittance` row — #32 only creates a `Remittance` *after* the transfer, and
  always stamps `remittedAt`, so a `Remittance` row means *settled*.
- **The amount owed per invoice is `premiumAmount − commissionDeducted`** —
  `computeRemittanceAmount`, exactly #32's `Remittance.amount` and what the
  eventual `Remittance` will carry (tax + fees stay with the broker). Derived
  in the pure builder, never re-typed. The **remitted** side is straight from
  the `Remittance.amount`s.
- **`asOf`** (bare `YYYY-MM-DD`, today or earlier — a future `asOf` → 422;
  default today) makes both sides point-in-time correct: a `Receipt` counts as
  collected when `receivedAt < asOf+1d`, a `Remittance` as remitted when
  `remittedAt < asOf+1d`, and an invoice is *outstanding as at `asOf`* when it
  was collected by then and its `Remittance` (if any) came after. The repo
  filter is one `where` on the `receipts` relation:
  `{ some: { receivedAt: { lt: X } }, none: { remittance: { remittedAt: { lt: X } } } }`
  (the cycle is 1:1:1). Non-policy invoices (`policyId IS NULL`) are skipped —
  no insurer to owe.
- **No ageing buckets** — #34's backlog line is "a query / obligations per
  insurer", not "an ageing query" like #33. A single `outstandingAmount` +
  `oldestDaysOutstanding` (whole UTC days since the earliest unremitted
  `Receipt.receivedAt`, `daysOverdue` reused; `-1` when nothing is
  outstanding). `Insurer.creditTermsDays` (a grace period before the
  remittance is "due") is **not** factored in — a deferred refinement.
- **Book-wide** (`insurer-accounting.read` = `[FINANCE_COLLECTIONS_OFFICER,
  BRANCH_DEPARTMENT_MANAGER, EXECUTIVE_MANAGEMENT, EXTERNAL_AUDITOR]`; the
  optional `insurerId` just narrows). Rows **worst-first** (largest
  days-outstanding, then largest amount owed, then insurer name, fixed `en`).
  Capped at `INSURER_PAYABLES_ROW_LIMIT = 5000` per side (the #30 / #33
  precedent — `logger.warn` on truncation). **No maker/checker** (a read).
  **Not audit-logged** — same Confidential tier / #31 decision as #33.
  Every figure pooled through `sumMoney`. No migration, no seed change
  (`insurer-accounting.read` pre-existed).

### Commission Calculation (Process 35)

*(All `ibms-app` product decisions filed via `/brain-gap` at Part C #35 — Part
3.6 says only "apply the correct commission rate from the agreement table (by
insurer + line)" and "a manual override with a mandatory reason + a separately
logged approval".)*

- **The governed rate table is `CommissionAgreement` — by (insurerId,
  insuranceLine), time-windowed.** `POST /commission/agreements`
  (`commission-rate.manage` — `[COMPLIANCE_OFFICER,
  BRANCH_DEPARTMENT_MANAGER]`, **not Finance**: Finance may *apply* the
  governed rate but "cannot alter commission rate tables without approval",
  `roles-and-segregation-of-duties.md`). A rate change **opens a new window and
  closes the prior open one at the same instant** (`effectiveTo =
  new.effectiveFrom`), both in ONE `$transaction` (`supersedeAndCreateAgreement`
  — the `reviseChain` / `createIssuanceArtifacts` `$transaction` exception). The
  partial `UNIQUE ("insurerId", "insuranceLine") WHERE "effectiveTo" IS NULL`
  (migration `20260903120000`, raw SQL) is the race backstop —
  **AT MOST ONE open window per pair**, `P2002` → 409. `effectiveFrom` may be
  future-dated (a scheduled change) but **not earlier than the window it
  supersedes** (422). A same-rate same-date re-`POST` returns the open window
  (idempotent, no churn).
- **`resolveGovernedRate(agreements, at)` (pure)** — the window whose
  `[effectiveFrom, effectiveTo)` contains `at` (`effectiveFrom` inclusive,
  `effectiveTo` exclusive; an open window has no upper bound). Contiguous
  closed windows + the one-open invariant ⇒ at most one match.
- **`POST /commission/entries` (`commission.calculate` / Finance)** records the
  **one** `CommissionLedgerEntry` per policy (`policyId @unique`, migration
  `20260903120000` — write-once, the #31 Invoice pattern) at the governed rate
  in force for the policy's `(insurerId, insuranceLine)` **at
  `inceptionDate ?? createdAt`** (the rate the business was written at, not the
  rate today). `amount = premium × ratePercent%` via `applyPercentage`; 422 if
  the policy has no `issuedPremium` or no agreement covers the pair at that
  date. The rate is bounded `0..COMMISSION_MAX_RATE_PERCENT` (= 100) so
  `amount ≤ premium`. **No maker/checker** — applying the governed figure is
  mechanical single-actor Finance work (like #31 raising an invoice); the
  maker/checker is on the *override*. Write-once: a re-`POST` with a matching
  governed figure resumes (200), a *different* governed figure (the rate table
  changed after the entry was recorded) → **409** ("recorded once — a
  correction is a manual override"); an already-overridden entry always
  resumes. `#31`'s `commissionDeducted` (the client-facing invoice figure) is
  **NOT** rewired to this table — it stays on the placed-quotation rate; the
  `CommissionLedgerEntry` is the broker's governed commission-earned record
  (reconciling the two is a later concern).
- **The manual override IS a maker/checker pair** (`CommissionLedgerEntry
  .overrideRequestedByUserId <> .overrideApprovedByUserId` — the
  `CommissionLedgerEntry_maker_checker_distinct` CHECK, migration
  `20260826091424`, + `assertDifferentActors`). `POST /commission/entries/:id/
  override` (`commission-override.raise` / Finance) — `{ overrideAmount,
  reason }`, `reason` mandatory (`@MinLength(10)`), `0 ≤ overrideAmount ≤
  premium`. It writes `overrideAmount` (the migration's new nullable column) +
  `isManualOverride` + `overrideReason` + `overrideRequestedByUserId`, and
  **leaves `amount` (the governed figure) untouched** — the override is
  *pending*. Finance may revise a still-pending override freely; once
  **approved** it is write-once (byte-identical resume / 409). `POST .../
  override/approve` (`commission-override.approve` / **Manager**) stamps
  `overrideApprovedByUserId` and **copies `overrideAmount` into `amount`**
  (status-conditional `updateMany` — 0 rows → 409; a different approver on an
  already-approved override → 409; the same one → idempotent; 422 if no
  override is pending; a null requester → 409, the #28 `'' === actor` fix).
  `CommissionLedgerEntryView.effectiveAmount` = `overrideApproved ?
  overrideAmount : amount`; `overridePending` = raised-not-approved.
- Audit: `CREATE CommissionAgreement` (+ `UPDATE` for the superseded window's
  `effectiveTo`), `CREATE CommissionLedgerEntry` (ids + the rate applied +
  amount, no free text), `UPDATE` (override raise) / `APPROVE` (override
  approve) — both carry `overrideReason` **verbatim** (the reason IS the
  "separately logged" requirement, and it is a business justification, not
  personal data — same as #22's `refundAuditSnapshot`). Book-wide reads
  (`GET /commission/agreements` `commission-rate.manage`;
  `GET /commission/entries` + `/:id` `financial-report.view`); a
  `GET /commission/insurers` `{ id, name }` helper for the web add form. **No
  seed change** (all four commission perms pre-existed); `vatAmount` stays `0`
  (VAT on commission is #36's "tax implications" line).

### Commission Reconciliation (Process 36)

*(All `ibms-app` product decisions filed via `/brain-gap` at Part C #36 — Part
3.6 says only "track rate / amount / tax / paid / outstanding / reversed" on
`CommissionLedgerEntry".)*

- **VAT on commission is GOVERNED on `CommissionAgreement`, not a global
  constant.** `CommissionAgreement.vatRatePercent` (migration
  `20260903130000`, `DECIMAL(5,2)`, default `0`) sits next to `ratePercent`:
  `commission-rate.manage` (Compliance / Manager) sets it, Finance only
  applies it (same segregation as the commission rate). `POST
  /commission/agreements` takes an optional `vatRatePercent` (`0..100`, 422
  outside; omitted → `0`); a same-rate re-post is idempotent only if **both**
  `ratePercent` **and** `vatRatePercent` match. The Jordan GST rate on the
  broker's commission income is otherwise unsourced — the field is the
  governed home, its value is a business input.
- **The rate is snapshotted onto the ledger entry at calculate.**
  `CommissionLedgerEntry.vatRatePercent` (same migration) freezes the
  governing agreement's `vatRatePercent` when `POST /commission/entries` runs,
  and `vatAmount = amount × vatRatePercent%` (`computeCommissionVat`,
  `applyPercentage`) is stamped then — no longer `0`. The invariant `vatAmount
  == amount × vatRatePercent%` holds after **every** write: an approved manual
  override recomputes `vatAmount` from `overrideAmount × the frozen rate`
  (`recordOverrideApproval`'s `data`, derived purely from fields the `where`
  already pins — no new race surface), and a later edit to the
  `CommissionAgreement` does **not** disturb a recorded entry.
  `CommissionLedgerEntryView` gains `vatRatePercent`, a non-zero `vatAmount`,
  and `grossAmount = amount + vatAmount` (commission incl. VAT).
- **`status` gets its `outstanding → paid | reversed` lifecycle.**
  `CommissionLedgerEntry` is **NOT** a `WorkflowTransitionService` entity (its
  `status` is a plain string, like `ReconciliationException.status`), but the
  legal moves live in `commission.config.ts`'s `COMMISSION_ENTRY_TRANSITIONS`
  (`outstanding: [paid, reversed]`, `paid: [reversed]`, `reversed: []`) and
  every move validates against it, writes an audit row, and persists via a
  **status-conditional `updateMany`** — never a bare `.status =`
  (`workflow-state-transitions.md` spirit + `race-safe-invariants.md`).
- **`outstanding → paid` is `POST /commission/entries/:id/settle`**
  (`commission.reconcile` — a **new seed perm**, `[FINANCE_COLLECTIONS_OFFICER]`;
  Finance *applies/settles* the governed figure, it is not an approval, so **no
  maker/checker** — same call as #32's remittance). `{ statementAmount,
  paymentReference }`: `statementAmount` **must equal the recorded `amount`
  exactly** (`compareMoney === 0`) — a variance is a **422** pointing at
  Process 39's `ReconciliationException`, never a silent short settle
  (`money-decimal-jod.md` at the door, the #32 rule). A **pending** manual
  override blocks settlement (422 — the amount is not final); a `reversed`
  entry cannot be settled (422). Stamps `status = 'paid'`, `paidAmount =
  amount`, `paidAt`, `paymentReference` (a pointer, not free text). Write-once:
  a re-`POST` with the same figure **and** reference resumes (200), a different
  one is a **409**; the status-conditional `updateMany` `where` re-asserts
  **every** condition the service validated (`race-safe-invariants.md`):
  `status`, the exact `amount` (a concurrent override-approve → clean 0-row
  409), "no pending override" (`OR: isManualOverride false |
  overrideApprovedByUserId not null`), **and** "no Process 22
  `CommissionReversal` on the policy" as a relation filter
  (`policy: { endorsements: { none: { commissionReversal: { isNot: null } } } }`)
  — so a `CommissionReversal` minted concurrently with the settle lands 0 rows
  → 409, not only the pre-check 422. The `outstanding → paid` move is also
  asserted against `COMMISSION_ENTRY_TRANSITIONS` in the service.
- **`{outstanding|paid} → reversed` is driven by Process 22, not an endpoint.**
  When a cancellation / negative `Endorsement` mints a `CommissionReversal` for
  the policy (`calculateAdjustment`), the endorsement service **best-effort**
  calls `CommissionLedgerService.reconcileReversalForPolicy(policyId, actorId)`
  (the #29 `lossRatio.recomputeForPolicy` precedent — only the actual
  transitioner, never fails the endorsement flow, the entry may not exist yet).
  It recomputes `reversedAmount` from **live** rows —
  `computeReversalState({ entryAmount, reversalAmounts })` pools every
  `CommissionReversal.amount` on the policy's endorsements, **caps at `amount`**
  (you cannot reverse more commission than was earned), and `fullyReversed`
  once the pool meets `amount`. It stamps `reversedAmount` / `reversedAt` /
  `reversalReason` (a system-generated pointer to the endorsement) and flips
  `status → reversed` **only when fully clawed back** — a partial cancellation
  leaves `status = 'outstanding'` with a partial `reversedAmount`. A missed
  best-effort call self-heals on the next endorsement, and `settle` re-checks
  the same live gate (422 if any un-reflected reversal exists). `EndorsementModule`
  imports `CommissionModule` (one-way — no cycle).
- Audit: `CREATE`/`UPDATE CommissionAgreement` now carry `vatRatePercent`;
  `CREATE CommissionLedgerEntry` carries `vatRatePercentApplied` + `vatAmount`;
  `settle` writes an `UPDATE CommissionLedgerEntry` (`settlementAuditSnapshot`
  — `paidAmount` + the statement `paymentReference`); the reversal reflection
  writes an `UPDATE` (`reversalAuditSnapshot` — `reversedAmount` + the reason
  verbatim, a business justification like `overrideReason`).
- **No commission-reconciliation summary report** (an AP-style
  outstanding-vs-paid-vs-reversed roll-up by insurer) — that is Financial
  Reporting (#40). The per-entry lifecycle fields + `GET /commission/entries`
  are the #36 deliverable.

## Where the code lives

- `apps/api/src/modules/finance/finance.config.ts` — `computeInvoiceFigures`,
  `invoiceFiguresMatch`, `deriveInvoiceView`, the audit snapshots, the drafted
  `INVOICE_MAX_DUE_DAYS_AHEAD` / `NEW_BUSINESS_PREMIUM_INVOICE_TYPE`;
  `computeRemittanceAmount`, `RECEIPT_METHODS`; `buildReceivablesAgeing`,
  `daysOverdue`, `ageingBucketFor`, `AR_AGEING_BUCKET_KEYS`,
  `AR_AGEING_INVOICE_LIMIT` (#33).
- `apps/api/src/modules/finance/client-accounting.service.ts` +
  `client-accounting.controller.ts` — the #33 ageing report
  (`GET /client-accounting/ageing`);
  `apps/api/src/repositories/invoice.repository.ts` gains
  `loadOutstandingReceivables`.
- `apps/web/app/(app)/client-accounting/page.tsx` +
  `apps/web/lib/client-accounting/ageing-api.ts` — the "Client accounting"
  screen.
- `apps/api/src/modules/finance/insurer-accounting.service.ts` +
  `insurer-accounting.controller.ts` — the #34 payables report
  (`GET /insurer-accounting/payables`); `finance.config.ts` gains
  `buildInsurerPayables` + `INSURER_PAYABLES_ROW_LIMIT`;
  `invoice.repository.ts` gains `loadInsurerObligations` /
  `loadInsurerRemittances`.
- `apps/web/app/(app)/insurer-accounting/page.tsx` +
  `apps/web/lib/insurer-accounting/payables-api.ts` — the "Insurer accounting"
  screen.
- `apps/api/src/modules/commission/` — Process 35: `commission.config.ts`
  (`resolveGovernedRate`, `computeCommissionAmount`, the views, the audit
  snapshots, `COMMISSION_MAX_RATE_PERCENT`), `commission-agreement.service.ts`
  (the rate table), `commission-ledger.service.ts` (`calculate` + the
  override maker/checker), `commission.controller.ts`;
  `apps/api/src/repositories/commission.repository.ts`
  (`supersedeAndCreateAgreement` `$transaction`, `findAgreementsForPair`,
  `recordOverrideRaise` / `recordOverrideApproval`).
  `packages/db/prisma/migrations/20260903120000_add_commission_calculation/` —
  the partial `UNIQUE` on the open agreement, `CommissionLedgerEntry.policyId
  @unique`, the `overrideAmount` column.
- Process 36: `commission.config.ts` gains `computeCommissionVat`,
  `computeReversalState`, `COMMISSION_ENTRY_TRANSITIONS` /
  `isCommissionEntryTransition`, `settlementAuditSnapshot` /
  `reversalAuditSnapshot`; `commission-ledger.service.ts` gains `settle` +
  `reconcileReversalForPolicy`; `commission.repository.ts` gains
  `recordEntrySettlement` / `recordEntryReversal` /
  `findCommissionReversalAmountsForPolicy`;
  `apps/api/src/modules/endorsement/endorsement.service.ts` calls
  `reconcileReversalForPolicy` best-effort after a `CommissionReversal`.
  `packages/db/prisma/migrations/20260903130000_add_commission_reconciliation/`
  — `CommissionAgreement.vatRatePercent`, `CommissionLedgerEntry.vatRatePercent`
  + `paidAmount` / `paidAt` / `paymentReference` / `reversedAmount` /
  `reversedAt` / `reversalReason`. **Seed: +`commission.reconcile`
  `[FINANCE_COLLECTIONS_OFFICER]`.**
- `apps/web/app/(app)/commission/page.tsx` +
  `apps/web/lib/commission/commission-api.ts` — the "Commission rates" screen
  (a VAT % column + input at #36);
  `apps/web/components/policy/CommissionSection.tsx` — the per-policy
  calculate / override / approve / **reconcile** block on the opportunity
  detail screen (VAT + gross + paid/reversed detail at #36).
- `apps/api/src/modules/finance/invoice.service.ts` — the #31 create/get/list
  orchestration.
- `apps/api/src/modules/finance/collection.service.ts` — the #32 cycle
  (`recordReceipt` / `reconcile` / `recordRemittance`).
- `apps/api/src/repositories/invoice.repository.ts` — `Invoice` + cycle reads,
  the `recordReceiptWithLedger` / `recordRemittanceWithLedger` `$transaction`
  writes.
- `packages/db/prisma/migrations/20260902210000_add_premium_billing_invoice/` —
  the `invoiceType` column + the partial `UNIQUE`. #32 needs no migration.
- `apps/web/components/policy/FinanceSection.tsx` — the "Billing" block on the
  opportunity detail screen (raise + the three cycle actions).

## Out of scope for this file

refunds (#37, covered under `policy-lifecycle.md`'s endorsement section),
payment channels (#38), bank reconciliation exceptions (#39 — the
`ReconciliationException` model + the investigate/resolve path, and the
`EXCEPTION_RAISED` / `EXCEPTION_RESOLVED` `Invoice` states), and financial
reporting (#40). Add each as its own section here as it is built.
