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
| 2026-08-25 | `ibms-app` pushed to [github.com/SHOUQALMAHARBAH/IBMS-APP](https://github.com/SHOUQALMAHARBAH/IBMS-APP) and now vendors this repo as a pinned git submodule at `ibms-app/ibms-brain/` (`ibms-app/CLAUDE.md` imports it on line 1). See `meta/designs/2026-08-ibms-app-brain-submodule-sync.md`. | A change here does not reach `ibms-app` until its submodule pin is bumped — see that design doc's "Consequences" |
| 2026-08-26 | New `meta/lex/backup-rpo-rto.md` — draft RPO (24h)/RTO (15min) targets for `ibms-app`, enforced by a real weekly restore-drill script (`ibms-app/scripts/backup-restore-drill.sh` + `.github/workflows/backup-drill.yml`), landed alongside `ibms-app` backlog A.9 (data masking/leakage prevention) and A.10 (SAST/DAST, env separation, backups). | Re-read `meta/lex/backup-rpo-rto.md` before citing an RPO/RTO figure — they're drafts pending business-continuity sign-off, not confirmed numbers |
| 2026-08-26 | New `meta/lex/kyc-aml-sla-timers.md` — filed via `/brain-gap` while building `ibms-app` backlog Part C #3-4 (Customer Acquisition/Onboarding): `meta/lex/pdpl-sla-timers.md`'s 14-entry registry is entirely PDPL-sourced and has no row for CBJ AML/KYC compliance-review turnaround or periodic re-KYC cadence (a different regulatory domain). Four draft, unsourced figures now tracked in code (`ibms-app`'s `sla-registry.config.ts`/`kyc.service.ts`) pending a real CBJ AML source document. | Re-read `meta/lex/kyc-aml-sla-timers.md` before citing a KYC/EDD review SLA or re-KYC cadence figure — all four are drafts pending a real source, not confirmed numbers |
| 2026-08-27 | New `meta/lex/race-safe-invariants.md` — filed via `/brain-gap` after `@code-reviewer` rated a `findMany().find()` check-then-act guarding an unconditional `create()` a BLOCKER in `ibms-app` backlog Part C #7 (`InsuranceProgram` assembly): two concurrent requests both pass the pre-check and both write. Second occurrence of the class (Part C #2 Prospect double-conversion was the first). Rule: a single-live-row / one-shot / no-duplicate invariant is enforced by a DB constraint (partial `UNIQUE` index, `CHECK`) or a status-conditional `updateMany`, never a read-then-decide-then-write. Enforced by the `@code-reviewer` gate (`MAJOR` from now on, not a judgment-call BLOCKER). | Re-read `meta/lex/race-safe-invariants.md` before adding any "only one of these can exist / this can only happen once" rule — a pre-check without a DB or conditional-write backstop is not an invariant |
| 2026-08-29 | `meta/context/policy-lifecycle.md` § "The rules that aren't obvious" gains a row on **RFQ follow-up / insurer non-response**: a lapsed `RFQInsurer.followUpThresholdDays` (default 9, Jordan business days) auto-marks the silent submission `NO_RESPONSE` via the workflow engine — not just an alert — and `NO_RESPONSE` is non-terminal (a late insurer can still be moved to QUOTED/DECLINED). Filed via `/brain-gap` while building `ibms-app` backlog Part C #12 (Market Placement); the threshold default and the auto-vs-alert choice are `ibms-app` product decisions, draft pending a real market-practice figure. | Re-read that section before touching RFQ follow-up / `RFQInsurer` status logic — the auto-advance and the "not terminal" point are both easy to get wrong |

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
