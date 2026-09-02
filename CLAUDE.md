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
| 2026-09-02 | `meta/context/claims-lifecycle.md` § "The rules that aren't obvious" — the **insurer non-response follow-up** row gains a Process 27 sub-point (filed via `/brain-gap` at `ibms-app` Part C #27, Claim Follow-up): the alert clock runs from the claim's `REGISTERED` `ClaimStatusHistory.changedAt` (one clock, NOT reset at `UNDER_ASSESSMENT`); "awaiting the insurer" = the pre-verdict statuses `REGISTERED` / `DOCUMENTATION_IN_PROGRESS` / `UNDER_ASSESSMENT`; the threshold is **per broad line family** (`motor` 7, `property` 10, `medical` 7, `liability`/`marine` 15, else 9 — **drafted, unsourced**, snapshotted onto `Claim.followUpAlertThresholdDays` at notification, Jordan business days via the shared `isFollowUpDue`); a `ClaimFollowUpAlert` is an accountability nudge, **NOT a `Claim` status change**, with **at most one unresolved per claim** as a partial `UNIQUE ... WHERE "resolvedAt" IS NULL` (raise = `create` + `P2002`→already-alerted); the nightly sweep raises for due pre-verdict claims and auto-resolves alerts whose claim has since progressed, plus a manual `claim.followup.manage` resolve; no maker/checker. All `ibms-app` product decisions, no source document. | Re-read that row before touching claim follow-up — the "clock from REGISTERED, one clock", "per-line threshold is drafted + snapshotted", and "an alert is not a status change; one open per claim is a DB constraint" points are easy to get wrong |
| 2026-09-02 | `meta/context/claims-lifecycle.md` § "The rules that aren't obvious" — a new **Claim Assessment (Process 26)** bullet (filed via `/brain-gap` at `ibms-app` Part C #26): Process 26 = adjuster survey/investigation stamps + two engine transitions (`DOCUMENTATION_IN_PROGRESS → UNDER_ASSESSMENT`, then `→ APPROVED | PARTIALLY_APPROVED | DECLINED`), each also writing a `ClaimStatusHistory` row; the four settlement figures are Process 28, not here. The `→ UNDER_ASSESSMENT` move is a **hard safety gate** on the mandatory-document checklist, recomputed from the live `ClaimDocument` rows (not a stored `documentationComplete` snapshot). The `→ verdict` move is gated on the loss adjuster having completed **both** the survey and the investigation — **drafted, unsourced** (Part 3.7 tracks the completion data but does not say it blocks the verdict), same status as `CLAIM_LARGE_THRESHOLD_JOD` / the #25 checklist matrix / #16's 10 % / 2 pp. Adjuster stamps + the verdict are write-once (409 on change); a disputed verdict routes to Complaint Management (Process 42), the claim status is not walked back. No maker/checker at Process 26 (single-actor Claims work; the second approver is at settlement, Process 28). All `ibms-app` product decisions, no source document. | Re-read that bullet before touching claim assessment — the "checklist gate is hard + live-recomputed", the "drafted adjuster-work gate on the verdict", and the "no maker/checker here" points are easy to get wrong |
| 2026-09-02 | `meta/context/policy-lifecycle.md` § "The rules that aren't obvious" — the **Policy Checking** row (filed via `/brain-gap` at `ibms-app` Part C #20) gains two sub-points: (1) **`DISCREPANCY` IS the Delivery block, so driving a Policy to it is a control action** — the check records its result authoritatively (the `PolicyChecking` row + the linked PI risk event in one transaction), then walks the parent `Policy` through the engine; that walk is best-effort for a clean `VERIFIED` outcome but an **unappliable `DISCREPANCY` outcome is a hard 409, not a swallowed warn** (else a concurrent divergent check could leave a policy `VERIFIED` with `discrepancyFound = true` and Delivery unblocked). Generalised: a best-effort status walk whose terminal state is a safety gate must fail loudly. Residual: two near-simultaneous divergent checks can still race on `discrepancyFound` itself — needs per-policy serialisation. (2) **maker/checker on `PolicyChecking` maps only `placedByUserId` today, but the checker compares against the *issued* schedule the issuing officer (#19) transcribed** — `ibms-app` enforces `checkedByUserId ≠ issuedByUserId` app-side as a stricter-than-lex belt; a decision is needed on whether `maker-checker-segregation.md`'s row + the DB `CHECK` should extend to `issuedByUserId`. All `ibms-app` product decisions, no source document. | Re-read that section before touching Policy Checking / the `Policy` status walk — the "an unappliable discrepancy must throw" rule and the issuer-segregation open question are easy to miss |
| 2026-09-02 | `meta/context/policy-lifecycle.md` § "The rules that aren't obvious" — the **Cancellation / Commission Reversal** row (filed via `/brain-gap` at `ibms-app` Part C #22, Endorsement Management) gains five sub-points: (1) `REFUND_APPROVAL_THRESHOLD_JOD` + `SHORT_PERIOD_CLIENT_RETURN_PERCENT` are **drafted, unsourced** product constants (like #16's 10% / 2 pp) — no Finance approval-matrix / short-period-scale source; (2) the **maker/checker gate on an above-threshold refund must be structural at the APPLY write**, not only the `REFUND_APPROVAL_PENDING` status — a crash / concurrent call between the two separate transitions can strand the endorsement at `FINANCIAL_ADJUSTMENT_CALCULATED` with an unapproved refund, and the engine map allows `→ APPLIED` unconditionally, so `apply` itself must refuse `refund && needsApproval && approvedByUserId == null`; (3) **at most one in-flight cancellation per policy** is a partial-`UNIQUE` invariant (`WHERE changeType='cancellation' AND status<>'CLIENT_NOTIFIED'`), not a `Policy.status==='ACTIVE'` check — the policy stays ACTIVE until APPLY, so a second cancellation would mint a duplicate `Refund` + `CommissionReversal`; (4) the cancellation `Policy ACTIVE → CANCELLED` walk is a **control action → fail loudly** (same generalisation as the Policy Checking row — a policy left ACTIVE after cover was cancelled still accepts claims / renewals); (5) endorsement `effectiveFrom` must sit inside the cover period and no earlier than the current open `PolicySchedule` version. All `ibms-app` product decisions, no source document. | Re-read that section before touching Endorsement / cancellation / Refund-approval logic — the "APPLY must re-check approval structurally", "one live cancellation is a DB constraint", and "the policy-cancel walk must throw" points are all easy to get wrong |
| 2026-09-02 | `meta/context/claims-lifecycle.md` § "The rules that aren't obvious" — two rows extended (filed via `/brain-gap` at `ibms-app` Part C #23, Claim Notification): **(A) coverage-in-force-at-loss-date** — resolve to the `PolicySchedule` version whose `[effectiveFrom, effectiveTo)` window contains the loss date; the set of versions IS the materialised endorsement history (no separate `Endorsement` query needed); **`Policy.expiryDate` is an independent upper bound** (nothing closes the open schedule row at expiry, so `effectiveTo` stays `null`); **reject on notify (422), never on a later read** — a validly-notified mid-term loss can become unresolvable after a #22 forward cancellation, and the read must still return the claim. **(B) large-claim threshold** — `CLAIM_LARGE_THRESHOLD_JOD` is a **drafted, unsourced** constant (like #16's 10%/2pp, #22's refund/short-period figures); `Claim.isLargeClaim` set at notification is an **advisory snapshot**, and Process 28's second-approver gate must be **re-derived from live data** (the approved amount) at the settlement decision point. All `ibms-app` product decisions, no source document. | Re-read that section before touching claim coverage-validation or the large-claim / second-approver gate — the "reject on notify not on read", "`expiryDate` is a separate bound", and "re-derive the #28 gate, don't trust the snapshot" points are all easy to get wrong |

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
