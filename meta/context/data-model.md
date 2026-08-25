# Core Data Model

**Last verified:** 2026-08-22 · **Owner:** shouq

## What this is

The entity map the whole system is built around. Source: Part 4 of `IBMS_Full_Scope_Context_Document.docx`, cross-checked against `PRIV-SRS-02_Data_Dictionary_and_Entity_Model.xlsx` (field-level schema for the PCMS entities). No physical schema exists yet — this is the logical model to design the database against, not a description of an existing one.

**The model is Customer-centric and Policy-centric simultaneously.** Do not build around "policies" alone: one Customer holds many Policies; each Policy carries many Endorsements, Claims, and PremiumTransactions.

## The shapes

```
Customer
  1..n Policy
  1..n RiskProfile
  1..n Complaint
  1..n Interaction (CRM log)

Lead / Prospect
  0..1 converts to → Customer

RiskProfile / Asset
  n..1 Customer
  1..n InsuranceProgramLine

Opportunity
  n..1 Customer
  1..n RFQ

RFQ / Quotation
  n..1 Opportunity
  n..1 Insurer
  versioned — never overwritten; renegotiation creates a new version

Recommendation / ClientDecision
  1..1 Opportunity

Policy
  n..1 Customer
  n..1 Insurer
  1..n Endorsement
  1..n Claim
  1..n PremiumTransaction

Endorsement
  n..1 Policy
  positive (adds premium) | negative (returns premium) — never overwrites prior history

Claim
  n..1 Policy
  1..n ClaimDocument
  1..1 Settlement
  — must validate against the coverage in force AT THE CLAIM DATE, accounting for
    endorsement history, not just the current schedule

PremiumTransaction / Invoice / Receipt
  n..1 Policy
  n..1 Customer
  n..1 Insurer

Commission / CommissionAgreement
  n..1 Insurer
  n..1 Policy/Transaction

Insurer
  1..n Policy
  1..n CommissionAgreement
  1..n Quotation

Complaint
  n..1 Customer
  0..1 Claim
  0..1 Policy

Document
  n..1 Customer/Policy/Claim/Opportunity (polymorphic)
  — version-controlled, date-controlled, access-controlled

User / Role / Permission
  n..n Role <-> Permission
  n..1 Employee

AuditLogEntry
  n..1 User
  polymorphic reference to any entity — immutable

ConsentRecord / DataSubjectRequest
  n..1 Customer (or any natural-person Data Subject — see Insured Person below)
```

## The rules that aren't obvious

- **A separate `Insured Person` entity is required**, distinct from `Customer`. A corporate Customer's data subjects extend beyond the Customer record itself — insured employees under Group Medical/Life, drivers under Motor Fleet, beneficiaries. Each carries its own ConsentRecord and data-subject-rights record where required. Do not model these as free-text fields on the Policy; they are first-class Data Subjects (Part 4.1 note, Part 6.3).
- **Claim validity is time-and-version-sensitive.** A Claim must resolve to the coverage that was actually in force at the loss date, which may not be the current PolicySchedule if an Endorsement happened in between. Query against Endorsement history, never against `Policy.current_schedule` alone (Part 3.7).
- **RFQ/Quotation are versioned, never overwritten.** A negotiation round produces a new Quotation version so the full negotiation history survives — this is the evidence trail for the Recommendation (Part 3.3).
- **Every Policy resolves to exactly one electronic Insurance File** — Application/Proposal, Risk Survey, Quotations, Comparison, Recommendation, Client Approval, Policy, Endorsements, Invoices, Receipts, Claims, Correspondence — each version-controlled and access-controlled, with deletion disallowed without a privileged, logged override (Part 4.2). This file, not the Policy row alone, is what an audit or regulator inspection actually looks at.
- **A file combining multiple classification levels is classified at the highest level present** — never averaged (`PRIV-STD-02` §6.7; see `meta/lex/sensitive-data-handling.md`). A Claim file with a medical report inside it is a Highly Confidential file.
- **AuditLogEntry is immutable and polymorphic** — every create/read/update/delete/approve action across every entity above, including read access to Sensitive Personal Data, not just writes (Part 10.3).

## Where the code lives

Nothing yet — no engineering repo exists. This section is the placeholder to fill the day schema design starts; do not invent file paths ahead of that.

## Out of scope for this file

Field-level types, required/optional flags, and validation rules for the 14 PCMS entities (PolicyDocument, DataInventoryItem, ConsentRecord, DataSubjectRequest, AccessProvisioningRequest, RetentionScheduleItem, ThirdParty/DPA, DataSharingApproval, IncidentReport, DPIARecord, CorrectiveAction, GapClosureTask, AuditLog, User/Role) live in `PRIV-SRS-02_Data_Dictionary_and_Entity_Model.xlsx` — that is the schema-design source for those entities, this file does not restate it. See `meta/context/pcms-privacy-modules.md` for how the two entity sets relate.
