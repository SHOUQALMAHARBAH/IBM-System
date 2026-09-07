# Consent Management (M03)

**Last verified:** 2026-09-06 · **Owner:** DPO (role, not yet a named person)

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

## Touchpoint wiring (2026-09-06, widened 2026-09-07)

The backlog names 7 explicit touchpoints where consent must be captured: lead
capture, onboarding/KYC, needs & risk assessment, RFQ/market placement, claims,
Group Medical/Life & Motor Fleet, and renewal & cross/up-sell. M03's original
build (above) shipped a generic capture screen with no per-touchpoint wiring —
the 2026-09-06 pass closed that gap for 5 of the 7 and documented the other 2
as a real, deliberate, still-open gap. A 2026-09-07 audit finding corrected
that gap analysis for Claims — see "Claims wired" below — leaving only Group
Medical/Life & Motor Fleet genuinely blocked on missing prerequisite
infrastructure.

**6 touchpoints wired — Lead capture, onboarding/KYC, needs & risk
assessment, RFQ/market placement, claims, cross-sell & up-sell:**

- **Lead capture is the one touchpoint that pre-dates a Customer row** — a
  `Lead` has no `customerId`/`insuredPersonId` to hang a `ConsentRecord` off
  of. `ConsentRecord` gained a THIRD optional owner column, `leadId`
  (migration `20260913120000`), FK to `Lead`, `ON DELETE SET NULL` (matching
  the existing `customerId`/`insuredPersonId` FKs). Exactly-one-of-three is
  validated by a NEW, Consent-specific function
  (`hasExactlyOneConsentOwner` in `consent.config.ts`) — deliberately NOT a
  generalization of the shared `common/dto.util.ts#hasExactlyOneOwner`,
  which DSR (M04) also depends on and has no `leadId` concept; two owner
  kinds and three owner kinds are genuinely different shapes for different
  callers, not a single function outgrowing its interface.
  `LeadRepository.create()` now creates the `Lead` row AND its lead-capture
  `ConsentRecord` (`purpose: MARKETING`, `granted: dto.marketingConsentGranted`)
  in ONE interactive transaction — a deliberate local exception to this
  codebase's no-`$transaction` convention, the
  `EmployeeRepository.terminate()` "create-together" shape.
  `Lead.marketingConsentGranted` (the pre-existing boolean, unticked by
  default since the original #1 build) is UNCHANGED and still the fast
  display read the Lead list/detail screens use — the new `ConsentRecord`
  row is additive, making the SAME decision register-visible and
  2-business-day-withdrawal-capable, which the bare boolean never was.
  `CreateLeadDto` gained a new mandatory `consentTextVersion` field
  (the exact `CreateConsentRecordDto.consentTextVersion` shape) — a real,
  intentional breaking change to `POST /leads`'s contract, not an
  oversight; every existing caller (e2e fixtures, the web intake form) was
  updated to supply it.
- **Onboarding/KYC, needs & risk assessment, RFQ/market placement,
  cross-sell, up-sell all already operate on an existing `Customer`** — no
  schema change needed for these five; each touchpoint's own web detail
  page mounts a new shared `apps/web/components/pdpl/ConsentCaptureWidget.tsx`,
  which is nothing more than a thin, reusable wrapper around the SAME
  generic `POST/GET /consent-records` API the standalone Consent page
  already called — no new backend capability, purely a UI-reachability fix
  (the requirement was never "build a new capture mechanism," it was "make
  the existing one reachable AT the touchpoint," per user direction after
  the two genuinely-blocked touchpoints below were flagged).
  - Needs Assessment has no direct `customerId` (only via
    `RiskProfile.customerId`) — `NeedsAssessmentService.get()` now resolves
    it via the ALREADY-INJECTED `RiskProfileRepository` (no new
    dependency, no repository/schema change).
  - RFQ has no direct `customerId` either (only via
    `Opportunity.customerId`) — `RfqService.get()` resolves it the same
    way, via the ALREADY-INJECTED `OpportunityRepository` and the
    visibility-check helper (`findVisibleRfq`) that was already resolving
    it internally. Widening the shared `RfqWithSubmissions` Prisma-payload
    type itself was tried first and reverted — resolving in the SERVICE
    from an already-injected repository is strictly less invasive than
    widening a type five other call sites share.
  - Purpose mapping per touchpoint: onboarding/KYC → `KYC_AML`; needs &
    risk assessment → `UNDERWRITING`; RFQ/market placement →
    `SHARING_WITH_INSURER` (data is being shared with insurers at this
    step); claims → `CLAIMS`; cross-sell and up-sell → `MARKETING` (a
    solicitation).
- **Claims wired 2026-09-07** — the 2026-09-06 pass's premise ("there is no
  web UI for an individual claim record anywhere in `apps/web`") was false
  by the time a code-reviewer audit checked it: `ClaimSection.tsx`
  (`apps/web/components/policy/ClaimSection.tsx`) is a real, reachable
  per-claim management UI (notification through closure), mounted on
  `apps/web/app/(app)/opportunities/[id]/page.tsx` since Part C #23-30
  shipped — a claims-analytics AGGREGATE page existing alongside it never
  meant a per-claim UI didn't. The opportunities detail page already
  resolves `opportunity.customerId` for its own "All opportunities" link,
  so no repository-resolution work was needed at all (LESS work than the
  needs-assessment/RFQ touchpoints, which needed to resolve `customerId`
  through an injected repository first). `ConsentCaptureWidget` is mounted
  directly in `opportunities/[id]/page.tsx`, immediately before
  `<ClaimSection>` (`purpose="CLAIMS"`, `label="Claims consent"`,
  `defaultConsentTextVersion="claims-notice-v1"`) rather than at the top of
  the page like the single-purpose touchpoint pages — this page stacks
  seven distinct process sections (Recommendation, Client Decision, Policy,
  Endorsement, Finance, Commission, Claims), so the widget sits at the top
  of ITS OWN section, the same "top of the relevant section" placement the
  single-section pages use.

**1 touchpoint deliberately NOT wired — a real, documented gap, not an
oversight:**

- **Group Medical/Life & Motor Fleet** — this touchpoint is about consent
  for the COVERED INDIVIDUALS (dependents/employees/drivers) under a
  group/fleet policy, which maps to `InsuredPerson`. `InsuredPerson` has
  ZERO CRUD anywhere in this codebase — no create/list/get, no web page,
  nothing to attach a widget to. Building an `InsuredPerson` management
  module is a substantial undertaking of its own (comparable in scope to
  #66 Employee or #69 InformationAsset), not something to build as a side
  effect of a Consent pass.

Closing this remaining touchpoint requires building the underlying
capability (an `InsuredPerson` CRUD module) FIRST — it is not a Consent bug,
it is missing prerequisite infrastructure. Note that `PrivacyNoticeDisplay`
(Part D's Notices system, `apps/web/components/pdpl/PrivacyNoticeDisplay.tsx`)
was mounted at the same 5 original touchpoints on the same "Claims has no UI"
premise and is now ALSO stale for Claims — that widget's own wiring is
`meta/context/part-d-completion.md`'s scope, not this file's, and was
deliberately left untouched by the 2026-09-07 Consent fix (a different,
undiscussed finding).

## Where the code lives

- `packages/db/prisma/schema.prisma` — `ConsentRecord`, `ConsentPurpose` (search "PART
  4.1" / "Consent Management").
- `apps/api/src/modules/pdpl/` — `consent.config.ts` (pure: view/audit-snapshot
  builders, `hasExactlyOneOwner` re-export, `hasExactlyOneConsentOwner`),
  `consent.service.ts` (the two-step withdrawal flow),
  `consent.controller.ts`, `dto/`.
- `apps/api/src/repositories/consent-record.repository.ts` — owns the writes.
- `apps/api/src/repositories/lead.repository.ts` — `create()`'s Lead+ConsentRecord
  transaction (touchpoint #1).
- `apps/api/src/repositories/communication.repository.ts`'s `marketingConsentRecords` +
  `apps/api/src/modules/customer-service/communication.config.ts`'s
  `evaluateMarketingConsent` — Process 44's pre-existing *reader*; M03 does not
  duplicate this logic, only feeds it real rows.
- `apps/api/src/modules/sla/sla-registry.config.ts` — the `consent_withdrawal` entry
  (2 business days, `PRIV-STD-01` §6.3 / `PRIV-SOP-04`), unused before this module.
- `apps/web/app/(app)/consent/page.tsx` + `apps/web/lib/pdpl/consent-api.ts` — the
  standalone register screen (now also supports the `leadId` owner kind).
- `apps/web/components/pdpl/ConsentCaptureWidget.tsx` — the shared touchpoint widget,
  mounted on `customers/[id]`, `needs-assessments/[id]`, `rfqs/[id]`,
  `opportunities/[id]` (Claims, added 2026-09-07), `cross-sell/[id]`, `up-sell/[id]`.

## Out of scope for this file

M04 (DSR) is now built too — see `meta/context/data-subject-requests.md`. Building an
`InsuredPerson` CRUD module — the one remaining prerequisite the deliberate touchpoint
gap above is waiting on — is out of scope here; when it lands, this file's own
touchpoint-wiring section is the place to add the 7th widget mount, not a new file.
Part D's other systems (Notices/RoPA/Cross-Border Transfer/Data Sharing/DPIA/DPO
Workspace — see `meta/context/part-d-completion.md`) are built but out of this file's
scope; in particular, `PrivacyNoticeDisplay`'s own Claims gap (noted above) is that
file's to close, not this one's. M05 (access governance — partially covered by
`roles-and-segregation-of-duties.md`), M07 (Vendor Risk), M09 (Incident & Breach — see
`meta/context/incident-management.md`) remain out of this file's scope.
`pcms-privacy-modules.md` is the M01-M12 map.
