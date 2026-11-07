"""
Does this edit set a workflow `status` outside the transition engine?

Backs `enforce-state-transitions.sh`. Enforces `meta/lex/workflow-state-transitions.md`.

## Three defects this replaces, each measured in `ibms-app` on 2026-11-07

**(a) THE EXEMPTION WAS BY PATH SUBSTRING AND EXEMPTED FAR MORE THAN THE ENGINE.** The old
line was:

    echo "$FILE_PATH" | grep -qiE 'transition|workflow|state_machine|stateMachine' && exit 0

Any file whose PATH contained "workflow" or "transition" was skipped whole. Measured against
`ibms-app`: **14 tracked source files match**, of which **5** are the engine and **9** are not
— four DTOs (`transition-lead.dto.ts`, `transition-renewal-case.dto.ts`,
`transition-rfq-insurer.dto.ts`, `workflow-history-query.dto.ts`), a React component
(`WorkflowHistoryLink.tsx`), a web lookup table, a migration, and two parity specs. A DTO is
exactly where a status default would be smuggled in, and it was exempt.

So the exemption is now a MARKER INSIDE THE FILE. A file claims the exemption by carrying
`@implements-workflow-transitions` in its own text, which means the claim is visible to anyone
reading the file and shows up in a diff when somebody adds it. A path cannot be made to do that.

**(b) THE PATTERN COULD NOT SEE THE SHAPE THIS STACK WRITES.** The old scan matched
`.status =`, `['status'] =` and `["status"] =` — an EQUALS. Prisma writes a COLON:

    prisma.policy.update({ where: { id }, data: { status: 'CLOSED' } })

Measured across `apps/api/src`: the old pattern found **8** non-spec lines (25 including
specs), while `status:` appears on **298** non-spec lines. So the guard was blind to the normal
way status is set in the repository it was written for, and the 8 it did find were the
in-memory and audit-snapshot shapes rather than database writes.

The fix is not "also match `status:`" — that would refuse correct work. `where: { status: … }`
is the OPPOSITE of a violation: it is the status-conditional write that
`meta/lex/race-safe-invariants.md` REQUIRES. So this scanner brace-matches the `data:` payload
of a Prisma write and looks only inside it, and says so in its message.

**(c) IT READ RAW TEXT, SO A COMMENT OR A STRING COUNTED.** Everything goes through
`code_text.blank()` first — see that module for the measured reason (a regex comment-stripper
truncated real code at every `http://` URL and moved a figure by four in the direction that
looked like progress). A guard that reads code TOKENISES.

## What it deliberately does not do

It does not resolve which models the engine governs — it cannot, because the hook sees one
edit, not the schema. `ibms-app` answers that question properly in
`apps/api/src/modules/workflow/status-writes.inventory.spec.ts`, which reads the whole tree,
resolves governed entities from `WORKFLOW_TRANSITIONS`, and runs in CI. **This hook is the
fast feedback at the keystroke; that spec is the gate.** Where the two disagree, the spec wins.

**AND THAT LIMIT IS WHY THIS HOOK IS NOT REGISTERED IN `ibms-app`.** Measured 2026-11-07,
before wiring it anywhere — the figure is the whole argument:

    files this scan would block:  63 of 1,861 tracked .ts/.tsx

and **not one of the three classes is a violation of the lex**:

  * **~40 are test fixtures.** `prisma.claim.create({ … status: 'REGISTERED' })` in an e2e
    spec is setting up a scenario, not bypassing the engine at runtime.
  * **2 are filter builders** — `where.status = filter.status` in
    `claim.repository.ts:113` and `policy.repository.ts:125`. Assigning into a `where`
    object is the opposite of a status write.
  * **The rest write a `status` column on an entity the lex does not govern** —
    `PaymentChannel`, `SlaPolicy`, `ServiceRequest`, `RiskRegisterItem`, `Role`,
    `ReconciliationException`, `WatchlistDatasetVersion` and a dozen more. The lex § Rule
    names the governed entities; nothing in a single edit says which list a model is on.

None of the three is fixable here without inventing an exemption the lex does not contain —
and a name-based exemption is the very defect (a) replaced. So the measurement is recorded,
the hook stays correct-by-the-letter for the repo it was written for, and the registration
decision is made on evidence rather than on the assumption that more guards are better.
**A ratchet on a partial resolver is a red build on a correct tree.**

Run `python status_write_scan.py --self-test` for the proof.
"""

