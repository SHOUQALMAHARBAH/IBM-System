# meta/ — Platform Intelligence Layer

`meta/` is the shared brain. Every developer who works in this repo gets this context automatically when their agent loads the workspace.

It is not documentation for documentation's sake — it is the ground truth that agents, tools, and developers use to make decisions consistently.

**The test for every file here:** *does an agent or a new hire make a different decision because this file exists?* If not, delete it.

## Structure

```
meta/
├── lex/         Mandatory rules. Every file has an enforcement mechanism.
├── context/     How things work here — models, contracts, vocabulary, runbooks.
├── designs/     Decisions with the reasoning preserved.
├── agents/      Agent definitions (source of truth).
├── guides/      Advisory. Onboarding, setup, contributing.
└── templates/   PR, ticket, and doc templates.
```

Four of these are load-bearing: `lex/`, `context/`, `designs/`, `agents/`. The other two are convenience.

**Do not add a seventh folder until a specific pain has happened twice.** Candidates that earn their place over time: `runbooks/` (same incident twice), `research/` (findings got lost and work was redone), `rca/` (post-incident writeups evaporating in Slack), `plans/`, `memory/`.

## How it gets used

**By agents.** Definitions in `meta/agents/` are mirrored to `.claude/agents/` and loaded automatically. Lex files are loaded via `CLAUDE.md`.

**By developers.**
- Starting a task? Read the relevant `context/` file first.
- Wondering if something will get rejected? `lex/`.
- About to change a decision that looks arbitrary? Check `designs/` — the reasoning is probably there.
- Writing a ticket or PR? `templates/`.

**By the reviewer.** `lex/` is the enforcement standard. Findings cite the lex file and section.

## Contribution rules

1. **`lex/` requires an enforcement mechanism.** A rule with an empty "How it is enforced" section is a suggestion. Suggestions go in `guides/`.
2. **Agent definitions are source-of-truth in `meta/agents/`.** The `.claude/agents/` mirror is automated by a hook. Never hand-copy — that is exactly how the two copies drift, and the stale one is the one that loads.
3. **Designs go in `designs/<service>/`** with a descriptive filename.
4. **Never create an empty folder.** A `.gitkeep` graveyard makes the brain look abandoned.
5. **One canonical location for cross-links.** If designs live in Notion, link Notion everywhere. If they live here, link here. Never both.
6. **Files come from observed gaps.** When an agent asks something this repo should have answered, write that. Do not write speculatively.
