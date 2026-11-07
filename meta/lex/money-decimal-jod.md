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

**Hook:** `.claude/hooks/enforce-money-decimal.sh` — `PreToolUse` on `Write|Edit`, exits 2 when a diff introduces `float(` or a bare `round(` adjacent to a money-shaped identifier. **The word list has ONE home: `MONEY_WORDS` in `.claude/hooks/money_scan.py`.** It is not restated here, because restating it is what produced the defect below.

**Corrected 2026-11-07 — THIS SECTION CONTRADICTED § Rule ABOVE IT, AND THE HOOK FOLLOWED THIS ONE.** § Rule names *"premium, **tax**, **fees**, commission, deductible, sum insured, claim estimate/approved/settled amounts, refunds"*. This paragraph then listed eight words and **dropped `tax` and `fees`** — and the hook's pattern matched this paragraph rather than the rule, so for as long as both have existed, float arithmetic on a tax or a fee was permitted by the guard that exists to forbid it. Both are money this system computes: `ibms-app`'s invoice DTO carries a required `taxAmount` and an optional `feesAmount`, and a real defect in exactly that pair was fixed in its module 0-c batch 6. Two statements of one list in one file is the drift this repository keeps paying for; there is now one list, in the scanner.

**The scan TOKENISES rather than greps**, so a comment or a string literal naming the forbidden shape is read as the prose it is. Words match as **identifier components**, so `tax` catches `taxAmount` and `tax_amount` and no longer catches `taxonomy`. Run `python .claude/hooks/money_scan.py --self-test` for the proof — 15 planted cases, four of which are the string-literal shapes that broke a figure in `ibms-app`.

**The operator list is still `float(` and a bare `round(`, and widening it is a decision nobody has taken.** The shapes that carry this risk in a TypeScript/Prisma stack are `parseFloat`, `Number(`, `Math.round(` and `toFixed(`. **Measured 2026-11-07 against `ibms-app`: the corrected word list blocks 0 of 1,712 tracked `.ts`/`.tsx` files, and a widened operator list would block 14** — because § What does NOT trigger this rule exempts display-only formatting, and that repo's `formatMoney` passes a money string through `Number()` at 92 product call sites. So widening would refuse correct work on a correct tree. The figure is recorded; the change is not made.

The keyword list was written broad and language-agnostic before any engineering repo existed. **That day has come** — `ibms-app` is the repo, and the honest position is that this hook is now the fast feedback at the keystroke while the real gates are two specs in that repo that run in CI and can see the whole tree: `apps/api/src/common/float-money.inventory.spec.ts` (every `Float`/`Double` column declared with a reason — Part G checklist item 5) and `money-fields.inventory.spec.ts` (every money `Decimal` is `Decimal(18,3)`). **Where this hook and those specs disagree, the specs win.**

**Review gate:** any PR touching premium, commission, or claim calculation code requires `@code-reviewer`.

## Rationale

Part 3.6 of the context document states plainly that a reconciliation mismatch (e.g., insurer statement shows JOD 100,000 collected, broker records show JOD 95,000) must be raised as an exception "never silently written off." A float-based ledger produces exactly that kind of silent drift — a JOD 0.001 rounding error compounded across thousands of policy transactions is indistinguishable from a real reconciliation problem, and undermines the one control (Part 3.6 Controls) that exists to catch client-funds commingling. JOD also has three decimal places (fils), which is the single most common place a generic two-decimal money library gets this currency wrong.
