# Part D completion — Cross-Border Transfer, Data Sharing (M08), DPIA (M10), Notices, RoPA, DPO Workspace

**Last verified:** 2026-09-07 · **Owner:** DPO (role, not yet a named person)

## What this is

The backlog's Part D §5.1 checklist names nine PDPL/PCMS systems, worked one at a time:
Consent (M03), Data Subject Requests (M04), Retention & Disposal (M06) — each has its
own context file — and the six covered here, all landing in the same session that closed
out Part D: Cross-Border Transfer, Third Parties & Data Sharing (M08), DPIA Screening
(M10), Notices, Records of Processing Activities (RoPA), and a DPO Workspace aggregate
screen. All six live in `apps/api/src/modules/pdpl/`, registered in the same
`PdplModule` as the first three.

## The module-number gap

**Two of these six — Cross-Border Transfer and Notices — do not map onto any single
named M01-M12 PCMS module.** Both models' own schema doc comments cite "Part 6.2"
(`IBMS_Full_Scope_Context_Document.docx`), but `pcms-privacy-modules.md`'s M01-M12 table
has no module by either name — M05 ("Data Collection & Access Governance") is a
different, already-built system (Vendor termination/quarterly-access-review SLAs). This
build initially mislabeled Cross-Border Transfer as "M05" by assuming the next
unused-looking number, rather than checking the actual module table — caught and fixed
across 8 files before push. Both are cited by "Part 6.2" alone in code comments now. Data
Sharing and DPIA correctly map onto **M08** and **M10** respectively — those citations
are unchanged. RoPA cites **Part 9.3** (matching the model's own schema doc comment, the
same section #65 Strategic Planning Inputs and #74 Knowledge Management use for their own
citations). The DPO Workspace has no PRIV-* citation at all — it is purely an aggregation
UI the backlog names directly by feature, not by a PCMS module.

## Cross-Border Transfer

