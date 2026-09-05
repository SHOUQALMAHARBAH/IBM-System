# Sales Performance (Process 59)

**Last verified:** 2026-09-10 · **Owner:** Branch/Department Manager, Executive
Management (roles, not yet named people)

## What this is

Backlog Part C #59, the second item in Domain G (Management) — "Sales
Performance: a query per employee/team against target." Like #58, this is a
one-liner with no named model and no target metric. Unlike #58 (which read
tables that already existed everywhere), #59 needed a genuinely new concept
this codebase had never had before: a **target** — a quota someone commits
to hitting, set by a Manager for an employee or a team ahead of time.

## The metric this process picked, and why

The target is `SalesTarget.targetNewProspects` — the count of `Prospect`
rows (a `Lead` successfully qualified, Process 1→2) attributable to one
Sales/Relationship Officer's `Lead.ownerUserId`/`Prospect.salesOwnerUserId`,
or to every user in one `Branch`, created inside `[periodStart, periodEnd)`.

This was **deliberately NOT premium or commission-based**, even though that
is the more obvious "sales performance" number a manager might expect:

- `Policy.placedByUserId` and `Opportunity.createdByUserId` name the
  **Placement** officer who bound the cover, not the Sales Officer who
  sourced the customer — Process 11 provenance, a different role in this
  codebase's segregation model (`roles-and-segregation-of-duties.md`).
- `Customer.prospectId` is **optional** — `CustomerService.create` accepts a
  Customer with no Prospect at all (a direct corporate onboarding), so there
  is no reliable way to walk `Policy → Opportunity → Customer → Prospect →
  salesOwnerUserId` for every policy. Some policies would have no
  attributable Sales Officer at all, and guessing would silently under- or
  over-count someone's quota.

`targetNewProspects` is the one Sales/CRM-domain outcome that is **always**
cleanly attributable via a bare scalar FK that already exists
(`Prospect.salesOwnerUserId`) — no attribution gap, no guessing. Premium/
commission-per-employee is exactly `EmployeePerformanceRecord.premiumWritten`
/ `commissionEarned` (Process 61, Part 13 core schema, not yet consumed by
any application code) — that dimension is deliberately left there rather
than duplicated here with a shakier attribution story.

## The model

