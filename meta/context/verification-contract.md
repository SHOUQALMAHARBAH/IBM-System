# Verification contract — what "working" means here

**Last verified:** 2026-08-25 · **Owner:** shouq

> This is the most valuable verification file in the brain. Without it, an agent invents its own standard of "done" — and it will be lower than yours.
>
> An agent will tell you the page looks great whether or not it ever rendered the page.
>
> **The rule: claims are not evidence. Exit codes, test results, API responses, database verification, and screenshots are evidence.**

A change is NOT done when the code is written. It is done when the applicable evidence below exists and is pasted or linked in the PR description.

---

## Current engineering baseline

The IBMS engineering stack is:

| Layer | Technology |
|---|---|
| Source control | GitHub |
| CI/CD | GitHub Actions |
| Frontend | Next.js + TypeScript |
| Backend | Node.js + TypeScript |
| Database | PostgreSQL |

The following were finalized when `ibms-app` was created (2026-08-25 — see
`meta/designs/2026-08-ibms-app-stack-and-repo-split.md`):

| Area | Choice |
|---|---|
| Frontend test framework | Vitest + Testing Library |
| Backend test framework | Vitest |
| E2E framework | Playwright |
| Accessibility tooling | axe-core |
| Database migration tooling | Prisma Migrate |
| API contract testing | OpenAPI, generated from `@nestjs/swagger` decorators and validated against real responses with `ajv` — `apps/api/test/contract.contract-spec.ts` |
| Containerization | Docker |
| Preview environment | Vercel — configured, not yet connected to a live project |
| Deployment platform | still **TBD** — see `ibms-app/README.md` § Deployment |

**Do not invent a command for a gate that does not exist yet.**

---

# Every change

All commands below run from the `ibms-app` repo root (Turborepo fans them out per
workspace) unless noted otherwise.

| Gate | Command | Evidence |
|---|---|---|
| Brain health | `bash scripts/brain-doctor.sh` (this repo) | exit 0 |
| No unfilled placeholders | part of brain-doctor | 0 unfilled fill-markers outside `_TEMPLATE.md` files |
| Type checking | `npm run typecheck` | exit 0 |
| Lint | `npm run lint` | exit 0 |
| Unit tests | `npm run test` | exit 0 + test count |
| Build | `npm run build` | exit 0 |
| Regulatory traceability | Manual | citation present in PR/ticket description |
| Evidence generation | CI artifact | artifact exists for the commit SHA — CI does not yet independently enforce this, see `meta/lex/definition-of-done.md` |

If `ibms-app` renames a script, update this contract instead of inventing an alias.

---

# Backend/frontend gate commands (ibms-app)

