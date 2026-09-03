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
| 2026-09-03 | `meta/context/finance-lifecycle.md` gains a **Client Accounting (Process 33)** section (filed via `/brain-gap` at `ibms-app` Part C #33). **`GET /client-accounting/ageing?customerId=&asOf=`** (`client-accounting.read`) — the accounts-receivable / ageing report, **one row per customer with an outstanding balance** split into `current` / `d1_30` / `d31_60` / `d61_90` / `d90_plus` buckets + a pooled `totals` row. **Computed on the fly — no stored aggregate table** (the #30 Claims Analytics shape; the unscoped `GET /invoices` 400 message points here). **"Outstanding" is structural — an `Invoice` with no collection `Receipt`** (#32 records exactly one per invoice for the full total, so a receipt = paid in full; no partial state). **`asOf`** is the ageing reference date (bare `YYYY-MM-DD`, today or earlier — a future date → 422; default today) and is **point-in-time correct for the outstanding set with no history table**: the query filters `Invoice.createdAt < asOf+1d` and requires `Receipt.receivedAt < asOf+1d` to be `none`, and `Invoice.dueDate` is write-once at #31. **Buckets are the textbook 30 / 60 / 90-day bands — drafted / unsourced** (`<= 0` days overdue → `current`, then 1–30 / 31–60 / 61–90 / 90+), same status as `INVOICE_MAX_DUE_DAYS_AHEAD` (#31) / `CLAIM_LARGE_THRESHOLD_JOD` (#23) / the #27 follow-up thresholds / the #29 loss-ratio "period". **Book-wide** (`client-accounting.read` = `[FINANCE_COLLECTIONS_OFFICER, BRANCH_DEPARTMENT_MANAGER, EXECUTIVE_MANAGEMENT, EXTERNAL_AUDITOR]`; the optional `customerId` just narrows), rows **worst-first** (largest days-overdue, then largest balance, then name), capped at `AR_AGEING_INVOICE_LIMIT = 5000` (the #30 `ANALYTICS_POLICY_LIMIT` precedent). **No maker/checker** (a read). **Not audit-logged** — an invoice total is Confidential, not Highly Confidential (the #31 decision: `GET /invoices` is likewise not audited); contrast the #30 breakdown, which aggregates HIGHLY_CONFIDENTIAL `Claim` rows and does write a `READ` row. Every figure pooled through `sumMoney` (`money.util.ts`). **No migration, no seed change** (`client-accounting.read` pre-existed — its seeded description is literally "View the client accounts-receivable/ageing report"). All `ibms-app` product decisions — Part 3.6 says only "an accounts-receivable / ageing report per customer". | Read the Client Accounting section of `finance-lifecycle.md` before touching #33–40 — "computed on the fly, no stored table", "outstanding = an invoice with no `Receipt` (structural, mirrors #32's one-receipt-per-invoice)", "`asOf` is point-in-time correct for the outstanding set via `createdAt` + `receivedAt` filters, relying on write-once `dueDate`", "30/60/90 buckets are drafted", and "book-wide, worst-first, NOT audited (Confidential, not Highly Confidential)" are all easy to get wrong |
| 2026-09-03 | `meta/context/finance-lifecycle.md` gains a **Collection (Process 32)** section (filed via `/brain-gap` at `ibms-app` Part C #32). `Invoice` IS a `WorkflowTransitionService` entity — #31 creates it at `@default(INVOICED)`, **#32 drives every subsequent hop through the engine**: `POST /invoices/:id/receipt` (`receipt.record`) → `INVOICED → COLLECTED`, `POST /invoices/:id/reconcile` (`receipt.record`) → `COLLECTED → RECONCILED`, `POST /invoices/:id/remittance` (`remittance.record`) → `RECONCILED → REMITTED` — one hop per endpoint, matching `WORKFLOW_TRANSITIONS.Invoice`. **#32 = one full-payment receipt per invoice**: `Receipt.amount` **must equal `Invoice.totalAmount` exactly** — a partial/over payment is a **422** (the `money-decimal-jod.md` "a mismatch is raised as an exception, never silently written off" rule at the door; the variance path is Process 39). The transition's status-conditional `updateMany` IS the "one receipt/remittance per invoice" race gate (no extra `@unique` on `Receipt.invoiceId`); artefacts are written **after** the transition (the #24 `register` pattern — lost race → resume/409; crash between → re-entry writes only the artefact). Reconcile **re-derives `sumMoney(receipts) === totalAmount` from the live rows** (the #16 rule). The remittance is **`premiumAmount − commissionDeducted` computed server-side** (`>= 0` since #31 bounds commission ≤ premium; tax+fees stay with the broker); `insurerId` from `Policy.insurerId`; a non-policy invoice → 422; deterministic figures → a re-`POST` is an idempotent no-op, a stored figure that disagrees is a **409**; `Remittance.receiptId @unique` + `P2002` backstop. **Part 7.3 client-money segregation**: every collection books an `in` `ClientFundsLedgerEntry`, every remittance an `out` one, each in the **same `$transaction`** as its `Receipt`/`Remittance`. **No maker/checker** (`roles-and-segregation-of-duties.md` — Finance/Collections single-actor; moving client money to the insurer is mechanical, not an approval). Audit: a `CREATE` row for each `Receipt` / `Remittance` / `ClientFundsLedgerEntry` (amount as a fixed string, no free text) + the three engine `TRANSITION` rows. No migration, no seed change. All `ibms-app` product decisions — Part 3.6 says only "the full Invoice → Collection → Receipt → Reconciliation → Remittance cycle". | Read the Collection section of `finance-lifecycle.md` before touching #32–40 — "every Invoice hop via the engine, the transition IS the race gate", "one exact-amount receipt (a variance is #39, never a silent write-off)", "remittance = premium − commission computed", and "a ClientFundsLedgerEntry per money movement, same $transaction" are all easy to get wrong |
| 2026-09-02 | **New `meta/context/finance-lifecycle.md`** (Domain D seed) — filed via `/brain-gap` at `ibms-app` Part C #31, Premium Billing. Covers **Process 31** only (the rest of Domain D grows the file as it lands): `POST /invoices` (`invoice.create` / Finance, **no maker/checker**) raises the one **new-business premium `Invoice`** per policy — `premiumAmount` **carried from `Policy.issuedPremium`** (422 if unissued), `commissionDeducted` **auto-derived** as `premium × Recommendation.recommendedQuotation.commissionRatePercent` (the placed rate, #22's lookup; 422 if the quote captured none — Process 35's `CommissionAgreement` will replace this), `taxAmount` + `feesAmount` the **only** money inputs (each `0 ≤ x ≤ premium`), **`totalAmount` ALWAYS `premium + tax + fees − commissionDeducted` computed server-side** (DTO rejects it — the #28 `netSettlement` lesson). `dueDate` a required `YYYY-MM-DD`, today..+365d (drafted). **One new-business premium invoice per policy** = partial `UNIQUE ("policyId") WHERE "invoiceType" = 'new_business_premium'` (migration `20260902210000`, raw SQL); write-once #24/#28-style (byte-identical re-POST → the existing row, any different figure → 409, concurrent → `P2002` → 409). `Invoice` IS a `WorkflowTransitionService` entity but #31 only creates it at `@default(INVOICED)` — the `INVOICED → COLLECTED` cycle is Process 32. Book-wide read (`client-accounting.read`; `GET /invoices` with no `policyId`/`customerId` scope = 400). Audit = one `CREATE Invoice` row (figures as fixed strings, no free text); reads not audited (Confidential, not Highly Confidential). All `ibms-app` product decisions — Part 3.6 says only "premium + tax + fees, net of commission, with a due date". | Read `finance-lifecycle.md` before touching billing / Domain D — "premium carried, commission auto-derived from the placed quote rate, tax+fees the only inputs, total always computed", "one new-business premium invoice per policy (partial UNIQUE)", and "creates at INVOICED only — the collection cycle is #32" are all easy to get wrong |
| 2026-09-02 | `meta/context/claims-lifecycle.md` § "The rules that aren't obvious" — the **Loss Ratio** bullet gains a Process 30 sub-point (filed via `/brain-gap` at `ibms-app` Part C #30, Claims Analytics): the **aggregate** `Claims ÷ Premium` breakdown (`GET /claims-analytics/loss-ratio?groupBy=customer\|policy\|line`, `claims-analytics.view` — a cross-book reporting perm, so **book-wide**, optional `customerId`/`policyId`/`insuranceLine` filters just narrow the set) is **computed on the fly — no stored aggregate table** (the per-`RenewalCase` `LossRatio` write stays #29's). Each group's ratio is `computeLossRatio` over the group's **pooled** net settlements and **pooled** written premium — NOT a sum/average of per-policy ratios; same **paid, all-time** basis as #29; `totals` pool every in-scope policy regardless of `groupBy`; rows ordered **worst-first**. The denominator is **written premium** — Σ `issuedPremium ?? requestedPremium` over policies past `PLACEMENT_CONFIRMED`; a `CANCELLED`/`EXPIRED` policy still contributes its **full** written premium (earned-premium proration + an *incurred* ratio adding open-claim reserves are renewal-module refinements, deferred). The read is audit-logged (`entityType: 'ClaimsAnalytics'`, counts/filters only, `isSensitiveDataAccess` when a claim contributed). All `ibms-app` product decisions, no source document. | Re-read that sub-point before touching claims analytics / Loss Ratio — "computed on the fly, no stored table", "pooled figures, not averaged ratios", "written premium (incl. full cancelled/expired) — not earned", and "book-wide read, audit-logged" are all easy to get wrong |
| 2026-09-02 | `meta/context/claims-lifecycle.md` § "The rules that aren't obvious" — a new **Claim Closure (Process 29)** bullet + the **Loss Ratio** bullet extended (filed via `/brain-gap` at `ibms-app` Part C #29, Claim Closure): `POST /claims/:id/closure` (`claim.close` / Claims Officer, **no maker/checker**) drives `Claim SETTLED → CLOSED` gated on `Settlement.clientPaymentConfirmedAt` (supplied in the body, **write-once**, past-only, **no earlier than the loss date** — a tighter "after the Settlement was recorded" bound deliberately not enforced, #21 `deliveredAt` latitude), or `DECLINED → CLOSED` directly (a `clientPaymentConfirmedAt` on a declined claim = 422). Any other status → 422; an already-`CLOSED` claim = 200 no-op that does **not** re-fire the recompute; a different confirmed instant once one is set = 409; the `→ CLOSED` move is a real engine transition (+ best-effort `ClaimStatusHistory` row, the #24–28 seam) and **only the call that actually transitions fires the Loss Ratio recompute** (best-effort, never throws back into closure). `LossRatio` is **renewal-case-scoped** (`renewalCaseId @unique`), so `LossRatioService.recomputeForPolicy` upserts the `LossRatio` for the policy's open `RenewalCase` — **a logged no-op when the policy has none** (the renewal module is not built); `periodClaims` = Σ `Settlement.netSettlement` over the policy's SETTLED/CLOSED claims, `periodPremium` = `issuedPremium ?? requestedPremium`, `ratio` 4 dp (zero premium → zero ratio), the "period" **drafted** as all-time. All `ibms-app` product decisions, no source document. | Re-read those bullets before touching claim closure / Loss Ratio — "closure needs a confirmed payment receipt (write-once, ≥ loss date)", "DECLINED closes directly", "only the transitioner fires the best-effort recompute", and "LossRatio is renewal-case-scoped, a no-op until renewal exists" are all easy to get wrong |

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
