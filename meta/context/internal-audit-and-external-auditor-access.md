# Internal Audit & External Auditor Access (Process 57)

**Last verified:** 2026-09-07 · **Owner:** Compliance / Branch-Department Manager / External Auditor (roles, not yet named people)

## What this is

Backlog Part C #57 closes Domain F with two checkboxes: "Record audit
findings, remediation path, and closure" and "Time-boxed read-only access
for the External Auditor role across all records, documents, and workflow
history." These are two genuinely separate deliverables sharing one backlog
number, built as two separate modules:

1. `apps/api/src/modules/compliance-risk/internal-audit-finding.
   {config,service,controller}.ts` — the `InternalAuditFinding` CRUD (first
   checkbox).
2. `apps/api/src/modules/audit-trail/` — the External Auditor's read-only
   lens over `AuditLogEntry` and `Document` (second checkbox).

Both needed **genuinely no migration, no seed change** — every model and
every permission this process consumes was already pre-provisioned before
any application code touched them.

## Checkbox 1 — `InternalAuditFinding`

`InternalAuditFinding` (core schema) is the exact same bare "generic
register" shape as `RiskRegisterItem` (#53-54), one model up in the same
`schema.prisma` file: `auditPeriodLabel`/`finding`/`remediationAction`/
`status`/`loggedAt`/`closedAt`, no maker/checker columns at all. Not a
`WorkflowTransitionService` entity — `status` is a plain string
`open -> closed`.

**`internal-audit.record` (`[COMPLIANCE_OFFICER]`) and
`internal-audit.close` (`[COMPLIANCE_OFFICER, BRANCH_DEPARTMENT_MANAGER]`)
are two DISTINCT permissions, not a maker/checker pair** — the model has no
maker/checker columns for `assertDifferentActors` to enforce anything
against. This is a deliberate authority split (only Compliance may RECORD a
finding or update its remediation plan; a Manager may also see one through
to CLOSURE), the same "two permissions, two different actions, no
dual-approval relationship between them" shape as #48's `aml.monitor` /
`aml.escalate`. Reads (`GET`) accept EITHER permission — a Manager
reviewing before closing needs to see the finding too.

## Checkbox 2 — the External Auditor's read-only lens

Part 5.1's own role table (`meta/context/roles-and-segregation-of-duties.md`)
names the scope precisely: "Read-only access to **logs, documents and
workflow history** for a defined engagement period" — not blanket read
access to every business table's live content. The backlog's own phrasing
("across all records, documents, and workflow history") reads more broadly
at first glance, but the pre-seeded permission grid had already settled
this the narrower way, **before this process ever ran**: `audit-log.read`,
`document-history.read`, and `workflow-history.read` were all seeded ahead
of time (module `compliance-risk`), and none of them is a generic
`customer.read`/`policy.read`/`claim.read`-style grant. This process is
simply their first real consumer — the same "genuinely no seed change"
shape #55's four permissions had.

**"All records" is satisfied by `AuditLogEntry` itself being polymorphic
across every entity type in the schema** — an auditor filters the SAME
table down to whichever record they're reviewing, rather than being handed
live read access to each business table directly. This is a materially
smaller, more defensible grant than the alternative reading of the
backlog's phrasing, and it matches Part 5.1's own "Cannot: Modify any
record" framing — an auditor with `audit-log.read` still cannot open a
`Customer`/`Policy`/`Claim` record directly through any endpoint that
permission gates; they can only read the audit trail ABOUT it.

