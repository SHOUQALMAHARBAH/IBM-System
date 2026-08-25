#!/usr/bin/env bash
# Health check for a brain repo. Run monthly, and in CI.
# Exit 1 if any ERROR-level problem is found.
set -uo pipefail

RED=$'\033[0;31m'; GRN=$'\033[0;32m'; YEL=$'\033[0;33m'; NC=$'\033[0m'
ERRORS=0; WARNINGS=0
ok()   { echo "  ${GRN}ok${NC}     $1"; }
warn() { echo "  ${YEL}warn${NC}   $1"; WARNINGS=$((WARNINGS+1)); }
err()  { echo "  ${RED}ERROR${NC}  $1"; ERRORS=$((ERRORS+1)); }

ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$ROOT" || exit 1

echo ""
echo "  brain-doctor — $ROOT"
echo ""

# ── 1. Mirror drift ─────────────────────────────────────────────────────────
echo "  Mirror drift"
if [ -d meta/agents ] && [ -d .claude/agents ]; then
  DRIFT=0
  for f in meta/agents/*.md; do
    [ -e "$f" ] || continue
    b=$(basename "$f"); [ "$b" = "README.md" ] && continue
    if [ ! -f ".claude/agents/$b" ]; then
      err "$b exists in meta/agents/ but not in .claude/agents/ — it will never load"
      DRIFT=1
    elif ! cmp -s "$f" ".claude/agents/$b"; then
      err "$b differs between meta/agents/ and .claude/agents/ — the LOADED copy is the stale one"
      DRIFT=1
    fi
  done
  for f in .claude/agents/*.md; do
    [ -e "$f" ] || continue
    b=$(basename "$f")
    [ -f "meta/agents/$b" ] || err "$b is in .claude/agents/ with no source in meta/agents/"
  done
  [ "$DRIFT" = 0 ] && ok "agent definitions in sync"
else
  warn "agent directories missing — skipped"
fi

# ── 2. Lex without enforcement ──────────────────────────────────────────────
echo ""
echo "  Lex enforcement"
if [ -d meta/lex ]; then
  UNENFORCED=0
  for f in meta/lex/*.md; do
    [ -e "$f" ] || continue
    b=$(basename "$f"); case "$b" in _TEMPLATE.md|README.md) continue;; esac
    if ! grep -q "How it is enforced" "$f"; then
      err "$b has no 'How it is enforced' section — this is a suggestion, not a lex"
      UNENFORCED=1
    else
      body=$(sed -n '/How it is enforced/,/^## /p' "$f" | sed '1d;/^## /d' | grep -v '^[[:space:]]*$' | grep -v '^>')
      [ -z "$body" ] && { warn "$b has an empty enforcement section"; UNENFORCED=1; }
    fi
  done
  [ "$UNENFORCED" = 0 ] && ok "every lex has an enforcement mechanism"
else
  warn "meta/lex/ missing"
fi

# ── 3. Dangling internal links ──────────────────────────────────────────────
echo ""
echo "  Internal links"
LINKOUT=$(python3 - <<'PYCHECK'
import os, re, sys
bad = []
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in ('.git', 'node_modules', '.venv')]
    for fn in files:
        if not fn.endswith('.md'):
            continue
        path = os.path.join(root, fn)
        try:
            text = open(path, encoding='utf-8', errors='ignore').read()
        except OSError:
            continue
        for target in re.findall(r'\]\(([^)]+)\)', text):
            t = target.split('#')[0].strip()
            if not t or t.startswith(('http://', 'https://', 'mailto:', '<')):
                continue
            if not os.path.exists(os.path.join(root, t)):
                bad.append(f"{path} -> {t}")
for b in bad:
    print(b)
PYCHECK
)
if [ -n "$LINKOUT" ]; then
  while IFS= read -r l; do err "dangling link: $l"; done <<< "$LINKOUT"
else
  ok "no dangling internal links"
fi

# ── 4. Referenced-but-missing lex ───────────────────────────────────────────
echo ""
echo "  Lex references"
MISSING_LEX=0
for ref in $(grep -rhoE 'meta/lex/[a-z0-9-]+\.md' --include='*.md' . 2>/dev/null | sort -u); do
  [ -f "$ref" ] || { err "referenced but missing: $ref"; MISSING_LEX=1; }
done
[ "$MISSING_LEX" = 0 ] && ok "every referenced lex exists"

# ── 5. What's New freshness ─────────────────────────────────────────────────
echo ""
echo "  CLAUDE.md hygiene"
if [ -f CLAUDE.md ]; then
  ROWS=$(sed -n "/## What's New/,/^## /p" CLAUDE.md | grep -cE '^\| [0-9]{4}-[0-9]{2}-[0-9]{2}')
  if [ "$ROWS" -gt 5 ]; then
    warn "What's New has $ROWS dated rows — cap is 5, drop the oldest"
  else
    ok "What's New within cap ($ROWS rows)"
  fi
  LAST=$(git log -1 --format=%ct -- CLAUDE.md 2>/dev/null)
  if [ -n "$LAST" ]; then
    DAYS=$(( ( $(date +%s) - LAST ) / 86400 ))
    if [ "$DAYS" -gt 21 ]; then warn "CLAUDE.md untouched for $DAYS days — is the brain still being used?"
    else ok "CLAUDE.md updated $DAYS day(s) ago"; fi
  fi
else
  err "CLAUDE.md missing — nothing will auto-load"
fi

# ── 6. Placeholders ─────────────────────────────────────────────────────────
echo ""
echo "  Placeholders"
PH=$(grep -rl '{{FILL' --include='*.md' . 2>/dev/null | grep -v '_TEMPLATE')
if [ -n "$PH" ]; then
  err "unfilled {{FILL}} markers remain — the brain is not ready to use:"
  echo "$PH" | sed 's/^/           /'
else
  ok "no unfilled placeholders"
fi

# ── 7. Empty folders ────────────────────────────────────────────────────────
echo ""
echo "  Structure"
EMPTY=$(find meta -type d -empty 2>/dev/null)
if [ -n "$EMPTY" ]; then
  warn "empty folders present:"; echo "$EMPTY" | sed 's/^/           /'
else
  ok "no empty folders"
fi

# ── 8. Hook exit codes (the silent-failure footgun) ─────────────────────────
echo ""
echo "  Hook enforcement"
if [ -d .claude/hooks ]; then
  HOOKBAD=0
  for f in .claude/hooks/*.sh; do
    [ -e "$f" ] || continue
    b=$(basename "$f")
    if grep -qE '^[[:space:]]*exit 1[[:space:]]*$' "$f"; then
      err "$b uses 'exit 1' — Claude Code treats that as a NON-blocking error and proceeds. Use 'exit 2' to actually block."
      HOOKBAD=1
    fi
    if grep -qE '^[[:space:]]*exit 2[[:space:]]*$' "$f" && ! grep -q '>&2' "$f"; then
      warn "$b exits 2 but writes no stderr — it will block with no explanation for the agent."
      HOOKBAD=1
    fi
  done
  [ "$HOOKBAD" = 0 ] && ok "hooks block correctly (exit 2 + stderr)"
else
  warn ".claude/hooks/ missing"
fi

# ── 9. AGENTS.md must be imported, not just present ─────────────────────────
echo ""
echo "  Instruction loading"
if [ -f AGENTS.md ]; then
  if grep -qE '^@AGENTS\.md' CLAUDE.md 2>/dev/null || [ -L CLAUDE.md ]; then
    ok "AGENTS.md is imported by CLAUDE.md"
  else
    err "AGENTS.md exists but CLAUDE.md does not import it — Claude Code reads CLAUDE.md only, so AGENTS.md never loads. Add '@AGENTS.md' as the first line of CLAUDE.md."
  fi
fi
if [ -f CLAUDE.md ]; then
  L=$(wc -l < CLAUDE.md | tr -d ' ')
  if [ "$L" -gt 200 ]; then
    warn "CLAUDE.md is $L lines — target is under 200. Longer files consume context every session and reduce adherence. Move detail into meta/ and reference it."
  else
    ok "CLAUDE.md is $L lines (under the 200-line target)"
  fi
fi

# ── Summary ─────────────────────────────────────────────────────────────────
echo ""
echo "  ────────────────────────────────────────────"
echo "  $ERRORS error(s), $WARNINGS warning(s)"
echo ""
[ "$ERRORS" -gt 0 ] && exit 1
exit 0
