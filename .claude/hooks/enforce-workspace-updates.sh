#!/bin/bash
# Claude Code hook: PreToolUse (matcher: Bash)
# Enforces meta/lex/workspace-updates.md
# Blocks `git commit` when developer-facing files are staged without CLAUDE.md + README.md.
#
# NOTE: exit 2 is what blocks. Exit 1 is treated as a NON-blocking error and the action
# proceeds — the single most common hook bug, and the one `brain-doctor.sh` checks for.
# `meta/lex/workspace-updates.md` § How it is enforced claimed this script "exits 1" until
# 2026-11-07; the SCRIPT was right and the LEX was wrong, and the lex is corrected rather
# than the exit code changed to match a sentence.

set -uo pipefail

INPUT=$(cat)

# python3 can resolve to a non-functional shim (e.g. a Windows Store app-execution-alias)
# even when a real interpreter exists under a different name — fall back to `python` if so.
PYTHON=python3
python3 -c "" >/dev/null 2>&1 || PYTHON=python

# A GUARD THAT CANNOT READ ITS INPUT HAS CHECKED NOTHING, SO IT BLOCKS.
#
# `README.md` § `.claude/` recorded this as a known gap: on a machine where `python3` is a
# stub (the Windows Store alias) and no real `python` exists either, the extraction below
# produced an empty string, `grep -qE "git.*commit"` found nothing in it, and the hook exited
# 0 — silently permitting every commit it exists to inspect. Added 2026-11-07.
if ! command -v "$PYTHON" >/dev/null 2>&1; then
  echo "" >&2
  echo "  GUARD CANNOT RUN — no python interpreter found." >&2
  echo "  enforce-workspace-updates.sh needs one to read the tool call." >&2
  echo "  This blocks rather than passes: a guard that cannot run has checked nothing." >&2
  echo "" >&2
  exit 2
fi

COMMAND=$(echo "$INPUT" | "$PYTHON" -c "
import sys, json
try:
    print(json.load(sys.stdin).get('tool_input', {}).get('command', ''))
except Exception:
    pass
" 2>/dev/null)

# Only care about commits.
echo "$COMMAND" | grep -qE "git.*commit" || exit 0

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
[ -z "$REPO_ROOT" ] && exit 0

# ── Name AND status, because two trigger classes need different treatment ───────
#
# `--name-status` rather than `--name-only`: see EXISTENCE_TRIGGERS below. An `A`/`D`
# (added or deleted) is a change to what EXISTS; an `M` is a change to CONTENT, and the
# lex treats those differently for exactly one path.
STAGED_STATUS=$(git -C "$REPO_ROOT" diff --cached --name-status 2>/dev/null)
[ -z "$STAGED_STATUS" ] && exit 0

# ── Trigger patterns (mirrors meta/lex/workspace-updates.md) ────────────────────
#
# ANY change to one of these is developer-facing.
ANY_CHANGE_TRIGGERS=(
  ".claude/agents/"
  ".claude/hooks/"
  ".claude/commands/"
  ".claude/settings.json"
  "meta/lex/"
  "meta/guides/"
  "meta/agents/"
  "scripts/"
)

# Only the EXISTENCE of one of these is developer-facing — adding or deleting a template
# changes the mechanics a developer meets; editing one's prose does not.
#
# `meta/templates/` sat in the list above until 2026-11-07, while the lex's own § What does
# NOT trigger this rule said *"Template content changes (the templates themselves, not their
# existence)"*. One of the two had to be wrong, and the LEX was right: the common case is
# editing a template's wording, and demanding a CLAUDE.md row plus a README edit for a
# reworded PR template is how a guard teaches people to work around it. The hook could
# always tell the two apart — it just was not asked to.
EXISTENCE_TRIGGERS=(
  "meta/templates/"
)

TRIGGERED_FILES=""

while IFS=$'\t' read -r status file rest; do
  [ -z "${file:-}" ] && continue
  for pattern in "${ANY_CHANGE_TRIGGERS[@]}"; do
    case "$file" in
      *"$pattern"*) TRIGGERED_FILES="$TRIGGERED_FILES\n    •  $file" ;;
    esac
  done
  # An added or deleted file only. `git` reports renames as `R###`, which is a
  # deletion plus an addition as far as existence goes.
  case "$status" in
    A | D | R*)
      for pattern in "${EXISTENCE_TRIGGERS[@]}"; do
        case "$file" in
          *"$pattern"*) TRIGGERED_FILES="$TRIGGERED_FILES\n    •  $file  (added/removed)" ;;
        esac
      done
      ;;
  esac
done <<< "$STAGED_STATUS"

[ -z "$TRIGGERED_FILES" ] && exit 0

STAGED_NAMES=$(echo "$STAGED_STATUS" | cut -f2-)
CLAUDE_STAGED=$(echo "$STAGED_NAMES" | grep -x "CLAUDE.md")
README_STAGED=$(echo "$STAGED_NAMES" | grep -x "README.md")

MISSING=""
[ -z "$CLAUDE_STAGED" ] && MISSING="$MISSING\n    ✗  CLAUDE.md  — add a dated row to ## What's New + update body"
[ -z "$README_STAGED" ] && MISSING="$MISSING\n    ✗  README.md  — update any affected section"

[ -z "$MISSING" ] && exit 0

# ── Block, and teach the rule while blocking ────────────────────────────────────
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
