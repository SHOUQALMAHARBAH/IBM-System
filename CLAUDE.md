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
| 2026-11-08 | **DECISION 33's FILE LANDED AND THE INDEX IS AT 48 — AND THE SHARPEST FINDING IS THAT TWO INDEPENDENT COUNTS AGREED ON 47 BECAUSE THEY SHARED ONE BLIND SPOT, NOT BECAUSE THEY WERE INDEPENDENT.** **(1) THE OWNER WROTE THE FILE AND THE GATE THEN WENT RED NAMING ITS OWN DECLARATION AS STALE**, which is the one proof a declaration list cannot rot: `KNOWN_MISSING` is empty now and its account of how 33 hid is kept, because the hole was a matcher's shape and not anybody's oversight. `meta/decision-index.md` is **48 rows**, the new one inserted after ٣٢ in numeric order with its text taken **from the file rather than from the brief**, byte-identically, which is what the gate enforces. **(2) THE 47 IS CORRECTED AND ITS HISTORY IS DELIBERATELY NOT DELETED.** The owner's Arabic method paragraph is left byte-untouched — it truthfully describes a method that really does yield 47 — and the English re-derivation note now carries why: decision 33 appears ONLY inside `decisions 32 and 33`, so both counts read the `32`. **Two counts agreeing is evidence only when they are independent in the thing that can be wrong**, and these shared their matcher's shape, so the agreement confirmed the arithmetic and could not confirm the coverage. **(3) AND DECISION 33's OWN COUNT HID THE SAME WAY, ONE LEVEL DOWN — IT IS TEN, NOT NINE.** `decisions 32 and 33` sits on one line in nine files; in `retention-notice.config.ts:62` the citation BREAKS ACROSS A LINE inside a block comment (`decisions 32 and` then ` *  33.`), so every single-line search finds nine of ten. `CITED_ONLY_JOINTLY` in `ibms-app` declares the wrap-tolerant method — needed at all because the narrow `decision 33` the other files declare measures **zero** here — and is asserted stale the day the narrow form appears. **(4) THE FILE'S OWN FIRST SENTENCE SAID TEN CATEGORIES AND THE TEMPLATE SHIPS EIGHT**, and that sentence is what the index row is byte-pinned to, so shipping it would have put a false measured claim in the document that gets read first. Confirmed three ways — eight entries, `retention-template.config.spec.ts:28` pins all eight BY NAME rather than by count, and that spec's own comment opens *"A batch that ships eight categories"*. Corrected to a DIGIT («٨ فئات»), following this register's own «٩ مواضع» convention, with the noun byte-untouched; **«ثماني فئات» was DECLINED because «ثماني» ships only as «على ثماني شاشات» and pairing it with a different feminine plural is gender AGREEMENT** — morphology, the one operation that may never be performed on her behalf. **(5) AND THE GATE HAD TWO DEFECTS OF ITS OWN, BOTH FOUND BY THIS ONE FILE.** `CLAIM_FOOTER` hardcoded the singular accusative «موضعاً» — the form ONLY 11–99 takes — so a correct figure of 3 to 10, which takes the genitive plural «مواضع», was **never checked at all**; every figure corrected in the previous batch happened to be ≥ 11, so the gap never showed. **The gate whose own error message says *correct the digit and never re-word the noun* could not see the other noun form.** And it printed Arabic to an unreconfigured stdout, so `npm run check:docs` **crashed with `UnicodeEncodeError: 'charmap' codec`** on any Windows shell while passing in CI — green where it is checked, broken where it is written, which is the worst direction. Both fixed, both reasons recorded in the script. **Verification**: `bash scripts/brain-doctor.sh` **0 errors, 0 warnings**; in `ibms-app` `npm run check:docs` exit 0 at **167 undated, at budget** with **360 tables / 0 malformed**, and `decision-index-fit --self-test` **12/12** (+2: the plural noun form, and a joint-only declaration going stale). | **THE INDEX IS 48 ROWS AND `KNOWN_MISSING` IS EMPTY** — read `meta/decision-index.md` before asking what an `OWNER DECISION <n>` comment means; four rows are still marked decided-not-built (9, 20, 46, 122). **DECISION 33 IS CITED TEN TIMES, NEVER ONCE ON ITS OWN** — never narrow `CITE_TAIL` back to the first number, and never count it with a single-line search: the tenth citation wraps a line inside a block comment. **A FIGURE BELOW 11 WAS INVISIBLE TO THE FIGURE CHECK UNTIL 2026-11-08** — 3–10 takes «مواضع» and 11–99 takes «موضعاً»; both are read now. **AND «٢ موضعاً» IN DECISION 52 IS WRONG AND KEPT, BY HER DECISION** — two takes a dual, correcting it is morphology, and her answer was *«ما بيفرق، خليه زي ما هو»*; it is a recorded decision, not an uncorrected error, so do not "fix" it. **A GATE INSIDE A `check:` CHAIN MUST SET ITS OWN STDOUT ENCODING** — documenting `PYTHONIOENCODING=utf-8` in a header is fine for a script a person invokes and useless for one `npm run` invokes. |
| 2026-11-08 | **THE DECISION REGISTER LANDED, AND THE SHARPEST FINDING IS THAT ONE DECISION HAS BEEN CITED NINE TIMES SINCE THE REGISTER EXISTED AND IS IN NO REGISTER AT ALL, BECAUSE OF THE SHAPE OF THE CITATION RATHER THAN ANYBODY'S OVERSIGHT.** **(1) `meta/decision-index.md` IS NEW AND THERE WAS NO DECISIONS INDEX HERE BEFORE** — measured, `git ls-files` matching `decision` or `index` returned zero. 47 rows, each carrying the decision's own text beside its number and a link to its file in `ibms-app/docs/`, because the owner's requirement is that a reader never has to come back to her: a row that is only a number and a link does not satisfy it. The texts live in `ibms-app/docs/` where eight prior `decision-*.md` files already set the precedent, and the index lives here because the brain is what gets read first — **one home per fact: the index links and never restates.** **(2) DECISION 33 IS CITED NINE TIMES AND HAS NO FILE AND NO ROW, AND NO MATCHER COULD SEE IT.** It appears only inside the phrase `decisions 32 and 33` — never once on its own — so every pattern anchored on the word `decision` immediately before a number reads the 32 and is blind to the 33. Found by widening the matcher to walk a multi-number citation, and the widening is self-tested in both the two-number and the four-number shape so the hole cannot reopen. **Its file is Arabic register content and is the owner's to write**; it is declared in the gate with its measurement so the gate is not permanently red, and the gate FAILS the day the file appears, so the declaration cannot go stale. **(3) THE COUNT WAS RE-DERIVED INDEPENDENTLY AND THE TWO ROUTES AGREE ON 47 BY DIFFERENT ARITHMETIC** — which is the only reason to trust either. The owner got 48 with one phantom (`202`, the date `2026-10-29`); re-running her stated method gives **52** with four different phantoms (`409` an HTTP status after `ClientDecision`, `6` a count of process outcomes, `17` a backlog process number, `1` a fixture id) plus `98`, which is real and already had its file. 52 − 4 − 1 = **47**, and the 47 numbers match the 47 filenames exactly in both directions. **(4) `workflow-state-transitions.md` NOW ANSWERS THE FIXTURE QUESTION RATHER THAN RECORDING IT AS OPEN.** A test fixture seeding a status is **out of scope**, which is what `money-decimal-jod.md` and `ibms-app`'s own gate (`status-writes.inventory.spec.ts:79`) have always enforced — the document was the only one of the three that was silent, so this records rather than loosens. **And the one hazard that exemption carries is named as a FINDING, not smuggled in as a rule**: a fixture may seed a status the transition graph cannot reach, making a test pass against a state the product can never be in. Turning that into an obligation is the owner's. **(5) `workspace-updates.md` IS EXTENDED, NOT DUPLICATED** — a twelfth law was deliberately not written. A decision number cited with no file joins the list of things a change must ask *what did this just make false?* about, because the index is a developer-facing document and rots exactly like `CLAUDE.md` and `README.md`. **(6) AND THE NOT-WIRED RECORD FOR `enforce-evidence.sh` WAS FALSE, WITH A PRECISE MECHANISM.** It claimed `scripts/verify.sh` never writes `artifacts/<sha>/gates.json` and there is no `artifacts/`. **`scripts/verify.sh` here CREATES the directory at line 13, WRITES the file at line 52 and SAYS SO at line 60** — and `enforce-evidence.sh` treats `pass`/`skip`/`n/a` as non-failing, so the `gates.json` this script produces satisfies the guard. **The cause: there are TWO files called `scripts/verify.sh`, one per repository** (this one, 2933 bytes, `gates.json` ×3; `ibms-app`'s, 8105 bytes, ×0), and the command recorded as PROOF read the wrong one — returning the answer that made the claim look true. **`definition-of-done.md` § How it is enforced has carried the correct account all along**, and it carries the `ibms-app/`-qualified path the broken record dropped. The conclusion still holds and the reason is now the true one, with a dated review. **(7) AND `git rev-parse --show-toplevel` IS CORRECT IN ONE LIVE HOOK AND WRONG IN ANOTHER, which is the distinction worth keeping.** `enforce-workspace-updates.sh` uses it to read **the staged index of the repository being committed to**, which is exactly what it wants — the trigger paths and the required `CLAUDE.md`/`README.md` are per-repository, and it greps them as root-relative names. **Not a defect.** `enforce-evidence.sh` uses it to find an artifact written by a script in a DIFFERENT repository, which is. **Verification**: `bash scripts/brain-doctor.sh` **0 errors, 0 warnings**; `status_write_scan.py --self-test` 15/15; `hook_health.py --self-test` 5/5; `code_text.py --self-test` 12/12; and in `ibms-app` `npm run check:docs` exit 0 at **167 undated, at budget** with the new gate's self-test at **10/10**. | **READ `meta/decision-index.md` BEFORE ASKING WHAT AN `OWNER DECISION <n>` COMMENT MEANS** — 47 rows, the decision's own sentence beside each number, and four marked decided-not-built (9, 20, 46, 122). **THE INDEX LINKS AND MUST NEVER RESTATE** — the texts are in `ibms-app/docs/decision-<n>-<slug>.md` and that is the one home. **A DECISION NUMBER CITED WITH NO FILE IS A DEFECT, NOT A BACKLOG ITEM**, and `npm run check:decision-index` in `ibms-app` gates it in both directions. **AND IT WALKS A MULTI-NUMBER CITATION ON PURPOSE** — `decisions 32 and 33` is how decision 33 stayed out of the register for its whole life; never narrow that matcher back to the first number. **DECISION 33's FILE IS OWED AND IS THE OWNER'S.** — **CLOSED 2026-11-08, SAME DAY: she wrote it, the index is at 48 rows, and `KNOWN_MISSING` is empty. Everything in this row about 33 having no file, and the *47 rows* and *two routes agree on 47* figures, is SUPERSEDED by the row above — and the reason both routes said 47 is that they shared one blind spot rather than being independent in the thing that could be wrong.** **A TEST FIXTURE SEEDING A STATUS IS OUT OF SCOPE OF `workflow-state-transitions.md`**, answered 2026-11-08 to match the money lex and `ibms-app`'s gate — but a fixture seeding a status the transition graph cannot reach is a recorded hazard and not yet a rule. **`enforce-evidence.sh` IS SATISFIABLE HERE AND STAYS UNWIRED ON COST, NOT IMPOSSIBILITY** — review 2027-02-08. **AND NEVER WRITE `scripts/verify.sh` UNQUALIFIED IN A MEASUREMENT**: two repositories have one, they differ, and the unqualified path is what made a false claim look proven. |
| 2026-11-07 | **THE HOOKS WERE NOT RUNNING, AND THE REASON WAS NOT THE ONE ANYBODY HAD WRITTEN DOWN.** **(1) ALL SEVEN HOOKS WERE RECORDED IN GIT AS `100644`.** `core.filemode` is `false` on the development host, so the local `rwxr-xr-x` is not what a clone gets — and every registration in this repo's own `.claude/settings.json` tested `[ -x "$script" ]` and fell through to `\|\| true`. **So on CI, or on any fresh clone, all six guards here were silently inert**, and `brain-doctor.sh` reported `ok`. Fixed in both directions: the modes are `100755`, and every registration now runs `bash "$script"` so a lost mode cannot disable a guard again. **(2) `|| true` ON THE DECIDING LINE IS GONE.** A missing or unreadable guard exited 0 — indistinguishable from a clean pass, and the same family as a missing `jq` binary that once turned two CI watches into silence while a build was red. Registrations exit **2** with the file named. **(3) `scripts/hook_health.py` IS THE NEW `brain-doctor` SECTION, and against this repo as it stood it found 14 errors.** § Hook enforcement already checked for the `exit 1` footgun, but **nothing checked that a hook file exists, that one is registered, or the executable bit.** It now checks all three plus the `\|\| true` shape, and runs each guard's own `--self-test`. **Four plants, each red and each naming its own condition**: unregister a hook, drop a recorded executable bit, delete a registered hook, break a guard's tokeniser. **(4) THREE GUARDS NOW BLOCK WHEN THEY CANNOT READ THEIR INPUT.** They parsed the tool call with an inline `python -c` ending in `2>/dev/null` and a bare `except: pass`, so unparseable input produced an empty string and the hook exited 0 — a guard that had checked nothing, reporting success. `hook_scan.py` is the one home for that parsing and a failure is loud. `enforce-credential-safety.sh` is deliberately unchanged. **(5) `code_text.py` — A GUARD THAT READS OR STRIPS CODE TOKENISES; IT DOES NOT REGEX.** Measured in `ibms-app`: a two-substitution comment-stripper reported a class falling by four and the conclusion drawn was that a ratchet had slack. Both were false — `(?m)//.*$` eats `//` inside a string literal, and the spec it ran over is full of `"http://localhost:4000/..."`, so it truncated real code at every URL. 12 planted cases, and **every guard here that reads source is proven on the shape it strips INSIDE a string literal.** **(6) FOUR LEX DEFECTS, AND TWO OF THEM WERE DOCUMENTS CONTRADICTING THEMSELVES.** `money-decimal-jod.md` § Rule names *premium, **tax**, **fees**, commission, …* while its own § How it is enforced restated the list as eight and **dropped `tax` and `fees`** — and the hook matched the restatement, so float arithmetic on a tax or a fee was permitted by the guard that exists to forbid it. There is now one list, `MONEY_WORDS` in `money_scan.py`, and the lex points at it. `workspace-updates.md` § How it is enforced claimed its hook *"exits 1"* — which would not block anything, and is **the single most common hook bug**, documented as this guard's behaviour in the one paragraph a reader consults to find out whether a rule is enforced. The script has always exited 2; **the sentence was corrected to match the code, not the code to match the sentence.** The same hook also treated `meta/templates/` like every other trigger while that rule's own § What does NOT trigger exempts template CONTENT changes — it reads `--name-status` now and distinguishes `A`/`D`/`R` from `M` for that path alone. And `workflow-state-transitions.md` § How it is enforced described three defects as if they were the design: a PATH-SUBSTRING exemption (measured against `ibms-app`: **14 files match, 5 are the engine and 9 are not**, including four DTOs), a pattern that matched `=` where Prisma writes `:` (**8 lines seen where `status:` appears on 298**), and a raw-text read. A file claims the exemption with `@implements-workflow-transitions` **in its own text** now. **(7) ONE QUESTION IS LEFT OPEN RATHER THAN ANSWERED BY A HOOK**: `workflow-state-transitions.md` does not say whether a TEST FIXTURE that seeds a status is in scope, where `money-decimal-jod.md` explicitly exempts fixtures. `ibms-app` has decided in practice — its gate excludes specs — so the code and the rule do not currently agree, and that is recorded in the lex rather than resolved by adding an exemption. **(8) THE 21-DAY STALENESS CHECK IS AN `err`, NOT A `warn`.** This brain's own staleness was found by hand twice; a warning in a 200-line report is a line nobody reads, and this is the one check whose whole job is to notice that nobody is reading. It BLOCKS, which is the intended cost. **Verification**: `bash scripts/brain-doctor.sh` — **0 errors, 0 warnings**, from 14 errors before the fixes; `hook_health.py --self-test` 5/5; `code_text.py --self-test` 12/12; `status_write_scan.py --self-test` 15/15; `money_scan.py --self-test` 15/15; every hook exercised end to end with real tool-call JSON, including the unparseable-input path. | **RUN `bash scripts/brain-doctor.sh` AND BELIEVE IT NOW** — it can finally see whether a hook exists, is registered and is executable, which it never could before. **NEVER WRITE `\|\| true` ON THE LINE THAT DECIDES WHETHER A GUARD RUNS**, and **run a hook with `bash "$script"`, never `exec "$script"`** — a git-recorded `100644` makes an `[ -x ]` test skip a guard in silence everywhere but the machine it was written on. **A GUARD THAT READS OR STRIPS CODE TOKENISES** — use `code_text.blank()`, never a regex, and prove it on the shape it strips inside a STRING LITERAL. **A GUARD THAT CANNOT READ ITS INPUT MUST BLOCK**, never exit 0. **THE MONEY WORD LIST HAS ONE HOME, `MONEY_WORDS` in `money_scan.py`** — do not restate it in the lex; restating it is what dropped `tax` and `fees` for months. **A FILE EXEMPTS ITSELF FROM THE TRANSITION RULE WITH `@implements-workflow-transitions` IN ITS OWN TEXT**, never by being named after a path. **AND WHETHER A TEST FIXTURE THAT SEEDS A STATUS IS IN SCOPE IS UNDECIDED AND IS THE OWNER'S** — the lex is silent, `ibms-app`'s gate excludes specs, and the two do not agree. |
| 2026-09-22 | **Two rules into `definition-of-done`, both from things that went wrong rather than from principle.** **DOC CURRENCY IS A GATE.** Measured: across a 30-commit branch, `CLAUDE.md` and `README.md` both still said "Insurer CRUD remains specification-only and is deliberately deferred" after insurer CRUD had shipped — and the workspace-updates HOOK caught it on the branch's last commit, not a person. A hook that fires at the end lets thirty commits accumulate a false claim and fires on whoever happens to stage the last developer-facing file, not on whoever made the statement false. So the check joins the gates: grep the feature's own NOUNS (a claim rots on the words it names, not the files it touches), and treat "X is not built" / "remains specification-only" / "is deferred" as the shapes that rot, because they are true when written and nobody revisits them. **Correct rather than delete** — a deferral usually had a reason that survives it. **REWRITING PUBLISHED HISTORY: THE TREE IS THE TEST.** `--force` is acceptable only when the TREE IS UNCHANGED (verify with `git diff --stat HEAD origin/<branch>` printing nothing), always `--force-with-lease`, never bare. If the tree changes, add a commit — because **CI validated a tree**, and rewriting it means the green you are standing on no longer describes what is there. One test, no judgement call. Disclose either way. | **Before pushing, ask what this change made FALSE in `CLAUDE.md` / `README.md`** — not what it touched. Those two files are what a newcomer and an agent read first, so a false claim there is believed before anyone opens the code. And a dated `## What's New` row belongs in the commit that earns it, not batched at the end of a branch where it becomes one row summarising work nobody can separate. |
| 2026-09-21 | **Verification now says WHERE each gate runs: targeted locally, FULL in CI, and CI is what gates the branch.** `meta/context/verification-contract.md` gains that rule plus three new gate rows for `ibms-app` (migration checksums, schema divergence, Playwright browser revisions). Adopted from measurement, not preference: the full 91-file api e2e suite is **14.1 min in CI** against **75 min** on the dev laptop when that laptop is quiet and freshly cleaned, and 5+ hours under ordinary desktop load — and the repo is public, so runners cost nothing. The deciding argument is not speed but that **CI's resources cannot vary**: a red local run carries a code-or-machine ambiguity that was in fact resolved WRONGLY once, where a full-disk explanation fit the evidence and was false. **Two traps recorded in the rule itself.** (1) A rule naming CI is VACUOUS until CI has seen the branch — this one already said "CI gates the branch" while a 24-commit feature sat unpushed on a single laptop, so the laptop was being used INSTEAD of CI rather than in addition to it, and the whole feature existed in exactly one place. (2) `ci.yml` triggers on `push: branches: [main]` and `pull_request` only, so pushing a feature branch runs NOTHING — the PR is the event that makes the rule real, which is what `AGENTS.md` § Session completion always said. **Blast radius checked before adopting**, because "full in CI" is a WEAKER gate than a local full run wherever CI runs only a subset: `ibms-app` is the sole repo vendoring this brain (no other repository on the account has a `.gitmodules` at all), and its CI runs the suite in one unfiltered `turbo run test:e2e` command. | **Run gates locally SCOPED to the change's blast radius; do not spend hours reproducing CI.** "Targeted" means scoped by blast radius, never by convenience — a response-shape or shared-fixture change is still the full suite locally. **Open the PR**: a pushed branch runs no CI, so an unopened PR means the branch is unverified no matter how green the laptop was. **A future repo syncing this brain must NOT adopt the CI row until its own CI is confirmed to run the FULL suite.** |

**Older rows are in [`meta/whats-new-history.md`](meta/whats-new-history.md), oldest first,
unchanged.** `scripts/brain-doctor.sh` caps this table at five dated rows; its message says
*drop the oldest*, and the oldest is MOVED instead — the convention `ibms-app` already uses
for its own twelve-row table. A row belongs to the commit that earned it, and deleting one
to satisfy a cap destroys the only record of why something was done. **The move happens in
the SAME COMMIT as the row that displaces it.**

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

`ibms-app` is a single web+api monorepo, **organised by module inside one service**: `apps/api/src/modules/` holds **45 modules** (measured 2026-11-06, `ls -d apps/api/src/modules/*/ | wc -l`) — `claim`, `policy`, `endorsement`, `pdpl`, `compliance-risk`, `management-reporting`, `supporting-operations` and the rest. **Corrected 2026-11-06: this said "it is not yet split by module or service boundary", which was false in the first half** — a reader was told to expect an undifferentiated codebase and would not have gone looking for `modules/`.

It is **not** split by SERVICE boundary, and that part stands: one deployable api, one deployable web. The table below is still a business view rather than a services table, and no service-boundary decision has been taken.

| Module | Governs |
|---|---|
| Core IBMS (Sales/CRM, Policy, Claims, Finance, Compliance) | The 74 business processes — see `meta/context/policy-lifecycle.md` and `meta/context/claims-lifecycle.md`. **`Compliance` added 2026-11-06: this row omitted it while `README.md` § Modules included it.** README was right — Domain F (Compliance & Risk, #47–57) is one of the eight domains and is built. |
| M01–M12 (PCMS) | Privacy/compliance modules — see `meta/context/pcms-privacy-modules.md` |

## Architecture relationships

**IBMS and the PCMS (Privacy Compliance Management System) are one system, not two.** PCMS is the source of truth for every privacy/consent/retention/breach/DSR rule; IBMS's compliance module consumes PCMS decisions and feeds it data (customers, policies, claims) — it must never re-derive or duplicate a privacy rule. See `meta/designs/2026-08-pcms-source-of-truth.md`.

`ibms-app` is a Next.js (web) + NestJS (api) + PostgreSQL/Prisma monorepo. See `meta/designs/2026-08-ibms-app-stack-and-repo-split.md` for why, including the Prisma 6-vs-7 and repo-split calls.

**The authentication boundary HAS been decided. Corrected 2026-11-06 (ibms-app module 0-c batch 5): this said "No call-direction / auth-boundary / system-of-record decision beyond 'web calls api' has been made yet. Do not invent one."** That order was right and is kept below for the decisions it still governs — but the auth boundary is not one of them. It was taken in the multi-tenancy specification (Part II §4.1–§4.10) and built; what follows is **transcribed** from `ibms-app/docs/auth-mfa-session.md`, which is the authority and was walked against a running stack:

- **The api is the boundary.** Every employee sign-in goes through it; the web calls it and holds no authority of its own.
- **Every step runs inside an Organization resolved from the subdomain.** `GET /orgs/resolve?subdomain=…` is public by necessity — it runs before there is anyone to authenticate — and returns only what a sign-in screen needs. **There is no route that lists offices**, because §4.10.4 says one office administrator must not learn that another office exists.
- **The session row is the system of record, not the token.** Every access token carries an `org` claim (§4.10.2), but `validateAndTouch` resolves the Organization from the session row and `JwtStrategy` rejects a token whose claim disagrees with its own session.
- **`TenantMatchGuard`** enforces §4.10.3 — the subdomain's office must match the session's. It deliberately does nothing when the host names no office (`localhost`, an IP, the apex, `api.`), and skips an unknown-but-well-formed subdomain rather than refusing, which would turn the guard into a way to probe which labels are registered.
- **Two session ceilings**: `idleExpiresAt` moves forward on each authenticated request; `absoluteExpiresAt` never moves (12h). Either elapsing **revokes** the session — a termination, not a screen lock.
- **MFA** is TOTP plus a 30-day `TrustedDevice` for standard roles only; `SYSTEM_SECURITY_ADMINISTRATOR`, `COMPLIANCE_OFFICER` and `DATA_PROTECTION_OFFICER` always step up and may not trust a device.

No **call-direction** or **service-boundary** decision beyond "web calls api" has been made. **Do not invent one.** Record it here the day it is decided.

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

Path-scoped rules live in `.claude/rules/` and load themselves when you touch matching files — none exist in **this** repo, which stays documentation-only. **Corrected 2026-11-06: this said "none exist yet because there is no code to scope them to", which stopped being the reason once `ibms-app` existed.** The code to scope them to is in `ibms-app`; `.claude/rules/` there is the place for them, and `ibms-app/README.md` § `.claude/` records which hooks are and are not wired.

## Domain glossary

See `meta/context/glossary.md`. Terms that mean something specific here — **account**, **customer**, **policy**, **loss ratio**, **maker/checker** — go there, not in this file.

---

## MR standards

**CORRECTED 2026-11-06 (ibms-app module 0-c batch 5). This said "Not yet decided — there is no engineering repo."** The engineering repo is `ibms-app` and it has conventions in use:

- **Branch naming** — `<module>/<batch>-<slug>`, e.g. `module-0c/batch-2-measure-first`.
- **Open the draft PR on commit one.** `ci.yml` triggers on `push: branches: [main]` and `pull_request` only, so **pushing a feature branch runs NOTHING** — the PR is the event that makes the verification contract real. 24 commits once sat on one laptop with no copy anywhere.
- **No push without evidence** from `meta/context/verification-contract.md`; `meta/lex/definition-of-done.md` is the rule.
- **A dated `## What's New` row belongs in the commit that earns it**, not batched at the end of a branch. `ibms-app/CLAUDE.md`'s table is capped at 12 rows (`npm run check:whats-new-cap`).

`meta/templates/pr-description.md` is still the description format.

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
