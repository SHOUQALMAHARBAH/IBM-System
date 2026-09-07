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
| 2026-09-08 | **Part F item #6 remainder — fuzzy transliteration matching — PARTIALLY built: a curated synonym table only**, by explicit user decision after a research spike's empirical findings were presented via `AskUserQuestion`. **Distance-based fuzzy matching was evaluated and REJECTED, not merely deferred**: a real npm `transliteration` package (Buckwalter-style: `محمد`→`mHmd`) plus `pg_trgm`/`fuzzystrmatch` similarity were tested against real name pairs on `db-test` (both reverted afterward — a research spike, not a build). True-positive pairs like "Yousef"/"يوسف" (Levenshtein 1, trigram 0.29) scored in the SAME range as a genuine false positive — "Khaled" matching a stored "Khalil," a different person (Levenshtein 1, trigram 0.43) — no threshold separates them; this is the same short-alphabet phonetic-key collision Soundex/Metaphone have on short English names, inherent to the algorithm class, not this specific normalization. A hand-rolled Arabic phonetic key would hit the identical ceiling for more build cost, so it was not attempted either. **Built instead**: `apps/api/src/common/name-transliteration.config.ts` — ~50 curated groups of KNOWN equivalent Latin/Arabic spellings for common Jordanian/Arab given names (hamza-dropped Arabic variant included, e.g. `أحمد`/`احمد`; diacritic-stripped before lookup). `expandSearchTerms(term)` tokenizes on whitespace and returns every OTHER spelling in any matched group — never a distance-based guess. Each of the 3 repositories' EXISTING `searchIds()` (item #6's own method) now ORs `[term, ...expandSearchTerms(term)]`, each still its own parameterized `websearch_to_tsquery(...)` call via `Prisma.sql`/`Prisma.join` (no string concatenation, same SQL-injection guarantee as before). **No schema migration, no new column** — this only expands the QUERY side; item #6's `searchVector` generated column is untouched. Zero false-positive risk (exact/stemmed lookup on a literal known term); coverage bounded to the table — same-script typo tolerance and `Insurer` search remain deferred, unchanged from item #6's own scope. **Verification**: +9 new api unit tests (`name-transliteration.config.spec.ts`) → api unit **2335/2335** (from 2326); +6 new api e2e tests (2 per entity × `Customer`/`Prospect`/`Vendor`: a Latin query finding a record whose name field contains ONLY the Arabic spelling, and the reverse — each proves the base bilingual tsvector query alone could NOT have found the match, since the two scripts share no tokens) → full 62-file api e2e suite **311/311** (from 305; 307 green on the first full run, the remaining 4 — `rbac.e2e-spec.ts` ×3, `up-sell.e2e-spec.ts` ×1 — hit the 30s default timeout under full-suite parallel load, re-confirmed clean in isolation with this suite's own established `--testTimeout=180000` precedent; `rbac.e2e-spec.ts` is an already-documented chronic flake, unrelated to this item). `npm run typecheck`/`lint`/`build`/`test` (api) OK. No web files touched, confirmed via `git diff --stat`. | No migration, no seed change. Read `ibms-brain/meta/context/bilingual-ui.md`'s "What item #6 remainder does NOT cover" before assuming item #6 is fully closed — it is NOT: same-script typo tolerance and `Insurer` search remain open, documented future work. A distance-based fuzzy matcher was deliberately REJECTED after the measured false-positive rate above — re-read that finding before re-attempting one; do not self-select resuming those, or starting item #7 (system-generated bilingual documents) or item #8 (four-state screenshot discipline). |
| 2026-09-08 | **Part F item #6 — bilingual full-text search — PARTIALLY built: full-text search only (Arabic + English), on `Customer`/`Prospect`/`Vendor`**, by explicit user scoping decision after presenting the bullet's 2 sub-problems. **Fuzzy transliteration matching** (typing "Ahmad" finding "أحمد" or vice versa) **and same-script typo tolerance** (`pg_trgm`) **both explicitly deferred** — no Postgres extension/library does transliteration well, nothing to build on. **Entity scope**: `Customer`/`Prospect`/`Vendor` — the only 3 with both a bilingual name field AND an existing list endpoint + web page; `Insurer` excluded after a follow-up finding — no dedicated module (`insurer.controller.ts`/`.service.ts` don't exist) and no `/insurers` web list page anywhere, the same class of gap item #4 hit with `InsuredPerson`. **Mechanism, empirically verified against the actual running Postgres (18-alpine), not assumed**: a real built-in `'arabic'` text-search config ships alongside `'english'` (genuine stemming confirmed: `to_tsvector('arabic', 'شركة الأفق للتأمين')` → definite articles/prefixes stripped); bilingual documents concatenate both configs' tsvectors (`to_tsvector('arabic', x) || to_tsvector('english', x)`, each config tokenizes the OTHER script's text without erroring); query side uses `websearch_to_tsquery` (never raw `to_tsquery`) OR'd across both configs — verified empty/junk input degrades safely, and an injection-shaped string is parsed entirely within tsquery's own mini-language when passed through Prisma's PARAMETERIZED `$queryRaw` (never `$queryRawUnsafe`) — the FIRST real use of `$queryRaw` with user input anywhere in this codebase. **Built**: one `GENERATED ALWAYS ... STORED` tsvector column + GIN index per model (`Customer.searchVector` from `legalName` ONLY — encrypted contact fields never indexed in plaintext; `Prospect.searchVector` from `companyName`+`contactPerson`; `Vendor.searchVector` from `name`); each repository gained a `searchIds(term)` method resolving matching ids, fed into the EXISTING `findMany()` via `id: { in: ids }` — no filter logic duplicated in raw SQL. Each list DTO gained a `search` field (`emptyStringToUndefined` is load-bearing: an empty search box must show everything, not match nothing — verified empirically). Web: none of the 3 list pages had ANY filter UI before this item — each gained a submit-triggered search input (`dir="auto"`, no debounce utility exists in this app). **Verification**: no new unit tests (needs real Postgres, a mock would prove nothing) — api unit stays 2326/2326; +12 new api e2e tests (4 per entity, each proving REAL stemming via a term that is never a literal substring of the stored value — English "trade" finds "Trading", Arabic singular finds a stored plural) → full 62-file api e2e suite **305/305** (from 293); +3 new Playwright wiring tests → full web suite **297/297** (from 294, 231 non-`@a11y` + 66 `@a11y`). `npm run typecheck`/`lint`/`build`/`test` (api + web) OK. | No seed change. Read `ibms-brain/meta/context/bilingual-ui.md`'s "What item #6 covers/does NOT cover" before assuming item #6 is fully closed — it is NOT: fuzzy transliteration, same-script typo tolerance, and `Insurer` search all remain open, documented future work; do not self-select resuming them or starting item #7. |
| 2026-09-07 | **CLOSES Part F item #4** ("Arabic-first input") — resumed its two deferred sub-problems by explicit user go-ahead. **Arabic keyboards confirmed CLEAR, no code change needed**: grepped all 67 `@Matches` validators across every api DTO — none restrict a name field to Latin-only characters; grepped every web `pattern=` attribute — only 3 exist, all on 6-digit MFA codes; `@Length`/`@MinLength` count Arabic script correctly (no surrogate-pair miscount). **National-ID-convention name-splitting built**: a real schema migration (`givenName`/`fatherName`/`grandfatherName`/`familyName`, all nullable) on the 3 models with both real CRUD AND an existing `nationalIdEnc` — `Customer` (INDIVIDUAL only), `Employee`, `UltimateBeneficialOwner` — scoped via `AskUserQuestion` before implementing. `InsuredPerson` (the 4th candidate) deliberately excluded — zero CRUD anywhere in this app yet. The existing flat field (`legalName`/`fullName`) stays computed/denormalized, auto-joined from the 4 parts by one new shared `apps/api/src/common/person-name.util.ts` helper — every existing consumer (Arabic sorting, `<bdi>` display, search, audit, exports) keeps working unchanged. `givenName`/`familyName` required whenever the split applies; `fatherName`/`grandfatherName` optional (a judgment call, flagged rather than assumed). No backfill — historical rows keep only their flat name. Web forms (`CustomerOnboardingWizard.tsx`'s profile step + UBO mini-form, `employees/page.tsx`'s create form) gained the 4-input treatment; 3 genuine pre-existing item #3 (`<bdi>`) gaps found and fixed along the way (`employees/page.tsx`'s list cell, `employees/[id]/page.tsx`'s heading, `customers/[id]/page.tsx`'s UBO row). **A real migration-tooling blocker**: Docker Desktop's engine was unresponsive for a large stretch of this session — root-caused via its own log (a background update in progress) and confirmed via `Get-Process` that the backend process hadn't actually restarted despite an app relaunch, until a full quit from the tray. Once genuinely restarted, the migration applied cleanly via this repo's established hand-authored-migration-plus-`migrate resolve` workaround (a pre-existing, unrelated checksum-drift issue on 3 older migrations blocks plain `migrate dev`). **Verification**: +5 unit tests (`person-name.util.spec.ts`) → api unit **2326/2326** (from 2321); full 62-file api e2e suite **293/293** (1 transient MFA/TOTP-timing flake in a shared setup helper, unrelated to this item, re-confirmed clean in isolation); full web suite **228/228** non-`@a11y` + **66/66** `@a11y` green. `npm run typecheck`/`lint`/`build`/`test` (api + web) OK. | No seed change. Read `ibms-brain/meta/context/bilingual-ui.md`'s "What item #4 covers/does NOT cover" — `InsuredPerson` name-splitting remains open, deferred until that model has real CRUD; this is a pre-existing gap, not new. Item #5 remains PARTIALLY built (Hijri calendar/multi-currency deferred) — do not self-select resuming it or starting item #6. |
| 2026-09-07 | **Part F item #5 — locale-aware number/date formatting — PARTIALLY built: number/date formatting only (sub-problem #1 of 3)**, by an explicit user scoping decision made mid-session (presented with the bullet's 3 sub-problems — number/date formatting, Hijri calendar ["optional" per the bullet], multi-currency for reinsurance — the user chose to fix #1 now, leaving the other two deferred future work). **Fixed**: one new shared `apps/web/lib/i18n/format.ts` (`formatMoney`/`formatDate`/`formatDateTime`) replacing ~9 duplicated local `money()`/`fmtMoney()`/`fmtDateTime()` implementations across `components/**` and `app/(app)/**/page.tsx` — every call site threads the live `useLanguage()` value through (directly via the hook, or as an explicit `language` parameter into a plain helper that can't call a hook itself, e.g. `coverageLabel(c, language)`). **Locale tags were empirically verified against Node's own ICU before being chosen, not assumed**: a region-qualified Arabic tag (`'ar-JO'`) silently switches to Eastern Arabic-Indic numerals for money amounts (`١٬٢٣٤٫٥٠٠` instead of `1,234.500`) — an unwanted surprise nothing in this app ever asked for — so bare `'ar'` (Western numerals, genuine Arabic date ORDER) was used instead, paired with `'en-GB'` (`DD/MM/YYYY`, matching the existing `audit-anomaly-detection.service.ts` backend precedent) rather than bare `'en'` (US-style `MM/DD/YYYY`); the user confirmed this exact tag pair directly via `AskUserQuestion` after seeing the empirical divergence. Every duplicate formatter's exact null/non-finite fallback behavior was preserved byte-for-byte — a behavior-preserving consolidation, not a new contract. A whole-codebase grep after the sweep confirmed zero remaining `toLocaleString`/`toLocaleDateString` calls and zero remaining local `money`/`fmtMoney`/`fmtDateTime` definitions anywhere in `apps/web` — the same exhaustive-sweep bar items #2/#3 held themselves to, not a sampled subset. **Verification**: +7 web unit tests (`format.test.ts`, new) → web unit **16/16** (from 9); +1 new Playwright spec (`locale-formatting.spec.ts`) driving the real, live language switcher against a real page — asserts a rendered date genuinely changes format on switch while the SAME money cell's digits stay byte-identical, the end-to-end proof the locale-tag choice holds outside the unit test's isolated calls — full web suite **294/294** (from 287, 228 non-`@a11y` + 66 `@a11y`, no flakes). `npm run typecheck`/`lint`/`build`/`test` (web) OK. No backend files touched — pure frontend change, confirmed via `git diff --stat` (25 files, all `apps/web`). | No migration, no seed change. Read `meta/context/bilingual-ui.md`'s "What item #5 covers/does NOT cover" before assuming item #5 is fully closed — it is NOT: Hijri calendar and multi-currency (reinsurance) remain open, documented future work; do not self-select resuming them or starting item #6. |
| 2026-09-07 | **Part F item #4 — Arabic-first input — PARTIALLY built: correct Arabic sorting only**, by an explicit user scoping decision made mid-session. The backlog bullet ("Arabic keyboards, national-ID-convention name fields, correct Arabic sorting") bundles three sub-problems of very different size — presented with that before implementing, the user chose to fix sorting only, explicitly deferring keyboards and name-splitting as documented future work (name-splitting in particular reads as a real schema migration touching every name field/form/consumer, far bigger than the other two). **Fixed**: every `localeCompare(x, 'en')` sorting a genuinely bilingual name/label field switched to `'ar'` — `finance.config.ts` (customer legal name, insurer name ×2, insurance-line/segment key), `loss-ratio.config.ts` (customer/insurer/insurance-line label), `profitability-analysis.config.ts` (insurance-line/segment key); two DB-level sorts using plain Postgres collation (`commission.repository.ts`'s `listInsurers()`, `rfq.repository.ts`'s `findSelectableInsurers()`, both on `Insurer.name`) converted from Prisma `orderBy` to a fetch-then-JS-sort with the same `'ar'` comparator. `'ar'` is HARDCODED, not the caller's own `languagePreference` — a second explicit scoping decision, also asked and confirmed directly rather than assumed. **Deliberately NOT touched**: `sla-dashboard.config.ts`'s `label` (a fixed, always-English SLA-workflow name) and `role.repository.ts`'s `Role.name` (a fixed `RoleName` enum) — both confirmed by reading the actual field source before deciding, not assumed from the field name; changing either would have been wrong, not a fix. **A genuine, empirically-verified test proves the mechanism**: `"إبراهيم للتأمين"` sorts before `"أحمد للتجارة"` under `'ar'` collation but after it under `'en'` — verified directly against Node's ICU before writing the assertion, not assumed, then locked in as a regression test. **Verification**: +1 unit test (`finance.config.spec.ts`) → api unit **2321/2321** (from 2320); targeted + adjacent e2e sweep across every touched config's own test file (`commission`, `claim`, `financial-dashboard`, `sla-dashboard`, `claims-dashboard`, `profitability-analysis`) — 25/25 green, none asserted an exact ordering the locale switch could have broken (confirmed by reading each assertion, not just trusting the exit code). `npm run typecheck`/`lint`/`test` (api) OK. No web files touched — pure backend change, confirmed via `git diff --stat`. | No migration, no seed change. Read `meta/context/bilingual-ui.md`'s "What item #4 covers/does NOT cover" before assuming item #4 is fully closed — it is NOT: Arabic keyboards and national-ID-convention name-splitting remain open, undocumented-in-detail future work; do not self-select resuming them or starting item #5. |

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
