# <Area / Service / Concept>

> **Written for an agent.** An agent cannot ask a follow-up question, cannot ask Sarah, and cannot infer your conventions. Use exact identifiers. Delete this block before committing.

**Last verified:** `<YYYY-MM-DD>` · **Owner:** `<name>`

## What this is

<Two or three sentences. What it does, where it sits, who calls it.>

## The shapes

<Exact model names, field names, enum values, endpoint paths, file paths.>

```
<ModelName>
  <field>: <type>          # <constraint or note>
  <status>: <ENUM_A | ENUM_B | ENUM_C>
```

## The rules that aren't obvious

<The things people get wrong. The transition that needs two approvers. The field that looks nullable but isn't. The endpoint that returns 200 on failure.>

## Where the code lives

- `<path/to/thing.py>` — <what's in it>
- `<path/to/other.py>` — <what's in it>

## Out of scope for this file

<What this deliberately does not cover, and where that lives instead. Prevents the file growing to cover everything and therefore nothing.>