`SalesTarget` (migration `20260910120000_add_sales_target`, a genuinely new
migration — unlike #60/#61's `InsurerPerformanceScore`/
`EmployeePerformanceRecord`, both already pre-existing in the core schema,
#59 had no schema at all before this process):

- `ownerUserId` / `branchId` — **bare scalars, no Prisma relations** (the
  `Opportunity.createdByUserId`/`Policy.placedByUserId` provenance shape).
  Exactly one is set, never both, never neither — enforced at THREE layers:
  `isExactlyOneScope()` (pure, in the DTO validation path), a hand-authored
  DB `CHECK` (`SalesTarget_owner_xor_branch`, since Prisma has no
  cross-column CHECK syntax), and re-checked again for the READ side's own
  scope resolution in `SalesPerformanceService.report()`.
- `periodLabel` + `periodStart`/`periodEnd` — unlike #60/#61's job-driven
  `periodLabel`-only rows (a job fully controls what window its own label
  represents), #59's target is resolved by a **live query**, so the actual
  date window is stored explicitly rather than re-derived from the label
  string. `periodLabel` stays purely a display convenience.
- `targetNewProspects` — the one number a Manager sets and can later PATCH
  to revise (the scope/period are fixed at creation — retargeting a
  different owner/branch/window is a new row, the
  `ProfessionalIndemnityPolicy` renewal-is-a-new-row shape).

### The uniqueness gotcha this process avoided

"At most one target per owner per period label" and "at most one target per
branch per period label" are enforced by **two separate hand-authored
PARTIAL unique indexes** —

```sql
CREATE UNIQUE INDEX "SalesTarget_owner_period_unique"
  ON "SalesTarget"("ownerUserId", "periodLabel") WHERE "ownerUserId" IS NOT NULL;
CREATE UNIQUE INDEX "SalesTarget_branch_period_unique"
  ON "SalesTarget"("branchId", "periodLabel") WHERE "branchId" IS NOT NULL;
```

**NOT** a single `@@unique([ownerUserId, branchId, periodLabel])`. The #48
AML gotcha applies here too: Postgres treats every NULL as distinct in a
plain (non-partial) unique index. Since `branchId` is NULL on every
owner-scoped row, a composite unique across all three columns would never
actually collide on two owner-scoped rows sharing the same owner+period —
the NULL in the `branchId` position makes Postgres treat them as distinct
tuples every time. Two partial indexes, each scoped to the column that's
never NULL for that half of the table, is the correct shape — the
`UpSellRecommendation`/`ClaimFollowUpAlert` precedent.

## How the read resolves

`GET /sales-performance?ownerUserId=&branchId=&periodLabel=`
(`dashboard.sales.view`, already pre-seeded for
`[SALES_RELATIONSHIP_OFFICER, BRANCH_DEPARTMENT_MANAGER,
EXECUTIVE_MANAGEMENT]`):

- A Sales/Relationship Officer is **forced to their own `ownerUserId`**
  regardless of what's passed, and 403s on a `branchId` request outright —
  the `lead.service.ts` `VIEW_ALL_OWNERS_ROLES` shape, reusing
  `common/rbac-visibility.util.ts`'s existing shared constant rather than a
  new local one.
- Manager/Executive must supply **exactly one** of `ownerUserId`/`branchId`
  (422 on both or neither) — there is no "give me everyone" default; a
  general, book-wide sales rollup is `kpi-dashboard.view`'s
  `sales.leadsByStatus`/`prospectsByStatus` (#58), not this endpoint's job.
- No `periodLabel` → resolves the target whose `[periodStart, periodEnd)`
  contains "now" for that exact scope. **No target found is a valid,
  expected response** (`target: null`, `actual: null`,
  `achievementPercent: null`), not an error — this feature's genesis means
  most scopes have no target set yet. An explicit `periodLabel` with no
  match IS a 404 (the caller named a specific period they expected to
  exist).
- A branch scope resolves to every `User.branchId` match, then counts
  `Lead`/`Prospect` across that whole user-id list in one call each — not
  N+1 per employee.

## Permission

`sales-target.manage` (`[BRANCH_DEPARTMENT_MANAGER, EXECUTIVE_MANAGEMENT]`,
151st permission) is the one genuinely new permission this process added —
gates `POST`/`PATCH`/`GET /sales-targets*` (the raw registry). The
performance READ reuses `dashboard.sales.view`, which was already pre-seeded
for `[SALES_RELATIONSHIP_OFFICER, BRANCH_DEPARTMENT_MANAGER,
EXECUTIVE_MANAGEMENT]` ahead of #59 ever being built — the same
"#59-65's permissions were pre-seeded, #58/#59 each needed exactly one real
new permission" pattern `kpi-dashboard.md` already documented for #58.

## Where the code lives

- `apps/api/src/modules/management-reporting/sales-performance.
  {config,service,controller,module}.ts` + `dto/`.
- `apps/api/src/repositories/sales-performance.repository.ts` — owns both
  `SalesTarget` CRUD and the live actual-count queries; there is no other
  natural home for a per-scope Lead/Prospect count the way there is for
  #58's book-wide aggregates.
- `apps/web/app/(app)/sales-performance/page.tsx` +
  `lib/management-reporting/sales-performance-api.ts`.

## Out of scope for this file

#60's `InsurerPerformanceScore` / #61's `EmployeePerformanceRecord` — both
already-schema'd periodic-job models, neither touched by this process.
Reconciling `targetNewProspects` against #61's future `premiumWritten`
figure if they're ever shown side by side — they measure different things
(pipeline throughput vs. bound premium) and are not meant to reconcile.
