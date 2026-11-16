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
| 2026-11-16 | **THE INDEX IS 72 ROWS: DECISION 143 NAMES THE BUTTON, AND THE ROUTE IT UNBLOCKS HAD BEEN BUILT, ENFORCED AND TESTED FOR A DAY WITH NO WAY IN FROM ANY SCREEN.** **(1) DECISION 143 — ONE CONTROL, ONE NAME.** «الزرّ الذي يربط مراسلة العميل بإعفاءٍ خامسٍ موسوم «بلا إثبات» اسمه «إرفاق المراسلة».» It completes decision 139: the fifth exemption now proceeds and is MARKED, and this is the control that lifts the mark. **(2) 🔴 THE DEBT WAS NAMED AND THE GATE WAS CARRYING IT, FOR THE SECOND TIME.** `POST /rfqs/:id/article-15-d/evidence` shipped on 2026-11-15 built, enforced on `rfq.communication.log` and e2e-tested in three directions — **and reachable by nobody**, because «إرفاق» ships only on the documents screens and «المراسلة» only in the plural on the request screen, and decision 125 forbids joining two shipped words into a third. `ibms-app`'s `unreachable-routes.py` carried it as a declared-unreached route with the creditor named in its own comment (*«one ratified word»*), exactly as it had carried the dismiss button a day earlier. ⟶ **Its DOWN direction FAILED on the commit that wired the button**, naming both figures to lower (17 → 16 routes, 9 → 8 controllers), which is what turns «it comes back when the word arrives» into a commitment rather than a hope. **(3) SHE RATIFIED THE PROPOSAL WHOLE** — «موافقة عليها» — so the label is sliced from her own one-sentence section and never retyped, and a test in `ibms-app` re-slices it and compares byte for byte. ⚠️ Her sentence carries TWO «…» spans and the label is the SECOND; the first is the MARK, «بلا إثبات». A slice taking the first would put the mark's own name on the control that clears it, and would still pass against a dictionary that had made the same mistake — so the test asserts the first span by name. **(4) AND DECISION 143 §4 CHANGES NOTHING ELSE**: the conditions that lift the mark are decision 139's unchanged — inbound, the request's own customer, one of the four approved means, and never WhatsApp — the empty list still renders decision 139's own sentence, and ⛔ no new permission is granted to any role in a real office (decision 131). **(5) THE FILE IS BYTE-IDENTICAL** (`sha256 d4e90c09`, 2713 bytes) and the index row was SLICED by script, which then ASSERTS on disk that the row and the sentence each land exactly once. **The gate needed no widening for the third batch running.** **Verification**: `bash scripts/brain-doctor.sh` **0 errors, 0 warnings**; in `ibms-app` `npm run check:decision-index` reads **72 cited / 72 files / 72 rows**, `check:docs` exit 0. | **READ `meta/decision-index.md` — 72 ROWS NOW.** **THE CONTROL THAT ATTACHES THE CUSTOMER'S MESSAGE IS «إرفاق المراسلة» (decision 143)** — ⛔ it is sliced from her paper, never retyped and never translated into a new Arabic phrase. **AND IT CLEARS THE MARK WITHOUT CHANGING WHAT CLEARS IT** — decision 139's four conditions are untouched, so ⛔ a picker must never offer a candidate the attach would refuse; one query answers both or the screen will contradict the server. **AND THE ATTACH IS WRITE-ONCE** — the row permits exactly one transition and no permission takes it back, so choosing a message and attaching it are two acts, not one click. |
| 2026-11-15 | **THE INDEX IS 71 ROWS: SIX DECISIONS IN ONE DAY, AND TWO OF THEM CLOSE A SECURITY FAULT AND REVERSE A RULING SHE HAD MADE HERSELF.** **(1) 140 — THE SELF-SIGNUP DOOR CLOSES.** «لا ينشئ أحدٌ حساباً في مكتب بلا دعوة.» `POST /auth/signup` was `@Public()` and its only protection was arithmetic: it refuses while the platform holds MORE than one brokerage office. **On the one-office platform this product is sold as, anyone on the internet got an account inside it.** Closed in the SERVICE so it is closed for every caller; production is a hard override no variable reopens; 117 test files keep their user factory and not one test was deleted. **(2) 139 — THE FIFTH EXEMPTION PROCEEDS, MARKED «بلا إثبات».** This REVERSES decision 129's fifth criterion and she took it knowing so: an act is blocked only when the harm is irreversible AND falls on somebody other than the office — here it falls on the office and is repaired by attaching the message, so refusing at the last step punished an employee for forgetting to log a phone call. The mark is what stops it becoming a hole: «لا إعفاء على الورق بلا دليل إلا ظاهراً، ويراه المفتّش». **(3) 🔴 AND THE ROW THE MARK HAD TO BE CLEARED ON WAS APPEND-ONLY BY TRIGGER.** Measured in `ibms-app`: `RfqArticle15DExemption` refuses every UPDATE under every permission (decision 129's criterion 7), so attaching evidence afterwards was impossible — the mark could be applied and never removed. ⛔ The trigger is NARROWED rather than dropped: exactly one transition, evidence NULL ⟶ NOT NULL, every other column unchanged. The column is WRITE-ONCE, which is append-only applied to a field, and «no permission removes the mark» is enforced by the database. **(4) 137, 138 AND 142 ARE RULED AND NOT BUILT** — durations split legal/office with a chain that never erases (module 2); one screen in module 1 for the three values the Central Bank has not issued, plus a reminder of everything the office must decide by hand; and every insurance certificate stored as a file with a `Document` row carrying the stamp. 🔴 **142 rests on a measurement that changes its size:** `Document.storageRef` is supplied by the UPLOADER, so **no service in that API stores bytes at all** — every `Document` row today is a pointer with nothing behind it. Her ruling: the bytes live in the database until a storage service exists. **(5) 141 closes module 1 with seven answers**, four of them small enough to ship in a batch. **(6) ALL SIX FILES ARE BYTE-IDENTICAL** and every row was SLICED by script from each file's own one-sentence section; the script now ASSERTS each row landed exactly once on disk, after last batch's `sed` matched nothing and silently re-inserted the previous batch's row while reporting success. **Verification**: `bash scripts/brain-doctor.sh` **0 errors, 0 warnings**; in `ibms-app` `npm run check:decision-index` reads **71 cited / 71 files / 71 rows**, `check:docs` exit 0. | **READ `meta/decision-index.md` — 71 ROWS NOW.** **NOBODY CREATES AN ACCOUNT IN AN OFFICE WITHOUT AN INVITATION (decision 140)** — ⛔ do not reopen `POST /auth/signup`, and do not remove its `@Public()` either: the closure is in the service, and the decorator is what lets 117 specs be TOLD the door is shut. **AN EXEMPTION 5 WITH NO EVIDENCE IS ACCEPTED AND MARKED, NOT REFUSED (decision 139)** — and ⛔ the evidence rules did NOT move: inbound, the opportunity's own customer, one of art. 22/s's four means, and WhatsApp never. **A DURATION WITH A STATUTE IS READ-ONLY TO THE OFFICE AND A TRANSACTION RUNS ON THE FIGURE IT STARTED ON (decision 137)** — module 2, and it CHANGES built behaviour, which she decided knowing so. **AND A CERTIFICATE IS STORED NOW (decision 142)** — ⛔ but nothing in that API stores bytes yet, so the bytes go in the database until storage exists, and how long they are kept is module 11's question (142 §4), unanswered and therefore nothing is deleted. |
| 2026-11-15 | **THE INDEX IS 65 ROWS: THE PROVIDER WILL ENTER AN INSTRUMENT'S FIGURE FROM A SCREEN, AND THE RENEWAL STAMP NEVER REACHES THE CUSTOMER'S PAPER.** **(1) DECISION 135 — a figure the instrument STATES is entered ONCE by us, from a screen, with its article and its effective date; it takes effect for every office from that date, the old value gains an end date rather than being deleted, each office administrator is notified, and «ولا يُلمَس الكود».** It COMPLETES decision 123 rather than contradicting it: 123 settled whose row a figure is, and this settles how the provider's changes. ⛔ Why «each office enters its own» was refused, in her own example: the Central Bank drops a ceiling from ٢٠٠٠ to ١٥٠٠, one office enters it that day, one forgets for three months and keeps exempting requests up to ٢٠٠٠ while stamping them «معفاة», and one types ٢٠٠٠٠ and exempts everything. **One instrument cannot have a different answer per office.** **(2) DECISION 136 — two rulings taken together.** (أ) The stamp «صدرت والتجديد قيد الدراسة» shows on screens and in the record and is **never printed** on the three documents the customer receives, because no provision of Instructions No. 9 of 2026 and nothing in the adviser's written opinion asks for it, and art. 19/c already protects the customer on the premium. (ب) The sentence shown when issuance is refused because nobody has declared yet: **«الترخيص قيدَ التجديد، ولم يُسجَّل الإقرار بعد. راجع مسؤول النظام في مكتبك.»** — two of its three parts already ship, and «ولم يُسجَّل الإقرار بعد» is new and hers. **(3) 🔴 AND DECISION 136 §6's ENGINEERING NOTE RESTS ON A ROW THAT DOES NOT EXIST.** It settles that the certificate is stamped on «the `Document` row the `ISSUE_CERTIFICATE` act creates». **Measured in `ibms-app` on 2026-11-15: the act creates none.** The service renders a PDF and returns a buffer, the route returns a `StreamableFile`, and all three generated documents write no record at all — on dev there has never been one certificate-of-insurance row. ⟶ So the sixth issuance act has nothing to carry a stamp, persisting certificates is a NEW CAPABILITY rather than a column, and that is the owner's decision. **Decision 128's build stopped there on her own instruction** («if it cannot, stop and report the smallest shape») rather than shipping five-sixths of a rule. **(4) BOTH FILES ARE BYTE-IDENTICAL** to her originals and both index rows were SLICED by script from each file's own `## القرار بجملة`; the gate needed **no widening for the second batch running**, and it then refused twice until each decision was cited where it governs. **Verification**: `bash scripts/brain-doctor.sh` **0 errors, 0 warnings**; in `ibms-app` `npm run check:decision-index` reads **65 cited / 65 files / 65 rows** with self-test 17/17, `check:docs` exit 0 at 167 undated and 0 malformed tables. | **READ `meta/decision-index.md` — 65 ROWS NOW.** **A FIGURE THE INSTRUMENT STATES IS ENTERED BY THE PROVIDER FROM A SCREEN, ONCE, FOR EVERY OFFICE (decision 135)** — ⛔ not by each office for itself, and ⛔ not by a code change; decision 123's criterion 7 (an office trying to write a provider figure is REFUSED) stands word for word. **NOT BUILT:** there is no legal-values screen for anyone, and a provider row has no column for the article's TEXT. **THE RENEWAL STAMP IS NEVER PRINTED ON THE CUSTOMER'S PAPER (decision 136/أ)** — screens and the record only; reopened by a CBJ text, the signed opinion, or a ruling of hers. **AND BEFORE BUILDING THE STAMP, KNOW THAT THE SIXTH ISSUANCE ACT HAS NO RECORD** — a certificate is streamed, never stored, so there is nothing to stamp until she decides whether certificates become persisted documents. |
| 2026-11-15 | **THE INDEX IS 63 ROWS: DECISION 134 RATIFIES THE TWO WORDS THAT WERE OWED, AND ONE OF THEM HAD BEEN HOLDING A BUILT ROUTE OUT OF THE PRODUCT.** **(1) DECISION 134 — TWO STRINGS, AND NEITHER WAS OURS TO WRITE.** «**إزالة علامة جديدة**» is the label on the control that clears the «جديدة» mark on a permission the office has decided NOT to grant — decision 131's second way of deciding, «يعطيها لدور، أو يقرّر فيها». And «**يُقرّ بإرسال طلب عرض سعر لأقل من ثلاث شركات تأمين بلا إعفاء، ويكتب السبب. وهي غير صلاحية إرسال الطلب.**» is the description of `declared-act.article-15-d.declare`. **(2) 🔴 THE FIRST WORD WAS A NAMED DEBT, AND THE DEBT WAS VISIBLE IN A GATE.** `POST /rbac/permissions/:code/dismiss` shipped built, enforced and e2e-tested on 2026-11-14 with **no way in from any screen**, because decision 125 forbids inventing the word and decision 133 did not contain one. `ibms-app`'s `unreachable-routes.py` carried it as a declared-unreached route with the creditor named in its own comment — *«one ratified word»* — and its DOWN direction **failed on the commit that wired the button**, which is what turned «it comes back to 16» from a hope into a commitment. **(3) AND THE SECOND REPLACED AN AGENT-COMPOSED LINE RATHER THAN APPROVING IT — THE THIRD OF TEN.** The seven of message 34 survived her reading unchanged; the two `legal-value.*` lines did not, and nor did this one. Hers is shorter and drops the regulatory-responsibility clause the composed line carried. ⟶ **So a line sitting on `AWAITING_OWNER_REVIEW` is not a line that is probably fine**, and the running tally is the only thing that makes that visible. **(4) BOTH STRINGS ARE SLICED BY SCRIPT FROM HER OWN TABLE AND NEVER RETYPED**, and a test in `ibms-app` re-slices both and compares BYTE FOR BYTE — a plant changing one word in each killed exactly its own test, by name. The index row was sliced the same way from the file's own `## ١ — القرار بجملة واحدة`, which the gate already understood: **no widening was needed for the first time in four batches.** **Verification**: `bash scripts/brain-doctor.sh` **0 errors, 0 warnings**; in `ibms-app` `npm run check:decision-index` reads **63 cited / 63 files / 63 rows** with self-test 17/17, and `check:docs` exit 0 at 167 undated and 0 malformed tables. | **READ `meta/decision-index.md` — 63 ROWS NOW.** **THE CONTROL THAT CLEARS THE «جديدة» MARK IS «إزالة علامة جديدة» (decision 134)** — it is the half of decision 131 that does NOT grant anything, so ⛔ a dismissal must never be allowed to grant the code, and the code must stay grantable afterwards. **AND A PERMISSION DESCRIPTION ON THE AWAITING LIST IS A PLACEHOLDER, NOT A DRAFT SHE WILL WAVE THROUGH** — three of the ten agent-composed lines have now been rewritten rather than approved. |
| 2026-11-10 | **THE INDEX IS 54 ROWS, AND A DECISION IS NOW MARKED STRUCK RATHER THAN QUIETLY REPLACED.** **(1) THREE NEW DECISIONS AND ONE REPLACEMENT.** **125 — the dash does not appear in the system at all**: every empty value AND every option inside a select carries a word fitted to its own screen, measured module by module. It replaces **decision 60**, whose guard it carries forward verbatim — ⛔ **الكلمةُ لا تُخترَع**: the word is sliced from text already shipping on that same screen or it is the owner's, and the table (site · word · where it was sliced from) is shown to her before it ships. **126 — the system warns and records and does not refuse**, except for four acts whose harm cannot be undone AND falls on someone other than the office; the window carries the article's own text, a written reason and a hand-ticked acknowledgement, and **the legal adviser's contrary advice is kept verbatim inside the decision** because an overruled opinion that is deleted stops being an overruled opinion. **127 — no permission code is ever shown to a user**: a short plain Arabic name, sliced from that permission's own shipped description. **And 123 is replaced by its THIRD form**, which splits the rule in two: a figure the instrument STATES is seeded by us with its article, and only a figure the instrument DEFERS to a ruling not yet issued is supplied by the office. **(2) 🔴 DECISION 60 WAS STRUCK ON 3 NOVEMBER AND THIS REPOSITORY CARRIED IT AS LIVE FOR A WEEK** — its file was written on 7 November from a code comment, four days after the owner had dropped it. **The file is MARKED, not deleted, and its row stays**: a struck decision whose record is erased reads as a decision nobody ever took, and the next person re-derives it. The marker carries why it was dropped (the dash itself stops work), why its own reasoning was right (a word forced into a place it does not fit is worse than a dash), and the date of the mistake. **(3) AND THE GATE REFUSED THREE TIMES ON THE WAY IN, EACH FOR A DIFFERENT REAL REASON.** 126 and 127 had a file and a row and were cited NOWHERE in code — closed by citing each where it governs rather than by weakening the check. And **decision 60's own stated citation figure went 12 → 16, because this batch's edits NAME decision 60** — a file that states how many places cite it is a figure that moves when the correction is written, which is the ratchet catching its own author for the third batch running. **Verification**: `bash scripts/brain-doctor.sh` **0 errors, 0 warnings**; in `ibms-app` `npm run check:decision-index` reads **54 cited / 54 files / 54 rows** with self-test 13/13, and `check:docs` exit 0 at 167 undated and 0 malformed tables. | **READ `meta/decision-index.md` — 54 ROWS NOW.** **THE DASH IS GONE FROM THE WHOLE SYSTEM (decision 125), INCLUDING AS A SELECT OPTION** — and ⛔ the replacement word is never invented: slice it from the same screen or ask the owner, and show her the table before shipping. **THE SYSTEM WARNS AND RECORDS AND DOES NOT REFUSE (decision 126)** — four refusals and no fifth without a decision, and the test for a fifth is *is the harm irreversible, and on whom does it fall?* **NO PERMISSION CODE IS EVER SHOWN TO A USER (decision 127).** **A LEGAL FIGURE THE INSTRUMENT STATES IS OURS TO SEED WITH ITS ARTICLE; ONLY A FIGURE DEFERRED TO AN UNISSUED RULING IS THE OFFICE'S (decision 123, third form)** — the earlier forms rested on eight figures believed unreadable, and they are all readable. **AND A STRUCK DECISION IS MARKED, NEVER DELETED** — decision 60 keeps its file and its row, because the record of a decision that was dropped is what stops it being re-derived. |

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
