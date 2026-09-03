@AGENTS.md

# CLAUDE.md — ibms-brain

Workspace instructions. Loaded into every Claude Code session in this repo and in every engineering repo that syncs the brain, once those repos exist.

<!-- The @AGENTS.md line above is an import, not a link. Claude Code reads CLAUDE.md and
     NOT AGENTS.md, so without that import the AGENTS.md file is dead weight for Claude
     while still being read by other agent tools. Keep the import on line 1.
     Target for this file: under 200 lines. Longer files reduce adherence. -->

---

## What's New

| Date | Change | Action required |
|------|--------|-----------------|
| 2026-09-03 | `meta/context/finance-lifecycle.md` gains a **Financial Reporting (Process 40)** section (filed via `/brain-gap` at `ibms-app` Part C #40) — **Domain D is now complete**. The backlog line has **no checkboxes** ("Financial Reporting — dashboard D in Part E"); "dashboard D" is Part E's Financial Dashboard (receivables & ageing, payables to insurers, commission income & outstanding, profitability by client segment / line). **`GET /financial-report/summary?asOf=`** (`financial-report.view` = `[FINANCE_COLLECTIONS_OFFICER, BRANCH_DEPARTMENT_MANAGER, EXECUTIVE_MANAGEMENT, EXTERNAL_AUDITOR]` — the **same perm** `GET /commission/entries` uses; **no seed change, no migration**) returns `{ asOf, currency:'JOD', receivables, payables, commission, profitability }`, **computed on the fly**, book-wide, **no maker/checker**. **`receivables`** = #33's `buildReceivablesAgeing(...).totals` verbatim (bucket totals + counts); **`payables`** = #34's `buildInsurerPayables(...).totals` verbatim — the service calls `ClientAccountingService` / `InsurerAccountingService` directly (truncation `logger.warn`s still fire) and passes `asOf` through (future → 422, default today); **these two sections are point-in-time at `asOf`**. **`commission`** = the NEW `buildCommissionRollup` (pure) — the "AP-style roll-up by insurer" #36 deferred here: per entry `earned = amount` (the *effective* commission — `deriveLedgerEntryView`'s rule), `paid = paidAmount ?? 0`, `reversed = reversedAmount ?? 0`, **`outstanding = max(0, amount − paid − reversed)`** (floored — a reconciled-then-clawed-back entry has `paidAmount == amount` AND `reversedAmount > 0`, a legal #36/#22 state, which would otherwise go negative). **`earned == paid + outstanding + reversed` holds ONLY without a paid+reversed overlap**; **`netEarned = earned − reversed`** is the recognised-income figure. `vat` / `gross` are on the *gross* `earned` (reversal-VAT not netted — deferred). Also `entryCount` / `byInsurer[]` (worst-first). **`profitability`** = the NEW `buildProfitability` (pure) — every written policy (the #30 `ANALYTICS_WRITTEN_POLICY_STATUSES`) grouped `byLine` (`insuranceLine`) and `bySegment` (`Customer.customerType`), each with `premiumWritten` / `claimsPaid` (Σ SETTLED/CLOSED net settlements) / `commissionEarned` (Σ `amount − reversedAmount`) and **`netPosition = premiumWritten − claimsPaid − commissionEarned`** (the backlog line's literal "premium − claims − commission" — a **drafted** metric; can be negative; worst-first). **`commission` + `profitability` are current-state** (`asOf` does not constrain them — the ledger / `issuedPremium` are not time-versioned). **The profitability section aggregates HIGHLY_CONFIDENTIAL `Claim` net settlements** → the service writes a **best-effort `READ` audit row** (`entityType: 'FinancialReport'`, `entityId: 'summary'`, counts + `asOf` only, `isSensitiveDataAccess` when a settled claim contributed — the #30 precedent); contrast #33 / #34 (Confidential-tier, not audited). All four reads under one `Promise.all`; each capped at `FINANCIAL_REPORT_ROW_LIMIT = 5000` (`logger.warn` on truncation). `finance.config.ts` gains `buildCommissionRollup` / `buildProfitability` (+ types), `FINANCIAL_REPORT_ROW_LIMIT`, `PROFITABILITY_GROUP_BY`; new `repositories/financial-report.repository.ts` (`loadCommissionRollupEntries` / `loadProfitabilityPolicies`). `apps/web/` gains a **"Financial report"** screen. **Deferred**: the `asOf` / line / insurer / branch / language **filters** + the dashboard UI are Part E; no point-in-time for commission / profitability; `netPosition` is drafted; no CSV / export; JOD-only; in-memory aggregation (capped). | Read the Financial Reporting section of `finance-lifecycle.md` before touching Part E's Financial Dashboard — "`GET /financial-report/summary`, `financial-report.view` (no new perm), no migration, no maker/checker", "`receivables` / `payables` are #33 / #34 totals VERBATIM (point-in-time at `asOf`); `commission` / `profitability` are NEW pure builders and CURRENT-STATE", "`buildCommissionRollup`: `outstanding = max(0, effective `amount` − paid − reversed)` (floored — a paid-then-reversed entry would go negative); `earned == paid + outstanding + reversed` ONLY without a paid+reversed overlap; `netEarned = earned − reversed` is the income figure", "`buildProfitability`: `netPosition = premiumWritten − claimsPaid − commissionEarned` — a DRAFTED metric, grouped byLine + bySegment", and "the profitability section touches HIGHLY_CONFIDENTIAL Claim rows so it writes a best-effort `READ` audit row (the #30 precedent) — #33 / #34 do NOT" are all easy to get wrong |
| 2026-09-03 | `meta/context/finance-lifecycle.md` gains a **Bank Reconciliation (Process 39)** section (filed via `/brain-gap` at `ibms-app` Part C #39). **`ReconciliationException` is a plain-string-`status` entity, NOT a `WorkflowTransition` entity** (the `CommissionLedgerEntry.status` pattern) — `RECON_EXCEPTION_TRANSITIONS` (`open: [investigating, resolved]`, `investigating: [resolved]`, `resolved: []`), each move validated + persisted via a status-conditional `updateMany`. **`POST /reconciliation-exceptions/detect` (`reconciliation-exception.investigate` / Finance)** runs the variance check over a batch of insurer-statement lines in the **request body** (`{ lines: [{ invoiceId, insurerStatementAmount }] }` — **no `InsurerStatement` model**): per line `brokerRecordAmount = premiumAmount − commissionDeducted` (`computeRemittanceAmount`, == #32's `Remittance.amount`), `varianceAmount = computeVariance(statement, broker) = subtractMoney(...)` **exact, ±**. Cap `RECON_DETECT_MAX_LINES = 500` (drafted); a duplicate `invoiceId` → 422; an unknown / non-policy invoice is **flagged per-line** (`invoice_not_found` / `not_a_policy_invoice`), not thrown. **A non-zero variance ALWAYS raises a `ReconciliationException`** (`open`, exact `varianceAmount` stored) — **never a silent write-off** (`money-decimal-jod.md`); a zero variance reconciles silently, no row. **One non-resolved exception per invoice** — partial `UNIQUE ("invoiceId") WHERE "status" <> 'resolved'` (migration `20260903150000`, raw SQL); same-figures re-detect → `exception_exists` (idempotent), different-figures → `conflicting_exception`, concurrent → `P2002`. **The parent `Invoice` IS a `WorkflowTransitionService` entity** — detect drives `COLLECTED \| RECONCILED → EXCEPTION_RAISED` through the engine **state-gated + best-effort** (any other invoice state → exception still recorded, no transition, `logger.error` not throw). **`POST .../:id/investigate`** (`reconciliation-exception.investigate`) — `open → investigating`, stamps `investigatedByUserId` (a claim — already-`investigating` idempotent regardless of who; `resolved` → 422). **`POST .../:id/resolve`** (`reconciliation-exception.resolve` / **Finance, Manager**) — `{ resolutionNote (mandatory `@MinLength(10)`, logged **verbatim** — the "closure path", like #35's `overrideReason`), resumeInvoiceAs? }`; `{open\|investigating} → resolved`; **NO figure is adjusted** (`varianceAmount` stays on the record). Then when the `Invoice` is mid-exception the engine drives it `EXCEPTION_RAISED → EXCEPTION_RESOLVED → RECONCILED` (or just the last hop on a crash re-entry); `resumeInvoiceAs` can only be **`RECONCILED`** (the map also allows `→ REMITTED`, but that would skip the `Remittance` + `out` `ClientFundsLedgerEntry` — Part 7.3), **required** when mid-exception (422 if omitted). **Ordering**: the invoice hops run BEFORE `recordResolution` (crash before the exception write = clean retry). Idempotent re-`resolve` same note → 200, different note → 409. **No maker/checker** (`roles-and-segregation-of-duties.md` — the Finance maker/checker pair is refunds / overrides; `investigate` [Finance] vs `resolve` [Finance, Manager] as distinct perms is the natural segregation). Audit: `CREATE ReconciliationException` (three figures as fixed 3dp strings + ids + status, no free text), `UPDATE` on investigate + on resolve (`resolutionNote` verbatim + `resolvedByUserId` + `resumeInvoiceAs`), + the engine `TRANSITION` rows. Book-wide reads. **No migration beyond the columns above; no seed change** (`reconciliation-exception.investigate` `[FINANCE]` / `.resolve` `[FINANCE, MANAGER]` seeded in `a440c1b`). All `ibms-app` product decisions — Part 3.6 says only "a variance-detection job (insurer statement vs. broker record) that ALWAYS raises an exception with the exact variance amount — never a silent write-off" + "an investigation and closure path". | Read the Bank Reconciliation section of `finance-lifecycle.md` before touching #39–40 — "`ReconciliationException` is plain-string status, NOT a WorkflowTransition entity; the parent `Invoice` IS", "detect ALWAYS raises an exception for any non-zero variance regardless of invoice state (never written off), but the `→ EXCEPTION_RAISED` engine hop is state-gated + best-effort", "resolve needs a mandatory verbatim `resolutionNote`, adjusts NO figure, and drives the invoice `EXCEPTION_RAISED → EXCEPTION_RESOLVED → RECONCILED` (`resumeInvoiceAs` — RECONCILED only, NOT REMITTED, else the Remittance + client-funds ledger entry is skipped; required when mid-exception) BEFORE writing the exception close", and "no maker/checker; statement lines come in the request body, there is no `InsurerStatement` model" are all easy to get wrong |
| 2026-09-03 | `meta/context/finance-lifecycle.md` gains a **Payment Processing (Process 38)** section (filed via `/brain-gap` at `ibms-app` Part C #38). **`PaymentChannel` is a governed reference list, NOT a workflow entity** — `POST /payment-channels` (`payment-channel.manage` — a **NEW seed perm `[FINANCE_COLLECTIONS_OFFICER]`**) records an approved channel for a customer (money **in**, on a `Receipt`) or an insurer (money **out**, on a `Remittance`); `ownerType` ∈ `{customer, insurer}` with exactly one of `customerId`/`insurerId` set to match — validated in the service AND the `PaymentChannel_owner_exactly_one` CHECK (migration `20260903140000`). Created `active`; `POST /payment-channels/:id/disable` is a status-conditional `updateMany` (0 rows → already disabled → idempotent). **No maker/checker** (a reference list). **Masked-only — NO full bank account / card number anywhere** (`sensitive-data-handling.md`: bank/card data is Highly Confidential, a list view showing a full account number is a violation). #38 stores `label` + `bankName` + **`accountLast4`** (`^\d{2,4}$`) only — the DTO has no full-number field, the model stays `CONFIDENTIAL`, and the audit snapshot carries `ownerType`/`channelType`/`label`/`bankName`/`status` but **never `accountLast4`**. **#32's `Receipt` / `Remittance` reference a channel — optional but validated**: `Receipt.paymentChannelId` / `Remittance.paymentChannelId` (nullable FKs, same migration); on `POST /invoices/:id/receipt` an optional `paymentChannelId` must be an **`active`** channel with `ownerType='customer'` + `customerId=invoice.customerId` (else 422; 404 unknown) and it **DERIVES `Receipt.method`** from `channel.channelType` (a caller `method` that disagrees → 422 — the "computed not an input when derivable" rule); the remittance is the insurer-side mirror. Keeping it optional leaves #32's contract + e2e unchanged (a hard "must use an approved channel" gate is a later tightening); #32's write-once/idempotency comparisons now ALSO compare `paymentChannelId` (a re-`POST` with a different channel → 409) — **both** `finishReceipt` **and** `finishRemittance`'s concurrent same-checks (the latter previously returned a silent 200) + both `P2002` resume branches, so neither remittance branch is an unconditional "deterministic resume". **Ordering** (the #31/#28 lesson): the channel id is *loaded* (404-only) up front, but the owner / status / **currency** (= invoice currency) / method checks run **after** #32's write-once resume — an idempotent retry after the channel was later disabled resumes 200, it does not 422. The two owner FKs are **`ON DELETE RESTRICT`** (`SET NULL` would violate `owner_exactly_one` on a hard delete of the owner). **`Remittance.remittedAt` is unchanged** (#32 already stamps it). Audit: best-effort `CREATE`/`UPDATE PaymentChannel`; the #32 `CREATE Receipt`/`Remittance` snapshots gain `paymentChannelId`. Book-wide reads. **`meta/lex/maker-checker-segregation.md` also gains a clause** (from the #38 `@code-reviewer` MINOR): maintaining a reference list that moves no money is single-actor — but the exemption ends the day the reference becomes load-bearing (mandatory on a receipt/remittance, or a "release payment" step executes a transfer), at which point the "approved-payee list" is a maker/checker control. All `ibms-app` product decisions — Part 3.6 says only "record approved payment channels for customers and insurers". | Read the Payment Processing section of `finance-lifecycle.md` before touching #38–40 (and the new `maker-checker-segregation.md` reference-list clause) — "`PaymentChannel` is a governed list, `payment-channel.manage`/Finance, no maker/checker YET (exemption ends when it becomes load-bearing)", "MASKED ONLY — `accountLast4`, no full number, never in the audit row", and "the channel on a Receipt/Remittance is OPTIONAL but validated (active + right owner + currency), DERIVES `Receipt.method`, and the usability checks run AFTER the write-once resume" are all easy to get wrong |
| 2026-09-03 | `meta/context/finance-lifecycle.md` gains a **Commission Reconciliation (Process 36)** section (filed via `/brain-gap` at `ibms-app` Part C #36). Completes the `CommissionLedgerEntry` lifecycle #35 stubbed. **VAT on commission is GOVERNED on `CommissionAgreement.vatRatePercent`** (migration `20260903130000`, `DECIMAL(5,2)` default 0) — Compliance / Manager set it beside `ratePercent` (`commission-rate.manage`), Finance only applies it; `POST /commission/agreements` takes an optional `vatRatePercent` (`0..100`, 422 outside), a same-rate re-post is idempotent only if **both** rate + VAT rate match. **The rate is SNAPSHOTTED** onto `CommissionLedgerEntry.vatRatePercent` at `calculate`, and `vatAmount = amount × vatRatePercent%` is stamped then (no longer 0); the invariant survives a manual override (`recordOverrideApproval` recomputes `vatAmount` from `overrideAmount × the frozen rate`, purely from fields the `where` already pins) and a later `CommissionAgreement` edit. `CommissionLedgerEntryView` gains `vatRatePercent`, non-zero `vatAmount`, `grossAmount = amount + vatAmount`. **`status` gets `outstanding → paid | reversed`** — `CommissionLedgerEntry` is NOT a `WorkflowTransitionService` entity (plain-string `status`), but the legal moves live in `commission.config.ts`'s `COMMISSION_ENTRY_TRANSITIONS` and every move validates + audits + persists via a **status-conditional `updateMany`** (never a bare `.status =`). **`outstanding → paid` = `POST /commission/entries/:id/settle`** (`commission.reconcile` — **NEW seed perm `[FINANCE_COLLECTIONS_OFFICER]`**, no maker/checker, like #32's remittance): `{ statementAmount, paymentReference }`, `statementAmount` **must equal `amount` exactly** (a variance → **422** pointing at Process 39, never a silent short settle); a **pending** override or a `reversed` entry blocks it (422); write-once (same figure + reference → resume 200, different → 409); the status-conditional `updateMany` `where` re-asserts **every** validated condition (`race-safe-invariants.md`) — `status`, exact `amount`, "no pending override", **and** "no Process 22 `CommissionReversal` on the policy" as a relation filter (`policy: { endorsements: { none: { commissionReversal: { isNot: null } } } }`), so a concurrently-minted reversal → clean 0-row 409, not only the pre-check 422; the `→ paid` / `→ reversed` moves are asserted against `COMMISSION_ENTRY_TRANSITIONS`. **`{outstanding|paid} → reversed` is DRIVEN BY Process 22, not an endpoint**: a cancellation / negative `Endorsement` minting a `CommissionReversal` calls `CommissionLedgerService.reconcileReversalForPolicy` **best-effort** (the #29 `lossRatio.recomputeForPolicy` precedent — never fails the endorsement flow, the entry may not exist); it recomputes `reversedAmount` from **live** `CommissionReversal` rows (`computeReversalState` — pooled, **capped at `amount`**), stamps `reversedAmount`/`reversedAt`/`reversalReason`, and flips `status → reversed` **only when fully clawed back** (a partial cancellation → `outstanding` + partial `reversedAmount`). `settle` re-checks the same live gate. `EndorsementModule` imports `CommissionModule` (one-way, no cycle). Audit: `CREATE`/`UPDATE CommissionAgreement` carry `vatRatePercent`; `CREATE CommissionLedgerEntry` carries `vatRatePercentApplied` + `vatAmount`; `settle` → `UPDATE` (`settlementAuditSnapshot`), the reversal reflection → `UPDATE` (`reversalAuditSnapshot`, reason verbatim). **No summary report** (that is #40). All `ibms-app` product decisions — Part 3.6 says only "track rate / amount / tax / paid / outstanding / reversed". | Read the Commission Reconciliation section of `finance-lifecycle.md` before touching #36–40 — "VAT is governed on `CommissionAgreement.vatRatePercent` + snapshotted onto the entry, `vatAmount == amount × vatRatePercent%` always", "settle needs an EXACT statement match (a variance is #39), no maker/checker, new `commission.reconcile` perm", and "`→ reversed` is NOT an endpoint — Process 22's `CommissionReversal` drives a best-effort recompute that only flips status on FULL clawback" are all easy to get wrong |
| 2026-09-03 | `meta/context/finance-lifecycle.md` gains a **Commission Calculation (Process 35)** section (filed via `/brain-gap` at `ibms-app` Part C #35). **The governed rate table is `CommissionAgreement`** — by `(insurerId, insuranceLine)`, time-windowed. `POST /commission/agreements` (`commission-rate.manage` = `[COMPLIANCE_OFFICER, BRANCH_DEPARTMENT_MANAGER]` — **NOT Finance**: Finance applies the governed rate but "cannot alter commission rate tables without approval"). A rate change **opens a new window and closes the prior open one at `new.effectiveFrom`**, both in ONE `$transaction`; the partial `UNIQUE ("insurerId", "insuranceLine") WHERE "effectiveTo" IS NULL` (migration `20260903120000`, raw SQL) = **at most one open window per pair** (`P2002` → 409). `effectiveFrom` may be future-dated but **not earlier than the window it supersedes** (422). **`resolveGovernedRate(agreements, at)` (pure)** = the window whose `[effectiveFrom, effectiveTo)` contains `at` (`from` inclusive, `to` exclusive). **`POST /commission/entries` (`commission.calculate` / Finance)** records the **one `CommissionLedgerEntry` per policy** (`policyId @unique`, write-once — the #31 pattern) at the governed rate in force at the policy's **`inceptionDate ?? createdAt`** (not today); `amount = premium × rate%` (`applyPercentage`, rate bounded `0..100` so `amount ≤ premium`); 422 if unissued / no covering agreement; a re-`POST` with a changed governed figure → **409** ("recorded once — a correction is a manual override"). **NO maker/checker on `calculate`** (mechanical, like #31 raising an invoice). **#31's `commissionDeducted` is NOT rewired** to this table — it stays on the placed-quotation rate; the ledger entry is the broker's governed record. **The manual override IS a maker/checker pair**: `POST /commission/entries/:id/override` (`commission-override.raise` / Finance) — `{ overrideAmount, reason }`, `reason` mandatory, `0 ≤ x ≤ premium`; writes the migration's new `overrideAmount` column + `isManualOverride` + `overrideRequestedByUserId` and **leaves `amount` (governed) untouched** (pending; Finance may revise a still-pending override freely). `POST .../override/approve` (`commission-override.approve` / **Manager**) — `assertDifferentActors` + the `CommissionLedgerEntry_maker_checker_distinct` CHECK (migration `20260826091424`), status-conditional `updateMany` (0 rows → 409), **copies `overrideAmount` into `amount`**; a null requester → 409 (the #28 fix), a different approver on an already-approved override → 409, the same one → idempotent. `CommissionLedgerEntryView.effectiveAmount` = `overrideApproved ? overrideAmount : amount`. Audit: `CREATE`/`UPDATE CommissionAgreement`, `CREATE CommissionLedgerEntry` (rate + amount), `UPDATE`/`APPROVE` (override) carrying `overrideReason` **verbatim** (the reason IS the "separately logged" requirement — a business justification, not personal data). Book-wide reads. **No seed change** (all four commission perms pre-existed); `vatAmount` stays `0` (VAT on commission is #36). **`meta/lex/race-safe-invariants.md` also gains a clause** (from the #35 `@code-reviewer` MINOR): a status-conditional `updateMany` must re-assert in its `where` **every** field the caller validated between the read and the write (the maker id `assertDifferentActors` checked, the amount about to be copied), not only `status` — so a concurrent edit is a clean 0-row → 409, never a stale write or a `CHECK` 500. All `ibms-app` product decisions — Part 3.6 says only "apply the correct rate from the agreement table (by insurer + line)" and "a manual override with a mandatory reason + a separately logged approval". | Read the Commission Calculation section of `finance-lifecycle.md` before touching #35–40, and the new `race-safe-invariants.md` "re-assert every validated field" clause before writing any approval `updateMany` — "the rate table is time-windowed, one open window per pair (partial UNIQUE), Compliance/Manager only (NOT Finance)", "calculate = the governed rate at the policy's inception, one entry per policy, NO maker/checker, #31 NOT rewired", and "the override IS maker/checker — raise leaves `amount` governed, approve copies `overrideAmount` in, the reason is logged verbatim" are all easy to get wrong |

---

## What this brain is for

**IBMS — Insurance Brokerage Management System.** A system for a licensed insurance/reinsurance broker operating in Jordan, covering the full loop from lead through claims and renewal, built to CBJ insurance regulation, Jordan PDPL No. 24/2023, and ISO/IEC 27001 + 27701.

This brain is seeded **before** a line of application code exists — from the approved Business & Technical Context Document and the already-approved Privacy Compliance Management System (PCMS) toolkit (1 policy, 4 standards, 10 procedures, 10 forms, 1 SRS), not from PR review history. That is a deliberate substitution of Input 1 in `INTAKE.md`: the "rules that would block a PR" already exist as signed-off regulatory documents. Once an engineering repo exists, add PR-derived lex the normal way and this note can go.

**Broker legal name:** not yet supplied to this brain — replace throughout once known. It does not block anything below.

---

## Staying current

Sync at session start — fetch, and pull only if behind **and** clean **and** on `main`. If dirty or on a feature branch, notify instead of pulling. Rule: `meta/lex/brain-freshness.md`.

---

## Repo map

```
meta/lex/         Mandatory rules. Read before non-trivial work.
meta/context/     How things actually work here. Read before touching an area.
meta/designs/     Why things are the way they are. Read before changing a decision.
meta/agents/      Agent definitions (source of truth).
meta/guides/      Advisory. Setup, onboarding, contributing.
meta/templates/   PR, ticket, and doc templates.
.claude/agents/   Mirror of meta/agents/ — what Claude Code actually loads.
.claude/hooks/    Enforcement scripts.
.claude/commands/ Slash commands.
```

---

## Modules (business view — not yet mapped to repos)

`ibms-app` exists as a single web+api monorepo — it is not yet split by module or service boundary. What exists is the module inventory from `PRIV-SRS-01` and the 74-process/8-domain inventory in the context document. Treat this as the module list, not a services table, until a service-boundary decision fills it in:

| Module | Governs |
|---|---|
| Core IBMS (Sales/CRM, Policy, Claims, Finance) | The 74 business processes — see `meta/context/policy-lifecycle.md` and `meta/context/claims-lifecycle.md` |
| M01–M12 (PCMS) | Privacy/compliance modules — see `meta/context/pcms-privacy-modules.md` |

## Architecture relationships

**IBMS and the PCMS (Privacy Compliance Management System) are one system, not two.** PCMS is the source of truth for every privacy/consent/retention/breach/DSR rule; IBMS's compliance module consumes PCMS decisions and feeds it data (customers, policies, claims) — it must never re-derive or duplicate a privacy rule. See `meta/designs/2026-08-pcms-source-of-truth.md`.

`ibms-app` is a Next.js (web) + NestJS (api) + PostgreSQL/Prisma monorepo. See `meta/designs/2026-08-ibms-app-stack-and-repo-split.md` for why, including the Prisma 6-vs-7 and repo-split calls. No call-direction / auth-boundary / system-of-record decision beyond "web calls api" has been made yet. **Do not invent one.** Record it here the day it's decided.

`ibms-app` vendors this repo as a pinned git submodule (`ibms-app/ibms-brain/`) rather than restating any rule — see `meta/designs/2026-08-ibms-app-brain-submodule-sync.md`. This repo has no reverse dependency on `ibms-app` and does not need one.

---

## Common commands

**This repo (`ibms-brain`) has none — it stays documentation-only.** For `ibms-app` (the engineering repo): `npm install`, `npm run dev`, `npm run test`, `npm run e2e` — see its own `README.md`/`CLAUDE.md`, not this file, for the full list and any changes to it.

## Environment

**This repo needs none.** `ibms-app` pins Node `20.13.0` (`.nvmrc`) and requires Docker — see its `README.md`. Record changes there, not here.

---

## Agents

| Agent | Use for |
|---|---|
| `@code-reviewer` | Review before push. **Mandatory** for any workflow/approval logic, financial (premium/commission/claim) calculation, or code touching Confidential/Highly Confidential data. |
| `@software-developer` | Implementation, bug fixes, refactoring. |

Definitions are source-of-truth in `meta/agents/` and mirrored to `.claude/agents/` by `.claude/hooks/mirror-agents.sh`. **Never hand-copy.**

---

## Mandatory rules

Loaded from `meta/lex/`. Enforcement level is stated in each file.

| Lex | Governs |
|---|---|
| `money-decimal-jod.md` | Decimal only for premium/commission/claim amounts |
| `workflow-state-transitions.md` | Never assign a workflow `status` directly — always through a transition function |
| `race-safe-invariants.md` | A "one of these / only once" invariant is a DB constraint or a status-conditional write, never a `findMany().find()` check-then-act |
| `maker-checker-segregation.md` | No self-approval on KYC, policy checking, refunds, disposal, DSR closure |
| `sensitive-data-handling.md` | Highly Confidential data (medical, financial, national ID, UBO) never logged/exported/shared unencrypted |
| `pdpl-sla-timers.md` | Every statutory SLA (consent withdrawal, DSR, breach containment, disposal) is a tracked deadline, not documentation |
| `backup-rpo-rto.md` | Encrypted backups + an actually-tested restore drill, not backup-only assurance |
| `kyc-aml-sla-timers.md` | KYC compliance-review turnaround + periodic re-KYC cadence are tracked deadlines (CBJ AML domain, not PDPL) — values currently draft/unsourced |
| `code-review.md` | Review format and severity levels |
| `definition-of-done.md` | No push without evidence from the verification contract |
| `workspace-updates.md` | Keeping this file and README current |
| `brain-freshness.md` | Session-start sync |

---

## What "working" means

`meta/context/verification-contract.md` defines the gates every change must pass and the evidence each produces. Run them with `bash scripts/verify.sh`. Claims are not evidence — exit codes and screenshots are. **In this repo, the only real gate is `bash scripts/brain-doctor.sh`** — it stays documentation-only. For `ibms-app` changes, real gates now exist: `npm run typecheck|lint|test|build|test:e2e|e2e` — see `meta/context/verification-contract.md` § Backend/frontend gate commands. Do not deploy to production; open a PR with evidence attached and let a human merge.

Path-scoped rules live in `.claude/rules/` and load themselves when you touch matching files — none exist yet because there is no code to scope them to.

## Domain glossary

See `meta/context/glossary.md`. Terms that mean something specific here — **account**, **customer**, **policy**, **loss ratio**, **maker/checker** — go there, not in this file.

---

## MR standards

**Not yet decided** — there is no engineering repo. Record branch naming, PR title format, and review rule here the day one is created. Until then, `meta/templates/pr-description.md` is the description format for any interim proposal/ticket writing.

---

## meta/ structure rules

1. Agent definitions are source-of-truth in `meta/agents/`. The mirror to `.claude/agents/` is automated — do not hand-copy.
2. Designs go in `meta/designs/<area>/` with a descriptive filename. No free-form naming.
3. A file belongs in `lex/` only if it has a filled "How it is enforced" section. Otherwise it goes in `guides/`.
4. Do not create a folder before it has content.
5. All cross-document links point to **this repo**. The PCMS documents (`PRIV-STD-*`, `PRIV-SOP-*`, `PRIV-FRM-*`, `PRIV-SRS-*`) are the canonical location for privacy/compliance detail — this brain cross-references them, it never restates them as a second source of truth.

---

## Mindset

Research before architecture. Architecture before execution.

`context/` exists so nothing has to be explained twice — to a human or to an agent.

The brain grows by use. When an agent asks something this repo should have answered, that gap is the next file. Run `/brain-gap`.