`CrossBorderTransferRecord` blocks any transfer of personal data outside Jordan unless
exactly one of three legal bases (`statutory_exception` / `standard_contractual_clauses`
/ `explicit_consent`) is recorded — a real DB column, not a checklist a caller ticks
separately. **`cross-border-transfer.approve` is the ONLY pre-seeded permission** (DPO
only) — there is no separate request/log permission, so `create()` IS the approval act
(the #74 KnowledgeBaseArticle "creation IS publishing" shape, reused): `approvedByUserId`
is always stamped to the caller's own id, never set by a separate action. The record is
append-only (no update/delete endpoint — the `Interaction` "no edit/delete of a logged
interaction" precedent) and `transferredAt` is never caller-suppliable (always
server-stamped, the DSR `receivedAt` anti-backdating discipline). The service also
rejects `destinationCountry: "Jordan"` (case-insensitively) as a 400 — a domestic
"cross-border" transfer would be a misuse of the model, a real business rule directly
derivable from the checklist's own "outside Jordan" framing, not fabricated.

## Third Parties & Data Sharing (M08)

`DataSharingApproval` is the one-off, non-recurring data-sharing path — `vendorId` is
optional precisely so a share can be logged with NO `Vendor` row at all, "separate from
the standing vendor relationship" per the checklist's own words. Two permissions:
`data-sharing.request` (the maker, broad — Sales/Placement/Claims/Finance/Compliance) and
`data-sharing.approve` (DPO, the checker) — a genuine maker/checker pair the covered-pairs
table (`common/maker-checker.util.ts`) already named ahead of time, backed by the
pre-existing `DataSharingApproval_maker_checker_distinct` DB CHECK (migration
`20260826091424`).

**This is the first real caller of backlog #71's `computeDataShareReadiness()`** —
built with "no live enforcement call site yet" explicitly flagged in its own header
comment. `create()` now calls it live: if `vendorId` is set and the channel is NOT
regulatory, the vendor must be risk-tiered and (for Medium/High tier) have a signed DPA
on file, else 422. "Regulatory channels ... are exempt from the standard vendor-risk
assessment but remain subject to classification and minimum-necessary-data checks" (the
checklist's own words) is modeled as skipping ONLY the readiness check — the
classification/channel check (`assertSecureChannel()`, already built for M08 ahead of
time) always runs regardless. "Minimum-necessary-data checks" has no dedicated schema
field to persist a structured attestation against; the DTO enforces a real minimum length
(20 chars) on the mandatory `description` field instead — a documented scope limit, not a
structured data-minimization review.

**The model tracks approval, not a status enum.** A decision is "approved"
(`approvedByUserId` + `decidedAt` both set) or "declined" (`decidedAt` set,
`approvedByUserId` left null) — both independently-nullable columns already on the
model, no migration needed for the decline path. The DB CHECK and `assertDifferentActors`
both only compare `approvedByUserId` against `requestedByUserId`, so a decline (which
never sets `approvedByUserId`) trivially satisfies both.

`slaDueAt` (`data_sharing_decision`: 3 business days / 1 for the regulatory-channel fast
track — `SlaTimerService.computeDueAt`'s `regulatoryChannel` option, itself unused by any
caller until this build) is a mandatory inline column, computed and persisted at
`create()` time, plus a matching generic `SlaTimer` row started (the entity is already in
`SLA_DASHBOARD_SENSITIVE_ENTITY_TYPES`).

## DPIA Screening (M10)

The 5-question yes/no form (`qSensitiveData`, `qLargeScaleProcessing`,
`qCrossBorderTransfer`, `qNewTechnologyMonitoring`, `qNewDigitalChannel`). Any single
"Yes" → `DPO_REVIEW_REQUIRED`, a 5-business-day SLA (`dpia_review`, already registered
with zero prior caller — this build is its first). An all-"No" result auto-approves,
subject only to an UN-TIMED DPO spot-check (`dpoSpotCheckedAt`) — the checklist names a
review DEADLINE only for the "any Yes" path, so a spot-check is a quality-assurance
sample, not a per-record statutory clock.

**`dpia.review` is the ONLY pre-seeded permission** (DPO-only — `roles.ts`'s own
description: "owns ... simplified DPIA decisions") — it gates the WHOLE surface
including submission, the same "one pre-seeded permission gates the whole CRUD"
precedent as #67/#69/#71/#74, a real, documented scope limit: in a fuller build, whoever
proposes a new product/system/campaign would submit this form themselves.

**`outcome` is a status-shaped enum column that is NOT named `status`**, so it cannot be
registered in `WORKFLOW_TRANSITIONS`/driven by `WorkflowTransitionService` — that
engine's `WorkflowDelegate` interface (`workflow-transitions.config.ts`) hardcodes reading
a column literally called `status`. `escalateToFullDpia()` is therefore a hand-written,
status-conditional repository `updateMany` instead (the `LegalHold.release()`/
`RetentionScheduleItem.confirm()` shape) — the same "never assign a workflow status
directly, only through a dedicated transition function" discipline, just not routed
through the generic engine because the column name doesn't match its contract. **This is
a reusable lesson**: a status-SHAPED field (an enum with terminal/non-terminal states)
does not automatically qualify for the generic workflow engine — check the column is
literally named `status` first.

The only real state move is `DPO_REVIEW_REQUIRED → ESCALATED_FULL_DPIA` — a DPO's
alternative to completing an ordinary review (`dpoReviewedAt` stamped, `outcome`
unchanged) for a "materially high-risk" case. **No numeric Yes-count threshold is
specified anywhere in the backlog** for what counts as "materially high-risk" —
escalation is a manual DPO judgment call, never automatic, so as not to invent an
unsourced threshold. `recordReview()` and `escalateToFullDpia()` are mutually exclusive,
single-shot actions (each re-asserts both `dpoReviewedAt: null` AND
`escalatedToFullDpiaAt: null` in its own `where`).

## Notices

`PrivacyNotice` — bilingual, version-controlled text per touchpoint. Unlike
`KnowledgeBaseArticle` (#74, bilingual OPTIONAL-per-article), `textAr`/`textEn` are BOTH
mandatory (`NOT NULL`) — the `DocumentTemplate` mandatory-both shape, since a
legally-reviewable notice needs both languages published together. **Creation IS
publishing** (the #74 shape again) — `privacy-notice.publish` (DPO + Compliance) gates
create/list/legal-review; `publishedAt` defaults to `now()` with no draft state.

**Version-controlled means append-only, never edited** — publishing a new version for a
touchpoint is a NEW row with `versionNumber` one higher than the previous highest for
that touchpoint, the `Quotation` negotiation-round shape (immutable history), NOT a
`Document`-style `previousVersionId` chain (the model has no such column — a simpler
shape faithful to what the schema actually provides). Closed a genuine race: migration
`20260915120000` adds `@@unique([touchpoint, versionNumber])` — a concurrent double-publish
for the same touchpoint now 409s (`isUniqueViolation`, the `rfq.service.ts` pattern)
rather than silently landing two rows on the same version number. "The current notice for
a touchpoint" is the row with the highest `versionNumber` — `GET /privacy-notices/current?
touchpoint=X` returns `{ notice: PrivacyNoticeView | null }`, NEVER a bare `null` —
**NestJS sends an EMPTY response body for a `null`/`undefined` controller return value,
not the JSON literal `null`**, which a caller (and this build's own first e2e attempt)
cannot distinguish from an absent response at all. Wrap any endpoint whose natural
"nothing found yet" answer is `null` in an object instead.

**`GET /privacy-notices/current` deliberately accepts a SECOND permission,
`consent.manage`** — not just `privacy-notice.publish`. The same touchpoint-facing roles
that capture consent (`ConsentCaptureWidget`'s `CONSENT_ROLES`: Sales/Placement/Claims/
DPO) need to read the notice text that applies there; gating even the READ behind
DPO/Compliance-only (the #74 KnowledgeBaseArticle precedent) would make "displayed at
every touchpoint" unreachable by the staff actually standing at that touchpoint. This is
a deliberate reuse of an existing permission for a second endpoint, not a new one.

**Touchpoint display wiring reuses the exact 5 mount sites Consent (M03) already
reached** — a new `PrivacyNoticeDisplay` component mounted alongside
`ConsentCaptureWidget` on `customers/[id]`, `needs-assessments/[id]`, `rfqs/[id]`,
`cross-sell/[id]`, `up-sell/[id]`, plus `LeadIntakeForm` for lead capture (6 mount sites,
5 distinct touchpoints since cross-sell and up-sell share `renewal_cross_sell`). Claims
and Group Medical/Life & Motor Fleet remain the SAME documented gap Consent already has
— no web UI/CRUD exists for either, so there is nowhere for a display widget to mount;
this is not a fresh scope decision, it inherits the one Consent's own build already made
(and the user already confirmed via AskUserQuestion at that time).

## Records of Processing Activities (RoPA)

`RopaEntry` (Part 9.3) — "an exportable register documenting every processing activity,
its data categories, purposes, recipients, and retention period." `ropa.manage`
(DPO-only) gates the whole surface — plain, fully-mutable CRUD (unlike `PrivacyNotice`'s
append-only versioning): a register entry is a living description of an ongoing
activity, corrected in place as its data categories or recipients change, the
`KnowledgeBaseArticle` mutability shape rather than `PrivacyNotice`'s immutable-history
one. `RopaEntry` carries no actor column — the `AuditLogEntry` trail already records who
wrote each row. **"Exportable" reuses the #65 Strategic Planning Inputs precedent** — the
previously-dormant `AuditAction.EXPORT` value, an `EXPORT` audit row with a synthetic
`entityId` (`'ropa-register'`, since there is no single row being exported) — not a real
CSV/file-download mechanism, since none exists anywhere else in this codebase either.

## DPO Workspace

Backlog item #9: "aggregating consent status + the DSR queue with SLA countdowns + the
incident/breach register + the DPIA register + the Legal Hold register + the
cross-border transfer register, on one screen." **Zero cross-module SERVICE
dependency** — the #58 KPI Dashboard / #63 Profitability Analysis shape —
`DpoWorkspaceService` reads five already-built PDPL repositories directly (Consent, DSR,
DPIA, Legal Hold, Cross-Border Transfer, all in `PdplModule`) plus ONE cross-module
repository, `IncidentRepository` (`compliance-risk`), injected directly rather than
importing `ComplianceRiskModule` — the established "give the other module's repository,
not the whole module" pattern.

**`dpo-workspace.view` is a genuinely NEW permission** — unlike every other Part D item
(all had at least one pre-seeded permission already), no permission was pre-seeded for
this screen at all, the #71 "vendor_termination_access_revocation... a genuine gap, not
dormant" precedent applied to a permission code instead of an SLA registry row. DPO-only,
matching the tightest defensible reading (every constituent system's own permission is
DPO-only or DPO+Compliance; the checklist names it "A DPO Workspace screen," not a
compliance one).

Each register section reuses its OWNING module's already-derived "View" shape verbatim —
no duplicated projection logic. Filtering: DSR queue excludes `CLOSED`; incident register
excludes `CLOSED`; DPIA register is `DPO_REVIEW_REQUIRED` only (what a DPO actually needs
to act on, not the full history); Legal Hold register is active-only; cross-border
transfers have no open/closed concept, so the most recent N are shown. The DSR queue adds
a plain `daysUntilDue` (calendar-day arithmetic against the SAME `slaDueAt` the DSR
module already computed business-day-aware at creation time) — a quick-glance dashboard
countdown, not a second SLA computation.

## Where the code lives

- `apps/api/src/modules/pdpl/cross-border-transfer.{config,service,controller}.ts` +
  `repositories/cross-border-transfer.repository.ts`.
- `apps/api/src/modules/pdpl/data-sharing-approval.{config,service,controller}.ts` +
  `repositories/data-sharing-approval.repository.ts` (injects
  `repositories/vendor.repository.ts` + `repositories/data-processing-agreement.repository.ts`
  directly for the readiness check).
- `apps/api/src/modules/pdpl/dpia-screening.{config,service,controller}.ts` +
  `repositories/dpia-screening.repository.ts`.
- `apps/api/src/modules/pdpl/privacy-notice.{config,service,controller}.ts` +
  `repositories/privacy-notice.repository.ts`; migration
  `20260915120000_add_privacy_notice_version_unique`.
- `apps/api/src/modules/pdpl/ropa-entry.{config,service,controller}.ts` +
  `repositories/ropa-entry.repository.ts`.
- `apps/api/src/modules/pdpl/dpo-workspace.{config,service,controller}.ts` (injects
  `repositories/incident.repository.ts` directly, the one cross-module import).
- `apps/web/app/(app)/{cross-border-transfers,data-sharing-approvals,dpia-screenings,
  privacy-notices,ropa-entries,dpo-workspace}/page.tsx` + matching
  `apps/web/lib/pdpl/*-api.ts` client libraries.
- `apps/web/components/pdpl/PrivacyNoticeDisplay.tsx` — the touchpoint display widget.

## Out of scope for this file

M01/M02/M05/M07 (beyond backlog #71's Vendor slice)/M09 (built separately as Part C
#55)/M11/M12 — see `pcms-privacy-modules.md`'s "Where the code lives" for the full
picture. `computeDataShareReadiness()`'s own design (risk tiering, DPA maker/checker) —
`meta/context/vendor-management.md`. The DB-CHECK/app-layer maker/checker mechanism
generally — `meta/lex/maker-checker-segregation.md`.