from __future__ import annotations

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from code_text import blank  # noqa: E402

#: A file carrying this in its own text IS the transition implementation and is exempt.
#: A marker, never a path substring — see the module docstring, defect (a).
EXEMPT_MARKER = "@implements-workflow-transitions"

#: Direct assignment to a `.status` property. `(?!=)` so `==` and `===` are comparisons.
_ASSIGN = re.compile(r"\.status\s*=(?!=)")

#: The closing half of a bracket assignment, `] = `. The KEY is read from the original text —
#: see `_bracket_assignments` for why it cannot be matched in one pass.
_BRACKET_ASSIGN = re.compile(r"\]\s*=(?!=)")

#: A quoted `status`, as a computed property key.
_STATUS_KEY_LITERAL = re.compile(r"^\s*['\"]status['\"]\s*$")


def _bracket_assignments(original: str, code: str) -> list[int]:
    """Offsets of every `x['status'] = …` in `code`, keyed from `original`.

    TWO PASSES, AND THE REASON IS WORTH KEEPING: `blank()` blanks a string literal's BODY,
    so by the time the code is safe to search, `row['status'] = 'OPEN'` reads
    `row['      '] = '    '` and the key has gone. Matching the key before blanking instead
    would read a quoted example inside a comment as a real write.

    So the STRUCTURE (`[ … ] =`) is found in the blanked code, where prose cannot forge it —
    a bracket inside a string literal is blanked along with the rest of the body — and the
    KEY is then read back out of the original text at that exact span.
    """
    found = []
    for m in _BRACKET_ASSIGN.finditer(code):
        close = m.start()
        depth = 1
        i = close - 1
        while i >= 0 and depth:
            if code[i] == "]":
                depth += 1
            elif code[i] == "[":
                depth -= 1
            i -= 1
        if depth:
            continue  # unbalanced fragment
        open_at = i + 1
        if _STATUS_KEY_LITERAL.match(original[open_at + 1 : close]):
            found.append(open_at)
    return found

#: The opener of a Prisma write whose argument object we then brace-match.
_WRITE = re.compile(r"\.(\w+)\.(create|update|updateMany|upsert|createMany)\(\s*\{")

#: `status:` — a key, not a comparison.
_STATUS_KEY = re.compile(r"\bstatus\s*:")


def _brace_body(text: str, open_at: int) -> str:
    """The text inside the `{ … }` whose opening brace is at `open_at`.

    Unbalanced input is normal here — a hook sees an edit fragment, not a whole file — so an
    unclosed brace yields everything to the end rather than raising.
    """
    depth = 1
    i = open_at + 1
    start = i
    while depth and i < len(text):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
        i += 1
    return text[start : i - 1 if depth == 0 else len(text)]


def _data_payload(body: str) -> str:
    """The `data: { … }` object inside a Prisma call's argument object, or ''.

    Only `data:` counts. `where: { status: … }` is the race-safe conditional the lex
    REQUIRES, and an early version of this scan in `ibms-app` conflated the two and
    reported four false positives.
    """
    m = re.search(r"\bdata:\s*\{", body)
    if not m:
        return ""
    return _brace_body(body, m.end() - 1)


def findings(file_path: str, content: str) -> list[str]:
    """Every status write in `content` that bypasses the engine, as `line: text`."""
    if EXEMPT_MARKER in content:
        return []

    ext = os.path.splitext(file_path)[1] or ".ts"
    code = blank(content, ext)
    lines = content.splitlines()
    hits: dict[int, str] = {}

    def record(offset: int) -> None:
        line_no = code.count("\n", 0, offset) + 1
        if line_no not in hits:
            raw = lines[line_no - 1].strip() if line_no - 1 < len(lines) else ""
            hits[line_no] = raw

    for m in _ASSIGN.finditer(code):
        record(m.start())

    for offset in _bracket_assignments(content, code):
        record(offset)

    for m in _WRITE.finditer(code):
        body = _brace_body(code, m.end() - 1)
        payload = _data_payload(body)
        if payload and _STATUS_KEY.search(payload):
            record(m.start())

    return [f"{n}: {hits[n]}" for n in sorted(hits)]


