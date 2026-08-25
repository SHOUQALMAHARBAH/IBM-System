# Domain Glossary

**Last verified:** 2026-08-22

Only terms that mean something specific here and something different everywhere else. Full bilingual (EN/AR) term list is in `IBMS_Full_Scope_Context_Document.docx` Appendix B — this file covers the subset that's easy to get wrong plus the ones with no Arabic equivalent worth restating.

| Term | Here it means | Not to be confused with |
|---|---|---|
| **Broker** | The system's own organization — a licensed insurance/reinsurance intermediary under CBJ Instructions No. (11) of 2005. Acts as **Data Controller** for its own client/prospect/employee data, and in some flows as a **processor-like** party for data received from insurers. | An insurer (a "Company" in local usage) — the broker places business *with* insurers, never underwrites itself. |
| **Customer** | Individual or corporate client holding one or more Policies; central entity alongside Policy (Part 4). Carries KYC, risk rating, contact data, and UBOs if corporate. | **Data Subject** — broader; includes insured employees under Group Medical/Life, drivers under Motor Fleet, and beneficiaries who are not the contracting Customer. Every Customer is a Data Subject; not every Data Subject is a Customer. |
| **Insured Person** | A natural person covered by a policy who is *not* the contracting Customer (an employee under Group Medical, a driver under Motor Fleet, a beneficiary). Carries their own consent and data-subject-rights record where required (Part 4.1 note). | Customer. |
| **Lead / Prospect** | Pre-Customer record from any acquisition source; converts 0..1 to Customer. | Customer — a Prospect cannot yet hold a Policy; onboarding/KYC gates the conversion. |
| **Opportunity** | A specific insurance placement need — new business or renewal — that an RFQ is issued against. | Policy — an Opportunity may close-lost and never become one. |
| **RFQ / Market Submission** | The broker's request sent to a shortlist of insurers for a given Opportunity. Tracked per insurer: sent / viewed / quoted / declined / no response. | Quotation — the insurer's *response* to an RFQ, not the request itself. |
| **Recommendation** | The broker's documented, reasoned advice on which quotation to take — retained as professional-indemnity evidence (Part 3.3). Never "cheapest wins" without the reasoning recorded. | A Quotation — a Recommendation is the broker's judgment call layered on top of one or more quotations. |
| **Policy Checking** | The mandatory, independent (maker/checker) line-by-line comparison of Requested Coverage vs. Issued Policy before delivery (Part 3.4). | Policy Issuance — Checking happens *after* the insurer issues, and blocks Delivery until any discrepancy is resolved. |
| **Cover Note / Binder** | An interim state providing urgent cover before full policy issuance, with a tracked expiry. | A Policy — a Cover Note is not the final contract and must resolve to one. |
| **Endorsement** | A mid-term amendment to an in-force Policy (add/remove vehicle, Sum Insured change, etc.). Positive (adds premium) or negative (returns premium) — never overwrites prior policy history. | Renewal — an Endorsement happens mid-cycle; a Renewal happens at expiry. |
| **Loss Ratio** | `Claims ÷ Premium` for a given client/policy/line/period (Part 3.9, 2.3 #30) — the number that drives renewal negotiation. | A claims count or a claim amount alone — Loss Ratio is always the ratio, computed, not eyeballed. |
| **Sum Insured** | The insured value basis for a property/asset line, derived from a Risk Assessment/Survey (Part 3.2) — not the same as market/replacement value unless explicitly reconciled. | Premium — Sum Insured drives Premium, it is not Premium. |
| **Maker/Checker** | The mandatory segregation-of-duties pattern: the person who requests/places/nominates an action is never the person who approves/checks it (Part 5.2). System-enforced, not a procedural courtesy — see `meta/lex/maker-checker-segregation.md`. | A second reviewer added informally — maker/checker requires the checker role to be *structurally* unable to be the maker. |
| **DPO** | Data Protection Officer — owns the Consent Register, DSR queue, Legal Hold register, breach classification, and final dual-control sign-off on record destruction (Part 5.1). May be the same person as the Compliance Officer *only* where no material conflict of interest with IT/security operations exists. | Compliance Officer — related but distinct role; the DPO's authority over data-subject rights and destruction is independent of general regulatory compliance duties. |
| **PCMS** | Privacy Compliance Management System — the already-approved governing Policy + 4 Standards + 10 Procedures + SRS that IBMS's compliance module consumes. See `meta/context/pcms-privacy-modules.md`. | A second, IBMS-specific privacy spec — there isn't one; PCMS is the single source of truth (`meta/designs/2026-08-pcms-source-of-truth.md`). |
| **DSR** | Data Subject Request — the PDPL Access/Correction/Deletion/Objection request type, SLA-governed (M04). | DSAR — some sources use this term; `PRIV-SRS-01` treats `DataSubjectRequest (DSR)` as canonical. |
| **Material** vs **Non-Material** (incident) | The formal severity classification of a personal-data incident (M09) that triggers regulator/data-subject notification. Material classification is irreversible without Senior Management co-sign. | "Severity" in a general engineering-incident sense — this is a specific, regulated classification with its own workflow gate. |

## Actor vocabulary

Who exists in the system and what each is allowed to do. Full role catalogue and mandatory segregation rules: `meta/context/roles-and-segregation-of-duties.md`.

| Actor | Can (summary) | Cannot |
|---|---|---|
| Sales / Relationship Officer | Create Lead/Prospect, capture KYC, initiate RFQ | Approve own KYC file or recommendation above threshold |
| Placement / Technical Officer | Manage RFQ, quotations, negotiation | Perform Policy Checking on a policy they placed |
| Policy Checking Officer | Independently verify issued policy vs. requested coverage | Have placed the policy under review |
| Claims Officer | Register, document, follow up claims | Approve large claim settlements alone |
| Finance / Collections Officer | Raise invoices, record receipts, calculate commission from governed rate tables | Approve own refunds/write-offs |
| Compliance Officer | Approve KYC/EDD, manage sanctions/PEP screening, conflict-of-interest disclosures | Originate sales transactions |
| DPO | Own Consent Register, DSR queue, breach classification, destruction final sign-off | Originate commercial/sales transactions |
| Branch/Department Manager | Approve escalations/refunds within delegated authority | Bypass maker/checker above their delegated authority |

## Deprecated terms

None yet — this is a new build with no prior codebase, so there is no legacy vocabulary to carry forward. Add rows here the first time a term is renamed after go-live.
