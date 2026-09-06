# PCMS — the privacy/compliance module map

**Last verified:** 2026-09-07 · **Owner:** DPO (role, not yet a named person)

## What this is

The organization already has an **approved** Privacy Compliance Management System (PCMS): 1 governing Policy, 4 Standards (`PRIV-STD-01..04`), 10 Procedures (`PRIV-SOP-01..10`), 10 Forms (`PRIV-FRM-01..10`), and a Requirements Specification (`PRIV-SRS-01`, companion data dictionary `PRIV-SRS-02`) defining 12 system modules, M01–M12. This is the single source of truth for every consent, retention, breach, DSR, and third-party rule IBMS needs. **IBMS does not define its own privacy rules — it implements PCMS.** See `meta/designs/2026-08-pcms-source-of-truth.md` for why that's a hard boundary, not a convenience.

## The shapes

```
M01  Governance & Policy Repository        — versioned policy documents, review cycles
M02  Data Inventory & Classification       — the four-tier model, per-product field templates
M03  Consent Management                    — ConsentRecord lifecycle, grant/withdrawal
M04  Data Subject Request (DSR) Management — Access/Correction/Deletion/Objection workflow
M05  Data Collection & Access Governance   — minimum-field templates; access provisioning/review
M06  Data Retention & Secure Disposal      — RetentionScheduleItem, DisposalBatch, LegalHold
M07  Third-Party & Vendor Risk Management  — risk tiering, DPA tracking
M08  Data Sharing Approval                 — one-off shares + regulatory-channel fast-track
M09  Incident & Breach Management          — detection → containment → notification → RCA
M10  DPIA / Privacy-by-Design Screening    — 5-question gate before any new product/vendor
M11  Compliance & Audit Toolkit            — checklists, KPI dashboard, corrective actions
M12  Gap-Closure Project Tracking          — the master remediation plan and its tasks
```

