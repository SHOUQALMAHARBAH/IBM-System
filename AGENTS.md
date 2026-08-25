# Agent Instructions

Routing rules for any agent working in this workspace or in a future IBMS service repo.

## Session start — sync the brain

```bash
git fetch origin main
git rev-list --left-right --count HEAD...origin/main   # ahead behind
```

If behind **AND** the tree is clean **AND** you are on `main`:

```bash
git pull --rebase origin main
```

Then re-read `CLAUDE.md` § What's New. If the tree is dirty or you are on a feature branch, **fetch and notify — do not auto-pull.** Full rule: `meta/lex/brain-freshness.md`.

## Non-interactive shell commands

Always use non-interactive flags. `cp`, `mv`, and `rm` may be aliased to `-i` on some systems, which hangs an agent session indefinitely waiting for input nobody will type.

```bash
cp -f source dest
mv -f source dest
rm -rf directory
apt-get -y install <pkg>
ssh -o BatchMode=yes <host>
```

## Routing

| Task | Agent |
|---|---|
| Implement a feature, fix a bug, refactor | `@software-developer` |
| Review completed work before push | `@code-reviewer` |
| Add your own as they earn their place | |

## Before you write code

1. Read the relevant `meta/context/` file for the area you're touching — start with `meta/context/pcms-privacy-modules.md` if the work touches any personal data at all, which in IBMS is almost everything.
2. Read `meta/lex/` rules that apply. They are mandatory, not advisory.
3. If a decision seems arbitrary, check `meta/designs/` before changing it — the reasoning is probably recorded.
4. If the change concerns a regulatory obligation (PDPL, CBJ, ISO 27001/27701), cite the source document (`PRIV-STD-*`, `PRIV-SOP-*`, or a Part/section of `IBMS_Full_Scope_Context_Document.docx`) in the ticket or PR — this is a compliance system; an uncited rule is a rule someone will argue with, correctly.

## Session completion

Work is not complete until it is pushed.

1. Run the quality gates in `meta/context/verification-contract.md` — today that is `bash scripts/verify.sh`, which is honest that most engineering gates don't exist yet.
2. Update `CLAUDE.md` § What's New if the change is developer-facing (see `meta/lex/workspace-updates.md`).
3. Commit and push. `git status` must show up to date with origin.
4. Hand off — leave context for the next session.

Never stop before pushing. Never say "ready to push when you are" — push.
