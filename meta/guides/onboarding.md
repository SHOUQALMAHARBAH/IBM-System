# Onboarding

**Advisory, not enforced.** Rules live in `meta/lex/`. This is the path through the first week.

## Day 1

1. Clone this repo and run `bash scripts/brain-setup.sh`.
2. Read `CLAUDE.md` top to bottom. It is the map.
3. Read every file in `meta/lex/`. There should be few enough that this takes under an hour. If it doesn't, the lex directory has grown past what a human can hold, and that is a bug — say so.
4. Open your agent in this workspace and ask it something only the brain knows. If it can't answer, loading is broken. Report it before doing anything else.

## Week 1

- Read the `meta/context/` file for whichever service you're starting in — before your first ticket, not during.
- Take a small real ticket. Work it with the brain loaded.
- **Write down every question you had to ask a human.** Each one is a gap. Turning those into files is your first contribution, and it is genuinely the most valuable thing a new joiner produces — you can still see what a senior has stopped noticing they know.

## Where things are

| I need... | Go to |
|---|---|
| To know if something will get rejected | `meta/lex/` |
| To know how an area works | `meta/context/` |
| To know why a decision was made | `meta/designs/` |
| A ticket or PR format | `meta/templates/` |

## Asking for help

Ask. Then write down the answer in `meta/context/` so nobody has to ask again. The second half is not optional — it is the whole point of the repo.
