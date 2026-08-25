# Lex: Workspace Update Tracking

**Enforcement level: mandatory — no exceptions.**

## Rule

Every change to the brain that a developer would need to know about — new agent, new hook, new rule, behaviour change, setup requirement, breaking change — must be reflected in **all of the following, in the same commit**:

1. **`CLAUDE.md` § What's New** — one dated row: what changed, whether action is required. Drop the oldest row when the table exceeds 5 entries.
2. **`README.md`** — update any affected section.
3. **`CLAUDE.md` body** — update the relevant section (repo map, agents table, commands, rules table).

## What triggers this rule

- New agent, hook, slash command, or tool
- New or changed file in `meta/lex/` or `meta/guides/`
- Changes to `.claude/settings.json` or MCP configuration
- Changes to setup or onboarding steps
- Breaking changes to existing behaviour

## What does NOT trigger this rule

- Content added inside `meta/designs/` or `meta/context/` (internal artefacts, not developer-facing mechanics)
- Bug fixes and internal refactors with no developer-facing impact
- Typo and formatting fixes
- Template content changes (the templates themselves, not their existence)

## How it is enforced

**Hook:** `.claude/hooks/enforce-workspace-updates.sh` — `PreToolUse` on `Bash`. Inspects `git commit` commands, checks staged files against the trigger list, exits 1 with instructions if `CLAUDE.md` and `README.md` are not staged alongside.

## Rationale

This is the rule that stops the brain rotting. Without it, `CLAUDE.md` — the file loaded into every single session — quietly becomes the least accurate document in the repo, and everything downstream inherits its staleness.
