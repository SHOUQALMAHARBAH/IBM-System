# Lex: KYC/AML SLA Timers

**Enforcement level: mandatory — no exceptions.**

## Rule

Every KYC file carries its compliance-review deadline and its periodic
re-KYC due date as queryable data with an automated escalation/sweep, the
same "tracked data, not a note in a ticket" posture
`meta/lex/pdpl-sla-timers.md` requires for PDPL SLAs — this file exists
because AML/KYC timing is a **different regulatory domain** (CBJ customer
due-diligence obligations, not PDPL) that `pdpl-sla-timers.md`'s registry
does not and should not cover.

Two SLA-shaped figures are current tracked deadlines with a real
enforcement mechanism (see below), but their **values are drafted
placeholders, not PRIV-SOP/PRIV-STD-sourced facts**:

| Timer | Draft value | Source |
|---|---|---|
| KYC compliance review (standard) | 5 business days from screening | **DRAFT, UNSOURCED** |
| KYC compliance review (enhanced due diligence) | 15 business days from screening | **DRAFT, UNSOURCED** |
| Periodic re-KYC — `RiskLevel.STANDARD` | 12 months from approval | **DRAFT, UNSOURCED** |
| Periodic re-KYC — `RiskLevel.HIGH` | 6 months from approval | **DRAFT, UNSOURCED** |

Do not cite these four numbers as compliant or PRIV-SOP-sourced in a
regulator-facing context, a PR, or a ticket until a real CBJ AML
customer-due-diligence source document supplies the actual figures — treat
them exactly as `meta/lex/backup-rpo-rto.md` treats its draft RPO/RTO
numbers: "the number currently being tested," not a confirmed one.

## What triggers this rule

- Any change to the four draft values above, or to which `RiskLevel` maps
  to which re-KYC cadence
- Building a Compliance Dashboard or any screen listing KYC files by
  deadline — it must read the live `SlaTimer`/`KYCRecord.nextReviewDueAt`
  field, not a derived guess (same requirement `pdpl-sla-timers.md` makes
  for its own registry)
- The day a real CBJ AML source document is identified — replace the
  `DRAFT, UNSOURCED` values and citations with the real ones in the same
  change that updates this file

## What does NOT trigger this rule

- The 14 PDPL-sourced SLA types already covered by
  `meta/lex/pdpl-sla-timers.md` — this file does not restate or duplicate
  that registry, it covers the two KYC/AML timers that registry explicitly
  does not
- An internal target with no statutory/contractual basis and no tracked
  deadline field behind it (there is none here — both timers described
  above are real tracked fields, only their values are draft)

## How it is enforced

**Code:** `apps/api/src/modules/sla/sla-registry.config.ts`'s
`kyc_standard_review`/`kyc_edd_review` entries (consumed by the same
generic `SlaTimerService`/escalation sweep backing the PDPL registry —
backlog A.8) track the compliance-review deadline; `apps/api/src/modules/
customer/kyc.service.ts`'s `REVIEW_CADENCE_MONTHS` constant computes
`KYCRecord.nextReviewDueAt` at approval time, swept daily by
`KycPeriodicReviewScheduler`. Both citation strings are literally
`DRAFT, UNSOURCED` in code, not a fabricated `PRIV-SOP-*` reference.

**Review gate:** `@code-reviewer` checks that any PR changing these four
values updates the citation here too, and does not silently upgrade a
draft value to look sourced without a real document backing it.

## Rationale

Backlog Part C #3-4 (Customer Acquisition/Onboarding) needed a KYC
compliance-review SLA and a re-KYC cadence to make the EDD path and
periodic-review sweep genuinely testable — but neither
`pdpl-sla-timers.md`'s registry (all 14 rows are PDPL-sourced: consent,
DSR, disposal, incident, DPIA, renewal, claim follow-up) nor any other
`meta/context`/`meta/lex` file covers CBJ AML customer-due-diligence
turnaround time at all. Shipping the feature with no number would leave
the EDD/periodic-review machinery permanently untested dead code; shipping
it with a number silently treated as authoritative would be worse — an
uncited timing rule in a compliance system is a rule someone will argue
with, correctly, the day a regulator asks where it came from. This file is
the explicit, findable place that number lives as a draft until Compliance
supplies the real one, the same treatment `backup-rpo-rto.md` gives its own
draft RPO/RTO figures.
