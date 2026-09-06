# Business Continuity & Disaster Recovery Planning (Domain H, backlog Part C #72-73)

**Last verified:** `2026-09-06` · **Owner:** `ibms-app`

## What this is

Process 72-73. Two checkboxes: a plan for every scenario the source names
explicitly (system outage, site/office loss, cyberattack/ransomware,
key-staff unavailability, insurer-side service interruption); a documented
RTO/RPO + last-tested date + next-test-due date per plan.

`BcpDrPlan` (schema's own doc comment: "Process 72-73 — continuity/DR
plans and tests") pre-exists in the core schema with zero prior application
code — the same "dormant model, first real writer" shape #58-71
repeatedly found. `bcp-dr.manage`
(`[SYSTEM_SECURITY_ADMINISTRATOR, COMPLIANCE_OFFICER]`) was already
pre-seeded — no seed change needed.

## The shapes

```
BcpDrPlan
  id:             String   @id
  scenario:       String   # system_outage | office_site_loss | cyberattack_ransomware
                            # | key_staff_unavailability | insurer_service_interruption
  planDocumentId: String?  # bare scalar, no Prisma relation — validated against a real Document
  rtoHours:       Int?
  rpoHours:       Int?
  lastTestedAt:   DateTime?
  nextTestDueAt:  DateTime?
```

No `createdAt`/`id`-ordering field exists at all — genuinely bare. No DB
unique constraint on `scenario` — multiple plan rows can exist per
scenario (e.g. a superseded plan kept for history); this process does not
invent a "current plan per scenario" resolution the model gives no
timestamp to support.

## The rules that aren't obvious

- **`meta/lex/backup-rpo-rto.md` already covers ONE narrow, already-tested
  slice of scenario #1 (`system_outage`) — the database backup/restore
  drill** (`.github/workflows/backup-drill.yml` +
  `scripts/backup-restore-drill.sh`, weekly, a real pass/fail on row-count
  parity + a timed RTO check). That lex file's own RPO/RTO figures (24h /
  15min) are DRAFT, database-specific, and pre-date this process — this
  module does not restate or duplicate them. A `BcpDrPlan` row for
  `system_outage` may cite that drill as supporting evidence, but the
  other four scenarios are organizational/procedural plans with NO
  code-level automation anywhere in this repo. `BcpDrPlan` is a plain
  record of a plan's existence and test history, not a system that
  executes or verifies the plan itself — don't conflate "this process is
  built" with "disaster recovery is automated."
- **No sourced test-cadence figure exists for BCP/DR plans generally.**
  Unlike #71's Vendor annual review (an explicit "Annual" cadence already
  in `pdpl-sla-timers.md`), nothing in this repo or `ibms-brain` names how
  often a `key_staff_unavailability` plan (say) must be re-tested.
  `nextTestDueAt` is therefore a plain CALLER-SUPPLIED field on
  `recordTest()` (`RecordBcpDrPlanTestDto.nextTestDueAt`, mandatory), never
  auto-computed from a fabricated interval — do not invent a cadence
  (annual, quarterly, or otherwise) without a real source citation.
- **This is deliberately NOT wired into `SLA_REGISTRY`
  (`sla-registry.config.ts`).** That registry is for PDPL-sourced SLAs
  `pdpl-sla-timers.md` tracks (M03-M10 business rules); BCP/DR testing
  cadence is a CBJ operational-resilience concern (Part 10.4/10.5), a
  different regulatory domain entirely. `isTestOverdue()` is a plain pure
  function (`bcp-dr-plan.config.ts`) computed on read, not a `SlaTimer`
  row with an escalation sweep — a real, deliberate scope difference from
  #66/#71's SLA-timer-backed processes, not an oversight.
- **Checkbox 1 ("plans for every scenario") is answered by a genuine
  coverage/gap check, not just a CRUD a caller must trust was populated
  correctly.** `GET /bcp-dr-plans/coverage` (`computeScenarioCoverage()`)
  returns all five named scenarios every time, each with its own `plans`
  array (possibly empty) and a `hasPlan` flag — the #59/#69 "verify
  coverage, don't just build a CRUD and assume backlog intent is
  satisfied" discipline applied to a five-item checklist instead of a
  single field.
- **`planDocumentId` is validated against a real `Document`** via
  `DocumentRepository.findById()` in the service layer (404 if not found)
  — the #66 `Employee.userId` / #69 `InformationAsset.ownerUserId`
  bare-scalar link-validation precedent, now reachable because #70
  (Document Management) built real `Document` CRUD for this process to
  validate against.
- **`scenario` is immutable once a plan is created** — `UpdateBcpDrPlanDto`
  does not accept it. Reclassifying a plan to a different scenario would
  just be creating a new plan for that scenario instead.

## Where the code lives

- `apps/api/src/modules/supporting-operations/bcp-dr-plan.config.ts` —
  `BCP_DR_SCENARIOS`, `isTestOverdue()`, `computeScenarioCoverage()`, the
  full design rationale as a header comment (including the
  `backup-rpo-rto.md` cross-reference).
- `apps/api/src/repositories/bcp-dr-plan.repository.ts` —
  `create`/`findById`/`findMany`/`update`/`recordTest`.
- `apps/api/src/modules/supporting-operations/bcp-dr-plan.service.ts` —
  the `planDocumentId` validation, `coverage()`.
- `apps/api/src/modules/supporting-operations/bcp-dr-plan.controller.ts` —
  `POST /bcp-dr-plans`, `GET /bcp-dr-plans` (+ `?scenario=`),
  `GET /bcp-dr-plans/coverage`, `GET /bcp-dr-plans/:id`,
  `PATCH /bcp-dr-plans/:id`, `POST /bcp-dr-plans/:id/record-test`.
- `apps/web/app/(app)/bcp-dr-plans/page.tsx` — the coverage view (all five
  scenarios, gaps flagged in red) + a create form + per-plan
  record-test action.

## Out of scope for this file

- The database backup/restore drill itself (`backup-rpo-rto.md`,
  `scripts/backup-restore-drill.sh`) — unchanged by this process, still
  the one piece of real infrastructure automation touching any of the
  five scenarios.
- Any future automated BCP/DR test-cadence SLA — would need a real sourced
  figure (a `PRIV-SOP`/CBJ circular citation) before joining
  `SLA_REGISTRY`, not invented here.
- Knowledge Management (`KnowledgeBaseArticle`, backlog #74) — the last
  remaining Domain H item, a separate, still-unbuilt model.
