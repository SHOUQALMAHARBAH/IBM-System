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
| 2026-09-22 | **Two rules into `definition-of-done`, both from things that went wrong rather than from principle.** **DOC CURRENCY IS A GATE.** Measured: across a 30-commit branch, `CLAUDE.md` and `README.md` both still said "Insurer CRUD remains specification-only and is deliberately deferred" after insurer CRUD had shipped — and the workspace-updates HOOK caught it on the branch's last commit, not a person. A hook that fires at the end lets thirty commits accumulate a false claim and fires on whoever happens to stage the last developer-facing file, not on whoever made the statement false. So the check joins the gates: grep the feature's own NOUNS (a claim rots on the words it names, not the files it touches), and treat "X is not built" / "remains specification-only" / "is deferred" as the shapes that rot, because they are true when written and nobody revisits them. **Correct rather than delete** — a deferral usually had a reason that survives it. **REWRITING PUBLISHED HISTORY: THE TREE IS THE TEST.** `--force` is acceptable only when the TREE IS UNCHANGED (verify with `git diff --stat HEAD origin/<branch>` printing nothing), always `--force-with-lease`, never bare. If the tree changes, add a commit — because **CI validated a tree**, and rewriting it means the green you are standing on no longer describes what is there. One test, no judgement call. Disclose either way. | **Before pushing, ask what this change made FALSE in `CLAUDE.md` / `README.md`** — not what it touched. Those two files are what a newcomer and an agent read first, so a false claim there is believed before anyone opens the code. And a dated `## What's New` row belongs in the commit that earns it, not batched at the end of a branch where it becomes one row summarising work nobody can separate. |
| 2026-09-21 | **Verification now says WHERE each gate runs: targeted locally, FULL in CI, and CI is what gates the branch.** `meta/context/verification-contract.md` gains that rule plus three new gate rows for `ibms-app` (migration checksums, schema divergence, Playwright browser revisions). Adopted from measurement, not preference: the full 91-file api e2e suite is **14.1 min in CI** against **75 min** on the dev laptop when that laptop is quiet and freshly cleaned, and 5+ hours under ordinary desktop load — and the repo is public, so runners cost nothing. The deciding argument is not speed but that **CI's resources cannot vary**: a red local run carries a code-or-machine ambiguity that was in fact resolved WRONGLY once, where a full-disk explanation fit the evidence and was false. **Two traps recorded in the rule itself.** (1) A rule naming CI is VACUOUS until CI has seen the branch — this one already said "CI gates the branch" while a 24-commit feature sat unpushed on a single laptop, so the laptop was being used INSTEAD of CI rather than in addition to it, and the whole feature existed in exactly one place. (2) `ci.yml` triggers on `push: branches: [main]` and `pull_request` only, so pushing a feature branch runs NOTHING — the PR is the event that makes the rule real, which is what `AGENTS.md` § Session completion always said. **Blast radius checked before adopting**, because "full in CI" is a WEAKER gate than a local full run wherever CI runs only a subset: `ibms-app` is the sole repo vendoring this brain (no other repository on the account has a `.gitmodules` at all), and its CI runs the suite in one unfiltered `turbo run test:e2e` command. | **Run gates locally SCOPED to the change's blast radius; do not spend hours reproducing CI.** "Targeted" means scoped by blast radius, never by convenience — a response-shape or shared-fixture change is still the full suite locally. **Open the PR**: a pushed branch runs no CI, so an unopened PR means the branch is unverified no matter how green the laptop was. **A future repo syncing this brain must NOT adopt the CI row until its own CI is confirmed to run the FULL suite.** |
| 2026-09-08 | **Part F item #8 — four-state (loading/empty/error/populated) screenshot evidence — PART F IS NOW COMPLETE.** Framed in the backlog as "a verification DISCIPLINE overlay on 1-7, not a separate build item." Two scoping decisions confirmed via `AskUserQuestion` after a research pass: (1) scope is the ~8 screens items #1-7 actually built/touched, not the whole app's 84 `page.tsx` files — only 13 commits were ever tagged "Part F item #N," touching mostly document-generation infra and global CSS/layout, not a broad per-page sweep; (2) capture mechanism is plain `page.screenshot()` PNG evidence, not Playwright's `toHaveScreenshot()` visual regression — matches `verification-contract.md`'s own framing ("a state with no screenshot is a state that is not implemented" — proof of existence, not a pixel-diff test) and avoids brittle cross-platform font-rendering failures on a bilingual RTL/LTR app. Research confirmed no screenshot infrastructure existed at all (no `toHaveScreenshot`, no screenshots dir, no `screenshot:` config) but the 4 states themselves mostly already exist in real code (checked `customers`/`leads` pages directly — genuine loading/empty/error/populated branches, an established house convention). New `apps/web/e2e/four-state-screenshots.spec.ts` — 10 tests across 8 screens (`/customers`, `/customers/[id]`, `/watchlist-sync`, `/complaints`, `/rfqs/[id]`, `/opportunities/[id]`, `/prospects`, `/vendors`), capturing whichever states are genuinely applicable per screen (skipping e.g. "empty" on a detail page, or "loading" where no visible indicator exists), rendered in Arabic where relevant to demonstrate RTL/bidi in the same screenshot. `/opportunities/[id]`'s populated capture shows all 4 of item #7's document-download buttons on that page at once (recommendation, policy schedule, certificate, invoice); spot-checked visually, not just asserted present. **Found and fixed a real bug in the new test's own fixtures (not application code)**: `GET /quotations?rfqId=` returns `QuotationChain[]` (grouped per insurer, `{current, versions, history}`), not a flat `QuotationVersion[]` — the wrong shape crashed `QuotationsSection.tsx` (`chain.current` undefined), surfacing as Chrome's own "This page couldn't load" rather than a React error boundary; found via `page.on('pageerror', ...)` in a throwaway diagnostic spec, not guessed. Screenshots save to `test-results/four-state-screenshots/<screen>/<state>.png`, already covered by the pre-existing `test-results/` gitignore entry — not committed, the same treatment Playwright's own trace files get. **Verification**: +10 new Playwright tests → full web suite **309/309 green** (a genuinely fresh full run, not assumed unaffected). `npm run typecheck`/`lint`/`build` (web) clean. No backend files touched, confirmed via `git diff --stat` (one new file). | No migration, no seed change. **Part F (backlog Part 11) is now fully complete** — all 8 named items either shipped or explicitly, deliberately scoped down by the user, every deferred edge documented in `ibms-brain/meta/context/bilingual-ui.md`. Do not self-select resuming item #5 (Hijri/multi-currency), item #6 (same-script typo tolerance/`Insurer` search), item #7 (real `Document` persistence), or item #8 (the other ~75 app pages, or visual-regression testing) without an explicit fresh user go-ahead — none of it is "finishing Part F." |
| 2026-09-08 | **Part F item #7 — invoice + certificate of insurance, the 5th and 6th (final) of 6 document types — ITEM #7 IS NOW COMPLETE.** Invoice (`GET /invoices/:id/document`, `client-accounting.read`): the first item #7 document with a FLAT, book-wide visibility permission rather than a scoped one — confirmed by re-reading `InvoiceService`'s own header comment ("there is no per-owner visibility filter") before building, so `InvoiceDocumentService` reads `InvoiceRepository`/`CustomerRepository`/`PolicyRepository` directly, no `getByIdWithCustomer()`-style helper needed. Content, confirmed via `AskUserQuestion`: deliberately EXCLUDES `commissionDeducted`/`netRemittance`/the insurer `Remittance` leg (internal broker-insurer economics) even though `FinanceSection.tsx`'s own "Billing" block shows them on screen — the recommendation-report document's "internal governance metadata stays internal" precedent, applied again. Certificate of Insurance (`GET /policies/:id/certificate` — a SEPARATE endpoint from the pre-existing `GET /policies/:id/document`, which stays the schedule-summary document): reuses the exact same `PolicyService.getByIdWithCustomer()` visibility read and `schedules.length === 0 → 422` gate the schedule-summary slice already built; content, also `AskUserQuestion`-confirmed, is a genuinely SHORTER, different Certificate-of-Insurance convention (insured/policy number/insurer/line/period/a one-line sum-insured summary) — deliberately not the schedule summary's content under a new heading. A shared `coverageFigureEntries()` helper was promoted (byte-identical relocation) from a private function in `policy-schedule-summary-document.service.ts` into `policy.config.ts`, since the certificate needed the identical JSON-entries-for-display read as a second consumer. **A `@code-reviewer` pass found 1 real BLOCKER, fixed before this was considered done**: the certificate made an UNCONDITIONAL present-tense "currently in force" attestation with no check on `policy.status` anywhere — a CANCELLED or EXPIRED policy would still get a certificate falsely claiming active coverage, and this document type exists specifically to be handed to a third party (landlord/regulator/lender) to rely on as proof of that; fixed by refusing with 422 (the same shape the existing data-availability gate already uses) for `CANCELLED`/`EXPIRED`, verified with a new e2e assertion. A MINOR was also fixed: the invoice document was rendering the raw internal `Invoice.status` collection-cycle enum (`RECONCILED`/`REMITTED`/etc. — the broker's own settlement progress with the insurer) verbatim, in tension with that same document's own stated commission-exclusion decision; replaced with a client-facing "Outstanding"/"Paid" label derived from whether the client's own collection receipt exists. **Verification**: +23 new api unit tests (`invoice-document.template.spec.ts` +12 incl. 1 added during the review fix, `certificate-of-insurance.template.spec.ts` +11) → api unit **2416/2417** (from 2394; the 1 failure is `app.controller.spec.ts`, a pre-existing zero-diff failure that also fails in complete isolation, unrelated to this change); +2 new api e2e tests, each with multiple assertions (permission/404/AR-EN-DUAL/invalid-language cases, `EXTERNAL_AUDITOR` proving the invoice endpoint's book-wide-not-owner-scoped permission, the new CANCELLED/EXPIRED 422 proof on the certificate, and a same-policy size proof that the certificate is genuinely smaller/different content than the schedule summary) — targeted run of the 2 directly-touched e2e files **16/16 green**, re-confirmed after the review-fix round; +richer assertions inside 2 pre-existing Playwright tests (no new test cases) — full `rfq.spec.ts` **29/29 green** (required a fresh `npm run build`, since Playwright's `webServer` serves the last build's output, not live source — a recurring gotcha this project's own history already hit twice before); full api+web `typecheck`/`lint`/`build` clean. **A genuine host-level disk-space crisis mid-session, unrelated to the code, consumed significant time**: the C: drive hit 0 bytes free (Docker Desktop's `docker_data.vhdx` had grown to ~42GB and never auto-shrinks — `docker builder prune` freed 22.82GB inside the VM but only ~640MB came back on the host), followed by a separate Docker Desktop stuck-backend recurrence (the same failure mode this project has hit before) — both required the user's own hands-on fix (an elevated VHDX compaction is still outstanding; a full tray quit + relaunch resolved the stuck backend). Given that time cost and this host's own repeated prior failure to complete either full suite under sustained memory pressure, **the full 63-file api e2e suite and the full 60+-file web suite were NOT attempted fresh this round** — the targeted evidence above stands in, the same accepted resolution every earlier item #7 round used. | No migration (two new `invoice`/`certificate_of_insurance` `DocumentTemplate` seed rows). **Part F item #7 (system-generated bilingual documents) is now fully built — all 6 named document types exist.** Read `ibms-brain/meta/context/bilingual-ui.md`'s "What item #7's invoice slice covers"/"What item #7's certificate-of-insurance slice covers" before assuming further scope: real persistence / a `Document` audit trail for a generated file remains explicit, documented future work (this app has no real object storage anywhere) — do not self-select building it. Both full suites (api e2e, web e2e) need a genuinely fresh run once host memory/disk allow. See project memory `project_docker_vhdx_disk_full.md` before troubleshooting a future disk-space issue on this host. |
| 2026-09-08 | **Part F item #7 — policy schedule summary, the 4th of 6 document types** (after complaint acknowledgement, quotation comparison, recommendation report). Derived from `Policy` + its most recent `PolicySchedule` — the backlog's own "Derive it from Policy + PolicySchedule" scoping decision, made earlier this item when scoping the certificate type, applies directly here too since a schedule summary IS that same underlying data. **Gated on a plain data-availability check, not a business-workflow one like the recommendation report's `blockedFromSend`**: a Policy has no coverage schedule to summarize until Process 19 issuance records the first one — `schedules.length === 0` before that, and the document endpoint 422s in that window ("has not yet been issued"). There is a real, brief crash-recovery window documented in `policy.service.ts#recordIssuance()` where `policyNumber` is written before the schedule is created; the gate is deliberately on `schedules.length`, not `policyNumber`, so that window is handled correctly without a special case. New `PolicyService.getByIdWithCustomer()` — the SAME visibility-preserving-read pattern the comparison and recommendation slices already established (`assertCustomerVisible()` widened to return the fetched `Customer` instead of `void`; the 3 pre-existing callers all ignored the return value, so this is a safe, non-breaking change; a new sibling method, never widening `loadVisible()`'s own signature, which has several other callers: `get()`, `place()`, `recordIssuance()`, `attachDocuments()`, plus the Process 20/21 sub-services). `Policy` already enforced real per-customer visibility before this item (inherited from its Customer, PLUS a Policy Checking Officer's documented cross-book reach for Process 20 QC) — confirmed by reading `policy.service.ts` before building, not assumed. "Most recent schedule" resolves to `schedules[0]` with no open/closed branching needed: `PolicyRepository`'s own `POLICY_INCLUDE` already orders `schedules` `effectiveFrom desc`, and closing one schedule + opening its replacement happen together in one interactive transaction (`versionScheduleForEndorsement()`), so the latest-effective row is always also the currently-open one whenever an open one exists; a cancelled policy's most recent schedule is its last CLOSED one, and the document still renders it as an "as at" historical snapshot rather than refusing outright. **First item #7 document to render `limits`/`sumsInsured` — a flagged content decision.** These are free-form JSON objects with NO fixed key vocabulary (`policy.config.ts#assertCoverageFigures` only checks "non-empty flat object of string/number scalars"). The quotation-comparison slice deliberately OMITTED `limits` for exactly this reason (no established display convention); that option doesn't exist here since the schedule IS the document's whole content. Resolved by rendering each key as literal, escaped, NEVER-translated text (the same treatment other free-text fields like `Complaint.issue` already get) and each value through `formatDocumentMoney` — the schema's own doc comment calls these figures "the requested/issued coverage snapshot", monetary by domain convention even though not yet `Decimal`-typed; a non-numeric string value degrades gracefully to that formatter's own existing escaped-raw-plus-currency-prefix fallback rather than crashing. Mirrors `PolicySection.tsx`'s own existing "Requested X · Issued Y (Δ Z)" premium display (reusing `policy.config.ts#premiumVariance()` as-is) and its "Effective FROM–TO/ongoing" schedule range wording — a printable rendering of the same data the web screen already shows. Web: the existing "Coverage schedule" block on `PolicySection.tsx` gained a "Download schedule summary (PDF)" button, rendered ONLY when `schedules.length > 0`. **Verification**: +15 new api unit tests (`policy-schedule-summary.template.spec.ts` — AR/EN/DUAL rendering, reference/policy numbers, full premium+variance rendering, every coverage-figure entry money-formatted with its raw key as the label, named-perils/extensions lists, em-dash-never-omitted rows, "ongoing" in each language, an empty coverage-figure table rendering nothing rather than crashing, no internal governance metadata, HTML-injection escaping on a coverage-figure key and on perils/extensions, a non-numeric coverage-figure value degrading gracefully, a null issued premium never omitting its row) → api unit **2394/2394** (from 2379); +1 new api e2e test (`policy.e2e-spec.ts`, multiple assertions: a placed-but-not-yet-issued policy → document endpoint 422; permission [403]/unknown-id [404]/non-owning-Sales-Officer-despite-`policy.read` [404]/cross-owner-Manager [200]; AR/EN customer-preference defaults, an explicit override, DUAL producing a genuinely larger PDF than AR alone; 400 on an invalid `language` value) — targeted run of the 4 directly-touched files (`policy`/`comparison`/`recommendation`/`complaint` e2e specs) **13/13 green**; +1 new Playwright test (extends the existing "places a policy from an accepted opportunity and records its issuance" test: asserts the download button is absent both before placement and immediately after PLACEMENT_CONFIRMED with no schedule, then appears and produces a real download once issuance records the first schedule) — full `rfq.spec.ts` file **29/29 green**; full api+web `typecheck`/`lint`/`build` clean. **The full 63-file api e2e suite was attempted fresh this round and was again killed partway through** by this machine's own sustained memory pressure (as low as ~514-580MB free RAM on an 8GB machine) — the SAME pre-existing host constraint recorded on the recommendation-report round immediately before this one, not a regression from this round's own changes. Real progress WAS made before the kill: 4 files unrelated to this change (`rbac.e2e-spec.ts`, `up-sell.e2e-spec.ts`, `audit.e2e-spec.ts`, `invoice.e2e-spec.ts`) completed with every test green, `rbac.e2e-spec.ts`'s own tests individually taking 100-330 SECONDS each under this pressure — genuinely slow, not hanging or failing. Following the exact resolution this table has now used on every document-type round: the targeted evidence above stands in for the incomplete full-suite run — a real, acknowledged verification gap, not a code issue, not re-litigated or re-explained at length each time it recurs. The full 60+-file web suite was not attempted either, for the same reason; `rfq.spec.ts` alone (the only file touching this round's web changes) was run in full instead, the same scope the recommendation-report round settled on under the identical constraint. | No migration (one new `policy_schedule_summary` `DocumentTemplate` seed row, seeded to both `db` and `db-test`). Read `ibms-brain/meta/context/bilingual-ui.md`'s "What item #7's policy-schedule-summary slice covers" before assuming item #7 is fully closed — it is NOT: 2 document types (invoice, certificate) and real persistence remain open, documented future work; do not self-select resuming them or starting item #8. Both full suites (api e2e, web e2e) need a genuinely fresh run once host memory allows — see "Verification — item #7's policy-schedule-summary slice" for the exact partial-progress evidence this round's targeted numbers stand in for. Before building either of the remaining 2: check whether the underlying entity already enforces per-customer visibility beyond a flat permission (as `ComparisonMatrix`, `Recommendation`, and `Policy` all do, but `Complaint` does not) — the document endpoint must inherit that check via the entity's own service, never its repository directly, or a real access-control regression follows. |

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
