# Lex: Brain Freshness

**Enforcement level: mandatory — no exceptions.**

## Rule

At the start of every session — in this repo or in any service repo — sync the brain before doing work.

```bash
git fetch origin main
git rev-list --left-right --count HEAD...origin/main   # ahead behind
```

Pull **only if** all three hold: behind origin, working tree clean, on `main`.

```bash
git pull --rebase origin main
```

If the tree is dirty or you are on a feature branch: **fetch and notify the developer. Do not auto-pull.**

Then re-read `CLAUDE.md` § What's New.

## What triggers this rule

- Every session start
- Every time you return to work after more than a day away
- Before opening a PR in any service repo

## What does NOT trigger this rule

- Mid-session, after an initial sync
- Read-only exploration where no work will be committed

## How it is enforced

**Hook:** `SessionStart` hook prints the ahead/behind count. **Review gate:** a reviewer citing a rule the author demonstrably could not have seen must check freshness before recording the finding.

## Rationale

A stale brain means a developer gets blocked by a rule they never saw. That is worse than having no rule, because it trains people to treat the reviewer as noise. Staleness does not degrade the brain gracefully — it discredits it.

The auto-pull guard exists because losing someone's uncommitted work once costs you their trust in the tooling permanently.
