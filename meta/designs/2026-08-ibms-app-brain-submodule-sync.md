# Design: `ibms-app` consumes `ibms-brain` via git submodule

**Status:** accepted · **Date:** 2026-08-25 · **Author:** shouq · **Service:** ibms-brain ↔ ibms-app sync

## Context

`meta/designs/2026-08-ibms-app-stack-and-repo-split.md` created `ibms-app` as a sibling
repo and explicitly left open how it would actually get `ibms-brain`'s content: "There is
currently no automated sync between the two repos (no submodule, no copy script) — that
mechanism is undecided... should not be invented without its own design note." Today
`ibms-app` got a real GitHub remote
(`https://github.com/SHOUQALMAHARBAH/IBMS-APP.git`), and the user asked for the two repos
to "talk to each other when you build the system" — i.e. building inside `ibms-app`
should actually have `ibms-brain`'s rules available, not just a README pointer telling a
human to go open a second folder.

## Decision

`ibms-app` vendors `ibms-brain` as a **git submodule** at `ibms-app/ibms-brain/`, pinned
to a specific commit (not auto-tracking `main`). `ibms-app/CLAUDE.md` imports it on line
1 (`@ibms-brain/CLAUDE.md`), the same pattern `ibms-brain/CLAUDE.md` already uses for
`@AGENTS.md` — so any Claude Code session opened in `ibms-app` loads the full brain
(`meta/lex/`, `meta/context/`, `meta/designs/`) automatically, transitively, with no
manual step. `ibms-app`'s CI (`actions/checkout@v4` with `submodules: recursive`) and
README document the same clone step for humans. Both GitHub repos are public, so no
deploy-key/PAT setup is needed for the submodule to resolve in CI or on Vercel.

The submodule is deliberately **pinned, not floating**: `ibms-brain` changing on `main`
does not silently change what `ibms-app` sees mid-build. Pulling in newer rules is an
explicit `cd ibms-brain && git pull && cd .. && git add ibms-brain && git commit` — the
same discipline as bumping any other dependency.

## Alternatives considered

| Option | Why it lost |
|---|---|
| Keep the "open both folders" README note (status quo) | This is exactly what the user asked to fix — it depends on a human remembering to do it, and gives a fresh `ibms-app` clone (or CI, or Vercel) zero access to the brain at all. Doesn't scale past this one machine. |
| Copy-script (`brain-setup.sh`-style rsync/copy of `meta/` into `ibms-app` on a schedule or via a hook) | Produces a second, driftable copy of content whose canonical home is `ibms-brain` — exactly the failure mode `meta/designs/2026-08-pcms-source-of-truth.md` already rejected for a different pair of documents (independently-maintained copies drift the moment one is updated). A submodule is a pointer, not a copy. |
| npm package (publish `ibms-brain`'s `meta/` as a versioned package `ibms-app` depends on) | `meta/` is prose for humans and agents, not code with an API — packaging it adds registry/publish-pipeline overhead (npm registry choice, versioning scheme, publish CI) to solve a problem submodules solve for free. Revisit only if `ibms-brain` content needs to be consumed by more than one downstream repo in a way that outgrows submodules. |
| Floating submodule tracking `main` (`git submodule update --remote` on every CI run) | Makes `ibms-app`'s build depend on `ibms-brain`'s latest commit at build time — a brain-repo typo or in-progress edit could break `ibms-app`'s CI with no corresponding `ibms-app` change to explain why. Pinning trades a little staleness for reproducibility, which is the right trade for a compliance-rules dependency. |

## Consequences

**Accepted cost:** `ibms-app`'s `ibms-brain/` pin goes stale unless someone deliberately
updates it — a new PDPL rule landing in `ibms-brain` does not reach `ibms-app` until that
sync commit happens. This is the same trade-off as any pinned dependency; the fix is
process (update the pin as part of picking up a new compliance requirement), not
tooling.

**Revisit if:** a second engineering repo needs `ibms-brain` too (still fine with
submodules — nothing here is `ibms-app`-specific) or the update-the-pin step turns out to
get skipped in practice, at which point a CI check that fails when the submodule pin is
more than N days/commits behind `ibms-brain`'s `main` would be the next step, not a
floating submodule.
