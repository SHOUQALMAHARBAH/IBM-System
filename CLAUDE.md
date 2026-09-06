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
| 2026-09-07 | **UPDATED `meta/context/data-retention-and-disposal.md`** (Part D §5.1, M06) — item #3 of Part D's 9-system checklist, worked one item at a time after Consent/M03 and DSR/M04. All four M06 entities (`RetentionScheduleItem`, `LegalHold`, `DisposalBatch`, `CertificateOfDestruction`) existed in the schema since the initial domain-model migration, but only `RetentionScheduleItem` had a single seeded row and a reader (`AuditLogEntry`, 2026-08-26) — nothing before this build ever wrote a `LegalHold` or `DisposalBatch` row, or let anyone add a SECOND schedule item. Built the first real CRUD across all three: schedule item create/update/confirm (a NEW permission, `retention-schedule.manage`, since no "Legal Counsel" role exists among the 11 seeded `RoleName` values — Compliance/DPO stand in, a documented limitation, not a workaround); Legal Hold place/review/release (a 6-month SLA re-basing via the DSR `applyExtension` start-then-resolve precedent); the full dual-control disposal workflow (nominate→manager-approve→dpo-approve→execute→certificate→close). **Closed a real, previously-flagged schema gap**: `RetentionScheduleItem.recordCategory` gained a genuine `@@unique` constraint (this file had explicitly flagged its absence as an accepted-but-not-ideal gap); the pre-existing seed script's hand-rolled find-then-create/update became a real Prisma `upsert`. **The "dual-control... two different users" checkbox wording only actually enforces HALF of what it names** — `DisposalBatch` has no `managerApprovedByUserId` column, only a timestamp; the DB `CHECK` constraint (pre-existing since migration `20260826091424`) compares only `dpoApprovedByUserId` against `nominatedByUserId`, so `MANAGER_APPROVED` is a self-transition checkpoint, not a second distinct human actor — confirmed by reading the constraint SQL directly rather than assuming the checkbox's prose matched the schema. **The Legal-Hold exclusion check is re-derived from live data at EVERY dual-control step** (nominate, manager-approve, AND dpo-approve), not cached from nomination time — the #16 Broker Recommendation "re-derive the approval gate from live data" precedent, since a hold placed between steps must still block execution. Disposal `execute()` remains a staff ATTESTATION (a status stamp + a `method` field), never a live `DELETE` — this file's own pre-existing "retention informs eligibility; it does not execute disposal" framing, deliberately avoiding a bypass of `AuditLogEntry`'s immutability trigger. **Verification**: +51 api unit (6 new spec files: `retention-schedule.config/service`, `legal-hold.config/service`, `disposal-batch.config/service`) → api unit **2171** (163 files, from 2120). New `test/retention-disposal.e2e-spec.ts` **2/2** — a full lifecycle walk (schedule create/409-duplicate → Legal Hold placed → disposal blocked while held (422) → hold released → nominate→manager-approve→403-self-DPO-approve→distinct-DPO-approve→execute→422-close-without-certificate→certificate→close→schedule confirm→422-edit-after-confirm) plus a second test covering permission-denial and Legal-Hold review re-basing. Full api unit suite 2171/2171 confirmed green; full 51-file api e2e suite green across 8 foreground sub-batches, both chronic flakes (`rbac`, `up-sell`) passing with `--testTimeout=90000`. New Playwright `retention-disposal.spec.ts` 3/3; full Playwright suite 246/246 (from 243). `npm run typecheck`/`lint`/`build` (api + web) OK — lint caught 5 real type-safety errors on first run (an untyped `let row` losing its Prisma type across a try/catch in `retention-schedule.service.ts`; two nested `expect.objectContaining()` calls inside `disposal-batch.service.spec.ts` assertions; one bare `expect.any(Date)` as an object-literal property value in `legal-hold.service.spec.ts`), all fixed following established codebase precedent (an explicit `let row: RetentionScheduleItem`; the DSR `dsr.service.spec.ts` "capture the mock call arg and assert a plain property" shape instead of nesting matchers) rather than suppressed. | Read `meta/context/data-retention-and-disposal.md` before touching M06 again, or any future dual-control workflow whose checkbox prose says "N different users" — "a DB CHECK constraint is the ground truth for which TWO actor columns a dual-control workflow actually compares; a workflow can have a THIRD approval-shaped status checkpoint with no distinct-actor column backing it at all, and the backlog's own prose won't tell you which is which", "a documented schema gap (`recordCategory` with no unique constraint) sitting in a context file for weeks is a real gap to CLOSE the day a real writer needs the invariant, not something to keep working around", "`expect.objectContaining()` nested inside another `expect.objectContaining()`'s property, or a bare `expect.any(X)` used as an object-literal property value rather than a bare argument, both trip `@typescript-eslint/no-unsafe-assignment` — capture the mock call's argument into a locally-typed `const` and assert its fields individually instead, the `dsr.service.spec.ts` precedent", and "a `let x;` declared with no initializer and assigned only inside a try block loses its inferred type across the try/catch boundary under this codebase's strict lint config — give it an explicit type annotation rather than letting TypeScript widen it to `any`" are all easy to get wrong. |
| 2026-09-06 | **RE-VERIFIED `meta/context/data-subject-requests.md`** (Part D §5.1, M04) — item #2 of Part D's 9-system checklist, worked one item at a time after Consent/M03. The checklist's own DSR clause ("logged the same business day regardless of channel, an identity-verification step, SLA computation (15/10 business days + an Access-only extension), a DPO handler assignment, a mandatory 'partially fulfilled' path when a retention flag is still open, never closeable as 'fully fulfilled'") maps onto ALREADY-BUILT M04 functionality clause-by-clause — a "verified, not built" outcome (the #47 KYC/#50 Conflict-of-Interest/#68 Internal IT shape), confirmed by re-running the full suite rather than just re-reading code. **The seed data's own permission descriptions quote this exact backlog wording near-verbatim** (`dsr.log`: "the same business day it is received"; `dsr.close`: "never closeable while a retention flag is open") — strong evidence M04 was built directly against this same source text, not coincidentally compatible. No code changes; api unit 53/53 (`dsr.config.spec.ts`/`dsr.service.spec.ts`), `test/dsr.e2e-spec.ts` 3/3, Playwright `dsr.spec.ts` 3/3, all re-confirmed green with zero regression from the 5+ sessions of unrelated work since M04 originally shipped. | Read `meta/context/data-subject-requests.md` before touching DSR again — when a backlog checklist's wording for an ALREADY-BUILT system is pasted again later (e.g. because the user works through a larger document one item at a time and an earlier item happened to build ahead), re-verify by RUNNING the tests and checking each clause against the actual permission/model text, not by trusting memory that "this was built already" — the verification itself, and its evidence, is the deliverable, matching the #47/#50/#68 discipline. |
| 2026-09-06 | **UPDATED `meta/context/consent-management.md`** (Part D §5.1, M03 touchpoint wiring) — filed at `ibms-app` after the user selected Part D's full 9-item checklist for one-item-at-a-time work, starting with Consent. The backlog names 7 explicit touchpoints (lead capture, onboarding/KYC, needs & risk assessment, RFQ/market placement, claims, Group Medical/Life & Motor Fleet, renewal & cross/up-sell); M03's original build shipped only a generic, unwired capture screen — flagged explicitly as deferred UI-integration work at the time. **5 of 7 wired, 2 deliberately left as a documented gap — confirmed with the user via AskUserQuestion before proceeding, not decided silently**: Claims (no web UI for an individual claim exists anywhere in `apps/web`, only the `claims-analytics` aggregate) and Group Medical/Life & Motor Fleet (maps to `InsuredPerson`, which has ZERO CRUD anywhere) both require building a genuinely separate, substantial prerequisite module first — not a Consent bug. **Lead capture required a real schema change** — `ConsentRecord` gained a THIRD optional owner column, `leadId` (migration `20260913120000`), since a Lead pre-dates a Customer/InsuredPerson row entirely; exactly-one-of-three is a NEW, Consent-local `hasExactlyOneConsentOwner` (deliberately not a generalization of the shared `common/dto.util.ts#hasExactlyOneOwner`, which DSR/M04 also depends on with a different, two-way shape). `LeadRepository.create()` now creates the Lead + its lead-capture ConsentRecord in ONE `$transaction` — a deliberate, documented local exception to this codebase's no-`$transaction` convention, the `EmployeeRepository.terminate()` "create-together" shape; `Lead.marketingConsentGranted` (the pre-existing boolean) stays unchanged, the ConsentRecord row is additive. **The other 5 touchpoints needed NO schema/backend capability change at all** — each already had (or, for Needs Assessment/RFQ, gained via an ALREADY-INJECTED sibling repository in the SERVICE layer, not a widened shared type) a resolvable `customerId`; a single new shared web component (`ConsentCaptureWidget.tsx`) mounted on 5 existing detail pages was the whole fix — the requirement was UI-reachability, not a new capture mechanism. **Verification**: +9 api unit → api unit **2120** (from 2111). Extended `test/lead.e2e-spec.ts` (+1, now 15) and `test/consent-record.e2e-spec.ts` (+1, now 2) for the leadId path; `needs-assessment.e2e-spec.ts`/`rfq.e2e-spec.ts` re-confirmed green against the widened `get()` responses. Full api unit suite 2120/2120 confirmed green; full 50-file api e2e suite green across 8 foreground sub-batches (one confirmed-transient TOTP-timing flake in `auth.e2e-spec.ts`, re-confirmed clean in isolation), both chronic flakes (`rbac`, `up-sell`) passing with `--testTimeout=90000`. Full Playwright suite 243/243 (from 242) — a real bug caught and fixed along the way: the RFQ detail page crashed outright in Playwright because the shared mock RFQ fixture lacked the new `opportunity.customerId` field the page now reads unconditionally. `npm run typecheck`/`lint`/`build` (api + web) OK — one real lint catch (the same `react-hooks/set-state-in-effect` false positive `internal-controls/page.tsx` hit before; fixed with the same async-IIFE wrapper). | Read `meta/context/consent-management.md` before touching Consent again, DSR, or any future PDPL touchpoint-wiring task — "a backlog checklist naming N touchpoints can have some that are genuinely blocked by MISSING prerequisite infrastructure (no web UI, no CRUD at all for the underlying entity) — confirm the scope decision with the user rather than silently building the missing infrastructure OR silently skipping the touchpoint", "when a shared cross-module validator (`hasExactlyOneOwner`) would need widening for ONE caller's new shape but another caller (DSR) doesn't share that shape, write a caller-local variant instead of generalizing the shared one", "prefer resolving a derived field (like a resolved `customerId` two hops away) via an ALREADY-INJECTED sibling repository in the SERVICE layer over widening a Prisma-payload TYPE that other call sites share — it was tried, reverted, and redone the lighter way here", and "a Playwright mock fixture object is a live contract with the page component — a page-level field access added without updating every shared fixture that feeds that page crashes the whole render, not just the missing field's own display" are all easy to get wrong. |
| 2026-09-20 | **NEW `meta/context/knowledge-management.md`** (Process 74 — CLOSES Domain H, #66-74) — filed via `/brain-gap` at `ibms-app` (backlog Part C #74). One checkbox: "a bilingual knowledge base: product knowledge, insurer appetite, rate guides, regulatory updates." `KnowledgeBaseArticle` (schema's own doc comment: "Process 74 — product knowledge, insurer appetite, rate guides, regulatory updates for staff") pre-exists with zero prior application code — the SAME "dormant model, first real writer" shape #58-73 repeatedly found, closing the domain on the same pattern it opened with. `kb.publish` was already pre-seeded. **"Bilingual" here is OPTIONAL-per-article, not mandatory-both** — the sibling `DocumentTemplate` model (Part 11.2, regulator-facing formal documents) has `nameEn`/`nameAr`/`bodyEn`/`bodyAr` ALL `NOT NULL`; `KnowledgeBaseArticle` is the opposite — only `title` is mandatory, `titleAr`/`bodyEn`/`bodyAr` are all nullable, so an article may exist in English only, Arabic only, or both, a deliberate reading of the schema's own nullability rather than "fixing" it to match the mandatory-both sibling. **Creation IS publishing** — `publishedAt` defaults to `now()` at the DB level with no nullable "draft" state, matching the pre-seeded permission's own verb (`kb.publish`, not `kb.manage`/`kb.create`). **`kb.publish` gates the WHOLE surface, not just the publish action** (the #67/#69/#71 "one pre-seeded permission gates the whole CRUD" precedent) — with a real, documented consequence: only `[COMPLIANCE_OFFICER, BRANCH_DEPARTMENT_MANAGER, PLACEMENT_TECHNICAL_OFFICER]` can even READ the knowledge base via this API, since no second, broader read permission was pre-seeded; a genuinely useful company-wide knowledge base would want much wider read access, but this is a real, deliberate scope limit of the backlog's own permission grid, documented rather than solved by inventing a permission the seed data doesn't define. `category` is mutable via `PATCH` — unlike #72-73's `BcpDrPlan.scenario` (deliberately immutable) — since recategorizing an article is just fixing metadata, not rewriting a scenario's own history; the SAME domain can make different mutability calls for a similarly-shaped "classifying dimension" field depending on what it actually represents. No maker/checker, no SLA timer, no cross-entity FK validation — the simplest Domain H CRUD built this session. No new permission, no migration. `apps/web/` gains a **"Knowledge Base"** screen (bilingual list with RTL-aware Arabic columns/inputs, a publish form, inline title/titleAr edit). **Verification**: +9 api unit (`knowledge-base-article.service.spec.ts`) → api unit **2111** (157 files, from 2102). New `test/knowledge-base-article.e2e-spec.ts` **5/5** — permission gating; a 400 rejecting a category outside the documented 4-value set; a real create(English-only)→list(filtered)→get→update(add Arabic translation) walk; a fully bilingual create in one call; 404s for an unknown article on both GET and PATCH. Full api unit suite 2111/2111 confirmed green; full 50-file api e2e suite green across 8 foreground sub-batches, both chronic flakes (`rbac`, `up-sell`) passing with `--testTimeout=90000`. New Playwright `knowledge-base.spec.ts` 5/5; full Playwright suite 242/242 (from 237). `npm run typecheck`/`lint`/`build` (api + web) OK. **Domain H (Supporting Operations, #66-74) is now COMPLETE** — #66 Employee, #67 Vendor CRUD, #68 verified-not-built, #69 InformationAsset, #70 Document, #71 Vendor risk-tiering/DPA, #72-73 BcpDrPlan, #74 KnowledgeBaseArticle. | Read `meta/context/knowledge-management.md` before touching any future "bilingual" data model or a process whose permission grid names only ONE narrow verb (here, "publish") for what functionally needs to be a much broader CRUD/read surface — "check whether 'bilingual' in a schema doc comment means mandatory-both (`DocumentTemplate`'s shape) or optional-per-item (`KnowledgeBaseArticle`'s shape) before assuming every bilingual model needs the same NOT NULL treatment", "gating an entire CRUD surface — including reads — behind the ONE pre-seeded permission a backlog line's own verb suggests (`kb.publish`) is the established precedent, but document the real consequence (a narrow read audience) as a genuine, deliberate scope limit rather than silently under-serving a 'for staff' knowledge base", and "two structurally-similar 'classifying dimension' fields in the SAME domain (`BcpDrPlan.scenario` vs `KnowledgeBaseArticle.category`) can get OPPOSITE mutability decisions — check what the field represents (a fixed identity vs. an editable classification) rather than copying the most recent sibling's choice" are all easy to get wrong. |
| 2026-09-20 | **NEW `meta/context/bcp-dr-planning.md`** (Process 72-73) — filed via `/brain-gap` at `ibms-app` (backlog Part C #72-73, Domain H). Two checkboxes: a plan for every scenario the source names explicitly (system outage, site/office loss, cyberattack/ransomware, key-staff unavailability, insurer-side service interruption); a documented RTO/RPO + last-tested date + next-test-due date per plan. `BcpDrPlan` (schema's own doc comment: "Process 72-73 — continuity/DR plans and tests") pre-exists with zero prior application code — the SAME "dormant model, first real writer" shape #58-71 repeatedly found. `bcp-dr.manage` was already pre-seeded — no seed change needed. **`meta/lex/backup-rpo-rto.md` already covers ONE narrow, already-tested slice of scenario #1 (`system_outage`)** — the database backup/restore drill (`.github/workflows/backup-drill.yml`, weekly, a real pass/fail on row-count parity + a timed RTO check). That lex file's own RPO/RTO figures (24h/15min) are DRAFT, database-specific, and pre-date this process — not restated or duplicated here. The other four scenarios are organizational/procedural plans with NO code-level automation anywhere in this repo — `BcpDrPlan` is a plain record of a plan's existence and test history, not a system that executes or verifies the plan itself. **No sourced test-cadence figure exists for BCP/DR plans generally** — unlike #71's Vendor annual review (an explicit "Annual" cadence already in `pdpl-sla-timers.md`), nothing names how often a plan must be re-tested; `nextTestDueAt` is therefore a plain CALLER-SUPPLIED field on `recordTest()`, never auto-computed from a fabricated interval — and this process is deliberately NOT wired into `SLA_REGISTRY` at all, since BCP/DR testing cadence is a CBJ operational-resilience concern (Part 10.4/10.5), a different regulatory domain from the PDPL-sourced SLAs that registry tracks. **Checkbox 1 is answered by a genuine coverage/gap check, not just a CRUD a caller must trust was populated correctly** — `GET /bcp-dr-plans/coverage` (`computeScenarioCoverage()`) returns all five named scenarios every time, each with its own `plans` array (possibly empty) and a `hasPlan` flag, the #59/#69 "verify coverage" discipline applied to a five-item checklist. `planDocumentId` (a bare scalar, no Prisma relation) is validated against a real `Document` via `DocumentRepository.findById()` — the #66/#69 link-validation precedent, now reachable because #70 (Document Management) built real `Document` CRUD for this process to validate against. `scenario` is immutable once a plan is created. `apps/web/` gains a **"BCP / DR plans"** screen (the coverage view with gaps flagged, a create form, per-plan record-test action). **Verification**: +16 api unit (`bcp-dr-plan.config.spec.ts` 6, `bcp-dr-plan.service.spec.ts` 10) → api unit **2102** (156 files, from 2086). New `test/bcp-dr-plan.e2e-spec.ts` **6/6** — permission gating; a 400 rejecting a scenario outside the documented 5-value set; a 404 creating a plan with a `planDocumentId` that doesn't reference a real `Document`; a real create→list(filtered)→get→update→record-test walk with a REAL linked `Document` fixture (scenario proven immutable across the update); 404s for an unknown plan on GET/PATCH; the five-scenario coverage view with a real gap-vs-covered assertion. Full api unit suite 2102/2102 confirmed green; full 49-file api e2e suite green across 7 foreground sub-batches, both chronic flakes (`rbac`, `up-sell`) passing with `--testTimeout=90000`. New Playwright `bcp-dr-plans.spec.ts` 5/5; full Playwright suite 237/237 (from 232). `npm run typecheck`/`lint`/`build` (api + web) OK. | Read `meta/context/bcp-dr-planning.md` before touching #72-74 or any future process naming an "RTO/RPO"/"test cadence" concept — "check `meta/lex/backup-rpo-rto.md` before assuming a BCP/DR-flavored process needs its OWN RTO/RPO figures from scratch — it already covers the database-restore slice of the FIRST of five named scenarios, with its own draft figures that should not be restated or duplicated", "not every regulatory-cadence field needs an SLA_REGISTRY entry — that registry is scoped to PDPL-sourced (M03-M10) SLAs specifically; a CBJ operational-resilience concern like BCP/DR testing cadence is a genuinely different regulatory domain, and inventing a fabricated interval (or force-fitting it into SLA_REGISTRY) would be worse than leaving the due-date field caller-supplied", and "a 'plan for every named scenario' checklist item is answered by a coverage/gap-check endpoint enumerating ALL named items every time (flagging which ones are missing), not by a plain list endpoint a caller has to manually verify against the backlog's own prose" are all easy to get wrong. |

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
