# Design: PCMS is the single source of truth for privacy — IBMS Parts 6/9 are a cross-reference

**Status:** accepted · **Date:** 2026-08-22 · **Author:** shouq · **Service:** IBMS ↔ PCMS boundary

## Context

`IBMS_Full_Scope_Context_Document.docx` (the master business/technical scope for the insurance-broker system) has its own Part 6 (Data Protection & Privacy Requirements) and Part 9 (ISO/IEC 27701 extension), written to make the document self-contained. Separately, the organization had **already approved** a full Privacy Compliance Management System before this document existed: a governing Policy, 4 Standards (`PRIV-STD-01..04`), 10 Procedures (`PRIV-SOP-01..10`), 10 Forms, and a Requirements Specification (`PRIV-SRS-01`, with companion data dictionary `PRIV-SRS-02`) defining 12 system modules (M01–M12).

The two documents describe overlapping ground — consent, DSR handling, retention, breach notification — from two different vantage points (business/insurance-domain vs. privacy-program-domain), written by different processes at different times. Where their terminology or specifics differ (the document gives an example: "DSAR" vs. the canonical `DataSubjectRequest (DSR)` entity), a build team could reasonably treat either as authoritative, and without a decision, different engineers would pick differently.

## Decision

PCMS (`PRIV-STD-*`, `PRIV-SOP-*`, `PRIV-FRM-*`, `PRIV-SRS-01/02`) is the **single source of truth** for every privacy/consent/retention/breach/DSR/third-party rule. `IBMS_Full_Scope_Context_Document.docx` Parts 6 and 9 are read as a **cross-reference into PCMS**, not a parallel specification — the source document says this explicitly in its own text ("Part 6 and Part 9 of this document are NOT a specification for a second, parallel data-protection system... PRIV-SRS-01 and its source Standards/Procedures are authoritative"). This brain encodes that instruction as a structural rule: `meta/context/pcms-privacy-modules.md` is the IBMS-side map of the PCMS modules, and it defers to the PRIV-* documents on every point of substance rather than restating them as independently maintained facts.

## Alternatives considered

| Option | Why it lost |
|---|---|
| Treat IBMS Part 6/9 as its own authoritative spec and re-derive privacy rules from it during build | Two independently-maintained descriptions of the same rules drift the moment either one is updated, and drift here isn't cosmetic — it's the difference between meeting a PDPL SLA and missing one. The source document itself calls this out as the wrong path. |
| Merge both documents into one master privacy spec before build starts | Different audiences and different change cadence: PCMS is a compliance artifact reviewed and re-approved through a governance process (`PRIV-STD-01` §review cycle, M01 in `PRIV-SRS-01`); the IBMS context document is an engineering input that will be superseded by actual architecture decisions. Merging them ties PCMS's approval cycle to engineering's, which is backwards — compliance should not need an engineering sign-off to update a retention schedule. |
| Keep both as independent references and let each PR author judge which one governs for their change | This is what "no decision" looks like in practice, and the terminology mismatch the source document itself flags (DSAR vs. DSR) shows it already produces inconsistency even in the specification phase, before any code exists. |

## Consequences

**Accepted cost:** every IBMS-side context file that touches privacy has to actively cross-reference PCMS rather than being self-contained — slightly more clicking, in exchange for one place a rule can actually be wrong.

**Revisit if:** the organization ever formally retires the standalone PCMS toolkit and folds its content into IBMS's own governance (unlikely — PCMS predates IBMS and covers the whole organization, not just this system), or if a second business system besides IBMS needs to consume the same PCMS rules, at which point PCMS's status as an organization-wide (not IBMS-specific) source of truth becomes even more load-bearing, not less.
