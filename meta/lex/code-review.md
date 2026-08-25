# Lex: Code Review

**Enforcement level: mandatory — no exceptions.**

## Rule

Every review finding must state a **severity**, a **location**, and a **cited rule or reason**. Findings without all three are opinions and must be marked as such.

**Severity levels:**

| Level | Meaning | Blocks merge |
|---|---|---|
| `BLOCKER` | Correctness, security, or data-loss risk | Yes |
| `MAJOR` | Violates a `meta/lex/` rule | Yes |
| `MINOR` | Maintainability or consistency concern | No |
| `NIT` | Style preference, explicitly optional | No |

A `MAJOR` must cite the lex file and section. If no lex covers it, it is at most a `MINOR` — **and that is a signal a lex is missing.** File it.

## What triggers this rule

- Every PR review, human or agent
- Any review comment intended to block a merge

## What does NOT trigger this rule

- Questions asked for understanding rather than change
- Praise and acknowledgement
- Draft PRs explicitly marked as work in progress

## How it is enforced

**Review gate:** `@code-reviewer` outputs in this format by definition. **Culture:** a `MAJOR` without a citation may be downgraded to `NIT` by the author, and that is a legitimate move — it keeps the rule honest.

## Rationale

Uncited blocking findings are how review becomes about seniority instead of standards. Requiring a citation forces the reviewer to check whether the rule actually exists, and every time it doesn't, that gap becomes a lex.
