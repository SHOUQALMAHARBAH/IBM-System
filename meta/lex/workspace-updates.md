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
- **A new owner-decision number cited in code with no file in `<repo>/docs/decision-<n>-<slug>.md` and no row in `meta/decision-index.md`.** Added 2026-11-08. This is an EXTENSION of the question this rule already asks — *what did this change just make false?* — not a twelfth law, because the index is a developer-facing document like `CLAUDE.md` and `README.md` and rots the same way. A number cited with nothing saying what it means sends the next reader to the owner, whose standing instruction is that nobody should have to come back to her. `ibms-app` gates it both ways with `npm run check:decision-index`, which also walks a multi-number citation — `decisions 32 and 33` is how decision 33 stayed out of the register for its whole life, cited nine times and never once on its own.

## What does NOT trigger this rule

- Content added inside `meta/designs/` or `meta/context/` (internal artefacts, not developer-facing mechanics)
- Bug fixes and internal refactors with no developer-facing impact
- Typo and formatting fixes
- Template content changes (the templates themselves, not their existence)

## How it is enforced

**Hook:** `.claude/hooks/enforce-workspace-updates.sh` — `PreToolUse` on `Bash`. Inspects `git commit` commands, checks staged files against the trigger list, and **exits 2** with instructions if `CLAUDE.md` and `README.md` are not staged alongside.

**Corrected 2026-11-07: this said "exits 1", and exit 1 would not have blocked anything.** Claude Code treats a hook's exit 1 as a non-blocking error and proceeds with the tool call; **only exit 2 blocks**. The script has always exited 2 — so the text documented the single most common hook bug as this guard's behaviour, in the one paragraph a reader consults to find out whether the rule is actually enforced. `scripts/brain-doctor.sh` § Hook enforcement exists specifically to catch an `exit 1` in a hook, and it was green the whole time because the defect was in the prose, not the script. **The exit code was not changed to match the sentence; the sentence was corrected to match the code.**

**The two trigger classes are not the same, and the difference is `meta/templates/`.** Any change to `.claude/{agents,hooks,commands}/`, `.claude/settings.json`, `meta/{lex,guides,agents}/` or `scripts/` triggers this rule. For `meta/templates/` **only the existence of a file triggers it** — an added, deleted or renamed template changes the mechanics a developer meets; rewording one does not, per § What does NOT trigger this rule above. The hook reads `git diff --cached --name-status` and distinguishes `A`/`D`/`R` from `M` for that path alone. **Before 2026-11-07 it treated `meta/templates/` like every other trigger**, so rewording a PR template demanded a dated `CLAUDE.md` row and a README edit — which is how a guard teaches people to route around it.

## Rationale

This is the rule that stops the brain rotting. Without it, `CLAUDE.md` — the file loaded into every single session — quietly becomes the least accurate document in the repo, and everything downstream inherits its staleness.
