# Lex: Money Arithmetic (JOD)

**Enforcement level: mandatory — no exceptions.**

## Rule

All monetary values — premium, tax, fees, commission, deductible, sum insured, claim estimate/approved/settled amounts, refunds — use a fixed-point/decimal type. Never a binary float, never the language's naked `round()`. Quantize to 3 decimal places (JOD's minor unit is the fils, 1/1000 JOD — not 2 decimal places as in most currencies) using a rounding mode fixed once for the whole codebase, e.g. `ROUND_HALF_UP`.

## What triggers this rule

- Any arithmetic on Premium, Commission, Claim, Settlement, Refund, or CommissionReversal amounts (Part 3.6, 3.5, 3.7 of `IBMS_Full_Scope_Context_Document.docx`)
- Commission rate application from the governed rate table (Motor 12%, Medical 10%, Property 15%, Life 20% — illustrative rates per Part 3.6)
- Proration, VAT/tax, and Loss Ratio (`Claims ÷ Premium`) calculations
- Parsing amounts received from an insurer statement, webhook, or uploaded document — they may arrive as strings or in a different currency; keep them as strings/decimals until converted, never via float
- Reconciliation variance calculations (Part 3.6: a mismatch must be raised as an exception with the exact variance amount, never silently written off or rounded away)

## What does NOT trigger this rule

- Display-only formatting in a UI layer — a formatted string for render is fine
- Percentages and ratios that never become a stored amount (e.g., an Insurer Performance Score)
- Test fixtures asserting on already-computed values

## How it is enforced

**Hook:** `.claude/hooks/enforce-money-decimal.sh` — `PreToolUse` on `Write|Edit`, exits 2 when a diff introduces `float(` or a bare `round(` adjacent to a money-shaped identifier (`premium`, `commission`, `claim`, `settlement`, `refund`, `invoice`, `deductible`, `sum_insured`). The keyword list is deliberately broad and language-agnostic for now — **tune it to the chosen language/stack the day the first engineering repo exists**, this is a starting point, not a finished linter.

**Review gate:** any PR touching premium, commission, or claim calculation code requires `@code-reviewer`.

## Rationale

Part 3.6 of the context document states plainly that a reconciliation mismatch (e.g., insurer statement shows JOD 100,000 collected, broker records show JOD 95,000) must be raised as an exception "never silently written off." A float-based ledger produces exactly that kind of silent drift — a JOD 0.001 rounding error compounded across thousands of policy transactions is indistinguishable from a real reconciliation problem, and undermines the one control (Part 3.6 Controls) that exists to catch client-funds commingling. JOD also has three decimal places (fils), which is the single most common place a generic two-decimal money library gets this currency wrong.
