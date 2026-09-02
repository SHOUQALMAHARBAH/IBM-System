# Claims lifecycle

**Last verified:** 2026-08-22 · **Owner:** shouq

## What this is

The path a reported loss takes from notification to closure, and how it feeds renewal negotiation via Loss Ratio. Source: `IBMS_Full_Scope_Context_Document.docx` Part 3.7 (and Part 3.8 for the complaint path a declined claim can trigger).

## The shapes

```
Claim.status:
  Notified → Registered → Documentation In Progress →
  Under Assessment (insurer) →
  Approved | Partially Approved | Declined →
  Settled → Closed

Complaint.status (triggered by a disputed claim decision):
  Logged → Assigned → In Progress → Resolved → Closed | Escalated
```

## The rules that aren't obvious

- **The system tracks Estimated Loss, Approved amount, Deductible, and Net Settlement as four distinct figures — not just the final payout.** Example from the source: Estimated Loss JOD 20,000 → Approved JOD 17,500 → Deductible JOD 2,500 → Net Settlement JOD 15,000. Collapsing these into one number loses the audit trail an insurer dispute needs (Part 3.7).
- **A claim must validate against the coverage in force at the loss date, accounting for endorsement history** — not just the current PolicySchedule. A claim under a policy that was endorsed mid-term needs the schedule *as it stood on the loss date* (Part 3.7, cross-referenced in `meta/context/data-model.md`).
  - *(filed via `/brain-gap` at `ibms-app` Part C #23, Claim Notification — all `ibms-app` product decisions, no source document)* The resolution is: find the `PolicySchedule` version whose window `[effectiveFrom, effectiveTo)` contains the loss date. The set of schedule versions **is** the materialised endorsement history (every #22 endorsement APPLY closes the open version at its effective date and opens a new one), so iterating them is "querying against endorsement history" — a separate `Endorsement`-table query is not needed.
  - **`Policy.expiryDate` is an independent upper bound.** Nothing closes the open schedule row at expiry, so its `effectiveTo` stays `null` forever — a post-expiry loss whose date is still `>= effectiveFrom` of an open version would otherwise resolve as covered. Reject it explicitly against the policy period.
  - **Reject on notify, don't reject on read.** An unresolvable loss date is a hard 422 at `POST /claims`. But a *later* read of an already-notified claim must not 422: a mid-term loss can be validly notified while cover is open, then a #22 cancellation closes that version forward, and re-resolving now finds no window. The read returns the claim with a "coverage not resolvable" flag, never an error.
- **Insurer non-response auto-generates a follow-up alert** once elapsed time since submission exceeds a configurable threshold (example given: no response after 9 days from a 1 August submission triggers an alert on day 10). This must be a scheduled/computed alert, not a manual tickler.
- **A claim declined by the insurer triggers a Complaint Management case if the client disputes it, and a Claims Analytics record regardless** — the analytics record is not conditional on a complaint being raised; every declined claim feeds Loss Ratio and Insurer Performance data whether or not the client pushes back.
- **Third-party-involved claims carry additional data and, where relevant, a subrogation/recovery flag** — do not model third-party claims as a variant of the same fields as a standard claim; the recovery flag is a distinct piece of state that drives a different downstream process.
- **Claim Documentation (Process 25) is a mandatory checklist per claim type**, computed from the doc types in the "four distinct figures" row above plus a `claim_form` and `correspondence` (claim form / police report / medical report / photos / invoices / repair estimate / expert report). The checklist is what gates the move to insurer assessment.
  - *(filed via `/brain-gap` at `ibms-app` Part C #25 — `ibms-app` product decisions, no source document)* **There is no per-line mandatory-document matrix in Part 3.7** (it lists the document *types* only) and **`Policy.insuranceLine` is un-enumerated free text**, so `ibms-app` derives a broad line *family* (`property` / `motor` / `medical` / `liability` / `marine` / `other`) by keyword and maps each family to a drafted required set (e.g. `property` → `claim_form` + `photo` + `repair_estimate`; `medical` → `claim_form` + `medical_report` + `invoice`; any third-party loss also → `police_report`). Both the classifier and the matrix are drafted / unsourced — same status as `CLAIM_LARGE_THRESHOLD_JOD` (#23), #16's 10 % / 2 pp, #22's refund / short-period constants. The `docType` enum has no "financial statements" value, so a Business Interruption claim (family `property`) inherits `photo` / `repair_estimate` rather than an accounts requirement — a known gap.
  - **The first document attach advances `Claim REGISTERED → DOCUMENTATION_IN_PROGRESS`** through the workflow engine, **best-effort** (`DOCUMENTATION_IN_PROGRESS` is a forward-progress marker, not a safety gate — unlike #20's `DISCREPANCY` — so a failed advance is logged and retried on the next attach, not thrown). Documents can be filed at any status from `REGISTERED` onward (Part 4.2 — the electronic file grows throughout the lifecycle).
  - **A claim `Document` is linked ONLY through the `ClaimDocument` join** (carrying `docType`), not `Document.policyId` — the join is the canonical link; a future "full insurance file" view unions `Document WHERE policyId = X` with the claim documents.
- **Claim Assessment (Process 26) = adjuster survey/investigation tracking + two engine transitions.** `ibms-app` models it as: (a) `POST /claims/:id/assessment/adjuster-progress` stamps `Adjuster.surveyCompletedAt` / `investigationCompletedAt`; (b) `POST /claims/:id/assessment/submit` drives `Claim DOCUMENTATION_IN_PROGRESS → UNDER_ASSESSMENT`; (c) `POST /claims/:id/assessment/decision` drives `UNDER_ASSESSMENT → APPROVED | PARTIALLY_APPROVED | DECLINED`. Each transition also writes a domain `ClaimStatusHistory` row. The four settlement figures (estimated / approved / deductible / net) are **not** recorded here — that is Process 28's `Settlement`; Process 26 records only the *decision*.
  - *(filed via `/brain-gap` at `ibms-app` Part C #26 — `ibms-app` product decisions, no source document)*
  - **The `→ UNDER_ASSESSMENT` move is a hard safety gate on the mandatory-document checklist**, not best-effort (contrast the #25 `REGISTERED → DOCUMENTATION_IN_PROGRESS` advance) — the row above already says "the checklist is what gates the move to insurer assessment", and `ibms-app` enforces it as a 422 recomputed from the live `ClaimDocument` rows at submit time (never a stored `documentationComplete` snapshot — the #16 "re-derive the gate from live data at the decision point" generalisation).
  - **The `UNDER_ASSESSMENT → verdict` move is gated on the loss adjuster having completed BOTH the survey and the investigation** (`Adjuster.surveyCompletedAt` AND `investigationCompletedAt` set) — a 422 otherwise. **Drafted, unsourced**: Part 3.7 lists "survey/investigation completion" as tracked data but does not state it blocks the verdict. Same drafted-rule status as `CLAIM_LARGE_THRESHOLD_JOD` (#23), the #25 checklist matrix, #16's 10 % / 2 pp. A real rule (does a desktop assessment with no site survey ever skip this? is investigation optional for a small motor claim?) should replace it.
  - **The adjuster completion stamps and the verdict are write-once** — a different value on an already-set stamp is a 409; a different verdict once one is recorded is a 409 (there is no amend endpoint). A client who disputes the verdict routes to **Complaint Management (Process 42)** — consistent with the "a declined claim triggers a Complaint case if the client disputes it" row below; the claim's own status is not walked backwards.
  - **No maker/checker at Process 26.** Recording the insurer's verdict is single-actor Claims work — it is not the broker approving a payment (`meta/lex/maker-checker-segregation.md` § "what does NOT trigger this rule"). The mandatory second approver is at settlement (Process 28).
- **Large claims and any claim payment processed by the broker require a second approver** — maker/checker again (`meta/lex/maker-checker-segregation.md`), same pattern as Policy Checking and refunds.
  - *(filed via `/brain-gap` at `ibms-app` Part C #23 — `ibms-app` product decisions, no source document)* **The "large claim" money threshold is a drafted, unsourced constant** (`ibms-app`'s `CLAIM_LARGE_THRESHOLD_JOD`) — no CBJ / Part-3.7 / broker authority-matrix figure specifies it; the Part 3.7 worked example uses an Estimated Loss of JOD 20,000 as a *routine* claim, which only weakly places the threshold above that. Same drafted-constant status as #16's 10% / 2 pp bands and #22's `REFUND_APPROVAL_THRESHOLD_JOD` / `SHORT_PERIOD_CLIENT_RETURN_PERCENT`. A real figure should replace it.
  - **`Claim.isLargeClaim` set at notification (Process 23) is an advisory SNAPSHOT, not the gate.** The second-approver requirement at settlement (Process 28) must be **re-derived from live data** — the approved amount once known, and whether the broker is processing the payment — at the decision point, never trusted from the notification-time flag. Same generalisation as the #16 review ("gates are re-derived from live data at the decision point, not read from a stale draft snapshot") and the #22 APPLY-must-re-check-approval point.
- **Claims feed Loss Ratio (`Claims ÷ Premium`), which is computed and surfaced before renewal recommendation is drafted** (Part 3.9) — Loss Ratio is not a report generated after the fact; it is an input the renewal workflow depends on.
- **Health/medical claim data is Sensitive/Highly Confidential Personal Data under PDPL** (Part 3.7 Regulatory Basis; see `meta/lex/sensitive-data-handling.md`) — claim documentation handling for medical lines is not just an operational concern, it's a classification-driven handling requirement from first contact.
  - *(Part C #25)* Concretely: a `medical_report` `ClaimDocument` may only be recorded at `HIGHLY_CONFIDENTIAL` — `ibms-app` rejects (422) any other classification on that `docType`. A claim document's `fileName` (it can name an injured person / describe a medical event) and `storageRef` are **excluded from the audit snapshot** (same rule as #18-19's `policyDocumentAuditSnapshot`); the authorised in-app read returns `fileName` but is itself logged as a sensitive-data access.

## Where the code lives

Nothing yet — no engineering repo exists.

## Out of scope for this file

Complaint Management as its own process (SLA, escalation to the regulator/dispute-resolution mechanism) — Part 3.8 of the context document; split into its own file the first time complaints handling causes a real gap independent of claims. Insurer Performance scoring — Part 2.3 process #60; not yet documented here.
