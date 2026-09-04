# Consent Management (M03)

**Last verified:** 2026-09-04 · **Owner:** DPO (role, not yet a named person)

## What this is

M03 (`meta/context/pcms-privacy-modules.md`) governs how a consent decision — a grant
or an explicit decline, at a defined touchpoint — is captured, and how a withdrawal
gets reflected in the register within its statutory SLA. `ibms-app`'s Prisma schema has
modeled `ConsentRecord` since the initial domain-model migration; the first real writer
landed 2026-09-04 (backlog Part D §5.1 / `IMPROVEMENTS.md` §5.1, filed under backlog
Process **#52 Data Protection Compliance**, which bundles all nine Part D systems). It
is the first of those nine to be built. `ConsentRecord` already had one *reader* before
this — Process 44 (Customer Communication)'s marketing-send gate — see "Where the code
lives" below.

## The shapes

```
ConsentRecord
  customerId: string?          # exactly one of customerId / insuredPersonId
  insuredPersonId: string?     # (service-level 422, not a DB CHECK — see "not obvious")
  purpose: ConsentPurpose      # UNDERWRITING | CLAIMS | MARKETING | KYC_AML |
                                # SHARING_WITH_INSURER | OTHER
  isMarketing: bool            # DERIVED = (purpose === MARKETING), never an input
  granted: bool                # explicit; defaults unchecked; a false row IS a decline,
                                # not the absence of a row
  consentTextVersion: string   # which approved wording the subject saw
  grantedAt: DateTime?         # set iff granted; stays null on a decline
  withdrawnAt: DateTime?       # set only via confirmWithdrawal — see below

SlaTimer (entityType: 'ConsentRecord', workflowName: 'consent_withdrawal')
  2 business days, one stage, escalateTo: null (the source table's "—")
```

No `status` field, no `WorkflowTransitionService` entity — the row is written once at
create and gets exactly one further field touched (`withdrawnAt`), never un-set. The
record's own history across multiple rows for the same subject+purpose IS the audit
trail — Process 44's pre-existing `evaluateMarketingConsent` already reads it that way
(latest active grant vs. latest withdrawal, by effective timestamp, not a single mutable
"current" row).

## The rules that aren't obvious

- **Withdrawal is a two-step flow, not one call** — `POST /consent-records/:id/
  request-withdrawal` (starts the `consent_withdrawal` SLA timer; touches no
  `ConsentRecord` field) then `POST /consent-records/:id/confirm-withdrawal` (sets
  `withdrawnAt`, resolves the timer). The model's own field comment — `withdrawnAt`
  "must reflect in register within 2 business days" — only makes sense if intake and
  reflection can be genuinely separate events (a phone call, an email, a walk-in
  request that sits with staff for a day or two); if they always collapsed into one
  atomic call the SLA would be vacuous by construction. `confirmWithdrawal` also works
  standalone, with no prior `requestWithdrawal` — `SlaTimerService.resolve` is a
  documented no-op when nothing is open, so a same-day self-service withdrawal never
  errors; it just never gets a tracked window.
- **`isMarketing` is derived, never accepted as input.** It is `true` iff
  `purpose === 'MARKETING'`. This is how "consent and contractual-necessity processing
  are always two separate, independently-actionable controls" (`PRIV-SOP-04`,
  `pcms-privacy-modules.md`) is enforced — structurally, not by validating a
  caller-supplied flag that could disagree with `purpose`.
- **"Exactly one of `customerId` / `insuredPersonId`" is app-level validation, NOT a DB
  CHECK** — unlike `PaymentChannel`'s `owner_exactly_one` (#38). That one guards against
  *concurrent* writes racing into an invalid combination; a `ConsentRecord` is written
  by exactly one call site, once, at creation, never edited afterward, so a single
  service-level 422 is proportionate. If a second creation path ever appears (a
  DSR-driven capture, a bulk import), reconsider — a CHECK is the right call at that
  point.
- **Once withdrawn, `confirmWithdrawal` is idempotent, not an error.** A record with
  `granted: false` (never granted) is the only 422 case — "there is nothing to
  withdraw."
- **Process 44's marketing gate already enforces "communications suppressed
  immediately" for free.** `evaluateMarketingConsent` (`communication.config.ts`) reads
  the live `withdrawnAt` on every send; the moment `confirmWithdrawal` sets it, the
  backlog's second withdrawal clause is satisfied by code that shipped before M03 did.
  M03 does not touch `CommunicationLog` or `communication.config.ts` at all — it only
  writes the field the other module was already reading.
- **`consent.manage` (`[SALES_RELATIONSHIP_OFFICER, PLACEMENT_TECHNICAL_OFFICER,
  CLAIMS_OFFICER, DATA_PROTECTION_OFFICER]`) was already seeded** before any M03 code
  existed — like every Domain E permission before it, the grid anticipated this module.
  One permission covers capture, withdrawal, and reads alike (the #41/#44/#45 "one perm
  for CRUD" shape) — there is no separate `consent.read`.
- **`requestWithdrawal` has no guard against a genuine concurrent double call** — two
  `POST .../:id/request-withdrawal` calls in flight at once can each create an open
  `consent_withdrawal` `SlaTimer` row for the same `ConsentRecord` (no unique constraint
  backs it, unlike `ServiceRequest.slaTimerId` / `Complaint.slaTimerId`'s direct FK).
  Reviewed and accepted as a MINOR, not hardened: `SlaTimerService.resolve()` matches on
  `workflowName.startsWith(...)` and closes every open row for the entity together, so
  nothing is ever left dangling, and nothing downstream (including the #43 SLA dashboard)
  assumes single-row-per-entity uniqueness for correctness. A cheap fix if this ever
  matters — check for an already-open timer before `startTimer()`, or a partial unique
  index on `SlaTimer(entityType, entityId, workflowName) WHERE resolvedAt IS NULL` — is
  worth doing opportunistically next time this file is touched, not before.

## Where the code lives

- `packages/db/prisma/schema.prisma` — `ConsentRecord`, `ConsentPurpose` (search "PART
  4.1" / "Consent Management").
- `apps/api/src/modules/pdpl/` — `consent.config.ts` (pure: view/audit-snapshot
  builders, `hasExactlyOneOwner`), `consent.service.ts` (the two-step withdrawal flow),
  `consent.controller.ts`, `dto/`.
- `apps/api/src/repositories/consent-record.repository.ts` — owns the writes.
- `apps/api/src/repositories/communication.repository.ts`'s `marketingConsentRecords` +
  `apps/api/src/modules/customer-service/communication.config.ts`'s
  `evaluateMarketingConsent` — Process 44's pre-existing *reader*; M03 does not
  duplicate this logic, only feeds it real rows.
- `apps/api/src/modules/sla/sla-registry.config.ts` — the `consent_withdrawal` entry
  (2 business days, `PRIV-STD-01` §6.3 / `PRIV-SOP-04`), unused before this module.
- `apps/web/app/(app)/consent/page.tsx` + `apps/web/lib/pdpl/consent-api.ts`.

## Out of scope for this file

The other eight Part D / PCMS systems — M04 (DSR), M05 (access governance — partially
covered by `roles-and-segregation-of-duties.md`), M06 (Retention & Disposal —
`data-retention-and-disposal.md`), M07 (Vendor Risk), M08 (Data Sharing), M09
(Incident & Breach), M10 (DPIA), the privacy-notice / RoPA requirements, and the DPO
Workspace dashboard — none of these are built yet. `pcms-privacy-modules.md` is the
M01-M12 map; a future module gets its own file here the same way this one did.
