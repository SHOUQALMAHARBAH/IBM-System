# Lex: Definition of Done

**Enforcement level: mandatory — no exceptions.**

## Rule

A PR may not be pushed until every gate in `meta/context/verification-contract.md` applicable to the changed paths has been run, and its output pasted into the PR description. The agent's assurance that something works is not evidence.

## Doc currency is part of done, not a hook that fires later

**A PR is not done while `CLAUDE.md` or `README.md` states something the PR has made false.**

This is a gate, not a courtesy. Those two files are the first thing a newcomer reads and the
first thing an agent loads, so a false claim there is the most expensive kind of stale
documentation — it is believed, and it is believed before anyone looks at the code.

Measured, 2026-09-22: across a 30-commit branch, both files still said "Insurer CRUD remains
specification-only and is deliberately deferred" after insurer CRUD had shipped. Nobody noticed;
`.claude/hooks/enforce-workspace-updates.sh` caught it on the last commit of the branch. **The
hook working is not the same as the rule working** — a hook that fires at the end lets thirty
commits accumulate a false claim, and it fires on the person who happens to stage the last
developer-facing file rather than on the one who made the statement false.

So the check belongs in the same pass as the gates:

1. **Does this change make any sentence in `CLAUDE.md` or `README.md` false?** Grep the
   feature's own nouns — a claim goes stale on the words it names, not on the files it touches.
   Statements of the form "X is not built", "X remains specification-only", "X is deferred" are
   the ones that rot, because they are true when written and nobody revisits them.
2. **Correct rather than delete.** A deferral usually had a REASON, and the reason often
   survives the deferral — the insurer codes above were deferred to protect a strict-subset
   property that is still protected, now by an explicit list instead. Deleting the sentence
   would have lost that.
3. **A dated `## What's New` row** per `meta/lex/workspace-updates.md`, in the same commit as
   the change it describes — not batched at the end of a branch, where it becomes one row
   summarising work nobody can now separate.

## Rewriting published history: the tree is the test

`git push --force` is acceptable **only when the TREE IS UNCHANGED** — a commit-message fix, a
rebase that alters no content. Verify it rather than assume it:

```bash
git diff --stat HEAD origin/<branch>    # must print nothing
git push --force-with-lease             # never bare --force
```

**If the tree changes, add a commit instead.** The reason is not etiquette: **CI validated a
tree.** Rewriting that tree means the green you are standing on no longer describes what is
there, and the PR's checks now refer to content that no longer exists. A new commit gets its own
run and its own green.

That single test — *did the tree change?* — settles every case without judgement. Disclose the
force-push either way; it is not an action to perform quietly on a branch anyone else can pull.

## What triggers this rule

The platform's module structure was decided 2026-08-25 — `ibms-app` (see
`meta/designs/2026-08-ibms-app-stack-and-repo-split.md`), a Next.js + NestJS + Prisma
Turborepo monorepo. These path globs are relative to that repo, not this one:

- Any PR touching a service's source code:
  - `apps/web/**` — Next.js frontend
  - `apps/api/**` — NestJS backend
  - `packages/db/**` — Prisma schema, migrations, generated client (`@ibms/db`)
- Any new or modified workflow, approval screen, or compliance-facing report:
  - `apps/web/features/**` — frontend feature UI (workflow/approval/report screens land here)
  - `apps/api/src/modules/**` — backend feature modules (workflow/approval business logic)
  - `apps/api/src/controllers/**`, `apps/api/src/services/**` — until a concern is promoted into its own module under `modules/`
  - No workflow/approval/report feature exists yet — these four are still empty scaffolding (see `ibms-app/README.md` § Layout). The globs are registered now so this rule fires the moment one lands, instead of being retrofitted after the fact.
- Any change to migrations, CI, containers, or deploy configuration:
  - `packages/db/prisma/migrations/**` — migrations
  - `.github/workflows/**` — CI
  - `docker-compose.yml`, `apps/*/Dockerfile` — containers
  - deploy configuration — no glob yet; deployment platform is still **TBD** (`ibms-app/README.md` § Deployment). Add one the day that's decided.
- Any change to `meta/lex/`, `meta/context/`, or `.claude/hooks/` in *this* brain repo — the equivalent gate here is `bash scripts/brain-doctor.sh`

## What does NOT trigger this rule

- Changes confined to `meta/guides/`, README files, or comments
- Draft PRs explicitly marked WIP
- Pure research/exploration commits with no shipped change

## How it is enforced

**Hook:** `.claude/hooks/enforce-evidence.sh` — `PreToolUse` on Bash, exit 2 on `git push` when `artifacts/<sha>/gates.json` is missing or contains a failing gate. `ibms-app/scripts/verify.sh` now runs every gate in `meta/context/verification-contract.md` § Backend/frontend gate commands for real — typecheck, lint, unit tests, security, `db:validate`, migrations (deploy + drift check), integration, contract, smoke, accessibility, e2e, build — against `db-test`, and prints a pass/fail summary for each. It does not yet write `artifacts/<sha>/gates.json` itself, so the hook still has nothing to read; that file still needs to exist for `git push` to pass the hook. Note also that this hook is defined in this brain repo but is not yet mirrored into `ibms-app/.claude/hooks/` — until it is, it isn't active in `ibms-app` sessions at all.

**CI:** `ibms-app/.github/workflows/ci.yml` runs on every pull request and on push to
`main`, split into three jobs: `frontend` (typecheck, lint, unit/component tests,
accessibility — `test:a11y`, axe-core — e2e via Playwright, build; uploads the Playwright
report as a CI artifact), `backend` (typecheck, lint, unit tests, security tests —
`npm run test:security`, `npm audit --audit-level=high` — against an ephemeral Postgres 18
service container: `db:validate`, `db:migrate:deploy`, `db:migrate:status` drift check,
integration tests via `test:e2e`, contract tests via `test:contract`, smoke tests via
`bash scripts/smoke.sh api`, build), and `docker` (matrix build of the `api`/`web`
Dockerfile images, no push — deployment target still TBD). It does not yet enforce *this*
rule itself — no step checks for `artifacts/<sha>/gates.json` or blocks a PR that's missing
evidence. That gap is next; until it's closed, evidence-pasting is enforced by review, not
by CI.

## Rationale

An agent that has written code is strongly inclined to report success. This is not dishonesty — it has no way to distinguish "I wrote plausible code" from "I verified it runs" unless verification is a required, checkable step. This rule makes the distinction mechanical, and it holds even in a pre-code repo: the "code" here is the brain's own rules and structure, and `brain-doctor.sh` is that verification.
