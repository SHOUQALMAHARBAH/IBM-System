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
| 2026-09-07 | **UPDATED `meta/context/data-subject-requests.md` + `data-retention-and-disposal.md`** — closed a real integration gap found during a meticulousness re-audit of Part D against the literal backlog text (a `/52 64` request to verify readiness, not build something new). DSR (M04) blocked a DELETION request from closing "fully fulfilled" while a retention flag was open using ONLY a staff attestation (`confirmNoOpenRetentionHold`) — honest when M04 shipped (Retention & Disposal / M06 didn't exist yet, so `LegalHold` had no structured subject reference to check), but the reasoning went STALE once M06 landed in a later session with a real, queryable register that nobody wired up — the DTO's own header comment kept saying "M06 is not built yet" long after it was, the same "stale flag surviving a later session's real build" pattern the Part D completion session already caught once for `internal-controls.config.ts`'s `dormant: true` flags. **Fix**: `LegalHold` widened with optional `customerId`/`insuredPersonId` (migration `20260916120000`, at most one of the two — `hasAtMostOneSubjectReference`, the ConsentRecord/DSR "at most" not "exactly" shape) since `LegalHold.scope` was free text with no structured reference to query against. `LegalHoldRepository.hasActiveHoldForSubject()` is the new live check; `DsrService.fulfil()` (same-module injection, both in `PdplModule` already) now calls it FIRST for a DELETION request and 422s outright if an active hold names the subject — the attestation can no longer override a REAL hold. The attestation still gates the one case the live check cannot cover (a record category whose retention period hasn't elapsed has no per-subject hold row to find) — a deliberate, honest, narrower scope limit, not the gap re-opened. `CreateLegalHoldDto`/`ListLegalHoldsQueryDto` gained matching optional fields (existence-checked, at-most-one validated); the `retention-disposal` web page gained Customer ID / Insured person ID inputs and a "Subject" column. **Verification**: +12 api unit (2 new DsrService.fulfil tests, 4 hasAtMostOneSubjectReference tests, 2 deriveLegalHoldView/audit-snapshot tests, 4 LegalHoldService.create/list tests) → api unit **2316** (185 files, from 2304). New DSR e2e test (full walk: place a hold naming the customer → fulfil blocked 422 even with the attestation ticked → partially-fulfil still works → release the hold → a FRESH DELETION request for the same customer fulfils normally, proving the check is live, not cached); new retention-disposal e2e test (at-most-one 422, unknown-customerId 404, list-by-customerId). Full api unit suite 2316/2316 confirmed green; full 62-file api e2e suite green across 8 foreground sub-batches. New Playwright coverage in `retention-disposal.spec.ts` (a pre-existing test needed a `.first()` fix — the new second Legal Hold fixture row made its own `getByRole('button', {name: 'Release'})` locator ambiguous, the same shared-fixture-affects-other-tests lesson caught before); full Playwright suite 4/4 on the affected spec, no other regressions. `npm run typecheck`/`lint`/`build` (api + web) OK. | Read `meta/context/data-subject-requests.md`'s "not obvious" DELETION bullet and `data-retention-and-disposal.md`'s matching `LegalHold` entry before touching either M04 or M06 again — "a code comment justifying a design choice by citing another module as 'not built yet' is a claim with an expiry date — the day that OTHER module ships in a LATER session, the justification is stale even though the code itself still compiles and passes every existing test; grep for cross-module 'not built yet' / 'doesn't exist yet' comments the same session you give THAT OTHER module its first real writer, the same discipline already applied once to dormant-flag registries", "a hold/exclusion/flag field that is free text (`LegalHold.scope`) cannot be live-queried no matter how well-intentioned the free text is — closing an integration gap like this one usually means a real schema widening (a structured FK), not just new application logic", and "adding a second row to a SHARED Playwright mock fixture can silently turn an existing test's strict-mode locator (`getByRole` with no `.first()`/`.nth()`) ambiguous — re-run every test that consumes a fixture you widen, not just the new test you wrote for it" are all easy to get wrong.
| 2026-09-07 | **UPDATED `meta/context/part-e-dashboards.md`** — CLOSES Part E (backlog Process #64): the sixth and final named dashboard, "Insurer & Employee Performance Dashboard — insurer performance score across 4 axes, employee KPI achievement," plus the cross-cutting closing bullet ("every dashboard filterable by branch/line/insurer/period, and renderable in either language"). **A third, distinct outcome shape — "verify, then close one small real gap"** — neither a fresh build (Sales/Policy/Claims/Compliance) nor Financial Dashboard's "close one real gap." Part E's OWN permission inventory already names `insurer-performance.view` + `employee-performance.view` (NOT a new `dashboard.*.view` code) as this 6th dashboard's own pair — the signal that #60/#61, already fully built, together already ARE the dashboard. Confirmed "insurer performance score across 4 axes" is a literal, exact match to `InsurerPerformanceScore`'s four columns; "employee KPI achievement" reads as #61's own `EmployeePerformanceRecord` scorecard, not #59's narrower `SalesTarget` mechanism. Both #60/#61's full existing suites were RE-RUN (not re-read) to confirm — the #47/#50/#68/DSR discipline. **One small, real, well-motivated gap closed**: `GET /employee-performance` gained a `branchId` filter (via the employee's optional linked `User.branchId`) — additive, no existing caller's call site changed. `GET /insurer-performance` deliberately left untouched (a book-wide, per-insurer score; branch/line scoping would mean recomputing a different metric, not filtering a read). A new, lightweight `/dashboards/insurer-employee-performance` web page presents both book-wide for one period side by side, reusing the existing API clients directly — the two existing single-lookup pages stay untouched, serving their own distinct purpose. **Cross-cutting bullet resolved as: the filter half is honestly satisfied per-dashboard (each of Part E's six own sections already documents exactly which of branch/line/insurer/period apply and which genuinely don't — a dimension-by-dimension audit, not a blanket checkbox); the bilingual half is NOT satisfied anywhere in the app and is explicitly, deliberately out of scope — Part F's own multi-bullet scope (i18n, RTL, bidi text, locale formatting, bilingual documents), nothing Part E's own dashboards could close.** **Verification**: +1 api unit (employee-performance.service.spec.ts) → api unit **2304** (185 files, from 2303). Widened `test/employee-performance.e2e-spec.ts` (+1, now 6/6) for the new branchId scoping; both #60/#61's full existing e2e suites (9 tests) re-confirmed green, unchanged. Full api unit suite 2304/2304 confirmed green; full 62-file api e2e suite green across 8 foreground sub-batches, both chronic flakes (`rbac`, `up-sell`) passing, one confirmed-transient TOTP-timing flake in an unrelated file (`information-asset.e2e-spec.ts`) re-confirmed clean in isolation. New Playwright `insurer-employee-performance-dashboard.spec.ts` 3/3; full Playwright suite **282/282** (from 279). `npm run typecheck`/`lint`/`build` (api + web) OK. **PART E (backlog Process #64) IS NOW COMPLETE** — all six named dashboards built/verified; only `dashboard.executive.view` (a future cross-department rollup, never one of the six named dashboards, no backlog bullet describing its content) remains unbuilt, plus the bilingual gap owned by Part F. **Follow-up audit** (same item, re-checked line-by-line against the literal backlog text on a "was this meticulous?" request) caught and closed ONE real UI gap: `GET /insurer-performance?insurerId=` already accepted an `insurerId` filter since #60's own original build (narrowing the list to one insurer, not a recompute), but the new combined page's first cut omitted the filter input despite the capability already existing end-to-end — added it, scoped to the insurer table only, with a new Playwright test proving it reaches only that request. Re-verified the whole Part E surface while auditing: management-reporting api unit suite re-run (24 files/190 tests), all 7 Part E-related api e2e files re-run live against the test DB (32/32), full Playwright suite re-run **283/283** (from 282), a11y suite separately 65/65 — 3 unrelated non-dashboard failures seen once under parallel load re-confirmed clean in isolation (the same pre-existing flake pattern, not a regression). | Read `meta/context/part-e-dashboards.md` before starting Part F (bilingual UI) or before assuming any FUTURE "Insurer & Employee Performance"-style backlog item needs a fresh build — "when a Part's own permission-grid inventory names an ALREADY-EXISTING permission pair (not a new dedicated code) for one of its named items, that is itself strong evidence the item is already built by those earlier processes, not a fresh-build signal — check the permission grid's OWN naming pattern across every sibling item before assuming uniform 'each needs new code'", "a cross-cutting requirement spanning N dashboards can be satisfied by an HONEST per-dashboard audit of which of its sub-parts genuinely apply — not by force-fitting every sub-part onto every dashboard as a uniform checkbox", and "a cross-cutting requirement's UNSATISFIED half (bilingual rendering here) should be explicitly, plainly documented as a known gap OWNED BY A DIFFERENT PART rather than silently dropped or silently attempted at a scale far beyond the current task's own scope" are all easy to get wrong. |
| 2026-09-07 | **NEW `meta/context/part-d-completion.md`** — CLOSES Part D §5.1's full 9-system checklist (items #4-9, after Consent/M03, DSR/M04, Retention & Disposal/M06). Six systems, all in `apps/api/src/modules/pdpl/`: Cross-Border Transfer (`cross-border-transfer.approve` DPO-only, creation IS approval, blocks a Jordan "destination" as a 400); Third Parties & Data Sharing/M08 (`DataSharingApproval` maker/checker, the FIRST real caller of backlog #71's previously-uncalled `computeDataShareReadiness()`, wired live — a regulatory channel skips ONLY the readiness check, never the classification/channel check); DPIA Screening/M10 (5-question form, `dpia.review` DPO-only gates the whole surface including submission, any single Yes → 5-business-day DPO review, escalation to Full DPIA is a manual judgment call with no numeric threshold); Notices (creation IS publishing, append-only versioning via a real NEW `@@unique([touchpoint, versionNumber])` migration, mounted via a new `PrivacyNoticeDisplay` widget at the same 5 touchpoints + lead capture Consent/M03 already reached); Records of Processing Activities (plain mutable CRUD + an `EXPORT`-audited register dump, the #65 precedent); a DPO Workspace aggregate screen (a genuinely NEW `dpo-workspace.view` permission, zero cross-module service dependency, reads 6 registers). **Found and fixed a real module-numbering bug before push**: Cross-Border Transfer was initially mislabeled "M05" across 6 files — M05 is already "Data Collection & Access Governance," a different system; both Cross-Border Transfer and Notices actually cite "Part 6.2" with no M01-M12 module name applying at all. **A second real bug found via a failing e2e test**: `GET /privacy-notices/current` returning a bare `null` for "no notice published yet" sent an EMPTY response body (NestJS's actual behavior for `null`/`undefined` controller returns, not the JSON literal `null`) — fixed by wrapping in `{ notice: PrivacyNoticeView | null }`. **Also fixed 3 stale `dormant: true` flags** in `internal-controls.config.ts` (`DisposalBatch`/`DataProcessingAgreement`/`DataSharingApproval` all now have real writers — the first two were stale from EARLIER sessions, not just this one) plus a hardcoded e2e assertion that expected `DisposalBatch` to still show `dormant: true`. **Verification**: +67 api unit (12 new spec files) → api unit **2238** (175 files, from 2171). 6 new e2e spec files, all green (32 tests) — full 57-file api e2e suite green across 8 foreground sub-batches, both chronic flakes (`rbac`, `up-sell`) passing with `--testTimeout=90000`. 6 new Playwright spec files (18 tests) — one real a11y bug caught and fixed (`scrollable-region-focusable` on the RoPA register table, missing `tabIndex`/`role="region"` on the horizontally-scrolling wrapper) — full Playwright suite **264/264** (from 246). `npm run typecheck`/`lint`/`build` (api + web) OK — lint caught the same `react-hooks/set-state-in-effect` false positive on the new `PrivacyNoticeDisplay` widget (same async-IIFE fix as every prior occurrence) plus 2 real unused-import/variable errors after `eslint --fix` removed now-redundant type casts. **Part D §5.1 (all 9 backlog items) is now COMPLETE.** | Read `meta/context/part-d-completion.md` before touching any of these six systems, or before citing an M-number for a NEW PDPL-adjacent backlog item — "check the actual M01-M12 table in `pcms-privacy-modules.md` before assuming the next unused-looking number is free; two backlog items in this same build cited a schema section ('Part 6.2') that doesn't map onto ANY M-number at all, and a plausible-looking guess (M05) turned out to already be a different, real system", "returning a bare `null` from a NestJS controller sends an EMPTY body, not the JSON literal `null` — wrap a genuinely-nullable 'nothing found yet' response in an object instead", "re-verify a `dormant: true` flag in a documentation/reporting registry (`internal-controls.config.ts`'s `MAKER_CHECKER_REGISTRY`) the same session you give that entity its first real writer — two of three flags here were ALREADY stale from earlier sessions that missed this step", and "a wide, action-column-free list table can trigger axe's `scrollable-region-focusable` rule that a narrower or button-containing table won't — add `tabIndex={0}` + `role=\"region\"` + an `aria-label` to the horizontally-scrolling wrapper div proactively on any new wide table" are all easy to get wrong. |
| 2026-09-07 | **UPDATED `meta/context/data-retention-and-disposal.md`** (Part D §5.1, M06) — item #3 of Part D's 9-system checklist, worked one item at a time after Consent/M03 and DSR/M04. All four M06 entities (`RetentionScheduleItem`, `LegalHold`, `DisposalBatch`, `CertificateOfDestruction`) existed in the schema since the initial domain-model migration, but only `RetentionScheduleItem` had a single seeded row and a reader (`AuditLogEntry`, 2026-08-26) — nothing before this build ever wrote a `LegalHold` or `DisposalBatch` row, or let anyone add a SECOND schedule item. Built the first real CRUD across all three: schedule item create/update/confirm (a NEW permission, `retention-schedule.manage`, since no "Legal Counsel" role exists among the 11 seeded `RoleName` values — Compliance/DPO stand in, a documented limitation, not a workaround); Legal Hold place/review/release (a 6-month SLA re-basing via the DSR `applyExtension` start-then-resolve precedent); the full dual-control disposal workflow (nominate→manager-approve→dpo-approve→execute→certificate→close). **Closed a real, previously-flagged schema gap**: `RetentionScheduleItem.recordCategory` gained a genuine `@@unique` constraint (this file had explicitly flagged its absence as an accepted-but-not-ideal gap); the pre-existing seed script's hand-rolled find-then-create/update became a real Prisma `upsert`. **The "dual-control... two different users" checkbox wording only actually enforces HALF of what it names** — `DisposalBatch` has no `managerApprovedByUserId` column, only a timestamp; the DB `CHECK` constraint (pre-existing since migration `20260826091424`) compares only `dpoApprovedByUserId` against `nominatedByUserId`, so `MANAGER_APPROVED` is a self-transition checkpoint, not a second distinct human actor — confirmed by reading the constraint SQL directly rather than assuming the checkbox's prose matched the schema. **The Legal-Hold exclusion check is re-derived from live data at EVERY dual-control step** (nominate, manager-approve, AND dpo-approve), not cached from nomination time — the #16 Broker Recommendation "re-derive the approval gate from live data" precedent, since a hold placed between steps must still block execution. Disposal `execute()` remains a staff ATTESTATION (a status stamp + a `method` field), never a live `DELETE` — this file's own pre-existing "retention informs eligibility; it does not execute disposal" framing, deliberately avoiding a bypass of `AuditLogEntry`'s immutability trigger. **Verification**: +51 api unit (6 new spec files: `retention-schedule.config/service`, `legal-hold.config/service`, `disposal-batch.config/service`) → api unit **2171** (163 files, from 2120). New `test/retention-disposal.e2e-spec.ts` **2/2** — a full lifecycle walk (schedule create/409-duplicate → Legal Hold placed → disposal blocked while held (422) → hold released → nominate→manager-approve→403-self-DPO-approve→distinct-DPO-approve→execute→422-close-without-certificate→certificate→close→schedule confirm→422-edit-after-confirm) plus a second test covering permission-denial and Legal-Hold review re-basing. Full api unit suite 2171/2171 confirmed green; full 51-file api e2e suite green across 8 foreground sub-batches, both chronic flakes (`rbac`, `up-sell`) passing with `--testTimeout=90000`. New Playwright `retention-disposal.spec.ts` 3/3; full Playwright suite 246/246 (from 243). `npm run typecheck`/`lint`/`build` (api + web) OK — lint caught 5 real type-safety errors on first run (an untyped `let row` losing its Prisma type across a try/catch in `retention-schedule.service.ts`; two nested `expect.objectContaining()` calls inside `disposal-batch.service.spec.ts` assertions; one bare `expect.any(Date)` as an object-literal property value in `legal-hold.service.spec.ts`), all fixed following established codebase precedent (an explicit `let row: RetentionScheduleItem`; the DSR `dsr.service.spec.ts` "capture the mock call arg and assert a plain property" shape instead of nesting matchers) rather than suppressed. | Read `meta/context/data-retention-and-disposal.md` before touching M06 again, or any future dual-control workflow whose checkbox prose says "N different users" — "a DB CHECK constraint is the ground truth for which TWO actor columns a dual-control workflow actually compares; a workflow can have a THIRD approval-shaped status checkpoint with no distinct-actor column backing it at all, and the backlog's own prose won't tell you which is which", "a documented schema gap (`recordCategory` with no unique constraint) sitting in a context file for weeks is a real gap to CLOSE the day a real writer needs the invariant, not something to keep working around", "`expect.objectContaining()` nested inside another `expect.objectContaining()`'s property, or a bare `expect.any(X)` used as an object-literal property value rather than a bare argument, both trip `@typescript-eslint/no-unsafe-assignment` — capture the mock call's argument into a locally-typed `const` and assert its fields individually instead, the `dsr.service.spec.ts` precedent", and "a `let x;` declared with no initializer and assigned only inside a try block loses its inferred type across the try/catch boundary under this codebase's strict lint config — give it an explicit type annotation rather than letting TypeScript widen it to `any`" are all easy to get wrong. |
| 2026-09-06 | **RE-VERIFIED `meta/context/data-subject-requests.md`** (Part D §5.1, M04) — item #2 of Part D's 9-system checklist, worked one item at a time after Consent/M03. The checklist's own DSR clause ("logged the same business day regardless of channel, an identity-verification step, SLA computation (15/10 business days + an Access-only extension), a DPO handler assignment, a mandatory 'partially fulfilled' path when a retention flag is still open, never closeable as 'fully fulfilled'") maps onto ALREADY-BUILT M04 functionality clause-by-clause — a "verified, not built" outcome (the #47 KYC/#50 Conflict-of-Interest/#68 Internal IT shape), confirmed by re-running the full suite rather than just re-reading code. **The seed data's own permission descriptions quote this exact backlog wording near-verbatim** (`dsr.log`: "the same business day it is received"; `dsr.close`: "never closeable while a retention flag is open") — strong evidence M04 was built directly against this same source text, not coincidentally compatible. No code changes; api unit 53/53 (`dsr.config.spec.ts`/`dsr.service.spec.ts`), `test/dsr.e2e-spec.ts` 3/3, Playwright `dsr.spec.ts` 3/3, all re-confirmed green with zero regression from the 5+ sessions of unrelated work since M04 originally shipped. | Read `meta/context/data-subject-requests.md` before touching DSR again — when a backlog checklist's wording for an ALREADY-BUILT system is pasted again later (e.g. because the user works through a larger document one item at a time and an earlier item happened to build ahead), re-verify by RUNNING the tests and checking each clause against the actual permission/model text, not by trusting memory that "this was built already" — the verification itself, and its evidence, is the deliverable, matching the #47/#50/#68 discipline. |

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
