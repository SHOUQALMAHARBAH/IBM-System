# Lex: Definition of Done

**Enforcement level: mandatory — no exceptions.**

## Rule

A PR may not be pushed until every gate in `meta/context/verification-contract.md` applicable to the changed paths has been run, and its output pasted into the PR description. The agent's assurance that something works is not evidence.

## What triggers this rule

- Any PR touching a service's source code, once a codebase exists
- Any new or modified workflow, approval screen, or compliance-facing report (paths not yet defined — there is no repo structure yet; this row must be filled in with real path globs the day the platform's module structure is decided, see `meta/designs/`)
- Any change to migrations, CI, containers, or deploy configuration, once those exist
- Any change to `meta/lex/`, `meta/context/`, or `.claude/hooks/` in *this* brain repo — the equivalent gate here is `bash scripts/brain-doctor.sh`

## What does NOT trigger this rule

- Changes confined to `meta/guides/`, README files, or comments
- Draft PRs explicitly marked WIP
- Pure research/exploration commits with no shipped change

## How it is enforced

**Hook:** `.claude/hooks/enforce-evidence.sh` — `PreToolUse` on Bash, exit 2 on `git push` when `artifacts/<sha>/gates.json` is missing or contains a failing gate. Works unchanged today: run `bash scripts/verify.sh` before pushing, even though most of its gates currently record `skip` rather than `pass` — see `meta/context/verification-contract.md` for why that is the honest state, not a shortcut.

**CI:** none yet — there is no CI pipeline until an engineering repo exists. Fill this in the same commit that stands up the first pipeline (see `meta/lex/workspace-updates.md`, which will require this file to be updated as part of that change).

## Rationale

An agent that has written code is strongly inclined to report success. This is not dishonesty — it has no way to distinguish "I wrote plausible code" from "I verified it runs" unless verification is a required, checkable step. This rule makes the distinction mechanical, and it holds even in a pre-code repo: the "code" here is the brain's own rules and structure, and `brain-doctor.sh` is that verification.
