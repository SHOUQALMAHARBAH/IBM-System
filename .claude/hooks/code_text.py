"""
ONE HOME FOR "WHAT IN THIS DIFF IS ACTUALLY CODE".

Every guard in `.claude/hooks/` that searches source for a forbidden shape has to answer
the same question first: which characters are code, and which are a comment or the inside
of a string literal? Both of the latter are prose. A guard that cannot tell them apart
reports the documentation of a fix as an instance of the defect, and — worse — truncates
real code when it tries.

## Why this file exists rather than a regex in each hook

Measured, 2026-11-07, in `ibms-app`. A comment-stripper written as two regex substitutions
reported a page-wide-absence class falling 42 -> 38 and the conclusion drawn was that the
ratchet "had carried four units of slack". Both were false. The line-comment pattern

    (?m)//.*$

eats `//` INSIDE A STRING LITERAL, and the spec file it ran over is full of

    "http://localhost:4000/..."

so it truncated real code at every URL. The four "false positives" it appeared to remove
were four real assertions it had destroyed. Nothing failed; the figure simply moved, in the
direction that looks like progress.

The rule that came out of it, and the reason this module is not optional:

    A GUARD THAT READS OR STRIPS CODE TOKENISES. IT DOES NOT REGEX.

A regex cannot do this at all — not with more cleverness, not with a longer pattern. Deciding
whether `//` opens a comment requires knowing whether you are already inside a string, which
requires having scanned everything before it. That is a state machine, and `blank()` below is
the smallest correct one.

## What it does

Returns the text with every comment and every string-literal BODY replaced by spaces, and
with all other bytes and every newline left exactly where they were. Positions are preserved
so a caller can still report a line number, and `splitlines()` still lines up with the
original file.

Handles, because each of these has produced a wrong figure in this codebase or its sibling:

  * `//` and `/* */`, including a `/*` that only appears inside a string
  * `'`, `"` and backtick strings, with backslash escapes (`"a\\"b"` does not end early)
  * `${...}` inside a template literal is CODE and is kept — a guard that blanked it would
    stop seeing `round(${premium})`
  * `#` comments, for the shell and python files these hooks are themselves written in

Deliberately NOT handled: nested `/* /* */ */` (not nestable in C-family languages anyway),
and regex literals (`/x/` is left as code, so a forbidden shape inside one is still reported;
the alternative needs a full parser and the false-negative is the safer direction).

Run `python code_text.py --self-test` for the proof. Every case in it is a shape that has
actually mis-measured something here.
"""

from __future__ import annotations

# Which comment syntaxes apply, by file extension. A `#` in a .ts file is not a comment
# (it is a private field), and `//` in a .sh file is not one either (it is a path).
_SLASH = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".java", ".c", ".h", ".cpp", ".go", ".rs", ".sql"}
_HASH = {".sh", ".bash", ".py", ".yml", ".yaml", ".toml"}


def blank(text: str, ext: str = ".ts") -> str:
    """`text` with comments and string bodies replaced by spaces, length and newlines kept.

    `ext` selects the comment syntax. The default suits the C-family files these guards
    were written for; pass the real extension when the caller knows it.
    """
    ext = ext.lower()
    # SQL uses `--` for line comments and does NOT use `//`.
    sql = ext == ".sql"
    slash = ext in _SLASH and not sql
    hash_ = ext in _HASH

    out = list(text)
    i = 0
    n = len(text)

    def space(start: int, end: int) -> None:
        """Blank [start, end), keeping newlines so line numbers survive."""
        for k in range(start, min(end, n)):
            if out[k] != "\n":
                out[k] = " "

    while i < n:
        c = text[i]

        # ── a line comment ──────────────────────────────────────────────────────
        if slash and c == "/" and i + 1 < n and text[i + 1] == "/":
            j = text.find("\n", i)
            j = n if j == -1 else j
            space(i, j)
            i = j
            continue
        if sql and c == "-" and i + 1 < n and text[i + 1] == "-":
            j = text.find("\n", i)
            j = n if j == -1 else j
            space(i, j)
            i = j
            continue
        if hash_ and c == "#":
            j = text.find("\n", i)
            j = n if j == -1 else j
            space(i, j)
            i = j
            continue

        # ── a block comment ─────────────────────────────────────────────────────
        if (slash or sql) and c == "/" and i + 1 < n and text[i + 1] == "*":
            j = text.find("*/", i + 2)
            j = n if j == -1 else j + 2
            space(i, j)
            i = j
            continue

        # ── a string literal ────────────────────────────────────────────────────
        if c in ("'", '"', "`"):
            quote = c
            j = i + 1
            while j < n:
                if text[j] == "\\":
                    j += 2  # an escape consumes the next byte, whatever it is
                    continue
                if quote == "`" and text[j] == "$" and j + 1 < n and text[j + 1] == "{":
                    # An interpolation is CODE. Blank the literal run that precedes it,
                    # then hand the braces back to the main loop by stepping out.
                    space(i + 1, j)
                    depth = 1
                    k = j + 2
                    while k < n and depth:
                        if text[k] == "{":
                            depth += 1
                        elif text[k] == "}":
                            depth -= 1
                        k += 1
                    # Re-enter the string after the interpolation closes.
                    i = k
                    # The remainder of the template is still a string; keep scanning it
                    # as one by rewriting the opening quote position.
                    rest = text.find(quote, k)
                    if rest == -1:
                        return "".join(out)
                    # Recurse over the inner expression so nested strings are handled.
                    inner = blank(text[j + 2 : k - 1], ext)
                    out[j + 2 : k - 1] = list(inner)
                    j = k
                    # Continue the while-loop looking for the closing quote.
                    continue
                if text[j] == quote:
                    break
                if text[j] == "\n" and quote != "`":
                    break  # an unterminated single-line string: do not eat the file
                j += 1
            space(i + 1, j)
            i = j + 1
            continue

        i += 1

    return "".join(out)


