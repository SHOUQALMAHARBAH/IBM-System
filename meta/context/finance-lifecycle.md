# Finance lifecycle

**Last verified:** 2026-09-03 · **Owner:** shouq

## What this is

The path premium money takes once a policy is bound: billing the client
(Invoice), collecting it (Receipt), reconciling and remitting to the insurer
(Remittance), the commission ledger, and the accounting/ageing reads. Domain D,
Processes 31–40. Source: `IBMS_Full_Scope_Context_Document.docx` Part 3.6.
Policy placement/issuance/endorsement is `meta/context/policy-lifecycle.md`;
claims payouts are `meta/context/claims-lifecycle.md`.

**Processes 31 (Premium Billing) and 32 (Collection)** are built in `ibms-app`
so far — the rest of this file will grow as #33–40 land.

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
Auditor).

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

## Where the code lives

- `apps/api/src/modules/finance/finance.config.ts` — `computeInvoiceFigures`,
  `invoiceFiguresMatch`, `deriveInvoiceView`, the audit snapshots, the drafted
  `INVOICE_MAX_DUE_DAYS_AHEAD` / `NEW_BUSINESS_PREMIUM_INVOICE_TYPE`;
  `computeRemittanceAmount`, `RECEIPT_METHODS`.
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

Client & insurer accounting/ageing reads (#33–34), commission agreements & the
ledger (#35–36), refunds (#37, covered under `policy-lifecycle.md`'s
endorsement section), payment channels (#38), bank reconciliation exceptions
(#39 — the `ReconciliationException` model + the investigate/resolve path, and
the `EXCEPTION_RAISED` / `EXCEPTION_RESOLVED` `Invoice` states), and financial
reporting (#40). Add each as its own section here as it is built. The
commission *rate* mechanics live in Part 3.6 of the context document until #35
justifies splitting them out.
