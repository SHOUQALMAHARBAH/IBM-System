# Incident Management (Process 55)

**Last verified:** 2026-09-06 · **Owner:** DPO / Executive Management (roles, not yet named people)

## What this is

Backlog Part C #55 has three checkboxes: "the full state machine: Reported→Contained
(4-hour target for critical)→Impact Assessed→Classified (Material requires DPO + Senior
Management co-sign)→Notified→Recovered→Closed (root cause mandatory)," "Senior management
notification within 1 hour of Material classification (job)," and "Independent
multi-regulator notification (CBJ, National Cybersecurity Centre, Personal Data Protection
Council) since one incident may trigger more than one regulator's obligations." One model,
`IncidentReport`, pre-existed as bare "core schema" (Part 6.2/7.4) with EVERY field this
needs, including both maker/checker columns — genuinely no field-level migration; the one
migration this process adds (`20260906120000`) only bolts on the missing DB `CHECK`
constraint. `WORKFLOW_TRANSITIONS.IncidentReport` (a strictly linear 7-state chain) and
`SLA_REGISTRY`'s two incident entries (`incident_containment` 4h, `incident_senior_
management_notification` 1h) also pre-existed — this module is their first real consumer.
No seed change — four permissions were pre-seeded ahead of time:
`incident.report` (broad — Sales/Placement/Claims/Finance/Compliance/Manager/Admin/DPO),
`incident.contain` (Admin/Compliance), `incident.classify` (DPO **and** Executive
Management), `incident.notify-regulator` (DPO/Compliance).

**This model is ALSO Part D's M09 (Incident & Breach Management)** —
`pcms-privacy-modules.md`'s own one-line summary ("detection -> containment -> notification
-> RCA") and governing-document citation (`Governing Policy §12`, `PRIV-SOP-09`) match this
model's own doc comment verbatim. Building backlog #55 is, in effect, also building M09 —
the same "one build satisfies two backlog references" shape #16/#50 established for
Conflict of Interest, just inverted (there #50 needed no separate build; here ONE build
covers both #55 and M09).

## The shapes

```
IncidentReport
  title, description: string        # NO_FULL_ACCOUNT_NUMBER-guarded free text
  severity: low | medium | high | critical    # plain string, not an enum
  status: IncidentStatus            # REPORTED -> CONTAINED -> IMPACT_ASSESSED ->
                                     # CLASSIFIED -> NOTIFIED -> RECOVERED -> CLOSED
                                     # (a strictly linear chain, no branching)
  reportedAt: DateTime              # ALWAYS new Date() at create() — never caller-suppliable
  containedAt, impactAssessedAt, recoveredAt, closedAt: DateTime?
  classification: NOT_YET_CLASSIFIED | MATERIAL | NON_MATERIAL
  classifiedByDpoUserId: string?    # the MAKER — DPO-role-checked, stamped at classify()
  seniorManagementCoSignUserId: string?  # the CHECKER — Executive-Management-role-checked,
                                          # write-once, MATERIAL only
  seniorManagementNotifiedAt: DateTime?  # manual stamp, MATERIAL only, resolves the SLA timer
  notifiedRegulators: string[]      # CBJ | NCSC | Personal_Data_Protection_Council
  notifiedAt: DateTime?
  affectedDataSubjectsNotifiedAt: DateTime?  # M09's own PDPL scope, not one of #55's
                                              # three named checkboxes — see below
  rootCauseAnalysis: string?        # MANDATORY before CLOSED

SlaTimer (entityType: 'IncidentReport')
  workflowName: 'incident_containment'                        # 4h, critical severity only
  workflowName: 'incident_senior_management_notification'     # 1h, MATERIAL only
