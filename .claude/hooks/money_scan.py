"""
Does this edit do float arithmetic on money?

Backs `enforce-money-decimal.sh`. Enforces `meta/lex/money-decimal-jod.md`.

## What changed and why, measured in `ibms-app` on 2026-11-07

**(1) THE WORD LIST WAS NINE AND THE RULE'S OWN SENTENCE NAMES ELEVEN.** The old list was

    premium|commission|claim|settlement|refund|invoice|deductible|sum_insured|sumInsured

and `tax` and `fees` were absent. Both are money this system does arithmetic on — the invoice
DTO carries `taxAmount` (required) and `feesAmount` (optional, documented default 0), and a
defect in exactly that pair was fixed in module 0-c batch 6 row 73.

**The sharper finding is that the rule contradicts ITSELF, and the hook was faithful to the
wrong half.** `money-decimal-jod.md` § Rule names *"premium, tax, fees, commission, deductible,
sum insured, claim estimate/approved/settled amounts, refunds"*. Its own § How it is enforced
then restates the list as eight and **drops `tax` and `fees`** — and the hook matched the
restatement. So the chart's "the text has eight and the hook nine" was right about the
numbers and wrong about which text: § Rule has eleven concepts, § How it is enforced has
eight, and they are in the same file. Both are corrected there; this module is the one list.

**(2) IT READ RAW TEXT.** `grep -inE "$MONEY_WORDS" | grep -iE 'float\\(|round\\('` matched a
comment or a string. `"premium rounded to the fils"` in a message is prose; `round(premium)` is
the defect. Everything goes through `code_text.blank()` now — see that module for what a regex
comment-stripper did to a figure here.

**(3) `tax` MATCHED `taxonomy` AND `fee` MATCHED `feedback`.** The old list was substrings with
no boundaries at all. Words are matched as IDENTIFIER COMPONENTS now: `tax` hits `tax`,
`taxAmount` and `tax_amount` and misses `taxonomy`, because the character after it is a
lowercase letter.

## What is deliberately NOT widened, and it is the owner's call

The operator list is still `float(` and a bare `round(`. The shapes that actually carry this
risk in a TypeScript/Prisma stack are `parseFloat`, `Number(`, `Math.round(` and `toFixed(` —
and **widening to them would refuse correct work today**, because `money-decimal-jod.md`
§ What does NOT trigger this rule exempts *"display-only formatting in a UI layer"* and
`ibms-app`'s own `formatMoney` passes a money string through `Number()` for display at
**92 product call sites across 20 files** (measured 2026-11-07). A guard that reds a correct
tree is the failure mode this repository has already paid for twice.

So the measurement is recorded and the widening is not taken. `ibms-app` gates the real
question properly and in CI, in two places this hook cannot reach:
`apps/api/src/common/float-money.inventory.spec.ts` (every `Float`/`Double` in the schema must
be declared with a reason — Part G checklist item 5) and `money-fields.inventory.spec.ts`
(every money `Decimal` is `Decimal(18,3)`). **Where this hook and those specs disagree, the
specs win.**

Run `python money_scan.py --self-test` for the proof.
"""

from __future__ import annotations

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from code_text import blank  # noqa: E402

#: Every money concept `meta/lex/money-decimal-jod.md` § Rule names, as identifier components.
#:
#: ONE HOME. The lex's prose and this list are kept equal by hand today; if a third copy ever
#: appears, that is the drift the lex itself warns about.
MONEY_WORDS = [
    "premium",
    "tax",
    "fee",
    "fees",
    "commission",
    "claim",
    "settlement",
    "refund",
    "invoice",
    "deductible",
    "sum_insured",
    "sumInsured",
    "reversal",
]

#: A money word as an IDENTIFIER COMPONENT, never a bare substring.
#:
#: `(?<![A-Za-z])` so `reclaim` does not match `claim`; `(?![a-z])` so `taxonomy` does not
#: match `tax` while `taxAmount` and `tax_amount` both do (the next character is `A` or `_`).
#:
#: THE CASE FLAG IS SCOPED TO THE WORD, `(?i:…)`, AND NOT APPLIED TO THE PATTERN. A global
#: `re.IGNORECASE` makes `(?![a-z])` reject an UPPERCASE letter too, which broke the boundary
#: it exists to draw: `taxAmount` failed its own test because `A` matched `[a-z]`. Caught by
#: this module's own self-test on its first run — three cases, including both of the words
#: this fix was written to add.
_MONEY = re.compile(
    "|".join(rf"(?<![A-Za-z])(?i:{re.escape(w)})(?![a-z])" for w in MONEY_WORDS)
)

