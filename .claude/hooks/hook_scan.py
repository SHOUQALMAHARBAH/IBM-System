"""
ONE HOME FOR READING A `PreToolUse` TOOL CALL AND HANDING IT TO A SCANNER.

Every `Write|Edit` guard in this directory needs the same two values out of the same JSON —
`file_path` and whichever of `content` / `new_string` the tool supplied — and each one used to
parse it with its own inline `python -c`, in a heredoc, inside the shell script.

That is three problems in one line. The duplication is the smallest of them:

  * **This host decodes backslash escapes inside heredocs.** A regex or an escape written
    through one arrives mangled, compiles fine, matches nothing, and the guard passes
    silently. It is a recorded hazard in this toolchain and it has already produced a
    pattern that matched nothing while reporting success.
  * **An inline `python -c` cannot be unit-tested.** The scanners next to this file have
    `--self-test` suites with planted inputs; code embedded in a shell string has nothing.
  * **Failure was indistinguishable from success.** Each old extraction ended in
    `2>/dev/null` with a bare `except: pass`, so unparseable input produced an empty string,
    which the hook then read as "nothing to check" and exited 0.

So: the shell scripts are now wrappers with no logic, this module does the parsing, and a
parse failure is LOUD — it exits 2 and says so, because a guard that cannot read its input
has not checked anything and must not pretend it has.

Usage, from a hook:

    python hook_scan.py status_write_scan    # or money_scan
"""

from __future__ import annotations

import importlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

#: Exit codes. 2 BLOCKS the tool call; 1 is a non-blocking error that Claude Code proceeds
#: past, which is the single most common hook bug. Nothing here may ever exit 1.
BLOCK = 2
ALLOW = 0


def main() -> int:
    if len(sys.argv) < 2:
        print("hook_scan: no scanner named", file=sys.stderr)
        return BLOCK

    raw = sys.stdin.read()

    try:
        payload = json.loads(raw)
    except Exception as exc:  # noqa: BLE001 — any failure here must be loud
        print(
            f"\n  GUARD COULD NOT READ ITS INPUT — {sys.argv[1]}\n\n"
            f"  The tool-call JSON did not parse: {exc}\n\n"
            "  This is a BLOCK rather than a pass, deliberately. A guard that cannot read\n"
            "  its input has checked nothing, and the old behaviour here was to swallow the\n"
            "  error and exit 0 — which is indistinguishable from a clean result.\n",
            file=sys.stderr,
        )
        return BLOCK

    tool_input = payload.get("tool_input") or {}
    file_path = tool_input.get("file_path") or ""
    content = tool_input.get("content") or tool_input.get("new_string") or ""

    if not content:
        return ALLOW  # nothing was written; nothing to scan

    try:
        scanner = importlib.import_module(sys.argv[1])
    except Exception as exc:  # noqa: BLE001
        print(f"\n  GUARD MISSING — cannot import {sys.argv[1]}: {exc}\n", file=sys.stderr)
        return BLOCK

    hits = scanner.findings(file_path, content)
    if not hits:
        return ALLOW

    for line in hits:
        print(line)
    return BLOCK


if __name__ == "__main__":
    raise SystemExit(main())
