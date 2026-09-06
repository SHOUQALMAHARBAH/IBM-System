# Document Management (Domain H, backlog Part C #70)

**Last verified:** `2026-09-06` · **Owner:** `ibms-app`

## What this is

Process 70. Two checkboxes: full version control (previous/next version) +
mandatory classification + a deletion lock disabled by default except via a
logged privileged override (`deletionOverrideByUserId`); and enforcing the
"highest classification present" rule when a file/record mixes
classification levels.

`Document` (Part 4.2 — the electronic Insurance File) pre-exists in the core
schema with THREE prior writers — Policy issuance/attach (#18-19), Claim
documentation (#25), Customer onboarding (#3-4) — each of which only ever
creates a version-1 row. `versionNumber`/`previousVersionId` and
`deletionLocked`/`deletionOverrideByUserId` had sat dormant since before
this process; `audit-trail.repository.ts`'s own `findDocumentVersionChain`
doc comment already said as much ("no application code creates a second
version yet") — a read-side capability (#57's External Auditor lens) had
existed for longer than any writer. #70 is that first real writer.

## The shapes

```
Document
  id:                        String   @id
  policyId:                  String?                 # direct link — the Policy issuance/attach path
  customerId:                String?                 # the Customer onboarding path
  category:                  DocumentCategory         # APPLICATION_PROPOSAL | RISK_SURVEY | ... | OTHER
  classification:            DataClassification       # mandatory on every version, not just the first
  fileName:                  String
  storageRef:                String                   # encrypted-at-rest object-storage key, never the bytes
  versionNumber:             Int      @default(1)
  previousVersionId:         String?  @unique          # doubly-linked chain; @unique makes it race-safe
  uploadedByUserId:          String
  deletionLocked:            Boolean  @default(true)   # disabled by default (Part 4.2, 5.2)
  deletionOverrideByUserId:  String?                   # privileged, logged override only
  createdAt:                 DateTime @default(now())

  claimDocuments: ClaimDocument[]   # the Claim documentation join (Document carries no claimId itself)
```

Two migration-time foreign-key behaviors matter for deletion, both
unchanged by this process (see "The rules that aren't obvious"):

- `Document_previousVersionId_fkey` — `ON DELETE SET NULL`.
- `ClaimDocument_documentId_fkey` — `ON DELETE RESTRICT`.

## The rules that aren't obvious

- **Deletion here is a single-actor privileged override, NOT the M06
  Disposal dual control.** `roles-and-segregation-of-duties.md`: "the
  resulting physical/technical destruction BATCH always requires dual
  control — Department Manager sign-off plus DPO final approval." That is a
  separate, still-unbuilt process over `DisposalBatch`
  (`raisedByUserId`/`approvedByUserId`, flagged `dormant: true` in
  `internal-controls.config.ts`'s `MAKER_CHECKER_REGISTRY`) — a *batch*
  destruction decision under the PDPL retention schedule. #70's own field
  (`deletionOverrideByUserId`, singular) and its pre-seeded permission
  (`document.delete-override`, one code, `[SYSTEM_SECURITY_ADMINISTRATOR,
  DATA_PROTECTION_OFFICER]` — not two distinct maker/checker codes) both
  anticipate the narrower, ad hoc, single-document shape instead. Do not
  retrofit a maker/checker pair onto this field without a source citation
  that actually asks for one.
- **A document can only be deleted from the leaf of its own version
  chain.** Before a delete, the service checks `hasSuccessor(id)` — if any
  row's `previousVersionId` points at `id`, the delete 409s. This is an
  APPLICATION-level guard, not a DB one: `Document_previousVersionId_fkey`
  is `ON DELETE SET NULL`, not `RESTRICT` — Postgres will not stop a delete
  that orphans a successor, it will silently null the successor's
  `previousVersionId` instead, breaking the chain. Changing that FK's
  `onDelete` to `RESTRICT` (a genuine DB-level backstop) was considered and
  deferred — not asked for by #70's own two checkboxes; the app-level
  pre-check is the only defense today, a documented, deliberate limitation.
- **A document still linked to a `ClaimDocument` cannot be deleted either**
  — `hasClaimLink(id)` is an app-level pre-check for a clear 409 message,
  but here the DB's `ON DELETE RESTRICT` on `ClaimDocument.documentId` is a
  genuine backstop if a race slips past the pre-check (unlike the
  `previousVersionId` case above).
- **`overrideDeletionLock` and `deleteIfUnlocked` are both status-conditional
  writes** (`race-safe-invariants.md`) — `updateMany({ where: { id,
  deletionLocked: true }, ... })` and `deleteMany({ where: { id,
  deletionLocked: false } })` respectively — never a `findUnique` followed
  by an unconditional write. A second concurrent override 409s instead of
  silently overwriting who is on record for it.
- **Creating a new version follows the exact `QuotationService.revise`
  shape**: `id` must be the chain's own CURRENT (leaf) version — passing a
  superseded id 422s ("create a new version from its own latest version
  instead"), never silently resolving to the real leaf. A genuine
  concurrent double-version loses `previousVersionId`'s own `@unique`
  constraint and 409s (caught via `Prisma.PrismaClientKnownRequestError`
  code `P2002`, the `isUniqueViolation` helper every service in this
  codebase re-declares locally rather than sharing).
- **A new version's `category`/`policyId`/`customerId` are inherited from
  its predecessor, never accepted from the caller** — a version is a
  revision of the SAME logical document, not a new artifact. Only
  `fileName`/`storageRef`/`classification` can change per version.
  `classification` stays mandatory on every version (not just the first),
  matching the Part 10.6 "the officer must say which, never assume"
  reasoning `create-customer-document.dto.ts` already established for
  version 1 — this process does not re-derive `create-customer-document.
  dto.ts`'s own narrower CONFIDENTIAL/HIGHLY_CONFIDENTIAL-only restriction
  for customer-linked chains on a NEW version, though; that stays a
  create-time-only rule, a deliberate, documented scope simplification.
- **The "highest classification present" rollup is scoped to
  `Document.policyId` only** (`PolicyFileClassificationView`,
  `GET /documents/classification-summary?policyId=`), matching the
  schema's own "every Policy resolves to ONE electronic Insurance File"
  framing (`data-model.md`). A claim-linked document (joined via
  `ClaimDocument`, never carrying its own `policyId`) is deliberately out
  of scope — not a gap, a literal reading of what the source text anchors
  the rule to. The rule itself is `sensitive-data-handling.md` /
  `PRIV-STD-02` §6.7 verbatim: "a file combining multiple classification
  levels is classified at the highest level present — never averaged."
- **`#70`'s own new routes (`document.manage`) do not duplicate `#57`'s
  existing `GET /audit-trail/documents/:id/history`** (`document-history.
  read`, `[COMPLIANCE_OFFICER, EXTERNAL_AUDITOR]` only). That route is a
  compliance/forensics lens (version list + `AuditLogEntry` rows) that the
  people who actually UPLOAD/VERSION documents (`document.manage`:
  `SALES_RELATIONSHIP_OFFICER`, `PLACEMENT_TECHNICAL_OFFICER`,
  `CLAIMS_OFFICER`, `FINANCE_COLLECTIONS_OFFICER`, `COMPLIANCE_OFFICER`)
  mostly cannot reach — a Placement officer versioning a policy document
  has no read access to `document-history.read`. #70's own `GET /documents`
  / `GET /documents/:id` are a plain OPERATIONAL browse ("what documents
  exist right now"), not a forensic view — a deliberate, non-overlapping
  addition, not a second copy of #57's work.

## Where the code lives

- `apps/api/src/modules/supporting-operations/document.config.ts` —
  `highestClassification()` (the pure PRIV-STD-02 §6.7 rank function),
  `documentAuditSnapshot()` (excludes `fileName`/`storageRef`, the #18-19 /
  #25 precedent), the full design rationale as a header comment.
- `apps/api/src/repositories/document.repository.ts` — `hasSuccessor`,
  `hasClaimLink`, `createVersion`, `setDeletionOverride`,
  `deleteIfUnlocked`, `classificationsByPolicyId`.
- `apps/api/src/modules/supporting-operations/document.service.ts` — the
  guards, the P2002 catch, the audit writes.
- `apps/api/src/modules/supporting-operations/document.controller.ts` —
  `GET /documents`, `GET /documents/:id`, `POST /documents/:id/versions`,
  `POST /documents/:id/deletion-override`, `DELETE /documents/:id` (204),
  `GET /documents/classification-summary?policyId=`.
- `apps/web/app/(app)/documents/page.tsx` — a policy-scoped lookup, per-row
  version/unlock/delete actions, and the classification-summary lookup.

## Out of scope for this file

- The M06 Disposal Management dual-control workflow (`DisposalBatch`,
  Department Manager + DPO) — a separate, still-unbuilt process; see
  `pcms-privacy-modules.md` for M06's own summary.
- `#57`'s External Auditor document-history lens (`audit-trail.
  config.ts`/`audit-trail.repository.ts`'s `findDocumentVersionChain`) —
  unchanged by this process, still the compliance-forensics view, not
  duplicated here.
- Hardening `Document_previousVersionId_fkey` from `ON DELETE SET NULL` to
  `RESTRICT` — a real, documented follow-up, not built here.
