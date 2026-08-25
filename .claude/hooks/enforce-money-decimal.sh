#!/bin/bash
# Claude Code hook: PreToolUse (matcher: Write|Edit)
# Enforces meta/lex/money-decimal-jod.md
# Blocks float()/round() adjacent to a money-shaped identifier in new/edited content.
#
# This is a starting pattern, not a finished linter — tune the keyword list and the
# language-specific float/round syntax to the chosen stack the day an engineering
# repo exists. Until then it is a language-agnostic best-effort check.

INPUT=$(cat)

# python3 can resolve to a non-functional shim (e.g. a Windows Store
# app-execution-alias) even when a real interpreter exists under a different
# name — fall back to `python` if so.
PYTHON=python3
python3 -c "" >/dev/null 2>&1 || PYTHON=python

CONTENT=$(echo "$INPUT" | "$PYTHON" -c "
import sys, json
try:
    d = json.load(sys.stdin).get('tool_input', {})
    print(d.get('content', '') or d.get('new_string', ''))
except Exception:
    pass
" 2>/dev/null)

[ -z "$CONTENT" ] && exit 0

MONEY_WORDS='premium|commission|claim|settlement|refund|invoice|deductible|sum_insured|sumInsured'

# float(...) or round(...) on a line that also mentions a money-shaped identifier
HIT=$(echo "$CONTENT" | grep -inE "$MONEY_WORDS" | grep -iE '(float\(|[^a-zA-Z_]round\()')

if [ -n "$HIT" ]; then
  echo "" >&2
  echo "  ┌────────────────────────────────────────────────────────────────┐" >&2
  echo "  │   MONEY ARITHMETIC — BLOCKED                                   │" >&2
  echo "  │   meta/lex/money-decimal-jod.md                                │" >&2
  echo "  └────────────────────────────────────────────────────────────────┘" >&2
  echo "" >&2
  echo "  float()/round() found near a money-shaped identifier:" >&2
  echo "" >&2
  echo "$HIT" | sed 's/^/    /' >&2
  echo "" >&2
  echo "  Use a fixed-point/decimal type, quantized to 3 places (JOD fils)," >&2
  echo "  with a rounding mode fixed once for the whole codebase." >&2
  echo "" >&2
  echo "  False positive? Rename the variable away from a money-shaped name," >&2
  echo "  or this check has not yet been tuned to your stack — update this" >&2
  echo "  hook, not just this one call." >&2
  echo "" >&2
  exit 2
fi

exit 0
