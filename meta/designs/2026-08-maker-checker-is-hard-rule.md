# Design: Maker/checker is a system-enforced hard rule, not a procedural guideline

**Status:** accepted · **Date:** 2026-08-22 · **Author:** shouq · **Service:** IBMS — approval workflows

## Context

Segregation of duties on high-risk actions (Policy Checking, KYC approval, refunds, commission reversal, record destruction) is common in insurance-broker operating procedure everywhere, and is often implemented as a documented procedure enforced by training and spot-audit rather than by the system itself — a manager tells staff not to self-approve, and periodic audit checks whether they did. `IBMS_Full_Scope_Context_Document.docx` explicitly considers this framing and rejects it: Part 5.2 states the Policy Checking segregation "is a hard rule, not just best practice."

The question this decision settles: does IBMS build maker/checker as a **procedural** control (documented, trained, spot-audited) or a **structural** one (the system will not let the same user identity fill both roles, full stop)?

## Decision

Maker/checker is structural. Every workflow table with an approval step carries a checker/approver identity distinct from the creator identity, and the system refuses the approval action when they match — this is a data-model and application-logic requirement, not a UI nicety or a documented convention. `meta/lex/maker-checker-segregation.md` is the enforceable form of this decision.

## Alternatives considered

| Option | Why it lost |
|---|---|
| Procedural control — documented policy, staff training, periodic internal audit sampling | Part 3.4 states that an undetected mismatch between requested and issued coverage is "the single largest source of broker professional-indemnity claims" in the source operating model. A procedural control catches this in a sample audit, after the fact — exactly the window in which the mismatch causes real client and broker harm. A structural control catches it at the moment of the attempted self-approval. |
| Structural control, but with a manager override that logs the exception | This reintroduces the procedural failure mode through a side door — an override that's "just this once, I'll log it" is exactly how the original problem happens, and a logged override still lets the bad state occur before anyone reviews the log. If a genuine emergency requires bypassing maker/checker, that is a break-glass path with its own post-hoc Compliance review (a different, explicitly separate control), not a quiet override baked into the same approval action. |
| Structural for financial actions (refunds, commission) only, procedural for KYC/policy-checking | Part 5.2 applies the same "hard rule" language uniformly across KYC approval, Policy Checking, and refunds — the source document does not distinguish financial from non-financial maker/checker pairs in how strictly they're enforced, and a mixed enforcement model would be its own source of confusion about which pairs are "real" rules. |

## Consequences

**Accepted cost:** every approval-bearing schema needs two identity fields and a guard from day one, even for low-volume workflows where a procedural control would have been cheaper to build first and harden later.

**Revisit if:** a specific approval pairing turns out, after real usage data, to have effectively zero self-approval attempts and a structural guard is measurably slowing down a time-critical workflow (e.g., the 4-hour incident-containment SLA in `meta/lex/pdpl-sla-timers.md`) — at that point the tradeoff between speed and structural safety for *that specific pairing* is worth re-examining, on evidence, not on convenience.
