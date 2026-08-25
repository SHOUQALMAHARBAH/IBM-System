#!/bin/bash
# Claude Code hook: PreToolUse (matcher: Write|Edit)
# Enforces meta/lex/workflow-state-transitions.md
# Blocks direct assignment to a `.status` field outside a transition/workflow function.

INPUT=$(cat)

# python3 can resolve to a non-functional shim (e.g. a Windows Store
# app-execution-alias) even when a real interpreter exists under a different
# name — fall back to `python` if so.
PYTHON=python3
python3 -c "" >/dev/null 2>&1 || PYTHON=python

FILE_PATH=$(echo "$INPUT" | "$PYTHON" -c "
import sys, json
try:
    print(json.load(sys.stdin).get('tool_input', {}).get('file_path', ''))
except Exception:
    pass
" 2>/dev/null)

CONTENT=$(echo "$INPUT" | "$PYTHON" -c "
import sys, json
try:
    d = json.load(sys.stdin).get('tool_input', {})
    print(d.get('content', '') or d.get('new_string', ''))
except Exception:
    pass
" 2>/dev/null)

[ -z "$CONTENT" ] && exit 0

# Exempt files whose name signals they ARE the transition/workflow implementation.
echo "$FILE_PATH" | grep -qiE 'transition|workflow|state_machine|stateMachine' && exit 0

HIT=$(echo "$CONTENT" | grep -nE "\.status\s*=[^=]|\['status'\]\s*=[^=]|\[\"status\"\]\s*=[^=]")

if [ -n "$HIT" ]; then
  echo "" >&2
  echo "  ┌────────────────────────────────────────────────────────────────┐" >&2
  echo "  │   WORKFLOW STATE TRANSITION — BLOCKED                          │" >&2
  echo "  │   meta/lex/workflow-state-transitions.md                      │" >&2
  echo "  └────────────────────────────────────────────────────────────────┘" >&2
  echo "" >&2
  echo "  Direct status assignment found outside a transition/workflow file:" >&2
  echo "" >&2
  echo "$HIT" | sed 's/^/    /' >&2
  echo "" >&2
  echo "  Route this through the entity's transition() function instead —" >&2
  echo "  direct assignment skips the audit row and any SLA timer the" >&2
  echo "  transition is supposed to start (see PRIV-SRS-01 §7)." >&2
  echo "" >&2
  exit 2
fi

exit 0
