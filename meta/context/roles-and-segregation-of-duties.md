# Roles and segregation of duties

**Last verified:** 2026-08-22 · **Owner:** unassigned

## What this is

The illustrative role catalogue and the mandatory segregation-of-duties (SoD) rules the access-control design must implement. Source: `IBMS_Full_Scope_Context_Document.docx` Part 5, cross-checked against the RBAC matrix in `PRIV-SRS-01` §9 for the PCMS-side roles (DPO, Legal Counsel, Senior Management, Auditor, System Administrator overlap with the IBMS-side roles below).

## The shapes

```
Role                          Can (summary)                          Cannot
─────────────────────────────────────────────────────────────────────────────────
Sales / Relationship Officer  Create Lead/Prospect, capture KYC,     Approve own KYC file, approve own
                               run Needs Assessment, initiate RFQ     recommendation above threshold

Placement / Technical Officer Manage RFQ, quotations,                Perform Policy Checking on a
                               negotiation, draft recommendation      policy they placed

Policy Checking Officer       Independently verify issued policy     Have placed the policy under review
                               vs requested coverage

Claims Officer                Register, document, follow up claims   Approve large claim settlements
                                                                       alone; approve own claim payments

Finance / Collections Officer Raise invoices, record receipts,       Approve own refunds/write-offs;
                               calculate commission from governed     alter commission rate tables
                               rate tables                            without approval

Compliance Officer            Approve KYC/EDD, manage sanctions/PEP  Originate sales transactions; act
                               screening, conflict-of-interest        as DPO on data-subject requests
                               disclosures, broker regulatory         unless formally dual-hatted
                               filings, third-party risk tiering

Branch/Department Manager     Approve escalations, refunds and       Bypass maker/checker above their
                               overrides within delegated authority;  delegated authority; self-approve
                               sign off destruction batch lists       their own escalations
                               (maker side of dual control)

Data Protection Officer (DPO) Owns Consent Register, DSR queue and   Originate commercial/sales
                               SLAs, Legal Hold register, Simplified  transactions; may be the same
                               DPIA decisions, breach classification  person as Compliance Officer only
                               and notification, final dual-control   where no material conflict with
                               sign-off on destruction                IT/security operations exists

System/Security Administrator Manage user provisioning, roles,       Access business data beyond what's
                               security configuration                 required for administration —
                                                                       must be logged and periodically
                                                                       reviewed

Executive / Management        View dashboards and reports across     Perform transactional maker/checker
                               the organization                       actions

External Auditor              Read-only access to logs, documents    Modify any record
(time-boxed)                  and workflow history for a defined
                               engagement period
```

## The rules that aren't obvious

- **Every mandatory SoD pairing is structural, not a UI convention** — the checker role must be *unable* to be the maker, enforced at the data/permission level. Full list and citations: `meta/lex/maker-checker-segregation.md`.
- **Data deletion of any Insurance File record is disabled by default.** The DPO alone decides whether a PDPL erasure request can be honored (checking the Retention Schedule and any Legal Hold), but the resulting physical/technical destruction batch always requires dual control — Department Manager sign-off **plus** DPO final approval — and is itself logged (Part 5.2, `PRIV-STD-03` §6.5).
- **Access to Sensitive Personal Data is restricted to roles with a documented need, and every access is logged** — including reads, not only writes (Part 5.2, Part 10.3).
- **The DPO/Compliance-Officer dual-hat is conditional, not default.** Do not assume org chart convenience settles this — Part 5.1 states it's allowed "only where no material conflict of interest with IT/security operations exists," which is a per-organization judgment call to record, not a system default.
- **System/Security Administrators are the one role explicitly required to have their own access logged and periodically reviewed** despite being the role that manages everyone else's access (Part 5.1) — don't treat admin accounts as exempt from the access-recertification cycle described in Part 10.1.
- **External Auditor access is time-boxed by design**, tied to a defined engagement period — not a standing role that happens to be read-only.

## Where the code lives

Nothing yet — no engineering repo exists. RBAC permission grid for the PCMS-side modules (M01–M12): `PRIV-SRS-01` §9.

## Out of scope for this file

Full field-level permission model (Read/Write/Request/Consult/Approve/Manage/Config, per `PRIV-SRS-01` §9's permission-level definitions) for each of the 12 PCMS modules — that table lives in `PRIV-SRS-01` and is cross-referenced from `meta/context/pcms-privacy-modules.md`, not restated here.