# ─────────────────────────────────────────────────────────────────────────────────
# Self-test — planted inputs, not a count floor. A count floor refuses a correct tree the
# moment the work it guards gets done; these hold at any count including zero.
#
# Per the batch rule this scanner was written under: EVERY guard that reads source is proven
# on a file carrying the shape it strips INSIDE A STRING LITERAL. Cases 5-8 are that proof.
# ─────────────────────────────────────────────────────────────────────────────────

_CASES = [
    # (name, path, source, expect_blocked)
    ("direct property assignment", "a.ts", "claim.status = 'CLOSED';", True),
    ("bracket assignment", "a.ts", "row['status'] = 'OPEN';", True),
    (
        "a Prisma data payload — the shape the old pattern could not see",
        "a.ts",
        "await p.policy.update({ where: { id }, data: { status: 'CLOSED' } });",
        True,
    ),
    (
        "a multi-line Prisma data payload",
        "a.ts",
        "await p.claim.update({\n  where: { id },\n  data: {\n    status: 'SETTLED',\n  },\n});",
        True,
    ),
    # ── the string-literal and comment proofs ───────────────────────────────────
    (
        "a URL in a string does not hide a real write, and does not create one",
        "a.ts",
        'await page.route("http://x/y", h);\nconst ok = 1;',
        False,
    ),
    (
        "a comment quoting the forbidden shape is not an instance of it",
        "a.ts",
        "// never write claim.status = 'CLOSED' here\nconst ok = 1;",
        False,
    ),
    (
        "the shape inside a string literal is prose",
        "a.ts",
        "const msg = \"do not use data: { status: 'X' }\";",
        False,
    ),
    (
        "a block comment explaining a removed write",
        "a.ts",
        "/* was: p.policy.update({ data: { status: 'OLD' } }) */\nconst ok = 1;",
        False,
    ),
    (
        "a BRACKET assignment quoted inside a string is prose — the two-pass proof",
        "a.ts",
        "const msg = \"row['status'] = 1 is forbidden\";",
        False,
    ),
    (
        "a bracket assignment to a DIFFERENT key is not a status write",
        "a.ts",
        "row['closedAt'] = now;",
        False,
    ),
    # ── the correct patterns, which must NOT be refused ─────────────────────────
    (
        "a status-conditional write is the race-safe pattern the lex REQUIRES",
        "a.ts",
        "await p.policy.update({ where: { id, status: 'OPEN' }, data: { closedAt: now } });",
        False,
    ),
    (
        "reading or comparing a status is not writing one",
        "a.ts",
        "if (claim.status === 'CLOSED' && row.status == x) return claim.status;",
        False,
    ),
    (
        "a status filter in a findMany is not a write",
        "a.ts",
        "await p.claim.findMany({ where: { status: 'OPEN' } });",
        False,
    ),
    # ── the exemption ───────────────────────────────────────────────────────────
    (
        "the engine exempts itself by MARKER",
        "whatever.ts",
        "/* @implements-workflow-transitions */\nrow.status = next;",
        False,
    ),
    (
        "a path that merely says 'workflow' is NOT exempt — the old defect",
        "modules/workflow/dto/transition-lead.dto.ts",
        "lead.status = 'QUALIFIED';",
        True,
    ),
]


def _self_test() -> int:
    failures = []
    for name, path, src, expect in _CASES:
        got = bool(findings(path, src))
        if got != expect:
            failures.append(
                f"{name}: expected {'BLOCK' if expect else 'ALLOW'}, got {'BLOCK' if got else 'ALLOW'}"
            )
    for f in failures:
        print(f"  FAIL  {f}")
    print(
        f"\n  status_write_scan self-test: {len(_CASES) - len(failures)}/{len(_CASES)} cases correct,"
        f" {len(failures)} failure(s)"
    )
    return 1 if failures else 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        raise SystemExit(_self_test())
    path = sys.argv[1] if len(sys.argv) > 1 else ""
    for hit in findings(path, sys.stdin.read()):
        print(hit)
