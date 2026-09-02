# Finance lifecycle

**Last verified:** 2026-09-02 · **Owner:** shouq

## What this is

The path premium money takes once a policy is bound: billing the client
(Invoice), collecting it (Receipt), reconciling and remitting to the insurer
(Remittance), the commission ledger, and the accounting/ageing reads. Domain D,
Processes 31–40. Source: `IBMS_Full_Scope_Context_Document.docx` Part 3.6.
Policy placement/issuance/endorsement is `meta/context/policy-lifecycle.md`;
claims payouts are `meta/context/claims-lifecycle.md`.

Only **Process 31 (Premium Billing)** is built in `ibms-app` so far — the rest
of this file will grow as #32–40 land.

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

Invoice is a WorkflowTransitionService entity (WORKFLOW_TRANSITIONS.Invoice),
but #31 only CREATES it at the schema @default(INVOICED) — no status write.
The INVOICED → COLLECTED cycle is Process 32.
```

Endpoints (`ibms-app`): `POST /invoices` (`invoice.create` / Finance),
`GET /invoices?policyId=|customerId=` and `GET /invoices/:id`
(`client-accounting.read` / Finance, Manager, Exec, Auditor).

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

## Where the code lives

- `apps/api/src/modules/finance/finance.config.ts` — `computeInvoiceFigures`,
  `invoiceFiguresMatch`, `deriveInvoiceView`, `invoiceAuditSnapshot`, the
  drafted `INVOICE_MAX_DUE_DAYS_AHEAD` / `NEW_BUSINESS_PREMIUM_INVOICE_TYPE`.
- `apps/api/src/modules/finance/invoice.service.ts` — the create/get/list
  orchestration, `parseDueDate`.
- `apps/api/src/repositories/invoice.repository.ts` — `Invoice` reads/writes.
- `packages/db/prisma/migrations/20260902210000_add_premium_billing_invoice/` —
  the `invoiceType` column + the partial `UNIQUE`.
- `apps/web/components/policy/FinanceSection.tsx` — the "Billing" block on the
  opportunity detail screen.

## Out of scope for this file

Collection / Receipt / Remittance / Reconciliation (#32), client & insurer
accounting/ageing reads (#33–34), commission agreements & the ledger (#35–36),
refunds (#37, covered under `policy-lifecycle.md`'s endorsement section),
payment channels (#38), bank reconciliation exceptions (#39), and financial
reporting (#40). Add each as its own section here as it is built. The commission
*rate* mechanics and the reconciliation-variance rule live in Part 3.6 of the
context document until #35/#39 justify splitting them out.
