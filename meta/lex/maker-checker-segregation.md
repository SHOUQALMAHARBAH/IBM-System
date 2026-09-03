# Lex: Maker/Checker Segregation of Duties

**Enforcement level: mandatory — no exceptions.**

## Rule

The person who **makes** (requests, captures, places, nominates) a high-risk action is never the same person who **checks/approves** it. This is a hard system rule, not a procedural guideline (`IBMS_Full_Scope_Context_Document.docx` Part 5.2 uses that exact phrase). The system must enforce it structurally — two distinct user identities on the maker and checker fields — not rely on a human remembering not to self-approve.

Covered actions (Part 5.2 and the M-series business rules in `PRIV-SRS-01`):

| Maker | Checker | Source |
|---|---|---|
| Officer who requests/places a policy | Policy Checking Officer | Part 5.2, Part 3.4 |
| Officer who captures KYC data | Compliance Officer who approves/activates | Part 5.2, Part 3.1 |
| Officer who raises a refund/write-off/commission reversal | Finance approver above the value threshold | Part 5.2, Part 3.5 |
| Department Manager who nominates a disposal batch | DPO who gives final approval | `PRIV-SRS-01` M06, Part 5.2 |
| Employee who requests a data share | DPO who approves it | `PRIV-SRS-01` M08 |
| Relationship Owner who assesses a third party | DPO who approves High-tier go-live | `PRIV-SRS-01` M07 |

## What triggers this rule

- Any new approval/workflow feature on the entities above
- Admin consoles and back-office override tools — **not exempt**; Part 3.1 states data deletion of an Insurance File record requires dual control (Department Manager + DPO) even when executed from an admin panel
- Database schema for any new workflow table — it must carry a checker/approver field distinct from the creator field

## What does NOT trigger this rule

- Read-only views
- Single-actor actions with no financial, legal, or data-deletion consequence (e.g., logging a customer interaction)
- Emergency break-glass access — but that path requires its own logged justification and post-hoc Compliance review, which is a separate control, not an exemption from this one
- **Maintaining a reference list** that only *records* data without executing anything — e.g. the `ibms-app` `PaymentChannel` list (Process 38): today a channel is optional metadata a `Receipt` / `Remittance` points at, it moves no money, so `payment-channel.manage` is single-actor Finance. **This exemption ends the moment the reference becomes load-bearing** — if the channel becomes mandatory on a receipt/remittance, or a "release payment" step ever executes a transfer against it, an "approved-payee list" is a classic maker/checker control and this table gains a row (maker: the officer who adds the channel; checker: a distinct Finance approver), plus the `<> creator` guard.

## How it is enforced

**Review gate:** `@code-reviewer` is mandatory on any PR touching approval/workflow logic (see `CLAUDE.md` § Agents) and must specifically check that maker and checker resolve to different user IDs at the database or application-logic level, not just in the UI.

**Schema check (once a schema exists):** any migration adding a workflow table with an approval step must include a `CHECK` constraint or application-level guard that `approved_by_user_id <> created_by_user_id` (naming per `PRIV-SRS-02_Data_Dictionary_and_Entity_Model.xlsx`, e.g. `PolicyDocument.approved_by_user_id` "must differ from `owner_user_id`"). This is a review-gate obligation today; convert to a CI schema-linter check the day migrations exist.

## Rationale

Part 3.4 states plainly that an undetected mismatch between requested and issued coverage — the exact failure this control catches — is "the single largest source of broker professional-indemnity claims" in the source operating model. Part 5.2 independently derives the same requirement for KYC, refunds, and data destruction. This is the one rule in the whole system with the highest cost if silently bypassed: a self-approved policy check, refund, or KYC record looks indistinguishable from a correctly-checked one until the claim, audit, or regulator inquiry that proves otherwise.