| Gate | Command | Evidence |
|---|---|---|
| Types | `npm run typecheck` | exit 0 |
| Lint | `npm run lint` | exit 0 |
| Unit tests | `npm run test` | exit 0 + test count |
| Build | `npm run build` | exit 0 |
| Integration tests (API) | `npm run test:e2e` | exit 0 — needs a reachable `DATABASE_URL` |
| Contract tests (API) | `npm run test:contract` (api workspace) | exit 0 — needs a reachable `DATABASE_URL`; validates real responses against the OpenAPI schema generated from controller decorators |
| E2E (web) | `npm run e2e` | exit 0 — functional flows only, excludes `@a11y`-tagged specs |
| Accessibility | `npm run test:a11y` (web workspace) — axe-core, split from `npm run e2e` by Playwright `@a11y` grep tag | 0 serious/critical violations |
| Security tests | `npm run test:security` (repo root — `npm audit --audit-level=high`) | exit 0 |
| Database migrations | `npm run db:migrate:deploy` (CI/prod) / `npm run db:migrate:dev` (local) | exit 0 |
| Database schema | `npm run db:validate` — `prisma validate` | exit 0 — schema is internally valid. NOT a drift check, and neither is `migrate status`: see the two rows below |
| Migration checksums | `npm run db:checksums` (`db:test:checksums` for the test DB) | exit 0 — every APPLIED migration's stored sha256 matches its file, whole set. `prisma migrate status` does not check this: measured with a drifted migration present, it printed "Database schema is up to date!" and exited 0 |
| Schema divergence | `npm run db:divergence` (`db:test:divergence`) | exit 0 — `schema.prisma` still describes what the database enforces. Asserts the `migrate diff` output is exactly a NAMED set (things Prisma's language cannot express: generated columns, GIN-on-`Unsupported`, composite FKs) and fails in BOTH directions |
| Playwright browsers | `npm run browsers:check` | exit 0 — every browser revision on disk is one the installed `playwright-core` can resolve. A version bump leaves the old revision unreachable on disk and nothing else notices |
| Smoke tests | `bash scripts/smoke.sh api` (repo root; also `npm run test:smoke`) | exit 0 + output |

These rows must be updated in the same commit that creates the relevant engineering capability.

A consolidated local/agent runner exists for this whole table: `ibms-app/scripts/verify.sh`
runs every gate above against `db-test` and prints each one's real evidence, ending in a
summary block suitable for pasting into a PR description.

## STEP ZERO OF STARTING A BRANCH: open the draft PR on the first commit

**Before the second commit, not after the last one.** Create the branch, make one commit, push,
and open the PR as a **draft**. Then every push is checked on fixed resources within about fifteen
minutes, and a red arrives while the commit that caused it is the last thing you touched.

This is a HABIT rather than a rule you consult, because the two failures it prevents are both
invisible from inside the work:

1. **A branch that has never been pushed exists in exactly one place.** A 24-commit feature —
   the whole of insurer management, including every measurement behind it — sat on a single
   laptop with no copy anywhere. Nobody had decided to carry that risk; nobody had looked.
2. **Pushing is not enough on its own.** `ibms-app`'s `ci.yml` triggers on
   `push: branches: [main]` and on `pull_request`. A feature-branch push runs **nothing**. So
   "push your work" would not have fixed (1) either — the PR is the event that makes CI real.

And the cost of skipping it compounds silently: those 24 commits reached CI in a single batch. A
red would have meant bisecting a month of work instead of reading one diff.

A draft PR costs nothing on a public repo, is not a request for review, and converts to ready
when the work is. `AGENTS.md` § Session completion has always ended at "open a PR with evidence
and let a human merge" — this moves that step to the beginning, where it does the work.

## WHERE each gate runs: targeted locally, FULL in CI, and CI is what gates the branch

**Adopted 2026-09-21, from measurement.** Run the gates locally SCOPED to what the change
touches. The authoritative full run is CI's, and a branch is not verified until CI has been
green on it.

| | full api e2e suite (91 spec files) |
|---|---|
| CI (`ci.yml`, `npx turbo run test:e2e --filter=api...`, no file filter) | **14.1 min**, measured |
| the current dev laptop, quiet and freshly cleaned | **75 min**, measured across seven batches |
| the same laptop under ordinary desktop load | 5+ hours, and it did not complete |

The repo is public, so GitHub-hosted runners cost nothing. CI is therefore faster than a
HEALTHY local run and free, which is not a close comparison.

**But do not keep this rule for the speed, because speed is the argument someone trades away on
a busy day.** Keep it for two properties a developer machine cannot offer at all:

**CI is the only environment that starts from NOTHING, every time.** It migrates and seeds an
empty database on every run. A long-lived dev database already holds rows that earlier migrations
created, so it exercises the update path and never the create path — which is exactly how a
broken seed passed locally and failed in CI during RBAC Phase 1, and how `packages/db`'s seed
turned out to be typechecked by nothing at all. The same structure made CI the only place the
migration-checksum and schema-divergence gates could be independently confirmed: until they ran
there, both were claims about two databases carrying whatever history they happened to carry.
**A clean build is not something you can arrange locally without destroying your own data.**

**CI's resources cannot vary.** A red local run carries an ambiguity CI structurally does not
have: the code, or the machine? That ambiguity is expensive to resolve and it was resolved
WRONGLY at least once — a full-disk explanation fit the evidence, was tidy, and was false
(`ibms-app/IMPROVEMENTS.md` § 1.32). On a fixed runner the question does not arise.

**The reason is not speed, though — it is that CI's resources cannot vary.** A red local run
carries an ambiguity CI structurally does not have: the code, or the machine? That ambiguity is
expensive to resolve and it was resolved wrongly at least once — a full-disk explanation fit the
evidence, was tidy, and was false (`ibms-app/IMPROVEMENTS.md` § 1.32). On a fixed-resource
runner the question does not arise.

**What "targeted" means:** the spec files covering the change's blast radius, plus the whole-set
inventory tests, plus every gate that is cheap (typecheck, lint, unit, the three database gates).
When a response SHAPE or a shared fixture changes, the local run is the full suite anyway —
targeted means scoped by blast radius, never scoped by convenience.

**Two traps this rule walked into on the day it was written, so nobody repeats them:**

1. **A rule naming CI is vacuous until CI has actually seen the branch.** This rule already
   said CI gates the branch while a 24-commit feature sat unpushed on one laptop, so CI had
   never run on any of it. The laptop was being used INSTEAD of CI, not in addition to it.
2. **`ci.yml` triggers on `push: branches: [main]` and on `pull_request` — not on a feature
   branch push.** Pushing a branch runs nothing. **Open the PR**; that is the event that makes
   this rule real. (Which is also what `AGENTS.md` § Session completion has always said:
   open a PR with evidence and let a human merge.)

**Scope of this rule:** `ibms-app`, whose CI genuinely runs the whole suite in one unfiltered
command. Checked on adoption: it is the only repo vendoring this brain — no other repository on
the account has a `.gitmodules` at all — so nothing else can inherit a weaker gate from it. **A
future repo that syncs this brain must not adopt this row until its own CI is confirmed to run
the FULL suite**, because "full in CI" is a weaker gate than a local full run if CI only runs a
subset.

---

# Backend services additionally

Every backend service must eventually have:

| Gate | Command | Evidence |
|---|---|---|
| Boots | `npm run start` | service starts successfully |
| Health | `curl /health` | HTTP 200 |
| Smoke | `bash scripts/smoke.sh <service>` (repo root) | exit 0 + output |
| Contract | `npm run test:contract` | exit 0 |
| Security | `npm run test:security` | exit 0 |
| Integration | `npm run test:e2e` | exit 0 |

**Write a case in `scripts/smoke.sh` for each service the day it exists**, dispatching to
that service's own real implementation (e.g. `apps/api/scripts/smoke.sh`, boots via
`npm run start`, curls `/health` and `/health/db`). There is one backend service today
(`api`) — the dispatcher exists so `bash scripts/smoke.sh <service>` is already the right
shape, but don't invent a case for a service (e.g. an `auth` service) that has no real
implementation behind it yet.

