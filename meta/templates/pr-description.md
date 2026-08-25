# PR Description Template

```markdown
## What

<One paragraph. What changed, in behaviour terms — not a file list. The reviewer can read the diff; they cannot read your intent.>

## Why

<Ticket link. The problem this solves. If it's not obvious from the ticket, say it here.>

## How

<The approach, and any non-obvious decision. If you considered another approach and rejected it, one line on why — this is what stops the reviewer suggesting the thing you already ruled out.>

## Testing

- [ ] <What you ran>
- [ ] <What you verified manually>
- [ ] <What you deliberately did not test, and why>

## Risk

**Blast radius:** <what breaks if this is wrong>
**Rollback:** <how to undo>

## Rules

- [ ] Read the relevant `meta/lex/` files
- [ ] Updated `meta/context/` if behaviour documented there changed
- [ ] `CLAUDE.md` / `README.md` updated if developer-facing (see `workspace-updates.md`)
```
