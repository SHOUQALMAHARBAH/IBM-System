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
| 2026-09-03 | `meta/context/finance-lifecycle.md` gains a **Payment Processing (Process 38)** section (filed via `/brain-gap` at `ibms-app` Part C #38). **`PaymentChannel` is a governed reference list, NOT a workflow entity** — `POST /payment-channels` (`payment-channel.manage` — a **NEW seed perm `[FINANCE_COLLECTIONS_OFFICER]`**) records an approved channel for a customer (money **in**, on a `Receipt`) or an insurer (money **out**, on a `Remittance`); `ownerType` ∈ `{customer, insurer}` with exactly one of `customerId`/`insurerId` set to match — validated in the service AND the `PaymentChannel_owner_exactly_one` CHECK (migration `20260903140000`). Created `active`; `POST /payment-channels/:id/disable` is a status-conditional `updateMany` (0 rows → already disabled → idempotent). **No maker/checker** (a reference list). **Masked-only — NO full bank account / card number anywhere** (`sensitive-data-handling.md`: bank/card data is Highly Confidential, a list view showing a full account number is a violation). #38 stores `label` + `bankName` + **`accountLast4`** (`^\d{2,4}$`) only — the DTO has no full-number field, the model stays `CONFIDENTIAL`, and the audit snapshot carries `ownerType`/`channelType`/`label`/`bankName`/`status` but **never `accountLast4`**. **#32's `Receipt` / `Remittance` reference a channel — optional but validated**: `Receipt.paymentChannelId` / `Remittance.paymentChannelId` (nullable FKs, same migration); on `POST /invoices/:id/receipt` an optional `paymentChannelId` must be an **`active`** channel with `ownerType='customer'` + `customerId=invoice.customerId` (else 422; 404 unknown) and it **DERIVES `Receipt.method`** from `channel.channelType` (a caller `method` that disagrees → 422 — the "computed not an input when derivable" rule); the remittance is the insurer-side mirror. Keeping it optional leaves #32's contract + e2e unchanged (a hard "must use an approved channel" gate is a later tightening); #32's write-once/idempotency comparisons now ALSO compare `paymentChannelId` (a re-`POST` with a different channel → 409) — **both** `finishReceipt` **and** `finishRemittance`'s concurrent same-checks (the latter previously returned a silent 200) + both `P2002` resume branches, so neither remittance branch is an unconditional "deterministic resume". **Ordering** (the #31/#28 lesson): the channel id is *loaded* (404-only) up front, but the owner / status / **currency** (= invoice currency) / method checks run **after** #32's write-once resume — an idempotent retry after the channel was later disabled resumes 200, it does not 422. The two owner FKs are **`ON DELETE RESTRICT`** (`SET NULL` would violate `owner_exactly_one` on a hard delete of the owner). **`Remittance.remittedAt` is unchanged** (#32 already stamps it). Audit: best-effort `CREATE`/`UPDATE PaymentChannel`; the #32 `CREATE Receipt`/`Remittance` snapshots gain `paymentChannelId`. Book-wide reads. **`meta/lex/maker-checker-segregation.md` also gains a clause** (from the #38 `@code-reviewer` MINOR): maintaining a reference list that moves no money is single-actor — but the exemption ends the day the reference becomes load-bearing (mandatory on a receipt/remittance, or a "release payment" step executes a transfer), at which point the "approved-payee list" is a maker/checker control. All `ibms-app` product decisions — Part 3.6 says only "record approved payment channels for customers and insurers". | Read the Payment Processing section of `finance-lifecycle.md` before touching #38–40 (and the new `maker-checker-segregation.md` reference-list clause) — "`PaymentChannel` is a governed list, `payment-channel.manage`/Finance, no maker/checker YET (exemption ends when it becomes load-bearing)", "MASKED ONLY — `accountLast4`, no full number, never in the audit row", and "the channel on a Receipt/Remittance is OPTIONAL but validated (active + right owner + currency), DERIVES `Receipt.method`, and the usability checks run AFTER the write-once resume" are all easy to get wrong |
| 2026-09-03 | `meta/context/finance-lifecycle.md` gains a **Commission Reconciliation (Process 36)** section (filed via `/brain-gap` at `ibms-app` Part C #36). Completes the `CommissionLedgerEntry` lifecycle #35 stubbed. **VAT on commission is GOVERNED on `CommissionAgreement.vatRatePercent`** (migration `20260903130000`, `DECIMAL(5,2)` default 0) — Compliance / Manager set it beside `ratePercent` (`commission-rate.manage`), Finance only applies it; `POST /commission/agreements` takes an optional `vatRatePercent` (`0..100`, 422 outside), a same-rate re-post is idempotent only if **both** rate + VAT rate match. **The rate is SNAPSHOTTED** onto `CommissionLedgerEntry.vatRatePercent` at `calculate`, and `vatAmount = amount × vatRatePercent%` is stamped then (no longer 0); the invariant survives a manual override (`recordOverrideApproval` recomputes `vatAmount` from `overrideAmount × the frozen rate`, purely from fields the `where` already pins) and a later `CommissionAgreement` edit. `CommissionLedgerEntryView` gains `vatRatePercent`, non-zero `vatAmount`, `grossAmount = amount + vatAmount`. **`status` gets `outstanding → paid | reversed`** — `CommissionLedgerEntry` is NOT a `WorkflowTransitionService` entity (plain-string `status`), but the legal moves live in `commission.config.ts`'s `COMMISSION_ENTRY_TRANSITIONS` and every move validates + audits + persists via a **status-conditional `updateMany`** (never a bare `.status =`). **`outstanding → paid` = `POST /commission/entries/:id/settle`** (`commission.reconcile` — **NEW seed perm `[FINANCE_COLLECTIONS_OFFICER]`**, no maker/checker, like #32's remittance): `{ statementAmount, paymentReference }`, `statementAmount` **must equal `amount` exactly** (a variance → **422** pointing at Process 39, never a silent short settle); a **pending** override or a `reversed` entry blocks it (422); write-once (same figure + reference → resume 200, different → 409); the status-conditional `updateMany` `where` re-asserts **every** validated condition (`race-safe-invariants.md`) — `status`, exact `amount`, "no pending override", **and** "no Process 22 `CommissionReversal` on the policy" as a relation filter (`policy: { endorsements: { none: { commissionReversal: { isNot: null } } } }`), so a concurrently-minted reversal → clean 0-row 409, not only the pre-check 422; the `→ paid` / `→ reversed` moves are asserted against `COMMISSION_ENTRY_TRANSITIONS`. **`{outstanding|paid} → reversed` is DRIVEN BY Process 22, not an endpoint**: a cancellation / negative `Endorsement` minting a `CommissionReversal` calls `CommissionLedgerService.reconcileReversalForPolicy` **best-effort** (the #29 `lossRatio.recomputeForPolicy` precedent — never fails the endorsement flow, the entry may not exist); it recomputes `reversedAmount` from **live** `CommissionReversal` rows (`computeReversalState` — pooled, **capped at `amount`**), stamps `reversedAmount`/`reversedAt`/`reversalReason`, and flips `status → reversed` **only when fully clawed back** (a partial cancellation → `outstanding` + partial `reversedAmount`). `settle` re-checks the same live gate. `EndorsementModule` imports `CommissionModule` (one-way, no cycle). Audit: `CREATE`/`UPDATE CommissionAgreement` carry `vatRatePercent`; `CREATE CommissionLedgerEntry` carries `vatRatePercentApplied` + `vatAmount`; `settle` → `UPDATE` (`settlementAuditSnapshot`), the reversal reflection → `UPDATE` (`reversalAuditSnapshot`, reason verbatim). **No summary report** (that is #40). All `ibms-app` product decisions — Part 3.6 says only "track rate / amount / tax / paid / outstanding / reversed". | Read the Commission Reconciliation section of `finance-lifecycle.md` before touching #36–40 — "VAT is governed on `CommissionAgreement.vatRatePercent` + snapshotted onto the entry, `vatAmount == amount × vatRatePercent%` always", "settle needs an EXACT statement match (a variance is #39), no maker/checker, new `commission.reconcile` perm", and "`→ reversed` is NOT an endpoint — Process 22's `CommissionReversal` drives a best-effort recompute that only flips status on FULL clawback" are all easy to get wrong |
| 2026-09-03 | `meta/context/finance-lifecycle.md` gains a **Commission Calculation (Process 35)** section (filed via `/brain-gap` at `ibms-app` Part C #35). **The governed rate table is `CommissionAgreement`** — by `(insurerId, insuranceLine)`, time-windowed. `POST /commission/agreements` (`commission-rate.manage` = `[COMPLIANCE_OFFICER, BRANCH_DEPARTMENT_MANAGER]` — **NOT Finance**: Finance applies the governed rate but "cannot alter commission rate tables without approval"). A rate change **opens a new window and closes the prior open one at `new.effectiveFrom`**, both in ONE `$transaction`; the partial `UNIQUE ("insurerId", "insuranceLine") WHERE "effectiveTo" IS NULL` (migration `20260903120000`, raw SQL) = **at most one open window per pair** (`P2002` → 409). `effectiveFrom` may be future-dated but **not earlier than the window it supersedes** (422). **`resolveGovernedRate(agreements, at)` (pure)** = the window whose `[effectiveFrom, effectiveTo)` contains `at` (`from` inclusive, `to` exclusive). **`POST /commission/entries` (`commission.calculate` / Finance)** records the **one `CommissionLedgerEntry` per policy** (`policyId @unique`, write-once — the #31 pattern) at the governed rate in force at the policy's **`inceptionDate ?? createdAt`** (not today); `amount = premium × rate%` (`applyPercentage`, rate bounded `0..100` so `amount ≤ premium`); 422 if unissued / no covering agreement; a re-`POST` with a changed governed figure → **409** ("recorded once — a correction is a manual override"). **NO maker/checker on `calculate`** (mechanical, like #31 raising an invoice). **#31's `commissionDeducted` is NOT rewired** to this table — it stays on the placed-quotation rate; the ledger entry is the broker's governed record. **The manual override IS a maker/checker pair**: `POST /commission/entries/:id/override` (`commission-override.raise` / Finance) — `{ overrideAmount, reason }`, `reason` mandatory, `0 ≤ x ≤ premium`; writes the migration's new `overrideAmount` column + `isManualOverride` + `overrideRequestedByUserId` and **leaves `amount` (governed) untouched** (pending; Finance may revise a still-pending override freely). `POST .../override/approve` (`commission-override.approve` / **Manager**) — `assertDifferentActors` + the `CommissionLedgerEntry_maker_checker_distinct` CHECK (migration `20260826091424`), status-conditional `updateMany` (0 rows → 409), **copies `overrideAmount` into `amount`**; a null requester → 409 (the #28 fix), a different approver on an already-approved override → 409, the same one → idempotent. `CommissionLedgerEntryView.effectiveAmount` = `overrideApproved ? overrideAmount : amount`. Audit: `CREATE`/`UPDATE CommissionAgreement`, `CREATE CommissionLedgerEntry` (rate + amount), `UPDATE`/`APPROVE` (override) carrying `overrideReason` **verbatim** (the reason IS the "separately logged" requirement — a business justification, not personal data). Book-wide reads. **No seed change** (all four commission perms pre-existed); `vatAmount` stays `0` (VAT on commission is #36). **`meta/lex/race-safe-invariants.md` also gains a clause** (from the #35 `@code-reviewer` MINOR): a status-conditional `updateMany` must re-assert in its `where` **every** field the caller validated between the read and the write (the maker id `assertDifferentActors` checked, the amount about to be copied), not only `status` — so a concurrent edit is a clean 0-row → 409, never a stale write or a `CHECK` 500. All `ibms-app` product decisions — Part 3.6 says only "apply the correct rate from the agreement table (by insurer + line)" and "a manual override with a mandatory reason + a separately logged approval". | Read the Commission Calculation section of `finance-lifecycle.md` before touching #35–40, and the new `race-safe-invariants.md` "re-assert every validated field" clause before writing any approval `updateMany` — "the rate table is time-windowed, one open window per pair (partial UNIQUE), Compliance/Manager only (NOT Finance)", "calculate = the governed rate at the policy's inception, one entry per policy, NO maker/checker, #31 NOT rewired", and "the override IS maker/checker — raise leaves `amount` governed, approve copies `overrideAmount` in, the reason is logged verbatim" are all easy to get wrong |
| 2026-09-03 | `meta/context/finance-lifecycle.md` gains an **Insurer Accounting (Process 34)** section (filed via `/brain-gap` at `ibms-app` Part C #34). **`GET /insurer-accounting/payables?insurerId=&asOf=`** (`insurer-accounting.read`) — the accounts-payable report, **one row per insurer** with `outstandingAmount` (owed right now), `remittedAmount` (paid to date), counts, and `oldestDaysOutstanding`, + a pooled `totals` row. The insurer-side **mirror of #33**; **computed on the fly, no stored aggregate**. **The obligation arises at collection, is discharged by the `Remittance`** — an **outstanding** obligation is a *collected-but-not-yet-remitted* invoice (a `Receipt` exists, no `Remittance`); it is **NOT** read from a `Remittance` row (#32 only creates a `Remittance` post-transfer and always stamps `remittedAt`, so a `Remittance` = settled). **Amount owed per invoice = `premiumAmount − commissionDeducted`** (`computeRemittanceAmount`, == #32's `Remittance.amount`, tax+fees stay with the broker), derived in the pure builder; the **remitted** side is straight from `Remittance.amount`. **`asOf`** (bare `YYYY-MM-DD`, today or earlier → 422 if future; default today) makes both sides point-in-time correct — `Receipt.receivedAt < asOf+1d` for collected, `Remittance.remittedAt < asOf+1d` for remitted, outstanding-as-at-`asOf` = collected by then and any `Remittance` came after (one `where` on `receipts`: `{ some: { receivedAt: { lt: X } }, none: { remittance: { remittedAt: { lt: X } } } }`). **No ageing buckets** (#34's line is "a query", not "an ageing query" like #33) — one `outstandingAmount` + `oldestDaysOutstanding` (whole UTC days since the earliest unremitted `Receipt.receivedAt`; `-1` when none); `Insurer.creditTermsDays` NOT factored in (deferred). Non-policy invoices skipped. **Book-wide** (`insurer-accounting.read` = `[FINANCE_COLLECTIONS_OFFICER, BRANCH_DEPARTMENT_MANAGER, EXECUTIVE_MANAGEMENT, EXTERNAL_AUDITOR]`; optional `insurerId` narrows), rows **worst-first**, capped `INSURER_PAYABLES_ROW_LIMIT = 5000` per side. **No maker/checker** (a read). **Not audit-logged** — same Confidential tier / #31 decision as #33. Every figure pooled through `sumMoney`. **No migration, no seed change** (`insurer-accounting.read` pre-existed). All `ibms-app` product decisions — Part 3.6 says only "accounts-payable / remittance obligations per insurer". | Read the Insurer Accounting section of `finance-lifecycle.md` before touching #34–40 — "outstanding = a collected-but-unremitted invoice, NOT a `Remittance` row (that means settled)", "amount owed = premium − commission = the eventual `Remittance.amount`", "`asOf` point-in-time via the `receipts` `{ some, none }` filter", and "book-wide, worst-first, no buckets, NOT audited" are all easy to get wrong |
| 2026-09-03 | `meta/context/finance-lifecycle.md` gains a **Client Accounting (Process 33)** section (filed via `/brain-gap` at `ibms-app` Part C #33). **`GET /client-accounting/ageing?customerId=&asOf=`** (`client-accounting.read`) — the accounts-receivable / ageing report, **one row per customer with an outstanding balance** split into `current` / `d1_30` / `d31_60` / `d61_90` / `d90_plus` buckets + a pooled `totals` row. **Computed on the fly — no stored aggregate table** (the #30 Claims Analytics shape; the unscoped `GET /invoices` 400 message points here). **"Outstanding" is structural — an `Invoice` with no collection `Receipt`** (#32 records exactly one per invoice for the full total, so a receipt = paid in full; no partial state). **`asOf`** is the ageing reference date (bare `YYYY-MM-DD`, today or earlier — a future date → 422; default today) and is **point-in-time correct for the outstanding set with no history table**: the query filters `Invoice.createdAt < asOf+1d` and requires `Receipt.receivedAt < asOf+1d` to be `none`, and `Invoice.dueDate` is write-once at #31. **Buckets are the textbook 30 / 60 / 90-day bands — drafted / unsourced** (`<= 0` days overdue → `current`, then 1–30 / 31–60 / 61–90 / 90+), same status as `INVOICE_MAX_DUE_DAYS_AHEAD` (#31) / `CLAIM_LARGE_THRESHOLD_JOD` (#23) / the #27 follow-up thresholds / the #29 loss-ratio "period". **Book-wide** (`client-accounting.read` = `[FINANCE_COLLECTIONS_OFFICER, BRANCH_DEPARTMENT_MANAGER, EXECUTIVE_MANAGEMENT, EXTERNAL_AUDITOR]`; the optional `customerId` just narrows), rows **worst-first** (largest days-overdue, then largest balance, then name), capped at `AR_AGEING_INVOICE_LIMIT = 5000` (the #30 `ANALYTICS_POLICY_LIMIT` precedent). **No maker/checker** (a read). **Not audit-logged** — an invoice total is Confidential, not Highly Confidential (the #31 decision: `GET /invoices` is likewise not audited); contrast the #30 breakdown, which aggregates HIGHLY_CONFIDENTIAL `Claim` rows and does write a `READ` row. Every figure pooled through `sumMoney` (`money.util.ts`). **No migration, no seed change** (`client-accounting.read` pre-existed — its seeded description is literally "View the client accounts-receivable/ageing report"). All `ibms-app` product decisions — Part 3.6 says only "an accounts-receivable / ageing report per customer". | Read the Client Accounting section of `finance-lifecycle.md` before touching #33–40 — "computed on the fly, no stored table", "outstanding = an invoice with no `Receipt` (structural, mirrors #32's one-receipt-per-invoice)", "`asOf` is point-in-time correct for the outstanding set via `createdAt` + `receivedAt` filters, relying on write-once `dueDate`", "30/60/90 buckets are drafted", and "book-wide, worst-first, NOT audited (Confidential, not Highly Confidential)" are all easy to get wrong |

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