A smoke test must assert the service's actual job. A process merely starting is not
sufficient — `apps/api`'s smoke test also hits `/health/db`, proving the service can reach
Postgres, not just that the process is alive. As real business logic lands, extend it (or
add sibling smoke scripts) to cover at least one critical business rule, such as:

- unauthorized user cannot approve a protected workflow;
- maker cannot approve their own transaction where maker/checker separation applies;
- a shared request becomes locked where the business rule requires locking;
- a historical insurance request remains linked to its original form version.

---

# Frontend pages additionally

Every changed frontend page must eventually have:

| Gate | Command | Evidence |
|---|---|---|
| Type checking | `npm run typecheck` | exit 0 |
| Lint | `npm run lint` | exit 0 |
| Unit/component tests | npm test | exit 0 + test count |
| E2E | npx playwright test | exit 0 |
| Screenshots | Playwright screenshots | required PNG states |
| Accessibility | axe-core + manual keyboard verification | 0 serious/critical violations + keyboard checks pass |
| Production build | `npm run build` | exit 0 |

---

# Required UI states

Every page ships with all four states implemented and verified:

1. **loading**
2. **empty**
3. **error**
4. **populated**

A state with no screenshot is a state that is not implemented.

For workflow-heavy IBMS pages, additional states may be required:

- draft
- submitted
- pending approval
- approved
- rejected
- returned
- cancelled
- locked
- archived
- expired

Only applicable states need to be implemented for a specific page.

---

# IBMS frontend requirements

Every affected IBMS page must be verified in:

### English

- LTR navigation
- LTR forms
- LTR tables
- LTR filters
- LTR dialogs
- LTR charts

### Arabic

- RTL navigation
- RTL forms
- RTL tables
- RTL filters
- RTL dialogs
- RTL charts

The test must verify the actual layout, not merely the text direction.

---

# Bidirectional text

IBMS must correctly display mixed Arabic/English values.

Examples include:

- Arabic customer/company names containing English codes
- Arabic insurance names containing policy/product codes
- English reference numbers inside Arabic forms
- Arabic addresses containing Latin characters

Evidence must show that mixed-content fields remain readable and correctly positioned in both LTR and RTL contexts.

---

# Keyboard accessibility

Every interactive element must have:

- visible keyboard focus;
- logical keyboard order;
- accessible name/label;
- usable keyboard interaction.


Accessibility tooling: axe-core.
Automated accessibility checks must report 0 serious/critical violations.
Keyboard navigation and focus behavior remain manually verified where automated tooling cannot establish usability.

---

# No layout shift

Pages must not materially shift when data changes from loading to populated.

This is especially important for:

- dashboards;
- tables;
- forms;
- insurance requests;
- claims;
- collections;
- governance screens.

---

# Responsive verification

IBMS pages must eventually be verified at:

- mobile breakpoint;
- tablet breakpoint where applicable;
- desktop breakpoint.

Exact breakpoint values are **TBD** until the design system is finalized.

---

# Authentication and authorization

Any change touching authentication or authorization must verify:

- successful authentication;
- invalid credentials;
- password policy;
- session handling;
- role-based access;
- permission denial;
- server-side authorization.

Hiding an action in the frontend is not authorization.

The backend must independently reject unauthorized operations.

---

# RBAC

Changes to roles or permissions must verify:

```text
User
  ↓
Role
  ↓
Permission
  ↓
Action