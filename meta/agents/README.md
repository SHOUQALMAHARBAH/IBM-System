# Agent definitions

**Source of truth.** These files are mirrored to `.claude/agents/` by `.claude/hooks/mirror-agents.sh`, which is what the agent runtime actually loads.

**Never hand-copy between the two directories.** That is precisely how the copies drift — and the dangerous one is the mirror, because it is the one being loaded. A stale mirror means the agent confidently follows a rule you replaced last month.

## Start with two

`code-reviewer` and `software-developer`. Add a third only when a role has been invoked repeatedly with the same hand-typed preamble. That preamble *is* the agent definition — you already wrote it, several times, badly.

## Anatomy

Each definition has frontmatter (`name`, `description`, `model`) and a body covering: who the agent is, what it must read before acting, its operating procedure, and its output format. Keep the "must read" section pointed at `meta/lex/` and `meta/context/` rather than restating rules — restated rules drift from their source.
