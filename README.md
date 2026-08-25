# ibms-brain

The shared brain for the **Insurance Brokerage Management System (IBMS)** build program — a system for a licensed insurance/reinsurance broker operating in Jordan, aligned to CBJ insurance regulation, Jordan's Personal Data Protection Law No. 24 of 2023 (PDPL), and ISO/IEC 27001 + 27701.

This repo is not itself a monorepo of services — the engineering codebase lives in the sibling [`ibms-app`](https://github.com/SHOUQALMAHARBAH/IBMS-APP) repo, which vendors this repo as a pinned git submodule. This repo is what `ibms-app` (and any future service repo) inherits: the standards, agent definitions, architecture decisions, and domain knowledge extracted from the approved business context and privacy-compliance documents.

> Unlike the starter kit's default flow, this brain was **not** filled from PR review history — there isn't any yet. It was filled from `IBMS_Full_Scope_Context_Document.docx` (the master business/regulatory scope) and the already-approved PCMS compliance package (`PRIV-STD-01..04`, `PRIV-SOP-01..10`, `PRIV-FRM-01..10`, `PRIV-SRS-01/02`). See `CLAUDE.md` § What this brain is for.

---

## Get started

```bash
bash scripts/brain-setup.sh
```

Then open this directory in Claude Code (or Cursor / Codex / Windsurf). `CLAUDE.md` and `AGENTS.md` load automatically.

Check health at any time:

```bash
bash scripts/brain-doctor.sh
```

---

## Staying current

This repo is loaded into every session, and rules land continuously. Before starting work — here or in a future service repo — sync:

```bash
git fetch origin main
git pull --rebase origin main   # only if behind AND clean AND on main
```

A stale brain means missing rules the reviewer blocks on. Full rule: [`meta/lex/brain-freshness.md`](meta/lex/brain-freshness.md).

---

## What's here

```
ibms-brain/
  meta/
    lex/          Rules that gate every PR — non-negotiable
    context/      Domain knowledge — data model, lifecycles, roles, PCMS module map, glossary
    designs/      Architecture/compliance decisions with the reasoning preserved
    agents/       Agent definitions (source of truth; mirrored to .claude/agents/)
    guides/       Setup and contributing guides — advisory, not enforced
    templates/    PR, ticket, and doc templates
  .claude/
    agents/       Mirror of meta/agents/ — this is what Claude Code loads
    hooks/        Enforcement scripts
    commands/     Slash commands
  CLAUDE.md       Loaded into every session
  AGENTS.md       Agent routing rules
```

---

## Modules

No repo/service split exists yet. The two module groups this brain currently governs:

| Module group | What it does |
|------|-------------|
| Core IBMS (Sales/CRM, Policy, Claims, Finance, Compliance) | The 74-process operating model — lead through renewal. See `meta/context/policy-lifecycle.md`, `meta/context/claims-lifecycle.md`. |
| PCMS M01–M12 | Governance, consent, DSR, data collection/access, retention/disposal, third-party risk, data sharing, incident/breach, DPIA, audit toolkit, gap-closure tracking. See `meta/context/pcms-privacy-modules.md`. |

---

## Agents

| Agent | Role |
|-------|------|
| `@code-reviewer` | Post-implementation quality and security review |
| `@software-developer` | Feature implementation, bug fixes, refactoring |

**Mandatory review gate:** any change touching workflow/approval logic, financial (premium/commission/claim) calculations, or Confidential/Highly Confidential data (see `meta/context/glossary.md` § data classification) must be reviewed before pushing.

---

## Standards

| Document | What it governs |
|----------|----------------|
| [`meta/lex/money-decimal-jod.md`](meta/lex/money-decimal-jod.md) | Decimal arithmetic on premium/commission/claim amounts |
| [`meta/lex/workflow-state-transitions.md`](meta/lex/workflow-state-transitions.md) | Status fields only change through a transition function |
| [`meta/lex/maker-checker-segregation.md`](meta/lex/maker-checker-segregation.md) | No self-approval on KYC, policy checking, refunds, disposal, DSR closure |
| [`meta/lex/sensitive-data-handling.md`](meta/lex/sensitive-data-handling.md) | Highly Confidential data handling |
| [`meta/lex/pdpl-sla-timers.md`](meta/lex/pdpl-sla-timers.md) | Statutory SLA timers are tracked data, not documentation |
| [`meta/lex/workspace-updates.md`](meta/lex/workspace-updates.md) | Keeping this repo's own docs current |
| [`meta/lex/brain-freshness.md`](meta/lex/brain-freshness.md) | Session-start sync |
| [`meta/lex/code-review.md`](meta/lex/code-review.md) | Review format, finding codes, severity |

---

## Mindset

Research before architecture. Architecture before execution. Never the other way.

Rules live in `lex/`. If it's not there, it's not a rule — it's a suggestion someone will forget by Thursday.

`context/` exists so nothing has to be explained twice. To a human or to an agent.

The brain grows by use, never by a documentation sprint.
