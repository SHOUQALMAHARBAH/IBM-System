#!/bin/bash
# Claude Code hook: PostToolUse (matcher: Write|Edit)
# Keeps .claude/agents/ in sync with meta/agents/ (source of truth).
#
# This hook exists because the alternative — a written rule telling humans to
# update both copies — is known to fail. When it fails, the STALE copy is the
# one that loads, so the agent confidently follows a rule you already replaced.

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
[ -z "$REPO_ROOT" ] && exit 0

SRC="$REPO_ROOT/meta/agents"
DST="$REPO_ROOT/.claude/agents"

[ -d "$SRC" ] || exit 0
mkdir -p "$DST"

CHANGED=0
for f in "$SRC"/*.md; do
  [ -e "$f" ] || continue
  base=$(basename "$f")
  [ "$base" = "README.md" ] && continue
  if ! cmp -s "$f" "$DST/$base"; then
    cp -f "$f" "$DST/$base"
    echo "  mirrored: meta/agents/$base -> .claude/agents/$base"
    CHANGED=1
  fi
done

# Remove mirrored files whose source is gone
for f in "$DST"/*.md; do
  [ -e "$f" ] || continue
  base=$(basename "$f")
  if [ ! -f "$SRC/$base" ]; then
    rm -f "$f"
    echo "  removed stale mirror: .claude/agents/$base"
    CHANGED=1
  fi
done

exit 0
