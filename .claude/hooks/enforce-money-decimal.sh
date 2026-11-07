#!/bin/bash
# Claude Code hook: PreToolUse (matcher: Write|Edit)
# Enforces meta/lex/money-decimal-jod.md
# Blocks float()/round() on a money-shaped identifier in new or edited content.
#
# NOTE: exit 2 is what blocks. Exit 1 is treated as a NON-blocking error and the action
# proceeds — the single most common hook bug, and the one `brain-doctor.sh` checks for.
#
# THE SCAN IS NOT IN THIS FILE. It is `money_scan.py`, which tokenises the edit so a
# comment or a string literal naming the forbidden shape is read as the prose it is, and
# which matches money words as IDENTIFIER COMPONENTS so `tax` no longer hits `taxonomy`.
#
# `tax` and `fees` were missing from the old nine-word list — and the sharper finding
# recorded in that module is that `money-decimal-jod.md` contradicted ITSELF: § Rule names
# both words, § How it is enforced dropped them, and this hook matched the wrong half.
#
# Prove it with:  python money_scan.py --self-test
#
# MEASURED 2026-11-07 against ibms-app, before wiring this anywhere: the corrected list
# blocks 0 of 1,712 tracked .ts/.tsx files, so it refuses nothing that is already correct.
# A widened operator list (parseFloat / Number( / Math.round / toFixed) would block 14 —
# which is why it is NOT widened here. See the module docstring; that is the owner's call.

set -uo pipefail

HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# python3 can resolve to a non-functional shim (e.g. a Windows Store app-execution-alias)
# even when a real interpreter exists under a different name — fall back to `python` if so.
PYTHON=python3
python3 -c "" >/dev/null 2>&1 || PYTHON=python

if ! command -v "$PYTHON" >/dev/null 2>&1; then
  echo "" >&2
  echo "  GUARD CANNOT RUN — no python interpreter found." >&2
  echo "  enforce-money-decimal.sh needs one to read the tool call." >&2
  echo "  This blocks rather than passes: an unrunnable guard has checked nothing." >&2
  echo "" >&2
  exit 2
fi

HITS=$("$PYTHON" "$HOOK_DIR/hook_scan.py" money_scan)
STATUS=$?

[ "$STATUS" -eq 0 ] && exit 0

echo "" >&2
echo "  ┌────────────────────────────────────────────────────────────────┐" >&2
echo "  │   MONEY ARITHMETIC — BLOCKED                                   │" >&2
echo "  │   meta/lex/money-decimal-jod.md                                │" >&2
echo "  └────────────────────────────────────────────────────────────────┘" >&2
echo "" >&2

if [ -n "$HITS" ]; then
  echo "  float()/round() on a money-shaped identifier:" >&2
  echo "" >&2
  echo "$HITS" | sed 's/^/    /' >&2
  echo "" >&2
  echo "  Use a fixed-point decimal quantized to 3 places (the JOD fils), with one" >&2
  echo "  rounding mode fixed for the whole codebase. In ibms-app that is" >&2
  echo "  apps/api/src/common/money.util.ts — addMoney / sumMoney / quantizeMoney." >&2
  echo "" >&2
  echo "  False positive? Rename the identifier away from a money word, or widen" >&2
  echo "  MONEY_WORDS in money_scan.py — and if the rule itself is wrong, fix the lex" >&2
  echo "  rather than this one call site." >&2
else
  echo "  The guard could not complete. See the message above." >&2
fi
echo "" >&2

exit 2