# ─────────────────────────────────────────────────────────────────────────────────
# Self-test. A count floor goes stale the moment the work it guards gets done; planted
# inputs hold at any count, including zero. Every case below is a shape that has produced
# a wrong number in this codebase or in `ibms-app`.
# ─────────────────────────────────────────────────────────────────────────────────

_CASES = [
    # (name, ext, source, must_still_contain, must_not_contain)
    (
        "a URL inside a string is not a comment  <- the 42->38 defect",
        ".ts",
        'await page.route("http://localhost:4000/api/x", h); const real = 1;',
        ["const real = 1", "page.route"],
        [],
    ),
    (
        "a real line comment goes",
        ".ts",
        "const a = 1; // .status = 'CLOSED'\nconst b = 2;",
        ["const a = 1", "const b = 2"],
        [".status ="],
    ),
    (
        "a block comment quoting the shape it explains removing",
        ".ts",
        "/* was: expect(page.getByText('x')).toHaveCount(0) */\nconst keep = 1;",
        ["const keep = 1"],
        ["toHaveCount", "getByText"],
    ),
    (
        "a quoted /* does not open a comment",
        ".ts",
        "const s = \"/* not a comment\"; const after = 2;",
        ["const s =", "const after = 2"],
        [],
    ),
    (
        "an escaped quote does not end the string early",
        ".ts",
        'const s = "a\\"// still in string"; const after = 3;',
        ["const after = 3"],
        ["still in string"],
    ),
    (
        "a template interpolation is code and survives",
        ".ts",
        "const t = `total ${round(premium)} JOD`;",
        ["round(premium)"],
        ["total", "JOD"],
    ),
    (
        "a hash in a .ts file is not a comment",
        ".ts",
        "class A { #priv = 1; }",
        ["#priv = 1"],
        [],
    ),
    (
        "a hash in a .sh file is a comment",
        ".sh",
        "MONEY='premium' # round(premium) in a comment\necho ok",
        ["echo ok", "MONEY="],
        ["round(premium)"],
    ),
    (
        "SQL uses -- and not //",
        ".sql",
        "-- CHECK (length(btrim(\"reason\")) >= 99)\nALTER TABLE x ADD CONSTRAINT c CHECK (length(btrim(\"reason\")) >= 10);",
        [">= 10"],
        [">= 99"],
    ),
    (
        "a // inside a SQL string is not a comment and -- inside one is not either",
        ".sql",
        "INSERT INTO t VALUES ('-- not a comment'); SELECT 1;",
        ["SELECT 1", "INSERT INTO t"],
        ["not a comment"],
    ),
    (
        "an unterminated string does not swallow the rest of the file",
        ".ts",
        "const bad = 'oops\nconst after = 4;",
        ["const after = 4"],
        [],
    ),
    (
        "positions and line count are preserved",
        ".ts",
        "a // x\nb /* y\nz */ c\nd",
        [],
        [],
    ),
]


def _self_test() -> int:
    failures = []
    for name, ext, src, must, must_not in _CASES:
        got = blank(src, ext)
        if len(got) != len(src):
            failures.append(f"{name}: length changed {len(src)} -> {len(got)}")
            continue
        if got.count("\n") != src.count("\n"):
            failures.append(f"{name}: newline count changed")
            continue
        for needle in must:
            if needle not in got:
                failures.append(f"{name}: lost code {needle!r}")
        for needle in must_not:
            if needle in got:
                failures.append(f"{name}: kept prose {needle!r}")

    for f in failures:
        print(f"  FAIL  {f}")
    print(f"\n  code_text self-test: {len(_CASES) - len({f.split(':')[0] for f in failures})}"
          f"/{len(_CASES)} cases clean, {len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    import sys

    if "--self-test" in sys.argv:
        raise SystemExit(_self_test())
    print(blank(sys.stdin.read(), sys.argv[1] if len(sys.argv) > 1 else ".ts"), end="")
