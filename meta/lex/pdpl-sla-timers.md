# Lex: PDPL SLA Timers Are Tracked Data

**Enforcement level: mandatory — no exceptions.**

## Rule

Every workflow with a statutory or contractual SLA carries the deadline as a **queryable field with an automated escalation job** — not as a note in a ticket, a comment, or tribal knowledge. If a workflow type has an SLA and ships without a timer + escalation, it is not done.

The current SLA registry (all sourced from `PRIV-SRS-01` §5, cross-checked against `IBMS_Full_Scope_Context_Document.docx` Part 6.2):

| Workflow | SLA | Escalation |
|---|---|---|
| Consent withdrawal (M03) | 2 business days | — |
| DSR — Access / Deletion (M04) | 15 business days (one +15 extension, Access only, reason logged) | Auto-escalate to DPO at T-3 days; to General Manager 3 days after that if still open |
| DSR — Correction / Objection (M04) | 10 business days | Same escalation path as above |
| Termination access revocation (M05) | Same business day | Critical alert to IT management if still open after 24h |
| Quarterly access review (M05) | 15 business days from cycle generation | — |
| Disposal batch execution (M06) | 30 days from batch approval | Feeds KPI: % disposal batches completed within 30 days |
| Legal Hold necessity review (M06) | Every 6 months | Auto-reminder to DPO/Legal Counsel |
| Vendor annual review (M07) | Annual, Medium/High tier | — |
| Data sharing decision (M08) | 3 business days standard; 1 business day for a recognized regulatory channel | — |
| Incident containment (M09) | 4 hours for critical severity | — |
| Material incident — Senior Management notification (M09) | 1 hour from Material classification | — |
| DPIA screening review (M10) | 5 business days if any screening question is "Yes" | — |
| Renewal workflow start | 90 days before expiry (default, configurable) | Escalates to Customer Retention on inactivity |
| Claim follow-up (insurer non-response) | Per broad line family (Jordan business days from the claim's `REGISTERED` timestamp): `ibms-app`'s drafted `CLAIM_FOLLOWUP_THRESHOLD_DAYS_BY_FAMILY` — `motor` 7 / `property` 10 / `medical` 7 / `liability` / `marine` 15 / else 9 (the Part 3.7 worked example). **The non-9 values are drafted / unsourced** (no per-line table in Part 3.7) — same status as `CLAIM_LARGE_THRESHOLD_JOD` / #16's 10 % / 2 pp; replace with sourced figures when a broker authority matrix / SOP supplies them. See `meta/context/claims-lifecycle.md` § insurer non-response (Process 27). | Auto-generated `ClaimFollowUpAlert` (nightly + on-demand sweep) |

## What triggers this rule

- Any new workflow type carrying a statutory or contractual deadline
- Any change to a value in the SLA registry above — it must be sourced from the governing PRIV-SOP/PRIV-STD document, not picked arbitrarily
- Building the DPO Workspace, Compliance Dashboard, or any screen listing open SLA-bearing items — it must read the live timer field, not a derived guess

## What does NOT trigger this rule

- Internal target times with no statutory or contractual basis (e.g., an informal "try to reply within a day" courtesy target) — track these as ordinary KPIs, not SLA timers
- Workflows explicitly exempt from a standard SLA path per their governing document (e.g., the M08 regulatory-channel fast-track)

## How it is enforced

**Review gate:** `@code-reviewer` checks that any new workflow with a row in the table above stores the deadline as data and that an escalation job/notification exists — cite this file and the specific `PRIV-SRS-01` module section in the finding.

**CI check (once a workflow engine exists):** a "workflow SLA lint" job that fails if a new workflow type is added to the codebase without a matching entry in a machine-readable SLA registry. This file is the source for that registry until one exists in code — when it does, this table should be generated from it, not maintained by hand in two places.

## Rationale

`PRIV-SRS-01` treats every one of these SLAs as a named business rule with its own escalation path (e.g., M04: "auto-escalate ... to the DPO and, after 3 additional days, to the General Manager, any DSR within 3 business days of SLA expiry that is not yet Closed"). A missed PDPL deadline is a regulator-facing compliance failure, not an internal miss — Jordan's PDPL grace period ended 17 March 2025, so these are live obligations, not future ones. A ticket comment saying "remember, DSRs are 15 days" degrades the moment the person who wrote it moves to a different ticket.
