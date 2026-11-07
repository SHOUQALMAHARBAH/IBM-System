#!/bin/bash
# Claude Code hook: PreToolUse (matcher: Write|Edit)
# Enforces meta/lex/workflow-state-transitions.md
# Blocks a write that sets a workflow `status` outside the transition engine.
#
# NOTE: exit 2 is what blocks. Exit 1 is treated as a NON-blocking error and the action
# proceeds — the single most common hook bug, and the one `brain-doctor.sh` checks for.
#
# THE SCAN IS NOT IN THIS FILE. It is `status_write_scan.py`, which tokenises the edit
# (comments and string bodies are prose, not code) and brace-matches a Prisma `data:`
# payload so that `where: { status: … }` — the race-safe conditional the lex REQUIRES — is
# not refused. Three measured defects in the old inline `grep` are recorded in that
# module's docstring, including the path-substring exemption that exempted 9 files which
# are not the engine.
#
# Prove it with:  python status_write_scan.py --self-test

set -uo pipefail

HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# python3 can resolve to a non-functional shim (e.g. a Windows Store app-execution-alias)
# even when a real interpreter exists under a different name — fall back to `python` if so.
PYTHON=python3
python3 -c "" >/dev/null 2>&1 || PYTHON=python

if ! command -v "$PYTHON" >/dev/null 2>&1; then
  echo "" >&2
  echo "  GUARD CANNOT RUN — no python interpreter found." >&2
  echo "  enforce-state-transitions.sh needs one to read the tool call." >&2
  echo "  This blocks rather than passes: an unrunnable guard has checked nothing." >&2
  echo "" >&2
  exit 2
fi

HITS=$("$PYTHON" "$HOOK_DIR/hook_scan.py" status_write_scan)
STATUS=$?

[ "$STATUS" -eq 0 ] && exit 0

echo "" >&2
echo "  ┌────────────────────────────────────────────────────────────────┐" >&2
echo "  │   WORKFLOW STATE TRANSITION — BLOCKED                          │" >&2
echo "  │   meta/lex/workflow-state-transitions.md                       │" >&2
echo "  └────────────────────────────────────────────────────────────────┘" >&2
echo "" >&2

if [ -n "$HITS" ]; then
  echo "  A status write outside the transition engine:" >&2
  echo "" >&2
  echo "$HITS" | sed 's/^/    /' >&2
  echo "" >&2
  echo "  Route it through the entity's transition() function — a direct write skips" >&2
  echo "  the audit row and any SLA timer the transition is supposed to start" >&2
  echo "  (see PRIV-SRS-01 §7)." >&2
  echo "" >&2
  echo "  A status-CONDITIONAL write is NOT this: \`where: { id, status: 'OPEN' }\` with" >&2
  echo "  \`data\` setting some other field is the race-safe pattern" >&2
  echo "  meta/lex/race-safe-invariants.md requires, and is not reported here." >&2
  echo "" >&2
  echo "  If this file IS the engine, say so IN THE FILE with the marker" >&2
  echo "  @implements-workflow-transitions — never by naming it after a path." >&2
else
  echo "  The guard could not complete. See the message above." >&2
fi
echo "" >&2

exit 2
