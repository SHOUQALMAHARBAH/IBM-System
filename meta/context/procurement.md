# Procurement (Process 67)

**Last verified:** 2026-09-18 · **Owner:** Compliance Officer,
Branch/Department Manager, System Security Administrator (roles, not yet
named people)

## What this is

Backlog Part C #67. The backlog's own text carries an explicit scope
warning — worth quoting in full, since it is the entire design brief:
"The two source documents give no more than a one-line general description
('purchase requests and vendor selection for non-insurance operational
needs') — no field-level detail or defined workflow in the source. The
only task actually executable from the source directly: use `Vendor`
(with `vendorType=other`) as the general vendor record for this purpose,
without inventing a purchase-request model that isn't in the text."

**No `PurchaseRequest` model, no approval workflow, nothing beyond the
literal instruction was built.** This is deliberate — this backlog is the
opposite case from most: instead of mapping a vague requirement to the
closest existing signal, the source material itself says exactly which
existing model to reuse and exactly what NOT to invent.

## `Vendor` is a genuinely shared register — three consumers, one model

`Vendor`'s own schema doc comment: "Merges Process 71 (Vendor Management)
and PDPL third-party governance — both describe the same register in
these two source documents." #67 adds a THIRD consumer to the same model:
Procurement's non-insurance vendors, `vendorType: 'other'`. All three
consumers — #67 (this process), #71 (Vendor Management, risk tiering +
DPAs + annual review), and Part D's Third-Party & Data Sharing PDPL
section — read and write the SAME `Vendor` rows, distinguished only by
`vendorType` and by which OPTIONAL fields each consumer populates.

`Vendor` had zero prior application code before this process — the same
"dormant model, first real writer" shape #58-66 repeatedly found.

## What #67 built vs. what stays #71's job

`VendorRepository`/`VendorService`/`VendorController` implement ONLY the
foundational CRUD: `create` (name, vendorType), `list` (optional
`vendorType` filter), `get`, `update` (name/vendorType only). **Deliberately
NOT touched by any #67 code path**: `riskTier`, `annualReviewDueAt`,
`terminationDataReturnConfirmedAt`, `accessRevokedAt` — all four exist on
the `Vendor` model already, all four are #71's own future feature (risk
tiering before any data share, the mandatory DPA-for-Medium/High-tier
rule, the `vendor_annual_review` `SLA_REGISTRY` entry already sourced in
`pdpl-sla-timers.md`). #71, when built, extends the SAME `VendorModule`
with new methods/routes on the SAME `VendorRepository` — not a second,
parallel Vendor CRUD.

`vendorType` is validated against the exact 7-value set from the schema's
own doc comment (`insurer | reinsurer | loss_adjuster | it_cloud |
printing_archiving | marketing_call_centre | other`) via `VENDOR_TYPES`
(`vendor.config.ts`) — a caller cannot write an arbitrary string into a
column with no DB-level enum.

## Permission

`vendor.manage` (`[COMPLIANCE_OFFICER, BRANCH_DEPARTMENT_MANAGER,
SYSTEM_SECURITY_ADMINISTRATOR]`) was already pre-seeded — zero seed
change, the Domain H "seed before code" pattern. Its own seed description
already says "Manage a vendor record AND ITS RISK TIER" — anticipating
#71's extension to the SAME permission, not a new one.

## Where the code lives

- `apps/api/src/modules/supporting-operations/vendor.
  {config,service,controller,module}.ts` + `dto/`.
- `apps/api/src/repositories/vendor.repository.ts`.
- `apps/web/app/(app)/vendors/page.tsx` — a single list+create+inline-rename
  screen (no separate detail page; nothing rich exists per vendor yet).

## Out of scope for this file

#68-74 (Internal IT, Cybersecurity, Document Management, Vendor
Management, BCP/DR, Knowledge Management) — the remaining Domain H items.
Risk tiering, DPAs, the annual-review SLA wiring, and data-sharing
approval — all #71's/Part D's own future work on this SAME `Vendor`
model, not a separate one.
