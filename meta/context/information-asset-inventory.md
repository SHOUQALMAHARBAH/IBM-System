# Information Asset Inventory (Cybersecurity, backlog Part C #69)

**Last verified:** `2026-09-06` · **Owner:** `ibms-app`

## What this is

Process 69 (Domain H, Supporting Operations). The backlog's own annotation
claims #69 is "fully covered by Part A + `IncidentReport` + `InformationAsset`."
That claim was verified rather than accepted (the same discipline #68 —
Internal IT — established), via a research-only subagent checking each named
piece against the real codebase. The verdict: **overstated, more so than
#68's case** — two of the three pieces were real, but `InformationAsset` (the
ISO 27001 Clause 8.1 asset inventory) was completely dormant, with zero prior
application code anywhere. This file documents the verification findings and
the CRUD this process built to close that one genuine gap.

## The verification findings

- **Part A** (A.1 Auth/Sessions, A.3 Encryption/Key Management, A.4 Immutable
  Audit Trail, A.9 Data Masking, A.10 Infra/Deployment) are all real
  cybersecurity-relevant controls, but each carries its own already-tracked
  gap: no hardware-token/WebAuthn MFA (A.1), key material is env-var-backed
  rather than a real KMS/HSM and encryption-at-rest is not configured (A.3),
  `assertSecureChannel()`/`assertExportAllowed()` (A.9) have zero real
  business-module callers, and Dev/Test/UAT/Prod separation (A.10) is
  self-documented as "scaffolded, not achieved." A.4 (the DB-level
  immutability trigger + `AuditAnomalyDetectionService`) is the one piece of
  Part A that is genuinely complete. **None of these gaps are restated here**
  — they already live in `ibms-app`'s own `README.md` § Known gaps.
- **`IncidentReport`** (`packages/db/prisma/schema.prisma`, built for backlog
  #55 / Part D M09) is genuinely built — full service/repository/controller,
  e2e-tested — and its own doc comment already frames it as a "unified
  security + personal-data breach workflow." It IS a real, working
  cyber-incident reporting path. It has no dedicated cyber/category field,
  though — incidents are typed by free-text `title`/`description` plus a
  `severity` string (`low|medium|high|critical`), not a taxonomy.
- **`InformationAsset`** was the one genuine gap: a model that existed in the
  core schema with **zero prior consumers anywhere** in `apps/api/src` — the
  same "dormant model, first real writer" shape #58-67 repeatedly found
  (Employee, Vendor, InsurerPerformanceScore, EmployeePerformanceRecord).

## The shapes

```
InformationAsset
  id:             String   @id @default(uuid())
  name:           String
  assetType:      String                              # no DB enum — validated app-side, see ASSET_TYPES below
  ownerUserId:    String                               # bare scalar, no Prisma @relation — validated against a real User in the service layer
  classification: DataClassification                   # PUBLIC | INTERNAL | CONFIDENTIAL | HIGHLY_CONFIDENTIAL
  createdAt:      DateTime @default(now())
```

`ASSET_TYPES` (`apps/api/src/modules/supporting-operations/information-asset.config.ts`):
`customer_data | policy_data | document_store | backup | integration | other`
— the same six values from the model's own schema doc comment, validated via
`@IsIn(ASSET_TYPES)` on create/update DTOs (never a free string, even though
the DB column itself carries no enum).

`DataClassification` is the same enum `sensitive-data-handling.md` and
`packages/db/prisma/schema.prisma` already define — validated with
`@IsIn(Object.values(DataClassification), { message: ... })`, matching the
established DTO pattern in
`apps/api/src/modules/claim/dto/attach-claim-documents.dto.ts` (not
`@IsEnum`).

## The rules that aren't obvious

- **`ownerUserId` is a bare scalar with no Prisma relation** (the
  `Opportunity.createdByUserId` shape). The SERVICE layer — not a DB
  foreign key — validates it references a real `User` via
  `UserRepository.findById()`, throwing `NotFoundException` if not found, on
  both create and update (reassignment). This is the same pattern #66 used
  for `Employee`'s optional `userId` link.
- **This is Domain H's first item that needed a genuinely NEW permission.**
  Every prior Domain H process (#66 `employee.manage`/`training.record`/
  `deprovisioning.execute`, #67 `vendor.manage`) found its permission already
  pre-seeded — the established "Domain H seed before code" pattern. #69
  breaks that pattern: `information-asset.manage` had no pre-seeded grant,
  requiring a real `packages/db/prisma/seed-data/permissions.ts` change and
  a re-seed of both dev and test databases. Roles: `[ADMIN, COMPLIANCE]`
  (`SYSTEM_SECURITY_ADMINISTRATOR`, `COMPLIANCE_OFFICER`) — the natural
  owners of an ISO 27001 asset inventory, deliberately not widened to
  `MANAGER` or `EXEC`.
- **The CRUD is deliberately minimal** — create/list(filtered by
  `assetType`/`classification`)/get/update on the model's own four fields,
  the same "foundational CRUD only" scope #67 used for `Vendor` (leaving
  `riskTier` etc. untouched for #71 to extend later). There is no equivalent
  future process expected to extend `InformationAsset` further, but the
  shape is the same: don't build past what the backlog line actually asks
  for.
- **A best-effort audit row never fails the read/write itself** — the
  `safeAudit` try/catch + `logger.error` pattern used consistently across
  every recent process (#60-68).

## Where the code lives

- `apps/api/src/modules/supporting-operations/information-asset.config.ts` —
  `ASSET_TYPES` + the verification-findings doc comment (this file's
  companion — read together, not duplicated).
- `apps/api/src/repositories/information-asset.repository.ts` — `create`/
  `findById`/`findMany`/`update`, wrapping `PrismaService.client.informationAsset`.
- `apps/api/src/modules/supporting-operations/information-asset.service.ts` —
  the `ownerUserId` validation, create/list/get/update, audit writes.
- `apps/api/src/modules/supporting-operations/information-asset.controller.ts`
  — `POST /information-assets`, `GET /information-assets`,
  `GET /information-assets/:id`, `PATCH /information-assets/:id`, all gated
  by `information-asset.manage`.
- `apps/web/app/(app)/information-assets/page.tsx` — list + create + inline
  rename, the `apps/web/app/(app)/vendors/page.tsx` shape.

## Out of scope for this file

- Part A's own gaps (hardware-token MFA, a real KMS/HSM, encryption-at-rest,
  unwired `assertSecureChannel`/`assertExportAllowed` callers, Dev/Test/UAT/
  Prod separation) — tracked in `ibms-app`'s own `README.md` § Known gaps,
  not restated here.
- `IncidentReport`'s own design (the #55 / M09 unified security + personal-
  data breach workflow) — that model's shape belongs in a #55-specific
  context file if one is ever filed; this file only records that it's real
  and what it lacks (a cyber-category taxonomy).
- Any future extension of `InformationAsset` beyond this flat CRUD (e.g. a
  risk-tiering or review-cadence field, mirroring `Vendor`'s own #67→#71
  extension path) — not asked for by backlog #69's own text, not built here.
