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
| 2026-09-07 | **CLOSES Part F item #3** ("Bidirectional (bidi) text handling for mixed-content fields"), after item #1 (language switch) and item #2 (RTL layout). Distinct from item #2 (whole-screen layout mirroring) and from `PrivacyNoticeDisplay`'s `textAr`/`textEn` (two whole separate fields, not one field mixing scripts) — item #3 is about a SINGLE field/string that may itself mix Arabic and Latin script (a legal name, an address, an insurance-line label sitting next to a Latin policy number). No concrete field list existed anywhere in the brain beyond `verification-contract.md`'s 4 example categories — a codebase survey (schema + render-site grep) identified the real at-risk fields. Fixed via two native, zero-JS-logic mechanisms across ~30 files: every dynamically-rendered value from an at-risk field wrapped in a native `<bdi>` element (isolates bidi runs, auto-detects direction — the HTML spec's own mechanism for "content of unknown directionality"), with two independently-directioned concatenated values (`PolicySection.tsx`'s `insuranceLine · policyNumber`, `ClaimSection.tsx`'s claim-number/`causeOfLoss — lossLocation`) each wrapped SEPARATELY so the separator glyph stays stable; `dir="auto"` added to every capture `<input>`/`<textarea>` for a field typeable in either script. Fixed once at the shared `ProfileField` primitive (`customers/[id]/page.tsx`, `prospects/[id]/page.tsx`) rather than per-call-site. Confirmed via grep that `WatchlistEntry`/`ScreeningResult` fields (also schema-level mixed-content risks) are never rendered on the frontend at all — genuinely nothing to fix there. **A build-cache gotcha caught while verifying**: the new spec's first run found zero `<bdi>` elements despite correct source edits — Playwright's `webServer` reuses an existing `next start` process serving the LAST `npm run build` output, not live source; the exact same class of gotcha item #2's own Claims-consent-widget fix hit once already. **Verification**: +1 new Playwright spec (`bidi-text.spec.ts`, 3 tests) → full web suite **227/227** non-`@a11y` + **66/66** `@a11y` green. `npm run typecheck`/`lint`/`build`/`test` (web) OK; no backend gate applies (web-only change, confirmed via `git diff --stat`). | No migration, no seed change. Read `meta/context/bilingual-ui.md`'s "What item #3 covers/does NOT cover" before starting item #4 (Arabic-first input/keyboards/sorting) — item #3 is mixed-SCRIPT isolation within a field, not translation of the ~80 still-English screens, and not Arabic keyboard/collation support. |
| 2026-09-07 | **CLOSES Part F item #2** ("full RTL layout for Arabic and LTR for English — navigation, forms, tables, charts genuinely mirrored, not just mirrored text"), after item #1. **Found substantial item #2 work already sitting uncommitted in the working tree at session start** — a prior session's unfinished, unverified, undocumented conversion of ~60 files' inline styles from physical CSS properties (`textAlign:'left'/'right'`, `marginLeft/Right`, `borderLeft/Right`) to their logical equivalents (`start`/`end`, `marginInlineStart/End`, `borderInlineStart/End`), relying on `dir="rtl"` cascading from `<html>` (item #1's own mechanism) plus plain `flexDirection: row` and native `<table>` column order to mirror for free — plus a new, untracked `apps/web/e2e/rtl-layout.spec.ts` asserting REAL bounding-box mirroring (a logical CSS value reads back unchanged via `getComputedStyle` in both directions, so only a bounding-box check actually proves mirroring happened). Reviewed the entire diff file-by-file before trusting it — no mistakes found, every change is the identical mechanical swap — and confirmed via a whole-codebase grep that zero physical-direction CSS properties remain anywhere in `apps/web`. **Charts: confirmed vacuously N/A, not silently skipped** — this app has no chart/graph/SVG/canvas visualization anywhere yet (grepped `recharts`/`chart.js`/`d3`/`<canvas>`/`<svg>` — only Next.js's own public boilerplate assets match); flagged as a re-check trigger for whenever this app's first real chart lands, since SVG/canvas do not inherit CSS logical-property mirroring the way flex/table layout does. **Forms and native `<table>` mirroring both confirmed already-structural, not new work** — the shared form-row/table primitives (`lead.styles.ts`, `auth-form.styles.ts`) were already direction-agnostic flex layouts, and `<table>` column mirroring under `dir="rtl"` is a plain browser default, spot-verified on one representative page. **Verification**: +1 new Playwright spec (`rtl-layout.spec.ts`, 2 tests) — full web suite **224/224** non-`@a11y` + **66/66** `@a11y` green (one `rfq.spec.ts` test hit a transient `write UNKNOWN` process-contention error under full-suite parallel load, re-confirmed clean 27/27 in isolation — not a regression). `npm run typecheck`/`lint`/`build`/`test` (web) OK; api suite re-run as a sanity baseline (2320/2320, unaffected — this item touches only `apps/web`). | Read `meta/context/bilingual-ui.md`'s "What item #2 covers/does NOT cover" before starting item #3 or assuming the other ~80 still-English screens are translated (they are not — item #2 is layout mirroring only, never text translation) — and don't assume a context file's "not started" claim reflects the current working tree: this item's own starting point was real, correct, uncommitted work sitting stale against a doc that still said "not started, wait for go-ahead." |
| 2026-09-07 | **Full-codebase code-review audit** (10 parallel `@code-reviewer` batches covering all 35 `apps/api/src/modules/*` plus the whole `apps/web` frontend, on a "review all the code" request) found and fixed 2 BLOCKER + 8 MAJOR findings; ~20 MINOR/NIT findings logged to a new root `IMPROVEMENTS.md` rather than fixed inline. **BLOCKERs**: (1) `WorkflowTransitionService.transition()` — the ONE shared status-transition engine 30+ services depend on — committed its status write and its TRANSITION audit row as two separate round-trips, not one transaction; a transient failure on the second could leave a status change persisted with no audit row and no SLA timer ever fired, exactly the "worse than an obviously broken record" failure `workflow-state-transitions.md`'s own rationale warns about — fixed by wrapping both in one `$transaction`, with `AuditService` gaining a `recordInTransaction()`/`runAnomalyDetection()` pair so anomaly detection (its own separate best-effort writes) still runs after commit, never inside the transaction. (2) The JWT access-token signing secret silently fell back to a hardcoded, publicly-visible dev string with no production fail-fast, unlike every other secret in this codebase — fixed with a shared `jwtSecret()` helper (`common/crypto.util.ts`) and a new `assertJwtSecretConfigured()` boot-time check in `main.ts`, mirroring `assertDatabaseTls()`'s exact shape. **MAJORs**: the same read-then-unconditionally-write race gap (`race-safe-invariants.md`) recurred in three unrelated places — Access Recertification's `decide()`, password-reset's `resetPassword()`, and Insurance Program's `reassemble()` (previously accepted as "narrows, doesn't fully close" on a since-invalidated "single-actor pool" premise — Placement is actually a book-wide role grant with no per-officer queue) — all three now use a status-conditional `updateMany`/transactional row-lock instead, each with a new concurrent-race test confirmed live against `db-test`. Compliance Dashboard and KPI Dashboard both omitted `isSensitiveDataAccess: true` on their audit rows despite aggregating KYC/Complaint/DSR/AML/Claim data, unlike every sibling Part E dashboard (`sensitive-data-handling.md`) — a compliance-dashboard unit test was even asserting the wrong value, now corrected. `PaymentChannel`'s `label`/`bankName` free-text fields were missing the `NO_FULL_ACCOUNT_NUMBER` guard every comparable free-text field elsewhere in this codebase already carries, sitting right next to the one masked bank-account fragment this app permits. A genuinely stale premise in `meta/context/consent-management.md` claiming "no web UI exists for an individual claim record" (used to justify skipping the Claims consent-capture touchpoint) was false — `ClaimSection.tsx` is exactly such a UI, already mounted with the exact `customerId` a `ConsentCaptureWidget` needs — now wired in (6 of 7 touchpoints wired; the 7th, Group Medical/Life & Motor Fleet, is genuinely still blocked on `InsuredPerson` having zero CRUD anywhere). **Verification**: api unit **2320/2320** (from 2316, +4 new tests); targeted e2e (`auth`, `rbac` with its established `--testTimeout=180000`, `insurance-program`, `invoice`) all green, each proving its own new concurrent-race test passes; web typecheck/lint/build/unit/full Playwright suite (224/224 + 66/66 `@a11y`) green after the consent-widget change. `npm run typecheck`/`lint` (api + web) OK throughout. | Read the new root `IMPROVEMENTS.md` for the ~20 logged MINOR/NIT items (stale doc comments citing modules as "not built yet" that have since shipped — the same pattern this brain has caught 3 times now; missing P2002-to-409 mapping on 2 creates; a few missing try/catch wraps around best-effort SLA-timer starts) before assuming this audit's scope was exhaustive — the web-frontend batch explicitly sampled ~45 of ~90 pages rather than reading every one, logged in that file's own coverage note. |
| 2026-09-07 | **NEW `meta/context/bilingual-ui.md` + `meta/designs/2026-09-bilingual-ui-i18n-architecture.md`** — opens Part F (backlog Part 11, "Bilingual UI Requirements"), item #1 of 8: "instant language switch without losing session context + a persistent per-user language preference." Worked one item at a time, the Part D/E pacing convention. `User.languagePreference` (`LanguagePreference` enum, `@default(AR)`) pre-existed in the schema (readable via `GET /auth/me`) but was write-once-at-signup only — this item adds `PATCH /auth/me/language` (`UserRepository.updateLanguagePreference()`, the `setMfaEnabled` self-service shape, no permission beyond being signed in). **Design decision: a hand-rolled `LanguageProvider` React context, not a locale-routing i18n library (`next-intl` etc.)** — see the new design doc's full reasoning: "instant... without losing session context" reads as a same-URL, client-only toggle, which a routing library's default App Router integration (URL-prefixed locales) does not give for free; migrating ~80 existing routes under a `[locale]` segment would also be a large, invasive restructure disproportionate to a bare switch. `LanguageProvider` (wraps `AuthProvider`'s children) syncs from the account ONCE per session load, then treats local state as authoritative (a manual switch is never silently overwritten by a stale re-render); every switch updates React state + `document.documentElement.lang/dir` synchronously (genuinely instant — no navigation, no URL change) and fires `PATCH /auth/me/language` in the background, best-effort (the SlaTimer-start precedent). A small, REAL (not stubbed) translation dictionary (`translations.ts`) backs a `t()` hook — deliberately scoped ONLY to the switcher control + `AppNav`'s account footer, proving the mechanism round-trips end to end; translating the other ~80 screens is items #2-5's own separate, much larger scope. Login/signup (outside the authenticated `AppNav` shell) get no switcher yet — a documented gap, not silently dropped. **A real regression caught while verifying**: the new Playwright spec's first draft used `page.route("**/leads**", ...)` with no host, which ALSO matched the page's OWN navigation request (`page.goto("/leads")`), rendering literal `[]` text instead of the real shell — fixed by scoping to the api origin (`http://localhost:4000/leads**`), the convention every other spec in this codebase already follows. **Verification**: +1 api e2e test in `auth.e2e-spec.ts` (12/12, was 11); +3 web unit tests (`translations.test.ts`, new); +3 new Playwright tests (`language-switcher.spec.ts`, new) — full suite **287/287** (was 283); 4 unrelated specs flaked once under a concurrent-process memory-pressure episode (running an unrelated api unit suite alongside the Playwright run), re-confirmed clean in isolation. Full api unit suite 2316/2316 confirmed green; full 62-file api e2e suite green across all 8 foreground batches, the chronic `rbac.e2e-spec.ts` flake needing its established `--testTimeout=180000` re-run (individual tests now 65-75s against the very large cumulative `db-test`). `npm run typecheck`/`lint`/`build` (api + web) OK. | Read `meta/context/bilingual-ui.md` before starting ANY other Part F item (#2 full RTL layout, #3 bidi text, #4 Arabic-first input, #5 locale formatting, #6 bilingual search, #7 document generation, #8 the four-state screenshot discipline) or before assuming item #1's infrastructure covers more than it does — "only the language switcher control and the `AppNav` account footer are actually bilingual today; the other ~80 screens remain English-only text, and `dir=\"rtl\"` alone does not achieve genuinely-mirrored RTL layout for a component that was never built RTL-aware", "a Playwright `page.route()` glob with no host prefix can match the page's OWN navigation request, not just XHR/fetch calls to a separate api origin — always scope mocks to the api's own `http://localhost:4000/...` prefix, the convention this whole codebase already follows", and "a design decision this foundational (which i18n architecture underpins every future Part F item) earns its own `meta/designs/` entry with a real alternatives-considered table, not just a context-file mention" are all easy to get wrong.
| 2026-09-07 | **UPDATED `meta/context/data-subject-requests.md` + `data-retention-and-disposal.md`** — closed a real integration gap found during a meticulousness re-audit of Part D against the literal backlog text (a `/52 64` request to verify readiness, not build something new). DSR (M04) blocked a DELETION request from closing "fully fulfilled" while a retention flag was open using ONLY a staff attestation (`confirmNoOpenRetentionHold`) — honest when M04 shipped (Retention & Disposal / M06 didn't exist yet, so `LegalHold` had no structured subject reference to check), but the reasoning went STALE once M06 landed in a later session with a real, queryable register that nobody wired up — the DTO's own header comment kept saying "M06 is not built yet" long after it was, the same "stale flag surviving a later session's real build" pattern the Part D completion session already caught once for `internal-controls.config.ts`'s `dormant: true` flags. **Fix**: `LegalHold` widened with optional `customerId`/`insuredPersonId` (migration `20260916120000`, at most one of the two — `hasAtMostOneSubjectReference`, the ConsentRecord/DSR "at most" not "exactly" shape) since `LegalHold.scope` was free text with no structured reference to query against. `LegalHoldRepository.hasActiveHoldForSubject()` is the new live check; `DsrService.fulfil()` (same-module injection, both in `PdplModule` already) now calls it FIRST for a DELETION request and 422s outright if an active hold names the subject — the attestation can no longer override a REAL hold. The attestation still gates the one case the live check cannot cover (a record category whose retention period hasn't elapsed has no per-subject hold row to find) — a deliberate, honest, narrower scope limit, not the gap re-opened. `CreateLegalHoldDto`/`ListLegalHoldsQueryDto` gained matching optional fields (existence-checked, at-most-one validated); the `retention-disposal` web page gained Customer ID / Insured person ID inputs and a "Subject" column. **Verification**: +12 api unit (2 new DsrService.fulfil tests, 4 hasAtMostOneSubjectReference tests, 2 deriveLegalHoldView/audit-snapshot tests, 4 LegalHoldService.create/list tests) → api unit **2316** (185 files, from 2304). New DSR e2e test (full walk: place a hold naming the customer → fulfil blocked 422 even with the attestation ticked → partially-fulfil still works → release the hold → a FRESH DELETION request for the same customer fulfils normally, proving the check is live, not cached); new retention-disposal e2e test (at-most-one 422, unknown-customerId 404, list-by-customerId). Full api unit suite 2316/2316 confirmed green; full 62-file api e2e suite green across 8 foreground sub-batches. New Playwright coverage in `retention-disposal.spec.ts` (a pre-existing test needed a `.first()` fix — the new second Legal Hold fixture row made its own `getByRole('button', {name: 'Release'})` locator ambiguous, the same shared-fixture-affects-other-tests lesson caught before); full Playwright suite 4/4 on the affected spec, no other regressions. `npm run typecheck`/`lint`/`build` (api + web) OK. | Read `meta/context/data-subject-requests.md`'s "not obvious" DELETION bullet and `data-retention-and-disposal.md`'s matching `LegalHold` entry before touching either M04 or M06 again — "a code comment justifying a design choice by citing another module as 'not built yet' is a claim with an expiry date — the day that OTHER module ships in a LATER session, the justification is stale even though the code itself still compiles and passes every existing test; grep for cross-module 'not built yet' / 'doesn't exist yet' comments the same session you give THAT OTHER module its first real writer, the same discipline already applied once to dormant-flag registries", "a hold/exclusion/flag field that is free text (`LegalHold.scope`) cannot be live-queried no matter how well-intentioned the free text is — closing an integration gap like this one usually means a real schema widening (a structured FK), not just new application logic", and "adding a second row to a SHARED Playwright mock fixture can silently turn an existing test's strict-mode locator (`getByRole` with no `.first()`/`.nth()`) ambiguous — re-run every test that consumes a fixture you widen, not just the new test you wrote for it" are all easy to get wrong.

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