Governing-document map (cite these, don't restate them):

| Module | Governing document(s) |
|---|---|
| M01 | Governing Policy |
| M02 | `PRIV-STD-02` |
| M03 | `PRIV-STD-01` §6.3, `PRIV-SOP-04`, `PRIV-FRM-04/05` |
| M04 | `PRIV-STD-01` §6.4, `PRIV-SOP-05`, `PRIV-FRM-01/02/03` |
| M05 | `PRIV-STD-02`, `PRIV-SOP-01/02/03` |
| M06 | `PRIV-STD-03`, `PRIV-SOP-07/08`, `PRIV-FRM-10` |
| M07 | `PRIV-STD-04`, `PRIV-SOP-10`, `PRIV-FRM-07` |
| M08 | `PRIV-STD-04` §6.1/§6.5, `PRIV-SOP-06`, `PRIV-FRM-09` |
| M09 | Governing Policy §12, `PRIV-SOP-09`, `PRIV-FRM-06` |
| M10 | `PRIV-STD-01` §6.6, `PRIV-FRM-08` |
| M11 | Compliance Toolkit (6 tools: checklist, annual plan, internal-audit checklist, management-review checklist, privacy KPI dashboard, corrective-action register) |
| M12 | The gap-closure master plan spreadsheet |

## The rules that aren't obvious

- **`IBMS_Full_Scope_Context_Document.docx` Part 6 and Part 9 are a cross-reference, not a second spec.** The document says this explicitly: "Wherever this document's terminology differs from the source documents ... PRIV-SRS-01 and its source Standards/Procedures are authoritative." If you find a discrepancy between this brain's context files and a PRIV-* document, the PRIV-* document wins — file a `/brain-gap` to fix the context file, don't code against the discrepancy.
- **Data classification is a single four-tier model, not per-entity ad hoc rules**: Public / Internal / Confidential / Highly Confidential (`PRIV-STD-02`; full handling requirements in `meta/lex/sensitive-data-handling.md`). Every Part 4 IBMS entity and every PCMS entity carries one of these four labels — there is no fifth tier and no IBMS-specific scheme.
- **Consent and contractual-necessity processing are always two separate, independently-actionable controls.** A single combined checkbox is a named compliance defect in `PRIV-SOP-04`, not a design choice available to engineering.
- **A Deletion DSR with an open retention flag cannot be closed as "fully fulfilled."** The system must force a partial-fulfilment outcome with a retained-data justification referencing the specific `RetentionScheduleItem` (M04 business rule). This is a common wrong-shortcut: closing the ticket instead of recording the partial state.
- **Record destruction is always dual-control** (Department Manager nominates, DPO approves) **and always produces a Certificate of Destruction** — a `DisposalBatch` cannot reach `Closed` without one attached (M06).
- **Regulatory-channel data shares (CBJ Data Portal/iFile) still get classification and minimum-necessary-data checks** even though the standard vendor-risk-assessment step is bypassed (M08, `PRIV-STD-04` §6.1). "It's going to the regulator" is not an exemption from classification discipline.
- **The DPO may be the same person as the Compliance Officer only where no material conflict of interest with IT/security operations exists** (Part 5.1) — do not assume the two roles are always distinct, or always combinable; it's a case-by-case call recorded per organization.
- **`IBMS_Full_Scope_Context_Document.docx`'s Part 6 section numbers and `PRIV-SRS-01`'s M01-M12 module numbers are two DIFFERENT taxonomies, not aliases of each other.** Two backlog Part D checklist items — Cross-Border Transfer and Notices — both cite "Part 6.2" in the Prisma schema's own doc comments, but NEITHER maps onto a single named M01-M12 module: M05 is already taken ("Data Collection & Access Governance," a different system), and no other M-number describes either one either. Discovered when a build session initially mislabeled Cross-Border Transfer as "M05" by pattern-matching the next unused-looking number instead of checking the module table above — caught and fixed before push. Cite these two by "Part 6.2" alone; do not invent an M-number for a backlog item the map doesn't name.

## Where the code lives

**All of Part D's nine backlog items now have real code** — `apps/api/src/modules/pdpl/`
(`ibms-app`), all under backlog Part D §5.1 / Process #52, built across four sessions:
**M03 (Consent Management)** and **M04 (Data Subject Request Management)** landed
2026-09-04/05 — see `meta/context/consent-management.md` and
`meta/context/data-subject-requests.md`. **M06 (Data Retention & Secure Disposal)**
landed 2026-09-07 — see `meta/context/data-retention-and-disposal.md`. The remaining six
items (Cross-Border Transfer, **M08** Third Parties & Data Sharing, **M10** DPIA
Screening, Notices, Records of Processing Activities, and the DPO Workspace aggregate
screen) landed the same day — see `meta/context/part-d-completion.md` for all six.
**M01, M02, M05, M07 (beyond backlog #71's Vendor risk-tiering slice), M09 (built
separately as Part C #55), M11, and M12 have no PDPL-module-specific code** — M09's own
Incident/breach workflow already exists (`compliance-risk` module), just not filed under
this PDPL umbrella; M07's Vendor/DataProcessingAgreement CRUD lives in
`supporting-operations` (backlog #67/#71), same situation.

Field-level schema for all 14 PCMS entities: `PRIV-SRS-02_Data_Dictionary_and_Entity_Model.xlsx`, sheets `PolicyDocument` through `User - Role`. Process flow, business rules, and service levels for each module: `PRIV-SRS-01_Privacy_Compliance_System_Requirements_Specification.docx` §5.1–5.12.

## Out of scope for this file

RBAC permission grid across all 12 modules — `PRIV-SRS-01` §9. IBMS-side business process detail (KYC, policy checking, claims) — `meta/context/policy-lifecycle.md` and `meta/context/claims-lifecycle.md`. SLA values and escalation — `meta/lex/pdpl-sla-timers.md`.
