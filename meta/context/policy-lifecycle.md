# Policy lifecycle — from Opportunity to Renewal

**Last verified:** 2026-09-01 · **Owner:** unassigned

## What this is

The path a piece of business takes from a confirmed insurance need through placement, issuance, mid-term change, and renewal. Source: `IBMS_Full_Scope_Context_Document.docx` Parts 3.2–3.6 and 3.9. Claims are handled separately — see `meta/context/claims-lifecycle.md`.

## The shapes

```
Opportunity.status:
  Needs Confirmed → RFQ Issued → Quotes Received → Comparison Built →
  Recommendation Drafted → (Compliance Check) → Sent to Client →
  Client Decision → Placement | Renegotiate | Closed-Lost

Policy.status (post-placement):
  Placement Confirmed → Issued (received from insurer) → Checking In Progress →
  Discrepancy | Verified → Delivered → Active

Endorsement/Cancellation.status:
  Requested → Submitted to Insurer → Insurer Confirmed →
  Financial Adjustment Calculated → (Refund Approval if applicable) →
  Applied → Client Notified

RenewalCase.status:
  Renewal Due → In Progress → Quotes Obtained → Recommended →
  Client Decision → Renewed | Lapsed | Cancelled
```

Client decision branches at two points and each routes differently: **Accept as recommended / Reject / Request further negotiation / Request alternative options / Request price reduction / Request coverage increase** — each is a distinct next step (Placement, RFQ closed, or renewed Negotiation), not a single generic "declined" state.

## The rules that aren't obvious

- **Policy Checking must be performed by someone other than whoever requested/placed the cover — a hard system rule, not best practice** (Part 3.4). See `meta/lex/maker-checker-segregation.md`. A discrepancy (e.g., requested limit JOD 5,000,000, issued limit JOD 3,000,000) puts the policy in `Discrepancy — Correction Requested` and blocks Delivery until resolved; this is logged as a Professional Indemnity risk event, not silently corrected and moved on.
- **Comparison is never price alone.** The Quotation Comparison must be built across price + coverage + exclusions + deductibles + limits + insurer quality + service. A submission on a price-only comparison is a controls failure, not a shortcut (Part 3.3 Controls).
- **A Recommendation favoring a materially higher-commission insurer over a comparable/better-value competing offer requires an explicit Conflict of Interest disclosure before it can be sent to the client** (Part 3.3) — this is a system gate, not a documentation afterthought.
- **Cover Notes/Binders are a real interim state with a tracked expiry**, used when urgent cover is needed before full policy issuance — model this explicitly, don't fake it as an early Policy row.
- **Negative endorsements (return premium) trigger the Refund Management workflow**, which is maker/checker-gated by value threshold — the officer who raises the endorsement never self-approves the refund (Part 3.5).
- **Cancellation always computes a Commission Reversal tied to the same premium adjustment** — the two numbers must move together; a cancellation without a matching commission reversal is a broker overpayment exposure waiting to surface (Part 3.5 Risks).
- **Renewal starts automatically at a configurable lead time before expiry (default 90 days)**, and the Loss Ratio for the expiring period is computed and surfaced *before* the recommendation is drafted — never negotiated blind (Part 3.9). No renewal action within the lead-time window escalates to Customer Retention, not silence.
- **A mid-cycle risk change since the last renewal** (new location, headcount growth) **triggers a fresh Risk Assessment before the renewal RFQ is issued** — a renewal is not automatically a roll-over of the last Risk Assessment.
- **Renewal terms declined or materially worsened by the insurer trigger full re-marketing** (a new RFQ to alternate insurers), not a simple roll-over attempt with the same insurer.
- **An RFQ follow-up threshold lapsing auto-marks the silent insurer's submission `NO_RESPONSE`** — it is not only an alert for a human to action. Each `RFQ` carries a configurable `followUpThresholdDays` (default 9), counted in Jordan business days from each `RFQInsurer.sentAt`; the nightly follow-up sweep (Process 12, Market Placement) stamps the alert *and* advances a still-`SENT`/`VIEWED` submission to `NO_RESPONSE` through the workflow engine. This is a status change by a system actor, so it is race-conditional: an insurer response landing first makes the auto-move a no-op. `NO_RESPONSE` is **not terminal** — a late-responding insurer can still be moved `NO_RESPONSE → QUOTED / DECLINED`. Source: no CBJ/Part-3.3 document specifies the turnaround or the auto-vs-alert choice — the threshold default and the auto-advance are `ibms-app` product decisions (backlog Part C #11–12), draft pending a real market-practice figure.

  - **"Silent" is decided against the `Quotation` table too, not `RFQInsurer.status` alone.** Capturing an insurer's quote (backlog Part C #13, `QuotationService`) writes a `Quotation` row directly and *best-effort* moves the matching `RFQInsurer` `→ QUOTED` — but that transition is logged, never thrown, so a race or a transient failure can leave the submission `SENT`/`VIEWED` while a current `Quotation` for its `(rfqId, insurerId)` already exists. The follow-up sweep must **skip any submission that has a current `Quotation`** — an insurer that quoted is not silent, even if its status column has not caught up. Generalised: **`RFQInsurer.status` is not the authoritative "has this insurer quoted?" signal — the `Quotation` table is** (`QuotationService` documents the same rule on its own side). If the sweep ignores this, a genuinely-quoted insurer is mislabelled `NO_RESPONSE` until someone revises the quote; the damage is bounded (`NO_RESPONSE → QUOTED / DECLINED` is legal, and downstream Comparison #14 / Recommendation #16 read the `Quotation` table, not the status column) but the status column is then wrong. `ibms-app` product decision (Part C #13), no source document.

## Where the code lives

Nothing yet — no engineering repo exists.

## Out of scope for this file

Needs Assessment and Risk Assessment (pre-Opportunity) — Part 3.2 of the context document; not yet split into its own file, add one the first time this area causes a real gap. Claims handling — `meta/context/claims-lifecycle.md`. Commission calculation mechanics and financial reconciliation — Part 3.6 of the context document; not yet split into its own file.
