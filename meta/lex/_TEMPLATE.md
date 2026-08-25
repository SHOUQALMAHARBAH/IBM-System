# Lex: <Name>

**Enforcement level: mandatory — no exceptions.**

> Delete this quote block before committing.
> If you cannot fill in "How it is enforced" below, this is not a lex. Move it to `meta/guides/`.

## Rule

<One paragraph. Imperative voice. No hedging, no "should generally", no "where possible". If the rule has legitimate exceptions, they belong in "What does NOT trigger this rule" — not in softening language here.>

## What triggers this rule

- <Specific, checkable condition. A path pattern, a file type, a command, a code shape.>
- <Another.>

## What does NOT trigger this rule

- <Specific exclusion.>
- <Another.>

> This section is what stops rule creep. Without it, every lex expands to cover every case anyone can imagine, and people stop reading.

## How it is enforced

<One of:>
- **Hook:** `.claude/hooks/<name>.sh` — blocks on `<trigger>`.
- **Review gate:** `@<agent>` must review any PR touching `<paths>`.
- **CI check:** `<job name>` in `<workflow file>`.

## Rationale

<Two or three sentences. What went wrong that made this necessary. Rules with a remembered incident behind them survive; rules that appeared from nowhere get argued with.>