**"Time-boxed" was already fully built and tested before this process
existed** — `User.accessValidUntil` + `SessionService.validate` revoke an
active session, log an `ACCESS_WINDOW_EXPIRED` audit row, and throw the
moment the window passes (see the Auth e2e's own "External Auditor
time-boxed access (Part 5.1)" suite). Nothing in this process re-implements
or extends that mechanism — it is a generic, per-user field any admin can
set on ANY role, not something specific to `EXTERNAL_AUDITOR` that needed
building here.

### The three endpoints

All three live on one controller, `AuditTrailController`
(`@Controller('audit-trail')`), and all three write a best-effort `READ`
`AuditLogEntry` row, unconditionally `isSensitiveDataAccess: true` — the
audit log, document history, or workflow history of an arbitrary record can
surface Highly Confidential content regardless of which specific entity is
being inspected, so this reader does not attempt the SLA dashboard's
per-entityType sensitivity classification; every read here is sensitive by
default.

- **`GET /audit-trail?entityType=&entityId=&userId=&action=&from=&to=`**
  (`audit-log.read` — `[COMPLIANCE_OFFICER,
  SYSTEM_SECURITY_ADMINISTRATOR, EXTERNAL_AUDITOR]`) — the general browse,
  every filter optional, newest-first, capped at
  `AUDIT_TRAIL_READ_LIMIT = 5000`. **No `where` pre-filtering assumption
  beyond what's given** — omitting every filter browses the whole (capped)
  log.
- **`GET /audit-trail/workflow-history?entityType=&entityId=`**
  (`workflow-history.read` — `[COMPLIANCE_OFFICER, EXTERNAL_AUDITOR]` — no
  Admin) — `AuditLogEntry` rows for that one record where
  `action = 'TRANSITION'`, chronological. This is literally the
  `WorkflowTransitionService`'s own audit trail, read back for the first
  time by anything other than the engine itself.
- **`GET /audit-trail/documents/:id/history`** (`document-history.read` —
  `[COMPLIANCE_OFFICER, EXTERNAL_AUDITOR]` — no Admin) — walks the
  `Document` version chain (`previousVersionId`/`nextVersion`, a doubly-
  linked list, `previousVersionId @unique`) in BOTH directions from the
  requested id, plus every `AuditLogEntry` row for `entityType: 'Document'`
  across every id in that chain.

**The `Document` version chain is dormant today** — no application code
creates a second version of a document yet (`versionNumber` stays `1`,
`previousVersionId`/`nextVersion` stay `null` for every row this codebase
has written so far). Most documents are their own whole one-row chain right
now. This is a forward-compatible walk, not dead code — the #48/#56
dormant-feature precedent: the day something starts versioning documents,
this endpoint already covers it with no further change.
`DOCUMENT_VERSION_CHAIN_WALK_LIMIT = 1000` is a pure safety valve against a
data anomaly (a cycle) turning the walk into an infinite loop, not a
realistic chain-length expectation.

**`Admin` (`SYSTEM_SECURITY_ADMINISTRATOR`) holds `audit-log.read` but
NEITHER `document-history.read` NOR `workflow-history.read`** — a real,
seed-level distinction worth remembering: Admin can browse the general log
(their own access is itself supposed to be logged and periodically
reviewed, Part 5.1) but the two narrower historical lenses are
Compliance/Auditor-only.

## Where the code lives

- `apps/api/src/modules/compliance-risk/internal-audit-finding.
  {config,service,controller}.ts` + `dto/`.
- `apps/api/src/repositories/internal-audit-finding.repository.ts`.
- `apps/api/src/modules/audit-trail/` — `audit-trail.
  {config,service,controller,module}.ts` + `dto/`.
- `apps/api/src/repositories/audit-trail.repository.ts`.
- `apps/web/app/(app)/internal-audit-findings/page.tsx` +
  `lib/compliance-risk/internal-audit-finding-api.ts`.
- `apps/web/app/(app)/audit-trail/page.tsx` +
  `lib/audit-trail/audit-trail-api.ts`.

## Out of scope for this file

A UI or workflow for an admin to actually SET `accessValidUntil` on an
External Auditor account for a defined engagement — the field and its
enforcement exist; provisioning tooling around it (if any is needed beyond
direct `User` record management) is a separate, undone concern. Extending
`workflow-history.read`/`document-history.read` to Admin, or `audit-log.
read` to any other role — a real, deliberate seed decision to leave alone
unless a future process has a specific reason to widen it. This process
also does not build any export/print capability over the audit trail — Part
10.6's watermarking/export-restriction rules (`meta/lex/sensitive-data-
handling.md`) would need to be satisfied first if one is ever added; today
these are read-only JSON API responses only.
