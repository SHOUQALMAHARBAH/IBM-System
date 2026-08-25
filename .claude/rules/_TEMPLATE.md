---
paths:
  - "{{FILL: glob, e.g. src/api/**/*.ts}}"
---

# {{FILL: rule set name}}

> **Path-scoped rules load only when the agent reads a matching file.**
> Zero context cost otherwise. This is the right home for area-specific
> standards that would otherwise bloat CLAUDE.md.
>
> Delete the `paths:` frontmatter to load this unconditionally at session start.
> Rename this file to something descriptive — `django-api.md`, `react.md`.

- {{FILL: short, concrete, checkable instruction}}
- {{FILL: another}}

> Keep these short. Long rule files reduce adherence. If a rule needs a full
> page of explanation and a rationale, it belongs in `meta/lex/` with a hook,
> and this file can cite it in one line.
