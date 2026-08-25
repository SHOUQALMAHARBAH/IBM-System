#!/bin/bash
# Claude Code hook: PreToolUse (matcher: Bash)
# Blocks commands that would write a secret to the filesystem or echo one into a log.
# Approved patterns instead: $GITHUB_ENV, process substitution <(...), secret mounts,
# or pulling server-side from your secret manager.

INPUT=$(cat)

COMMAND=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    print(json.load(sys.stdin).get('tool_input', {}).get('command', ''))
except Exception:
    pass
" 2>/dev/null)

[ -z "$COMMAND" ] && exit 0

# Redirecting something secret-shaped into a file
DANGER=$(echo "$COMMAND" | grep -iE '(echo|printf|cat).*(SECRET|TOKEN|PASSWORD|API_KEY|PRIVATE_KEY|CREDENTIAL).*>')
# Writing a .env or key material
DANGER2=$(echo "$COMMAND" | grep -iE '>[[:space:]]*[^|]*\.(env|pem|key|p12|jks)([[:space:]]|$)')

if [ -n "$DANGER" ] || [ -n "$DANGER2" ]; then
  echo "" >&2
  echo "  ┌────────────────────────────────────────────────────────────────┐" >&2
  echo "  │   CREDENTIAL SAFETY — BLOCKED                                  │" >&2
  echo "  └────────────────────────────────────────────────────────────────┘" >&2
  echo "" >&2
  echo "  This command appears to write credential material to disk:" >&2
  echo "" >&2
  echo "    $COMMAND" >&2
  echo "" >&2
  echo "  Secrets must never touch the filesystem. Use instead:" >&2
  echo "    •  \$GITHUB_ENV / \$GITHUB_OUTPUT for CI values" >&2
  echo "    •  process substitution:  mycmd --key-file <(get-secret NAME)" >&2
  echo "    •  BuildKit secret mounts:  RUN --mount=type=secret,id=NAME" >&2
  echo "    •  a server-side pull from your secret manager at runtime" >&2
  echo "" >&2
  echo "  If this is a false positive, rename the variable or run it outside the agent." >&2
  echo "" >&2
  exit 2
fi

exit 0
