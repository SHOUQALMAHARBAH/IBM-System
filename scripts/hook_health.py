"""
IS EVERY GUARD IN `.claude/hooks/` ACTUALLY WIRED, PRESENT, AND ABLE TO RUN?

Backs `scripts/brain-doctor.sh` § Hook wiring. Run it directly for the detail:

    python scripts/hook_health.py                 # report, exit 1 on any error
    python scripts/hook_health.py --self-test     # prove it can fail

## Why this file exists

`brain-doctor.sh` is the health check for the brain, and until 2026-11-07 it could not see
the largest thing wrong with the brain's enforcement. It checked hook EXIT CODES (§ Hook
enforcement — an `exit 1` in a hook does not block, which is the classic footgun) and nothing
else about hooks. Specifically it had **no check that a hook file exists**, **none that a hook
is registered in `settings.json`**, and **none for the executable bit**. It reported `ok`.

Measured the same day, which is what the checks below are for:

  * **`ibms-app/.claude/settings.json` registers 2 of the 6 hooks that exist here.**
    `enforce-state-transitions`, `enforce-money-decimal`, `enforce-sensitive-data` and
    `enforce-evidence` are not registered in the repository where the code lives, so four
    guards — including the money-arithmetic and sensitive-data ones — do not run while
    anybody works on the system.
  * **Every hook in this directory was recorded in git as `100644`, not `100755`.** With
    `core.filemode = false` on the development host the local filesystem reports `rwxr-xr-x`
    and nothing looks wrong — but a fresh clone (CI, or a colleague) gets no executable bit.
    The brain's own registration tested `[ -x "$script" ]` and fell through to `|| true`, so
    **on a fresh clone all six guards here would have silently done nothing.** That is worse
    than the unregistered four, because this is the repo where they ARE wired.
  * **Every registration ended in `|| true`**, so a missing or unreadable guard exits 0. It
    is the same `|| true`-on-the-deciding-line family that turned a missing `jq` binary into
    two CI watches that printed nothing and exited 0 while the build was red.

The rule underneath all three: **a guard whose failure path is indistinguishable from its
success path is not a guard.**
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys

#: Hook script paths as they appear inside a registration command string.
_HOOK_PATH = re.compile(r"[\w./-]*\.claude/hooks/([\w-]+\.(?:sh|py))")

#: A registration that swallows its own absence. `|| true` on the line that DECIDES whether
#: the guard runs is the defect; `|| true` elsewhere in a command is not this check's business.
_SWALLOWS = re.compile(r"\|\|\s*true\s*'?\s*$")


def _commands(settings: dict) -> list[tuple[str, str, str]]:
    """Every hook command in a settings.json, as (event, matcher, command)."""
    out = []
    for event, groups in (settings.get("hooks") or {}).items():
        for group in groups or []:
            matcher = group.get("matcher", "")
            for hook in group.get("hooks") or []:
                cmd = hook.get("command", "")
                if cmd:
                    out.append((event, matcher, cmd))
    return out


def _git_modes(root: str, rel_dir: str) -> dict[str, str]:
    """Git-recorded file mode per basename under `rel_dir`, or {} outside a git tree."""
    try:
        out = subprocess.run(
            ["git", "-C", root, "ls-files", "-s", rel_dir],
            capture_output=True,
            text=True,
            timeout=30,
        ).stdout
    except Exception:  # noqa: BLE001
        return {}
    modes = {}
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) == 2:
            modes[os.path.basename(parts[1])] = parts[0].split()[0]
    return modes


def check(root: str) -> tuple[list[str], list[str]]:
    """(errors, notes) for the brain repo rooted at `root`."""
    errors: list[str] = []
    notes: list[str] = []

    hooks_dir = os.path.join(root, ".claude", "hooks")
    settings_path = os.path.join(root, ".claude", "settings.json")

    if not os.path.isdir(hooks_dir):
        return ([".claude/hooks/ is missing — no guard in this repo can run"], [])
    if not os.path.isfile(settings_path):
        return ([".claude/settings.json is missing — nothing is registered"], [])

    try:
        settings = json.load(open(settings_path, encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return ([f".claude/settings.json does not parse: {exc}"], [])

    on_disk = {f for f in os.listdir(hooks_dir) if f.endswith((".sh", ".py"))}
    registered: set[str] = set()

    # ── 1. every REGISTERED script must exist, be readable, and not swallow its absence ──
    for event, matcher, cmd in _commands(settings):
        # `dict.fromkeys`, not `set`: order is kept so the report is stable, and the dedupe
        # matters because a loud registration names its script TWICE — once to resolve it and
        # once in the message it prints when the file is missing. Found by planting a deleted
        # hook and reading two identical errors for one problem.
        named = list(dict.fromkeys(_HOOK_PATH.findall(cmd)))
        if not named:
            notes.append(f"{event}/{matcher or '*'}: a command naming no hook script (not checked)")
            continue
        for base in named:
            registered.add(base)
            path = os.path.join(hooks_dir, base)
            if not os.path.isfile(path):
                errors.append(
                    f"{base} is REGISTERED ({event}) but does not exist — "
                    "a configured guard that is missing must fail the action, not pass it"
                )
            elif not os.access(path, os.R_OK):
                errors.append(f"{base} is registered ({event}) but is not readable")
        if _SWALLOWS.search(cmd):
            errors.append(
                f"{', '.join(named)} is registered ({event}) with a trailing `|| true` — "
                "a missing or unreadable guard would exit 0 and the action would proceed"
            )

    # ── 2. every hook ON DISK must be registered, or it never runs ──────────────────────
    #
    # A library module is not a hook; it is imported by one. Only entry points are expected
    # to be registered.
    libraries = {"code_text.py", "hook_scan.py", "status_write_scan.py", "money_scan.py"}
    for base in sorted(on_disk - registered - libraries):
        errors.append(
            f"{base} exists in .claude/hooks/ but is registered nowhere in settings.json — "
            "it will never run"
        )

    # ── 3. the executable bit, as GIT records it ────────────────────────────────────────
    #
    # Not `os.access(X_OK)`: on Windows that is meaningless, and with core.filemode=false
    # the local mode is not what a fresh clone gets. Git's index is the thing that travels.
    modes = _git_modes(root, ".claude/hooks")
    for base in sorted(on_disk):
        mode = modes.get(base)
        if mode is None:
            notes.append(f"{base} is untracked — a guard nobody else gets")
        elif base.endswith(".sh") and mode != "100755":
            errors.append(
                f"{base} is recorded in git as {mode}, not 100755 — on a fresh clone it has "
                "no executable bit, and any registration testing `[ -x ]` would skip it in silence"
            )

    return errors, notes


def main() -> int:
    root = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True
    ).stdout.strip() or os.getcwd()

    errors, notes = check(root)
    for n in notes:
        print(f"  note   {n}")
    for e in errors:
        print(f"  ERROR  {e}")
    if not errors:
        print("  ok     every hook exists, is registered, is executable, and fails loudly")
    return 1 if errors else 0


# ─────────────────────────────────────────────────────────────────────────────────
# Self-test. A doctor that has never failed is not a doctor — so each condition is PLANTED
# in a throwaway tree and the check must report it.
# ─────────────────────────────────────────────────────────────────────────────────


def _self_test() -> int:
    import shutil
    import tempfile

    def build(tmp: str, *, settings: dict, files: dict, chmod: dict | None = None) -> None:
        os.makedirs(os.path.join(tmp, ".claude", "hooks"), exist_ok=True)
        for name, body in files.items():
            with open(os.path.join(tmp, ".claude", "hooks", name), "w", encoding="utf-8") as fh:
                fh.write(body)
        with open(os.path.join(tmp, ".claude", "settings.json"), "w", encoding="utf-8") as fh:
            json.dump(settings, fh)
        subprocess.run(["git", "-C", tmp, "init", "-q"], check=False)
        subprocess.run(["git", "-C", tmp, "add", "-A"], check=False)
        for name, mode in (chmod or {}).items():
            subprocess.run(
                ["git", "-C", tmp, "update-index", f"--chmod={mode}", f".claude/hooks/{name}"],
                check=False,
            )

    def reg(name: str, loud: bool = True) -> dict:
        tail = (
            'if [ -r "$s" ]; then exec bash "$s"; else echo missing >&2; exit 2; fi'
            if loud
            else '[ -x "$s" ] && exec "$s" || true'
        )
        return {
            "hooks": {
                "PreToolUse": [
                    {
                        "matcher": "Bash",
                        "hooks": [{"type": "command", "command": f's=".claude/hooks/{name}"; {tail}'}],
                    }
                ]
            }
        }

    cases = []

    # clean
    tmp = tempfile.mkdtemp()
    build(tmp, settings=reg("a.sh"), files={"a.sh": "#!/bin/bash\nexit 0\n"}, chmod={"a.sh": "+x"})
    cases.append(("a clean repo reports nothing", check(tmp)[0], False))
    shutil.rmtree(tmp, ignore_errors=True)

    # planted: registered but missing
    tmp = tempfile.mkdtemp()
    build(tmp, settings=reg("gone.sh"), files={"a.sh": "x\n"}, chmod={"a.sh": "+x"})
    cases.append(("PLANT a registered hook that does not exist", check(tmp)[0], True))
    shutil.rmtree(tmp, ignore_errors=True)

    # planted: on disk but unregistered
    tmp = tempfile.mkdtemp()
    build(
        tmp,
        settings=reg("a.sh"),
        files={"a.sh": "x\n", "orphan.sh": "x\n"},
        chmod={"a.sh": "+x", "orphan.sh": "+x"},
    )
    cases.append(("PLANT a hook registered nowhere", check(tmp)[0], True))
    shutil.rmtree(tmp, ignore_errors=True)

    # planted: lost executable bit in git
    tmp = tempfile.mkdtemp()
    build(tmp, settings=reg("a.sh"), files={"a.sh": "x\n"})
    cases.append(("PLANT a hook recorded 100644", check(tmp)[0], True))
    shutil.rmtree(tmp, ignore_errors=True)

    # planted: the silent registration shape
    tmp = tempfile.mkdtemp()
    build(
        tmp,
        settings=reg("a.sh", loud=False),
        files={"a.sh": "x\n"},
        chmod={"a.sh": "+x"},
    )
    cases.append(("PLANT a registration ending in `|| true`", check(tmp)[0], True))
    shutil.rmtree(tmp, ignore_errors=True)

    failures = []
    for name, errs, should_fail in cases:
        did_fail = bool(errs)
        if did_fail != should_fail:
            failures.append(
                f"{name}: expected {'ERROR' if should_fail else 'clean'}, got "
                f"{'ERROR: ' + '; '.join(errs) if did_fail else 'clean'}"
            )
        else:
            print(f"  ok     {name}" + (f"  ->  {errs[0][:70]}" if errs else ""))
    for f in failures:
        print(f"  FAIL   {f}")
    print(
        f"\n  hook_health self-test: {len(cases) - len(failures)}/{len(cases)} cases correct,"
        f" {len(failures)} failure(s)"
    )
    return 1 if failures else 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        raise SystemExit(_self_test())
    raise SystemExit(main())
