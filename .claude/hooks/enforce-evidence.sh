#!/bin/bash
# Claude Code hook: PreToolUse (matcher: Bash)
# Enforces meta/lex/definition-of-done.md
# Blocks `git push` unless artifacts/<sha>/gates.json exists and all gates pass.
#
# NOTE: exit 2 is what blocks. Exit 1 is treated as a non-blocking error and the
# action proceeds — the single most common hook bug. Block reasons go to stderr.

INPUT=$(cat)

COMMAND=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    print(json.load(sys.stdin).get('tool_input', {}).get('command', ''))
except Exception:
    pass
" 2>/dev/null)

echo "$COMMAND" | grep -qE '\bgit[[:space:]]+push\b' || exit 0

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
[ -z "$REPO_ROOT" ] && exit 0
cd "$REPO_ROOT" || exit 0

SHA=$(git rev-parse HEAD 2>/dev/null)
GATES="artifacts/$SHA/gates.json"

if [ ! -f "$GATES" ]; then
  cat >&2 <<MSG

  ┌────────────────────────────────────────────────────────────────┐
  │   DEFINITION OF DONE — no evidence for this commit             │
  │   meta/lex/definition-of-done.md                               │
  └────────────────────────────────────────────────────────────────┘

  No verification record found at:
      $GATES

  Run the gates, then push:
      bash scripts/verify.sh

  It runs every gate in meta/context/verification-contract.md that applies
  to the changed paths, and writes gates.json plus any screenshots.

  Then paste the summary into the PR description. Your assurance that it
  works is not evidence — the exit codes are.

MSG
  exit 2
fi

FAILING=$(python3 - "$GATES" <<'PY' 2>/dev/null
import json, sys
try:
    g = json.load(open(sys.argv[1]))
except Exception:
    print("unreadable"); sys.exit(0)
bad = [k for k, v in g.items() if str(v).lower() not in ("pass", "skip", "n/a")]
print(", ".join(bad))
PY
)

if [ -n "$FAILING" ]; then
  cat >&2 <<MSG

  ┌────────────────────────────────────────────────────────────────┐
  │   DEFINITION OF DONE — failing gates                           │
  └────────────────────────────────────────────────────────────────┘

  These gates did not pass for $SHA:
      $FAILING

  Fix them and re-run:  bash scripts/verify.sh

MSG
  exit 2
fi

exit 0
