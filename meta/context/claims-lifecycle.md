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
- **Large claims and any claim payment processed by the broker require a second approver** — maker/checker again (`meta/lex/maker-checker-segregation.md`), same pattern as Policy Checking and refunds.
  - *(filed via `/brain-gap` at `ibms-app` Part C #23 — `ibms-app` product decisions, no source document)* **The "large claim" money threshold is a drafted, unsourced constant** (`ibms-app`'s `CLAIM_LARGE_THRESHOLD_JOD`) — no CBJ / Part-3.7 / broker authority-matrix figure specifies it; the Part 3.7 worked example uses an Estimated Loss of JOD 20,000 as a *routine* claim, which only weakly places the threshold above that. Same drafted-constant status as #16's 10% / 2 pp bands and #22's `REFUND_APPROVAL_THRESHOLD_JOD` / `SHORT_PERIOD_CLIENT_RETURN_PERCENT`. A real figure should replace it.
  - **`Claim.isLargeClaim` set at notification (Process 23) is an advisory SNAPSHOT, not the gate.** The second-approver requirement at settlement (Process 28) must be **re-derived from live data** — the approved amount once known, and whether the broker is processing the payment — at the decision point, never trusted from the notification-time flag. Same generalisation as the #16 review ("gates are re-derived from live data at the decision point, not read from a stale draft snapshot") and the #22 APPLY-must-re-check-approval point.
- **Claims feed Loss Ratio (`Claims ÷ Premium`), which is computed and surfaced before renewal recommendation is drafted** (Part 3.9) — Loss Ratio is not a report generated after the fact; it is an input the renewal workflow depends on.
- **Health/medical claim data is Sensitive/Highly Confidential Personal Data under PDPL** (Part 3.7 Regulatory Basis; see `meta/lex/sensitive-data-handling.md`) — claim documentation handling for medical lines is not just an operational concern, it's a classification-driven handling requirement from first contact.

## Where the code lives

Nothing yet — no engineering repo exists.

## Out of scope for this file

Complaint Management as its own process (SLA, escalation to the regulator/dispute-resolution mechanism) — Part 3.8 of the context document; split into its own file the first time complaints handling causes a real gap independent of claims. Insurer Performance scoring — Part 2.3 process #60; not yet documented here.
