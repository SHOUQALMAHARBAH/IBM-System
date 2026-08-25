# Lex: Definition of Done

**Enforcement level: mandatory — no exceptions.**

## Rule

A PR may not be pushed until every gate in `meta/context/verification-contract.md` applicable to the changed paths has been run, and its output pasted into the PR description. The agent's assurance that something works is not evidence.

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

**Hook:** `.claude/hooks/enforce-evidence.sh` — `PreToolUse` on Bash, exit 2 on `git push` when `artifacts/<sha>/gates.json` is missing or contains a failing gate. Works unchanged today: run `bash scripts/verify.sh` before pushing, even though most of its gates currently record `skip` rather than `pass` — see `meta/context/verification-contract.md` for why that is the honest state, not a shortcut.

**CI:** `ibms-app/.github/workflows/ci.yml` exists (`test` job: migrate deploy, lint, typecheck, build, unit tests, API e2e, Playwright + axe-core e2e; `docker` job: builds the `api`/`web` images). It does not yet enforce *this* rule itself — no step checks for `artifacts/<sha>/gates.json` or blocks a PR that's missing evidence. That gap is next; until it's closed, evidence-pasting is enforced by review, not by CI.

## Rationale

An agent that has written code is strongly inclined to report success. This is not dishonesty — it has no way to distinguish "I wrote plausible code" from "I verified it runs" unless verification is a required, checkable step. This rule makes the distinction mechanical, and it holds even in a pre-code repo: the "code" here is the brain's own rules and structure, and `brain-doctor.sh` is that verification.