#: Binary-float arithmetic, and a naked round. A qualified `Decimal.round` is fine — only a
#: BARE `round(` is the language's own.
_FLOAT_OP = re.compile(r"\bfloat\s*\(|(?<![A-Za-z_.])round\s*\(", re.IGNORECASE)


def findings(file_path: str, content: str) -> list[str]:
    """Every line doing float arithmetic on a money-shaped identifier, as `line: text`."""
    ext = os.path.splitext(file_path)[1] or ".ts"
    code = blank(content, ext)
    raw = content.splitlines()
    hits = []
    for i, line in enumerate(code.splitlines(), start=1):
        if _FLOAT_OP.search(line) and _MONEY.search(line):
            hits.append(f"{i}: {raw[i - 1].strip() if i - 1 < len(raw) else ''}")
    return hits


# ─────────────────────────────────────────────────────────────────────────────────
# Self-test — planted inputs. Cases 6-9 are the string-literal proof the batch rule requires
# of every guard here that reads source.
# ─────────────────────────────────────────────────────────────────────────────────

_CASES = [
    ("float on a premium", "a.ts", "const p = float(premium);", True),
    ("bare round on a commission", "a.ts", "const c = round(commissionAmount);", True),
    # ── the two words that were missing, which is the whole point of (c) ─────────
    ("tax — absent from the old list", "a.ts", "const t = round(taxAmount);", True),
    ("fees — absent from the old list", "a.ts", "const f = float(feesAmount);", True),
    ("snake-case tax", "a.py", "t = round(tax_amount)", True),
    # ── the string-literal and comment proofs ───────────────────────────────────
    (
        "a comment naming the forbidden shape is not an instance of it",
        "a.ts",
        "// never round(premium) — use quantizeMoney\nconst ok = 1;",
        False,
    ),
    (
        "prose in a string literal",
        "a.ts",
        'throw new Error("do not call round(premium) here");',
        False,
    ),
    (
        "a URL in a string does not break the scan",
        "a.ts",
        'const u = "http://x/premium"; const v = quantizeMoney(premium);',
        False,
    ),
    (
        "a block comment explaining a removed call",
        "a.ts",
        "/* was: round(settlementAmount) */\nconst ok = 1;",
        False,
    ),
    # ── the boundary cases the old substring list got wrong ─────────────────────
    ("taxonomy is not tax", "a.ts", "const x = round(taxonomyDepth);", False),
    ("feedback is not a fee", "a.ts", "const x = round(feedbackScore);", False),
    ("reclaim is not claim", "a.ts", "const x = round(reclaimedSpace);", False),
    # ── the correct patterns, which must NOT be refused ─────────────────────────
    (
        "the house money helper is the point of the rule",
        "a.ts",
        "const total = quantizeMoney(addMoney(premium, taxAmount));",
        False,
    ),
    (
        "a QUALIFIED round is a Decimal's own, not the language's",
        "a.ts",
        "const p = premium.round(3);",
        False,
    ),
    (
        "a float call with no money anywhere near it",
        "a.ts",
        "const ratio = float(pixelDensity);",
        False,
    ),
]


def _self_test() -> int:
    failures = []
    for name, path, src, expect in _CASES:
        got = bool(findings(path, src))
        if got != expect:
            failures.append(
                f"{name}: expected {'BLOCK' if expect else 'ALLOW'}, got {'BLOCK' if got else 'ALLOW'}"
            )
    for f in failures:
        print(f"  FAIL  {f}")
    print(
        f"\n  money_scan self-test: {len(_CASES) - len(failures)}/{len(_CASES)} cases correct,"
        f" {len(failures)} failure(s)"
    )
    return 1 if failures else 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        raise SystemExit(_self_test())
    path = sys.argv[1] if len(sys.argv) > 1 else ""
    for hit in findings(path, sys.stdin.read()):
        print(hit)
