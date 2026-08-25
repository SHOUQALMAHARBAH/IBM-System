#!/usr/bin/env bash
# Runs every gate from meta/context/verification-contract.md that applies today,
# and records the result at artifacts/<sha>/gates.json.
#
# Honest state (2026-08-22): no engineering repo/stack/CI exists yet. The only
# real gate is this brain's own health check. Engineering gates (types, lint,
# unit, build, smoke, e2e) are recorded as `skip` — not faked as passing — until
# the day a stack is chosen. Update this script in the SAME COMMIT that adds
# real commands; see meta/lex/workspace-updates.md.
set -uo pipefail

ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd); cd "$ROOT" || exit 1
SHA=$(git rev-parse HEAD 2>/dev/null || echo "no-git"); OUT="artifacts/$SHA"; mkdir -p "$OUT"

GRN=$'\033[0;32m'; RED=$'\033[0;31m'; DIM=$'\033[0;90m'; NC=$'\033[0m'
declare -A RESULT
run(){ # run <gate-name> <command...>
  local name="$1"; shift
  printf "  %-16s" "$name"
  if "$@" > "$OUT/$name.log" 2>&1; then
    echo "${GRN}pass${NC}"; RESULT[$name]=pass
  else
    echo "${RED}FAIL${NC}  ${DIM}→ $OUT/$name.log${NC}"; RESULT[$name]=fail
  fi
}
skip(){ printf "  %-16s${DIM}skip${NC}  ${DIM}%s${NC}\n" "$1" "${2:-no codebase yet}"; RESULT[$1]=skip; }

echo ""
echo "  verify — $SHA"
echo ""

# ── The one real gate today ─────────────────────────────────────────────────
run brain bash scripts/brain-doctor.sh

# ── Engineering gates — honestly not real yet ───────────────────────────────
skip types
skip lint
skip unit
skip build
skip smoke  "run 'bash scripts/smoke.sh <service>' directly once a service exists"
skip e2e
skip shots
skip a11y

# ── Record ──────────────────────────────────────────────────────────────────
python3 - "$OUT/gates.json" "${!RESULT[@]}" <<PY
import json, sys
keys = sys.argv[2:]
vals = """$(for k in "${!RESULT[@]}"; do echo "${RESULT[$k]}"; done)""".split()
json.dump(dict(zip(keys, vals)), open(sys.argv[1], "w"), indent=2)
PY

echo ""
echo "  recorded → $OUT/gates.json"
FAILED=0; for k in "${!RESULT[@]}"; do [ "${RESULT[$k]}" = fail ] && FAILED=1; done
if [ "$FAILED" = 1 ]; then
  echo "  ${RED}The brain-health gate failed. Fix before pushing.${NC}"; echo ""; exit 1
fi
echo "  ${GRN}All real gates passed.${NC} The engineering gates above are 'skip' because"
echo "  there is no codebase yet — that is the correct, honest state, not a shortcut."
echo "  Paste this summary into the PR."
echo ""