```

## The rules that aren't obvious

- **`incident.classify` is the ONE permission in this codebase's entire seed grid shared by
  BOTH roles of a maker/checker pair** (`DATA_PROTECTION_OFFICER` and
  `EXECUTIVE_MANAGEMENT`), rather than two distinct codes the way every other pair here
  works (`dsr.handle`/`dsr.close`, `kyc.capture`/`kyc.approve`, ...). The segregation is
  enforced one layer deeper: `IncidentService.classify()` explicitly checks
  `actor.roles.includes('DATA_PROTECTION_OFFICER')`, `coSign()` checks
  `actor.roles.includes('EXECUTIVE_MANAGEMENT')`, on top of `assertDifferentActors` +
  the new `IncidentReport_classification_maker_checker_distinct` CHECK. A `@code-reviewer`
  MINOR verified this actually holds even for a single user who happens to hold BOTH
  roles simultaneously (RBAC assigns roles per-user; nothing structurally prevents a dual
  assignment): `classify()` passes that user's DPO check and stamps
  `classifiedByDpoUserId = actor.id`; `coSign()` passes their EXEC check, but
  `assertDifferentActors` then rejects it because the two ids match. See
  `ibms-brain/meta/lex/maker-checker-segregation.md` § "A maker/checker pair sharing ONE
  permission across two roles" for why this is an accepted exception, not a violation —
  and why new pairs should default to two distinct codes unless there's a specific reason
  to share one.
- **The "senior management notification (job)" checkbox has NO bespoke scheduler.**
  `classify()` starts the pre-existing `incident_senior_management_notification` SLA timer
  (1 hour) the moment classification becomes MATERIAL; `notifySeniorManagement()` is a
  MANUAL stamp — this codebase has no real email/SMS/notification-sending infrastructure
  anywhere (confirmed by grep: zero `sendEmail`/`EmailService`/`NotificationService`/
  `nodemailer` call sites in the whole `apps/api/src` tree), the same `CommunicationLog`
  "logs what happened, does not send" shape every other "notification" concept in this
  codebase uses. If that manual duty is missed, the ALREADY-RUNNING generic
  `SlaTimerScheduler` (runs every 15 minutes, backlog A.8) is the "(job)" that catches it —
  it escalates the unresolved timer past the 1-hour deadline and surfaces it on the #43 SLA
  dashboard, which already listed `IncidentReport` in
  `SLA_DASHBOARD_SENSITIVE_ENTITY_TYPES` before this process touched anything. Building a
  second, bespoke scheduler here would duplicate infrastructure that already exists and
  already does exactly what the registry's own `pdpl-sla-timers.md` row describes for this
  entry (no named escalation target beyond a bare "—", unlike DSR's two-stage
  DPO-then-General-Manager escalation).
- **The Material co-sign gate is re-derived LIVE, in two places, from the SAME check** —
  the #16/#51 pattern. Both `notifyRegulators()` (CLASSIFIED -> NOTIFIED, one of #55's three
  named checkboxes) and `notifyAffectedSubjects()` (M09's own scope, not one of the three)
  independently re-check `classification === 'MATERIAL' && !seniorManagementCoSignUserId`
  immediately before their own write, rather than trusting a value cached from whenever
  `classify()` ran. A `@code-reviewer` MINOR on the first pass had this gate on
  `notifyRegulators()` only — `notifyAffectedSubjects()` could notify affected subjects
  before Senior Management had even co-signed a Material classification, an asymmetry with
  no principled reason (both are equally consequential, irreversible external actions for a
  Material incident). Fixed by adding the identical gate to both. This is safe against a
  genuinely concurrent double-call without needing to re-assert the co-sign inside the
  engine's own `updateMany` `WHERE`, because classification and the co-sign are both
  write-once/monotonic fields on this entity — nothing can un-set a recorded co-sign between
  the guard check and the transition, unlike DSR's `applyExtension` or #53-54's
  `findCurrent()`, where the underlying "current" answer genuinely could change mid-flight.
- **`notifyAffectedSubjects()` exists even though it is not one of #55's three named
  checkboxes** — the model's own field, and M09's own PDPL scope (per
  `pcms-privacy-modules.md`'s citation match above) plausibly requires notifying affected
  data subjects for a personal-data breach, not just regulators. `@code-reviewer` assessed
  this as reasonable scope, not `2026-08-pcms-source-of-truth.md`-style rule re-derivation —
  it writes a single pre-existing timestamp field with an uncontroversial precondition
  (classification must be decided), not a new substantive privacy rule.
- **Reads are audited** (`isSensitiveDataAccess: true` on both `get()` and `list()`) even
  though `IncidentReport` carries no `DataClassification` field on the model itself — the
  same reasoning DSR/`TransactionMonitoringAlert` used: a security/personal-data breach
  report is squarely in that territory, closer in kind to those than to the Confidential-
  tier no-read-audit precedent (#33/#34/#41/#44/#45/#46/#51/#53-54's own `RiskRegisterItem`/
  `ProfessionalIndemnityPolicy`).
- **`title` needs the SAME `NO_FULL_ACCOUNT_NUMBER` guard as `description`** — a
  `@code-reviewer` MAJOR on the first pass had it only on `description`. A reporter's first,
  least-considered input during an active incident is exactly the field most likely to get
  sensitive detail typed into it before a fuller, guarded description is written, and it is
  embedded verbatim into every CREATE/UPDATE audit row plus every `incident.report`-holder's
  read (eight roles) and the web table.

## `@code-reviewer` findings (resolved)

Mandatory (a new maker/checker pair + a new DB CHECK migration + a new
`WorkflowTransitionService` entity + Highly-Confidential-adjacent breach data) → CHANGES
REQUESTED → resolved: **1 MAJOR** (the `title` guard above) **+ several MINORs** (the
missing `maker-checker-segregation.md` row and the new "shared permission" exception clause,
both above; this very file not existing at review time — the same #51 MAJOR-3 lesson,
"documentation is part of done"; the `notifyAffectedSubjects` gate-parity fix above; the web
page showing the Classify buttons to an Executive-Management-only user and the Co-sign
button to a DPO-only user — both would always 403 server-side, fixed by splitting button
visibility to the SPECIFIC role each sub-action needs) **+ a NIT** (an explicit dual-role
unit test proving self-classify-and-co-sign is blocked end-to-end, not just inferable from
the same-actor test).

## Where the code lives

- `packages/db/prisma/schema.prisma` — `IncidentReport`, `IncidentStatus`,
  `IncidentClassification` (search "Process 55").
- `packages/db/prisma/migrations/20260906120000_add_incident_maker_checker_check/` — the
  one CHECK constraint this process adds.
- `apps/api/src/modules/compliance-risk/` — `incident.{config,service,controller}.ts`, `dto/`.
- `apps/api/src/repositories/incident.repository.ts`.
- `apps/api/src/modules/sla/sla-registry.config.ts` — `incident_containment` /
  `incident_senior_management_notification`, both pre-existing before this module.
- `apps/web/app/(app)/incidents/page.tsx` + `lib/compliance-risk/incident-api.ts`.

## Out of scope for this file

An actual real-time notification-sending integration (email/SMS/paging) for Senior
Management or regulators — this codebase has none anywhere, and building one is a distinct,
separate infrastructure decision, not part of #55. A `DataClassification` field on
`IncidentReport` itself (the model pre-dates this process; unlike #49's `WatchlistEntry`
BLOCKER, this isn't a new model this PR introduces without one). Domain F's other
processes — see `meta/context/transaction-monitoring.md` (#48), `sanctions-pep-screening.md`
(#49), `regulatory-compliance.md` (#51), and `operational-pi-risk.md` (#53-54) for the
sibling "Out of scope" lists.
