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
| 2026-11-22 | **THE INDEX IS 86 ROWS: DECISION 157 GIVES THE ENGLISH LEFT ON THE DEMO PATH ITS ARABIC, AND THE SHARPEST FINDING IS THAT A SENTENCE RATIFIED THREE DAYS EARLIER WAS TRUE OF ONE STATUS IN EIGHT.** **(1) IT ANSWERS THE FOURTH ANSWER SHEET AND AMENDS TWO ROWS OF DECISION 153.** Twelve items, every one approved: thirteen shipping words take new sites, eleven empty cells take the suggestions put to her, the dual-control table loses its programmatic-name column, and the eleven «اعرف عميلك» hold sentences are carried to module 15 **after** the demo — with that list out of the demo scenario entirely. **(2) 🔴 AND RULING 1 IS A CORRECTION TO HER OWN DECISION 153, FOUND BY MEASURING THE SERVER RATHER THAN THE SCREEN.** 153 ratified «لا يُنشأ طلب عرض أسعار على هذه الفرصة لأنها في مرحلة التنسيب.» — but the server refuses in **every** status other than `NEEDS_CONFIRMED` and `RFQ_ISSUED`, so a closed-lost opportunity would be told it is in the placement stage. ⟶ **The status names itself now**, from the eight shipping labels. **(3) AND THE MEASUREMENT FOUND MORE THAN THE DECISION IT SERVED.** 24 English sites on the demo path that no walk and no decision had recorded — most of them on the opportunity screen and the claim card — and **the repo's own guard sees nine of the paper's fifty-six and reports «zero undeclared»**, blind to a capitalised word before `{`, to a literal opening with « · », to an all-lowercase literal, to a label in `lib/`, and to a stored value rendered as text. **(4) THE FILE HAS A `## القرار بجملة` SECTION**, so the gate needed no widening for the eighth batch running, and the index row was SLICED by script from the paper's own sentence. **Verification**: copied byte-identically (`sha256 0dd4653f`); `npm run check:decision-index` reads **86 files / 86 rows**, self-test 24/24. | **READ `meta/decision-index.md` — 86 ROWS NOW.** **A REFUSAL SENTENCE NAMES THE STATE IT IS REFUSING (decision 157 ruling 1)** — ⛔ a sentence that names one state is wrong on the other seven, and it was ratified that way because the question was put from the screen and not from the server. **AND A SHIPPING WORD IN A NEW SITE GETS ITS OWN KEY WITH THE SAME TEXT (ruling 2)** — ⛔ never a second render of the existing key: a later change to one would move the other, on a screen nobody was looking at. **AND THE DUAL-CONTROL TABLE IS SIXTEEN OPERATIONS WITHOUT THE PROGRAMMATIC COLUMN (ruling 11)** — ⚠️ the two needs-assessment rows carry the same permission and will read alike; the owner ruled it knowing. **⛔ AND THE ELEVEN KYC HOLD SENTENCES ARE MODULE 15, AFTER THE DEMO (ruling 12)** — and that list is out of the demo scenario, so there is nothing to work around. |
| 2026-11-19 | **THE INDEX IS 85 ROWS: DECISION 155 SENDS THE ENGLISH HALVES AFTER THE ARABIC, AND 156 SETTLES THE DATE SHAPE, THE BELL SENTENCE AND ONE WORD ON THE ROLES SCREEN.** **(1) DECISION 155 — FOUR RULINGS, AND ONLY THE FOURTH IS BUILT NOW.** Rulings 1 and 2 are already built (messages 48 and 49); ruling 3 — the uuid and the three raw values printed in the four papers — is a later batch by her own words («في رسالة ٥١ إن اتّسع الوقت، وإلا بعد العرض»). **Ruling 4 is the one that moves: what decision 151 deleted from the Arabic is deleted from the English by the same deletion** — the «Part N» references in seven texts and the self-service signup sentence. ⛔ «لا كلمة أخرى تتغيّر». That closes the empty cell message 49 reported rather than filled: her annex named ARABIC spans only, so the English was not a leftover but an unruled half. **(2) ⚠️ AND THE PAPER LEAVES ONE THING OPEN ABOUT ITS OWN SUBJECT** — the owner asked that the certificate be «نظامية», and §مفتوح records that its contents have **not** been measured against any official text; CBJ broker instruction 9/2026 is to be searched for an article that fixes them, and failing that it is a question for the legal adviser before the first real office. **(3) DECISION 156 — THREE RULINGS ON WHAT A SCREEN SHOWS.** One date shape («31/12/2028», the function already shipping on most screens — ⛔ the paper certificate and the four papers keep the written month name); the bell sentence does not print a name that is already the first words of its own description; and the family verb beside a permission name is **«تعطيل»**, not «تقاعد». **(4) 🔴 AND RULING 3 GREW A CONTINUATION THE SAME DAY, BECAUSE ONE WORD ON ONE SCREEN WAS THREE MORE STRINGS.** Changing only the matrix verb would have left the roles screen saying «تعطيل» in the table and «تقاعد الدور» on the button beside it. The owner was shown the other three and ruled «أ» on all of them, so the screen now has one word for one act. ⛔ `secKeysRetired` and `encryption-key.read` are NOT touched: a retired KEY is a different thing. **(5) BOTH FILES HAVE A `## القرار بجملة` SECTION**, so the gate needed no widening for the seventh batch running, and both index rows were SLICED by script from each paper's own sentence. **Verification**: both files copied byte-identically (`sha256 2cc52709` / `2cb3c456`); `npm run check:decision-index` reads **85 files / 85 rows**, self-test 24/24. | **READ `meta/decision-index.md` — 85 ROWS NOW.** **WHAT A DECISION DELETED FROM THE ARABIC IS DELETED FROM THE ENGLISH BY THE SAME DELETION (decision 155 ruling 4)** — ⛔ and by nothing more: if a removal leaves a sentence that reads badly, the sentence stays as it is and is REPORTED, because rewriting it would be deciding words she has not ruled. **A DATE ON A SCREEN GOES THROUGH THE SHIPPING FORMATTER (decision 156 ruling 1)** — ⛔ never a `.slice(0, 10)` of what the server sent, which prints the UTC day and can show yesterday in Amman; ⛔ and the paper certificate keeps its written month name. **AND A BELL SENTENCE DOES NOT SAY THE SAME WORDS TWICE (ruling 2)** — 158 of the 196 names are sliced from the opening of their own description, so the template with the name slot is the WRONG one for them; ⛔ neither template's words change. **AND THE WORD FOR THE ACT IS «تعطيل» ON THE WHOLE ROLES SCREEN (ruling 3 and its continuation)** — ⛔ a retired encryption KEY keeps «متقاعد», and ⛔ the English half («Retire») is unruled and untouched. |
| 2026-11-19 | **THE INDEX IS 83 ROWS: DECISION 153 PUTS THE OFFICE ON THE CERTIFICATE AND NAMES THE DECLARATION BUTTON, AND 154 TAKES THE CONSENT QUESTION AWAY FROM THE ENGINEER AND GIVES IT TO MODULE 11.** **(1) DECISION 153 — THREE RULINGS BUILT AND THIRTEEN STRINGS WAITING.** The certificate a customer receives carried a 36-character uuid under «رقم المرجع», named no office at all while its own text says «يرجى التواصل معنا», and printed the insurer and the line in English beside an Arabic insured name. Her rulings: the reference IS **the policy number**, the certificate carries **the office name and its licence number**, and the renewal declaration button is **«تسجيل الإقرار»**. §٢ ratifies thirteen more English spans inside screens; the rest of that table is a later batch. **(2) 🔴 AND THE BUTTON SHE RENAMED WAS ONE KEY SERVING TWO CONTROLS.** `rcRecordRenewalButton` is rendered TWICE on the licence screen — once on the control that FILES the renewal application and once on the control that records the DECLARATION — so the two acts had the same name and one of them was wrong. ⛔ The filing control keeps its label; the declaration takes its own key, which is the «one key that cannot move» shape decision 152 already made this repository write down. **(3) DECISION 154 REPLACES DECISION 153’s ITEM 19, WHICH SHE SUSPENDED ONE MINUTE AFTER APPROVING IT.** «لحظة … الموافقة لازم تيجي من العميل مش انا اتنبأ انه هو موافق عليها» — so the consent-text-version field and the consent card are **untouched by anybody** until module 11 builds her method: the system displays the approved text, the employee ticks two separate boxes, picks a channel, and the system records the date, the employee, the purpose and the version shown. ⛔ **Copy only here.** **(4) BOTH FILES HAVE A `## القرار بجملة` SECTION, so the gate needed no widening for the sixth batch running**, and both index rows were SLICED by script from each paper’s own sentence and never retyped. **Verification**: both files copied byte-identically (`sha256 96de8fb3` / `91916de3`); `npm run check:decision-index` reads **83 files / 83 rows**. ⚠️ And it correctly reports a decision with a file and a row and no citation in code until the code that cites it lands in the same batch — which is the register working as designed. | **READ `meta/decision-index.md` — 83 ROWS NOW.** **THE CERTIFICATE’s REFERENCE IS THE POLICY NUMBER (decision 153 ruling 1)** — ⛔ never the uuid, in the document or in its file name; a customer and an insurer both know the policy number and neither has ever seen the other. **AND IT CARRIES THE OFFICE NAME AND ITS LICENCE NUMBER (ruling 2)** — the licence number comes from the term in force AT ISSUANCE, which the licence gate has already chosen at the instant the act was permitted; ⛔ do not read the licence a second time, which would ask at a second instant. **AND THE DECLARATION BUTTON IS «تسجيل الإقرار» (ruling 3), IN ITS OWN KEY** — ⛔ the filing control keeps «تسجيل تقديم طلب التجديد»: one key cannot name two different acts. **⛔ AND NOTHING TOUCHES THE CONSENT TEXT VERSION OR THE CONSENT CARD (decision 154)** — decision 153’s item 19 is SUSPENDED by her own instruction, and 154 is module 11’s, after the demo. |
| 2026-11-18 | **THE INDEX IS 81 ROWS: DECISION 151 ANSWERS A SECOND WALK AND 152 NAMES THE OPPORTUNITIES BUTTON, AND THE SHARPEST FINDING IS THAT THE PIN INVENTED FOR A RULINGS-TABLE PAPER COULD NOT SEE AN ANCHOR CARRYING HER OWN BOLD.** **(1) DECISION 151 — SEVEN RULINGS, AND THE SIXTH IS THE ONLY ONE BUILT AGAINST.** It answers the second demo walk: a dead sentence on the users screen goes, seven internal clause references go while the ISO one stays, the Arabic name is mandatory and the English optional, «الامتثال» becomes «الالتزام», two spans that talk about the code leave the licence screen, and the two «المحاربه» customers STAY because they are hers. **Ruling 6 governs the demo seed: «لا يُزرَع دور يحملها» — the presenter creates the role and grants `license-renewal.declare` live, in front of the brokers, so decision 131 holds with no exception even in demo data.** **(2) DECISION 152 — «عرض الفرص», and «Process N — » leaves the ENGLISH descriptions too**, the half decision 150 ruling 3 left standing because its own rulings name Arabic spans only. **(3) 🔴 AND 151 IS THE SECOND PAPER WITH NO ONE-SENTENCE SECTION, WHICH IS WHAT EXPOSED THE HOLE.** `RULINGS_TABLE_ONLY` stripped `**` from the body and from the index row and left the ANCHOR as written — so a declared span carrying her inner bold could never be found in a body that had just had every `**` removed. **Four of 151's seven rulings carry it; all four were reported missing from a file they are plainly in.** Decision 150's five anchors happen to carry none, which is why the hole lived from the day the declaration was invented until the day it was used twice. ⛔ The anchors are NOT declared with their bold stripped out — that would make a declared span one the paper does not contain. Self-test **23 → 24**, and the new case is non-vacuous by its NEEDLE: the plant makes it report *the paper moved* instead of *the row drifted*. **(4) ALL SEVEN RULINGS ARE PINNED, NOT A CHOSEN FIVE** — on a paper whose rulings are its whole content there is no principled way to call one less load-bearing, and the unpinned one is the one a row drifts on. **(5) THE ANNEX IS DECLARED** (`decision-151-ratified-strings.md`) and takes **no index row**. ⚠️ And her own `## تكملة القرار ١٥١` was appended BELOW the rulings table, so every line under it has already moved once — the slicer is keyed on CONTENT, never a line number. **Verification**: all three files copied byte-identically (`sha256 106456db` / `783bbc2b` / `f50b9b19`); `npm run check:decision-index` reads **81 files / 81 rows**, self-test 24/24. | **READ `meta/decision-index.md` — 81 ROWS NOW.** **A RULINGS-TABLE ANCHOR MAY CARRY HER OWN `**` AND THE GATE NOW STRIPS IT FROM ALL THREE SIDES** — ⛔ do not "fix" a failing anchor by deleting its bold from the declaration: the declaration would then hold a span the paper does not. **NO SEEDED ROLE HOLDS `license-renewal.declare`, IN DEMO DATA TOO (decision 151 ruling 6)** — ⛔ granting it to make a demo screen work is the one thing decision 131 forbids, and the presenter granting it live IS the demonstration. **AND «Process N — » LEAVES THE ENGLISH (decision 152)** — decision 150 could not say so: every row of its annex names an Arabic span, so the English was an EMPTY CELL and is now ruled. ⛔ Next.js is NOT upgraded in this batch — after the demo build is tagged, before any real office. |
| 2026-11-17 | **THE INDEX IS 79 ROWS: DECISION 149 CLOSES THE LAST HOLE IN THE STORED CERTIFICATE, AND THE GATE MET THE FIRST DECISION PAPER IN 79 WITH NO ONE-SENTENCE SECTION.** **(1) DECISION 149 — EVERY CERTIFICATE HANDED OVER HAS A STORED COPY.** Decision 142 stored ONE per (policy, language); measured in message 44, an endorsement that changed the policy then a second download handed the customer a NEW document while the stored copy stayed the FIRST — a paper in the world with no record of it here, which is the state 142 exists to end. **(2) 🔴 AND THE DECISION RULES OUT THE OBVIOUS ANSWER BY NAME.** §٤: «ولا يُعتمَد على بصمة الملف». That is measured, not feared — Chromium stamps a creation date into the render, so a digest of the PDF identifies the RENDER and not the document, and keying on it is the exact defect message 44 shipped and its own e2e caught on the next run. ⟶ **The digest is taken over the rendered HTML**, which is a pure function of everything the certificate displays. ⛔ Not a hand-written list of fields: a list falls behind the template the first time it renders one more fact, and the failure is silent — a CHANGED certificate recognised as the old one and never stored. **(3) THE COPIES ARE CHAINED IN THE SCHEMA'S OWN SHAPE** (`versionNumber`, `previousVersionId`), so «بجانب القديمة» is recorded rather than left to `createdAt` and hope. **(4) 🔴 THE GATE MET A NEW SHAPE OF FILE.** Decision 150 states eight rulings as a TABLE and has no `## القرار بجملة` section — the first of 79. ⛔ Her paper is not re-headed to suit a matcher, and ⛔ the row is not left unpinned: `RULINGS_TABLE_ONLY` pins it to FIVE anchor spans sliced from the table, checked in THREE directions — an anchor gone from the file, an anchor missing from the row, and **the declaration itself going stale the day the paper gains a sentence**. Self-test **20 → 23**. **(5) AND A HAND-SPELLED ANCHOR DRIFTED BY ONE SHADDA**, which is why every span is sliced; the slicer was then re-keyed on CONTENT after the owner appended a second addendum mid-batch and every line number moved. **Verification**: `bash scripts/brain-doctor.sh` **0 errors, 0 warnings**; in `ibms-app` `npm run check:decision-index` reads **79 cited / 79 files / 79 rows** with self-test 23/23, `check:docs` exit 0, `from-empty.sh` **175 migrations from nothing, every assertion green**. | **READ `meta/decision-index.md` — 79 ROWS NOW.** **A STORED CERTIFICATE IS KEYED ON (policy, file name, FACTS DIGEST)** — ⛔ never on the PDF's digest, which is not byte-stable and identifies the render; decision 149 §٤ rules it out by name. **AND THE FACTS DIGEST IS THE RENDERED HTML, NOT A FIELD LIST** — a list cannot fall behind the template silently; a digest of its output cannot. **A DECISION PAPER MAY NOW HAVE NO ONE-SENTENCE SECTION** — declare it in `RULINGS_TABLE_ONLY` with the spans its index row is pinned to; ⛔ it is not an amnesty and ⛔ her heading is never edited to suit the gate. **AND `rfqNewRefusalAct` KEEPS «سعر» AS A STRUCK EXCEPTION (decision 150)** — the owner was shown that it contradicts decision 144 ruling 8-أ on the same screen and ruled it so knowing; ⛔ do not align it. |

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
