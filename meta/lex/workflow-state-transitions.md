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

**Hook:** `.claude/hooks/enforce-state-transitions.sh` — `PreToolUse` on `Write|Edit`, exits 2 on a direct status assignment. The scan is `.claude/hooks/status_write_scan.py`; run `python status_write_scan.py --self-test` for its 15 planted cases.

**Rewritten 2026-11-07. The previous paragraph described three defects as if they were the design**, and all three are measured in that module's docstring:

- **It exempted by PATH SUBSTRING** — *"outside a file/function named like `transition`, `workflow`, or `state_machine`"*. Measured against `ibms-app`: **14 tracked files match, 5 are the engine and 9 are not** — four DTOs, a React component, a web lookup table, a migration and two parity specs, all skipped whole. A DTO is exactly where a status default gets smuggled in. **A file now claims the exemption with the marker `@implements-workflow-transitions` IN ITS OWN TEXT**, so the claim is visible in the file and in a diff. A path cannot be made to do that.
- **It could not see the shape a Prisma stack writes.** It matched an `=`; Prisma writes a `:` — `data: { status: 'CLOSED' }`. The old pattern found **8** non-spec lines in `apps/api/src` where `status:` appears on **298**. The scan now brace-matches the `data:` payload and looks only inside it, so `where: { status: … }` — the race-safe conditional `race-safe-invariants.md` REQUIRES — is still not reported.
- **It read raw text**, so a comment or a string literal naming the shape counted as an instance of it. It tokenises now (`code_text.py`).

**THIS HOOK IS KEYSTROKE FEEDBACK, NOT THE GATE, AND IN `ibms-app` IT IS DELIBERATELY NOT REGISTERED.** Measured 2026-11-07 before wiring it: the corrected scan would block **63 of 1,861** tracked files there, and **none of the three classes is a violation of this rule** — ~40 are test fixtures seeding a scenario; two are filter builders (`where.status = filter.status`); the rest write a `status` column on an entity this rule does not govern (`PaymentChannel`, `SlaPolicy`, `ServiceRequest`, `RiskRegisterItem`, `Role` and a dozen more). **The cause is structural: § Rule above names the governed entities, and a hook that sees one edit cannot resolve that list.** `ibms-app` gates the question properly in CI with `apps/api/src/modules/workflow/status-writes.inventory.spec.ts`, which reads the whole tree, resolves the governed set from `WORKFLOW_TRANSITIONS`, and brace-matches single-line and multi-line payloads alike. **Where that spec and this hook disagree, the spec wins.**

**ONE THING THIS RULE DOES NOT SAY, and it is the owner's to settle**: whether a TEST FIXTURE that seeds a status is in scope. § What does NOT trigger this rule is silent on it, where `money-decimal-jod.md` explicitly exempts test fixtures. `ibms-app` has decided in practice — its gate excludes `.spec.` files and `apps/api/test/` — so the code and this document do not currently agree, and that is recorded here rather than resolved by a hook's exemption list.

**Review gate:** `@code-reviewer` checks admin/back-office tooling specifically — this is where the equivalent rule was violated most often in the reference example this brain's mechanics were modeled on, and IBMS has more admin-adjacent surfaces than a typical SaaS app (Compliance Officer console, DPO workspace, Branch/Department Manager approval screens).

## Rationale

Two independent parts of the source specification depend on transitions being the *only* path to a state change:

1. **Audit trail integrity.** Part 10.3 requires an immutable audit log of every create/read/update/delete/approve action with before/after values. A direct field write bypasses whatever code path writes that log.
2. **SLA and escalation timers.** `PRIV-SRS-01` ties the DSR, Incident, and Disposal SLA clocks to specific transitions (e.g., M04 step 2: "System automatically routes the DSR to the DPO and starts the applicable SLA timer" the moment status becomes `Received`). A direct assignment produces a record that *looks* like it reached the right state while every timer, notification, and escalation that was supposed to fire on that transition silently never runs — which is a worse failure than an obviously broken record, because nobody notices until an SLA is already breached.
