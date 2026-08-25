#!/bin/bash
# Claude Code hook: PreToolUse (matcher: Write|Edit)
# Enforces meta/lex/sensitive-data-handling.md
# Blocks logging calls that interpolate a Highly Confidential field (PRIV-STD-02 §6).

INPUT=$(cat)

CONTENT=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin).get('tool_input', {})
    print(d.get('content', '') or d.get('new_string', ''))
except Exception:
    pass
" 2>/dev/null)

[ -z "$CONTENT" ] && exit 0

LOG_CALL='(logger\.|console\.(log|error|warn|info)|print\(|logging\.)'
SENSITIVE_FIELD='national_id|nationalId|bank_account|bankAccount|card_number|cardNumber|\bcvv\b|medical|health_report|healthReport|clinical'

HIT=$(echo "$CONTENT" | grep -inE "$LOG_CALL" | grep -iE "$SENSITIVE_FIELD")

if [ -n "$HIT" ]; then
  echo "" >&2
  echo "  ┌────────────────────────────────────────────────────────────────┐" >&2
  echo "  │   SENSITIVE DATA IN LOG — BLOCKED                              │" >&2
  echo "  │   meta/lex/sensitive-data-handling.md                         │" >&2
  echo "  └────────────────────────────────────────────────────────────────┘" >&2
  echo "" >&2
  echo "  A logging call appears to interpolate a Highly Confidential field:" >&2
  echo "" >&2
  echo "$HIT" | sed 's/^/    /' >&2
  echo "" >&2
  echo "  Log an identifier instead (customer.id, policy.id, claim.id)." >&2
  echo "  Per PRIV-STD-02 §6, this classification tier must never leave" >&2
  echo "  the organization unencrypted, and a log aggregator is exactly" >&2
  echo "  that kind of channel." >&2
  echo "" >&2
  exit 2
fi

exit 0
