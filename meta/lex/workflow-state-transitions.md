# Lex: Workflow State Transitions

**Enforcement level: mandatory — no exceptions.**

## Rule

Never assign a workflow `status` field directly. Every entity that carries a workflow state — KYC/Customer onboarding, Policy Checking, Claim, Complaint, Endorsement/Cancellation, DisposalBatch, DataSubjectRequest (DSR), IncidentReport, DPIA screening, ThirdParty assessment — moves through a `transition()` (or equivalently named) function that validates the move is legal, writes the audit row, and fires any side effect the transition implies (e.g., an escalation timer, a notification, a KPI recompute). Assigning `.status = 'Approved'` directly skips all of it.

## What triggers this rule

- Any assignment to a status/state field on the entities listed above (full list: Part 4.1 core entities in `IBMS_Full_Scope_Context_Document.docx`, and the per-module state machines in `PRIV-SRS-01` §7 — DSR: `Received → Identity Verified → ... → Closed`; Incident: `Reported → Contained → Impact Assessed → Classified → Notified → Recovered → Closed`)
- Admin/back-office tooling and one-off scripts — **not exempt**
- Batch/nightly jobs that move many records at once (e.g., a renewal-due sweep, a retention-eligibility sweep)

## What does NOT trigger this rule

- Reading a status field
- API/serializer fields exposing status as read-only
- A one-time data migration backfilling historical rows, where the workflow engine did not exist at the time the row was created — but this must be called out explicitly in the migration, not silent

## How it is enforced

**Hook:** `.claude/hooks/enforce-state-transitions.sh` — `PreToolUse` on `Write|Edit`, exits 2 on a regex matching direct status assignment (`\.status\s*=`, `\['status'\]\s*=`, `.status = "..."` shapes) outside a file/function named like `transition`, `workflow`, or `state_machine`. This is a starting pattern to tune once the stack is chosen — the point is that the check exists from day one, not that the regex is perfect.

**Review gate:** `@code-reviewer` checks admin/back-office tooling specifically — this is where the equivalent rule was violated most often in the reference example this brain's mechanics were modeled on, and IBMS has more admin-adjacent surfaces than a typical SaaS app (Compliance Officer console, DPO workspace, Branch/Department Manager approval screens).

## Rationale

Two independent parts of the source specification depend on transitions being the *only* path to a state change:

1. **Audit trail integrity.** Part 10.3 requires an immutable audit log of every create/read/update/delete/approve action with before/after values. A direct field write bypasses whatever code path writes that log.
2. **SLA and escalation timers.** `PRIV-SRS-01` ties the DSR, Incident, and Disposal SLA clocks to specific transitions (e.g., M04 step 2: "System automatically routes the DSR to the DPO and starts the applicable SLA timer" the moment status becomes `Received`). A direct assignment produces a record that *looks* like it reached the right state while every timer, notification, and escalation that was supposed to fire on that transition silently never runs — which is a worse failure than an obviously broken record, because nobody notices until an SLA is already breached.
