# Vendor Management (Domain H, backlog Part C #71 — M07)

**Last verified:** `2026-09-06` · **Owner:** `ibms-app`

## What this is

Process 71 — M07 (Third-Party & Vendor Risk Management: "risk tiering, DPA
tracking" per `pcms-privacy-modules.md`). Three checkboxes: risk tiering
(low/medium/high) before any data share or access grant; a mandatory Data
Processing Agreement for Medium/High tier with additional DPO approval for
High tier before the first share; mandatory annual review + confirmation of
data return/destruction on termination + access revocation within 2
business days.

Backlog #67 (Procurement) built the FOUNDATIONAL `Vendor` CRUD
(name/vendorType only) and explicitly deferred `riskTier`/
`annualReviewDueAt`/`terminationDataReturnConfirmedAt`/`accessRevokedAt` to
this process — same model, same module (`vendor.{config,service,
controller,module}.ts`), extended rather than duplicated.

## The shapes

```
Vendor
  riskTier:                          String?    # low | medium | high — no DB enum
  annualReviewDueAt:                 DateTime?
  terminationDataReturnConfirmedAt:  DateTime?  # the termination event itself
  accessRevokedAt:                   DateTime?  # must follow termination

DataProcessingAgreement
  vendorId:             String
  signedAt:              DateTime?
  assessedByUserId:      String?    # maker
  dpoApprovedByUserId:   String?    # checker — required only for High tier
  expiresAt:              DateTime?
```

`DataProcessingAgreement`'s maker/checker pair already had a DB `CHECK`
constraint (`DataProcessingAgreement_maker_checker_distinct`, migration
`20260826091424`, the A.5 foundational work) and an entry in
`common/maker-checker.util.ts`'s covered-pairs table — both dormant, zero
prior writer, until this process.

## The rules that aren't obvious

- **Checkbox 1 ("risk tiering ... before any data share or access grant")
  has NO live call site to enforce against.** `DataSharingApproval` (M08)
  has zero prior writer anywhere in this codebase (flagged `dormant: true`
  in `internal-controls.config.ts`'s `MAKER_CHECKER_REGISTRY`, same as
  `DataProcessingAgreement` was before this process), and no model
  represents a generic "access grant" at all. This process therefore built
  `computeDataShareReadiness()` (`vendor.config.ts`) as a pure, queryable
  rule (`GET /vendors/:id/data-share-readiness`) — an honest,
  forward-compatible gate with no live enforcement call site yet, NOT a
  claim that anything is actually blocked today. When M08 is eventually
  built, its own create path should call this function (or the service
  method wrapping it) rather than re-deriving the same rule.
- **Deletion-lock/dual-control confusion to avoid**: `roles-and-
  segregation-of-duties.md` and `maker-checker-segregation.md` both
  describe dual control (Department Manager + DPO) for "data deletion of
  an Insurance File record" / "the resulting physical/technical
  destruction batch" — that is the M06 Disposal `DisposalBatch` workflow
  (`raisedByUserId`/`approvedByUserId`, still unbuilt), a DIFFERENT,
  larger process from this one. #71's own maker/checker pair
  (`assessedByUserId`/`dpoApprovedByUserId` on `DataProcessingAgreement`)
  is a real, separate, ALREADY-NAMED pair in the maker/checker table — do
  not conflate the two when reading either lex file.
- **`vendor_termination_access_revocation` is a genuinely NEW SLA registry
  entry, not a dormant pre-seeded one.** Every other Domain H/G SLA this
  session found dormant-but-present (`termination_access_revocation` for
  #66, `vendor_annual_review` for this same process) already had a row in
  `pdpl-sla-timers.md`'s lex table before the process that consumed it
  landed. This one did not — `pdpl-sla-timers.md` had ONLY "Vendor annual
  review (M07) | Annual, Medium/High tier | —", nothing for termination
  access revocation. Both the lex table AND `sla-registry.config.ts`
  needed a new row, sourced directly from backlog #71's own "2 business
  days" text (the M03 consent-withdrawal precedent for sourcing an SLA
  value straight from a backlog line rather than inventing one). Check
  `pdpl-sla-timers.md` doesn't silently have every SLA a new process needs
  — Vendor's OWN registry entry, ironically, was the counter-example.
- **`Vendor` has no explicit "terminated" status field** — termination is
  represented entirely by `terminationDataReturnConfirmedAt` going
  null-to-set (the #66 `Employee.terminationDate` shape). The officer must
  pass an explicit `confirmDataReturnOrDestruction: true` attestation
  (`TerminateVendorDto`, checked in the service — the `FulfilDsrDto`
  staff-attestation precedent) since there is no automated verification
  that data was actually returned/destroyed. `accessRevokedAt` is a
  SEPARATE, subsequent stamp that requires termination to have happened
  first (422 otherwise) — two independently status-conditional actions
  (`VendorRepository.terminate`/`.revokeAccess`, both `updateMany` guards),
  not one compound action.
- **Risk tiering auto-schedules the annual-review SLA on the FIRST
  Medium/High tiering, and does not un-schedule on a later downgrade.**
  Moving a vendor from Medium back to Low leaves an already-scheduled
  `annualReviewDueAt` in place — a deliberate simplification, not handled
  by re-deriving the schedule from the current tier on every read.
  `recordAnnualReview()` re-bases the schedule +12 months by resolving the
  old `SlaTimer` row(s) (`createdBefore: now`, the re-basing shape
  `SlaTimerService`'s own doc comment describes) and starting a new one —
  422s if no review is currently scheduled (i.e. the vendor was never
  tiered Medium/High).
- **DPO approval is a genuinely separate permission code from `vendor.
  manage`, not a shared one.** `dpa.approve` (`[DATA_PROTECTION_OFFICER]`
  only) was already pre-seeded DISTINCTLY from `vendor.manage` — the
  maker-checker default (two codes)
  `maker-checker-segregation.md` recommends, not the `incident.classify`
  shared-permission exception. DPO approval is NOT restricted to only
  fire on a High-tier vendor's DPA — it can be recorded on any tier's DPA;
  the "mandatory for High tier" rule is enforced by
  `computeDataShareReadiness()`, not by blocking the approval action
  itself for other tiers.
- **`DataProcessingAgreementRepository.findActiveByVendorId`** resolves
  "the" DPA that counts for readiness purposes: signed, and either
  open-ended (`expiresAt: null`) or not yet expired, ties broken by
  `signedAt` descending then `id` descending — the #53-54
  `PiPolicyRepository.findCurrent()` deterministic-tiebreak precedent.

## Where the code lives

- `apps/api/src/modules/supporting-operations/vendor.config.ts` —
  `RISK_TIERS`, `dpaRequiredForTier`/`dpoApprovalRequiredForTier`,
  `computeDataShareReadiness()`, the two new SLA workflow name constants.
- `apps/api/src/repositories/vendor.repository.ts` — `setRiskTier`,
  `scheduleAnnualReview`, `terminate`, `revokeAccess` (all status-
  conditional where relevant).
- `apps/api/src/repositories/data-processing-agreement.repository.ts` —
  `create`/`findByVendorId`/`findActiveByVendorId`/`sign`/`dpoApprove`.
  `DataProcessingAgreement`'s first real writer.
- `apps/api/src/modules/supporting-operations/vendor.service.ts` —
  `setRiskTier`, `recordAnnualReview`, `terminate`, `revokeAccess`,
  `dataShareReadiness`.
- `apps/api/src/modules/supporting-operations/data-processing-
  agreement.{service,controller}.ts` — the maker/checker pair's first
  real writer, registered in the SAME `vendor.module.ts`.
- `apps/api/src/modules/sla/sla-registry.config.ts` —
  `vendor_termination_access_revocation` (new).
- `apps/web/app/(app)/vendors/[id]/page.tsx` — the vendor detail screen
  (risk tiering, readiness check, DPA lifecycle, termination/revocation) —
  #67's list page gained a "Manage" link into it.

## Out of scope for this file

- M08 (Data Sharing Approval / `DataSharingApproval`) — a separate,
  still-unbuilt PCMS module; `computeDataShareReadiness()` is built for
  M08 to eventually call, not a substitute for building it.
- M06 (Data Retention & Secure Disposal / `DisposalBatch`) — the batch
  destruction dual-control workflow `maker-checker-segregation.md`'s own
  "Insurance File record" language describes; a separate, still-unbuilt
  process, not this one.
- Hardening `vendor_termination_access_revocation`'s SLA figure against an
  independent `PRIV-SOP-10` citation beyond the backlog's own text — the
  same documented-sourcing-gap shape as `CLAIM_LARGE_THRESHOLD_JOD`, kept
  here rather than in `pdpl-sla-timers.md` since the figure IS directly
  quoted from the backlog, matching the M03 precedent, not invented.
