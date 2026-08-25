#!/bin/bash
# Claude Code hook: PreToolUse (matcher: Bash)
# Enforces meta/lex/workspace-updates.md
# Blocks `git commit` when developer-facing files are staged without CLAUDE.md + README.md.

INPUT=$(cat)

# python3 can resolve to a non-functional shim (e.g. a Windows Store
# app-execution-alias) even when a real interpreter exists under a different
# name — fall back to `python` if so.
PYTHON=python3
python3 -c "" >/dev/null 2>&1 || PYTHON=python

COMMAND=$(echo "$INPUT" | "$PYTHON" -c "
import sys, json
try:
    print(json.load(sys.stdin).get('tool_input', {}).get('command', ''))
except Exception:
    pass
" 2>/dev/null)

# Only care about commits
echo "$COMMAND" | grep -qE "git.*commit" || exit 0 >&2

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
[ -z "$REPO_ROOT" ] && exit 0

STAGED=$(git -C "$REPO_ROOT" diff --cached --name-only 2>/dev/null)
[ -z "$STAGED" ] && exit 0

# ── Trigger patterns (mirrors meta/lex/workspace-updates.md) ────────────────
TRIGGERS=(
  ".claude/agents/"
  ".claude/hooks/"
  ".claude/commands/"
  ".claude/settings.json"
  "meta/lex/"
  "meta/guides/"
  "meta/agents/"
  "meta/templates/"
  "scripts/"
)

TRIGGERED=false
TRIGGERED_FILES=""

for pattern in "${TRIGGERS[@]}"; do
  matches=$(echo "$STAGED" | grep "$pattern")
  if [ -n "$matches" ]; then
    TRIGGERED=true
    while IFS= read -r f; do
      [ -n "$f" ] && TRIGGERED_FILES="$TRIGGERED_FILES\n    •  $f"
    done <<< "$matches"
  fi
done

[ "$TRIGGERED" = false ] && exit 0

CLAUDE_STAGED=$(echo "$STAGED" | grep -x "CLAUDE.md")
README_STAGED=$(echo "$STAGED" | grep -x "README.md")

MISSING=""
[ -z "$CLAUDE_STAGED" ] && MISSING="$MISSING\n    ✗  CLAUDE.md  — add a dated row to ## What's New + update body"
[ -z "$README_STAGED" ] && MISSING="$MISSING\n    ✗  README.md  — update any affected section"

[ -z "$MISSING" ] && exit 0

# ── Block, and teach the rule while blocking ────────────────────────────────
echo "" >&2
echo "  ┌────────────────────────────────────────────────────────────────┐" >&2
echo "  │   WORKSPACE UPDATE TRACKING — LEX VIOLATION                    │" >&2
echo "  │   meta/lex/workspace-updates.md                                │" >&2
echo "  └────────────────────────────────────────────────────────────────┘" >&2
echo "" >&2
echo "  Developer-facing changes are staged:" >&2
echo -e "$TRIGGERED_FILES" >&2
echo "" >&2
echo "  STOP. Stage these before committing:" >&2
echo -e "$MISSING" >&2
echo "" >&2
echo "  Steps:" >&2
echo "    1. Update CLAUDE.md — add a dated row to ## What's New, update the body" >&2
echo "    2. Update README.md — update any affected section" >&2
echo "    3. git add CLAUDE.md README.md" >&2
echo "    4. Re-run the commit" >&2
echo "" >&2

exit 2
