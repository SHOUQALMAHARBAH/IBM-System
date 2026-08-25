# Design: First engineering repo (`ibms-app`) — repo split and stack

**Status:** accepted · **Date:** 2026-08-25 · **Author:** shouq · **Service:** repo topology / stack

## Context

`ibms-brain` was seeded before any application code existed (see `CLAUDE.md` § What
this brain is for). `README.md` and `CLAUDE.md` both stated explicitly that no
engineering repo, stack, or service boundary had been chosen, and told agents not to
invent one. That changed today: the user specified a concrete stack (Next.js, NestJS,
PostgreSQL/Prisma, Docker, GitHub Actions, Vercel preview; production deployment target
explicitly left TBD) and asked for the project structure and infrastructure to be
created.

Two structural questions had to be settled before any scaffolding: where the new code
lives relative to this brain, and what to do about the stack's own version drift (Prisma
released a major version — 7 — with a materially different setup than the one almost
every existing tutorial/example assumes).

## Decision

**Repo split:** `ibms-app` is a new, separate sibling repo — not a folder inside
`ibms-brain`. This matches what `README.md` already documented as the intended shape
("not a monorepo of services... this repo is what every future service repo will
inherit"). `ibms-brain` stays documentation/standards-only; `ibms-app` is the first
consumer.

**Stack, as specified, with two version calls the user left open:**

| Layer | Choice |
|---|---|
| Backend framework | NestJS (user offered it as the example; no reason to deviate) |
| Monorepo tool | npm workspaces + Turborepo (`apps/web`, `apps/api`, `packages/db`) |
| ORM version | **Prisma `6.19.3`, not the current-latest `7.x`** |
| Node version | `20.13.0`, pinned via `.nvmrc` |

**Why Prisma 6, not 7:** verified directly (not from docs alone) that `prisma@7` requires
Node ≥20.19/22.12/24 — the local dev environment runs Node `20.13.0`, which fails
Prisma 7's preinstall check outright. Prisma 7 also replaces the classic
`provider = "prisma-client-js"` generator with a mandatory `output` path, a required
driver adapter package (`@prisma/adapter-pg`), and a `prisma.config.ts` file — a much
larger surface to get right on a brand-new major version. Prisma 6.19.3 (the last 6.x
release) needs only Node ≥18.18, uses the well-documented classic client, and is not
EOL. This was verified by actually installing both in a scratch directory, not inferred.

**Docker:** both `apps/api` and `apps/web` build via `turbo prune --docker`, the
Turborepo-documented pattern for pruning a workspace to just what one app needs before
`npm install` — avoids hand-rolling which `package.json`/lockfile subset a naive
multi-stage COPY would need. `apps/web` additionally uses Next's `output: "standalone"`
for a minimal runtime image.

**CI:** GitHub Actions runs lint/typecheck/build/unit tests/API e2e (against a real
`postgres:16-alpine` service) /web e2e+axe-core on every push and PR, plus a separate job
that builds (never pushes) both Docker images to catch Dockerfile regressions. No
registry push step exists — see next point.

**Deployment target: still TBD, deliberately.** The user's instruction was explicit that
this stays undecided. Docker images are runtime-target-agnostic; nothing in CI assumes
AWS/Azure/Fly/Render/etc. Vercel is preview-only, for `apps/web`.

## Alternatives considered

| Option | Why it lost |
|---|---|
| Put `apps/`, `packages/` inside `ibms-brain` itself (single repo) | Directly contradicts what `README.md` already told every future reader ("not a monorepo of services"). Would have mixed a governance-reviewed compliance-doc history with application commit history in one git log — bad for both audiences. |
| Prisma 7 (the actual current latest) | Would have required bumping the team's Node baseline as a side effect of a docs-scaffolding task, and adopting a driver-adapter architecture with a much smaller base of examples/Stack Overflow history at the time of writing, for no benefit this project needed yet. Revisit when Node 22 LTS becomes the floor. |
| pnpm workspaces instead of npm workspaces | pnpm wasn't installed in the target environment and Corepack activation is an extra step with its own failure modes; npm ships with Node and Turborepo supports it equally well. Nothing in the user's stack list named a package manager. |
| No monorepo tool (plain npm workspaces, no Turborepo) | Works, but loses task-graph caching and the well-documented `turbo prune --docker` pattern that makes the two Dockerfiles tractable to get right. Turborepo is free, Vercel-maintained, and pairs directly with the Vercel-preview requirement already in the stack. |

## Consequences

**Accepted costs:** `ibms-app` is on a Prisma major version one behind current-latest,
and will need a deliberate upgrade (Node bump + driver-adapter migration) at some point
— tracked here, not silently inherited by whoever hits it first. There is currently no
automated sync between `ibms-brain` and `ibms-app` (no submodule, no copy script) — an
engineer or agent working in `ibms-app` has to open `ibms-brain` separately. That
sync mechanism is itself undecided and should not be invented without its own design
note.

**Revisit if:** the team moves its Node baseline to ≥20.19 (Prisma 7 becomes free to
adopt), a second engineering repo needs the same brain (the sync-mechanism gap above
becomes actively painful rather than theoretical), or a production deployment target is
chosen (update `ibms-app/README.md` § Deployment in the same change, per
`meta/lex/workspace-updates.md`).
