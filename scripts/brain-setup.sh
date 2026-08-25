#!/usr/bin/env bash
# One-time setup for a new brain repo.
# Idempotent — safe to re-run.
set -uo pipefail

RED=$'\033[0;31m'; GRN=$'\033[0;32m'; YEL=$'\033[0;33m'; NC=$'\033[0m'
ok()   { echo "  ${GRN}ok${NC}    $1"; }
warn() { echo "  ${YEL}warn${NC}  $1"; }
fail() { echo "  ${RED}fail${NC}  $1"; }

ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$ROOT" || exit 1

# python3 can resolve to a non-functional shim (e.g. a Windows Store
# app-execution-alias) even when a real interpreter exists under a different
# name — fall back to `python` if so.
PYTHON=python3
python3 -c "" >/dev/null 2>&1 || PYTHON=python

echo ""
echo "  Brain setup — $ROOT"
echo ""

# 1. git
if [ -d .git ]; then ok "git repo initialised"
else
  git init -q && ok "git repo initialised"
fi

# 2. hooks executable
if [ -d .claude/hooks ]; then
  chmod +x .claude/hooks/*.sh 2>/dev/null
  ok "hooks marked executable ($(ls .claude/hooks/*.sh 2>/dev/null | wc -l | tr -d ' ') found)"
else
  fail ".claude/hooks/ missing"
fi

# 3. mirror agents
if [ -d meta/agents ]; then
  mkdir -p .claude/agents
  n=0
  for f in meta/agents/*.md; do
    [ -e "$f" ] || continue
    b=$(basename "$f"); [ "$b" = "README.md" ] && continue
    cp -f "$f" ".claude/agents/$b"; n=$((n+1))
  done
  ok "mirrored $n agent definition(s) to .claude/agents/"
else
  warn "meta/agents/ missing — no agents to mirror"
fi

# 4. settings valid
if [ -f .claude/settings.json ]; then
  if "$PYTHON" -c "import json,sys; json.load(open('.claude/settings.json'))" 2>/dev/null; then
    ok ".claude/settings.json is valid JSON"
  else
    fail ".claude/settings.json is not valid JSON — hooks will not load"
  fi
else
  warn ".claude/settings.json missing — hooks will not run"
fi

# 5. placeholders
PH=$(grep -rl '{{FILL' --include='*.md' . 2>/dev/null | grep -v '_TEMPLATE' | head -20)
if [ -n "$PH" ]; then
  warn "{{FILL}} markers still present — fill these before your first real commit:"
  echo "$PH" | sed 's/^/          /'
else
  ok "no unfilled {{FILL}} markers"
fi

# 6. empty folders
EMPTY=$(find meta -type d -empty 2>/dev/null)
if [ -n "$EMPTY" ]; then
  warn "empty folders (delete them — a .gitkeep graveyard makes the brain look abandoned):"
  echo "$EMPTY" | sed 's/^/          /'
else
  ok "no empty folders"
fi

echo ""
echo "  Next:"
echo "    1. Work through FILL-CHECKLIST.md — every {{FILL}} marker, in order"
echo "    2. Write 3-5 lex files from your real PR review comments (see INTAKE.md)"
echo "    3. Open this directory in your agent and ask it something only the brain knows"
echo "    4. Run: bash scripts/brain-doctor.sh"
echo ""
