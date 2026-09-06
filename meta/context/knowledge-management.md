# Knowledge Management (Domain H, backlog Part C #74 — closes Domain H)

**Last verified:** `2026-09-06` · **Owner:** `ibms-app`

## What this is

Process 74 — the LAST Domain H (Supporting Operations, #66-74) item. One
checkbox: "a bilingual knowledge base: product knowledge, insurer
appetite, rate guides, regulatory updates."

`KnowledgeBaseArticle` (schema's own doc comment: "Process 74 — product
knowledge, insurer appetite, rate guides, regulatory updates for staff")
pre-exists with zero prior application code — the same "dormant model,
first real writer" shape #58-73 repeatedly found, closing out the whole
domain on the same pattern it opened with (#66 Employee/#67 Vendor were
also dormant-model first-writers).

`kb.publish` (`[COMPLIANCE_OFFICER, BRANCH_DEPARTMENT_MANAGER,
PLACEMENT_TECHNICAL_OFFICER]`) was already pre-seeded — no seed change
needed, Domain H's "seed before code" pattern (broken once, by #69)
holding for the domain's final item too.

## The shapes

```
KnowledgeBaseArticle
  id:          String   @id
  title:       String                # mandatory
  titleAr:     String?                # optional
  category:    String                 # product_knowledge | insurer_appetite | rate_guide | regulatory_update
  bodyEn:      String?
  bodyAr:      String?
  publishedAt: DateTime @default(now())  # no draft state
```

## The rules that aren't obvious

- **"Bilingual" here is OPTIONAL-per-article, not mandatory-both.** The
  sibling model `DocumentTemplate` (Part 11.2 — "bilingual master data:
  coverage types, exclusion clauses, notification templates maintained in
  parallel EN/AR ... for regulator-facing documents") has `nameEn`/
  `nameAr`/`bodyEn`/`bodyAr` ALL `NOT NULL` — both languages are mandatory
  before that kind of document can be used at all. `KnowledgeBaseArticle`
  is the opposite: only `title` is mandatory; `titleAr`/`bodyEn`/`bodyAr`
  are all nullable. An article may exist in English only, Arabic only
  (via `titleAr` with no `bodyEn`), or both — this is a deliberate reading
  of the schema's own nullability, not something to "fix" by making the
  Arabic fields mandatory just because the backlog line says "bilingual."
  Check WHICH bilingual shape a model actually implements (mandatory-both
  vs. optional-per-item) before assuming a word like "bilingual" always
  means the same schema pattern.
- **Creation IS publishing — there is no draft/review workflow.**
  `publishedAt` defaults to `now()` at the DB level with no nullable
  "unpublished" state to represent a draft. This matches the pre-seeded
  permission's own verb: `kb.publish`, not `kb.manage`/`kb.create`/
  `kb.draft`. `POST /knowledge-base-articles` never accepts a
  caller-supplied `publishedAt` — the DB default is the only source.
- **`kb.publish` gates the WHOLE surface (create/list/get/update), not
  just the publish action** — the #67/#69/#71 "one pre-seeded permission
  gates the whole CRUD" precedent applied again. This has a real,
  documented consequence: only `[COMPLIANCE_OFFICER,
  BRANCH_DEPARTMENT_MANAGER, PLACEMENT_TECHNICAL_OFFICER]` can even READ
  the knowledge base via this API — no second, broader read permission
  was pre-seeded for this process. A genuinely useful company-wide
  knowledge base would likely want much wider read access (Sales, Claims,
  Finance, ...), but the backlog's own permission grid doesn't anticipate
  that, and there is no second permission code to expand into. This is a
  real, deliberate scope limit — documented, not solved by inventing a
  permission the seed data doesn't define.
- **`category` is mutable via `PATCH`, unlike #72-73's `BcpDrPlan.scenario`
  (deliberately immutable there).** Recategorizing an article is just
  fixing metadata (an editor mis-picked the category), not rewriting a
  scenario's own history the way changing a disaster-recovery plan's
  scenario would. Different models in the SAME domain can make different
  mutability calls for the SAME-shaped "classifying dimension" field —
  check what the field actually represents (a fixed identity vs. an
  editable classification) rather than copying the immutability decision
  from the most recently built sibling process.
- **No maker/checker, no SLA timer, no cross-entity FK validation** — the
  simplest Domain H CRUD built this session, comparable to #67 Vendor's
  original minimal scope. There is nothing else in this schema for a
  `KnowledgeBaseArticle` to reference (unlike #72-73's `planDocumentId`
  validated against `Document`), and nothing in the backlog names an
  approval step for publishing.

## Where the code lives

- `apps/api/src/modules/supporting-operations/knowledge-base-article.
  config.ts` — `KB_CATEGORIES`, the full design rationale (including the
  `DocumentTemplate` bilingual-shape contrast).
- `apps/api/src/repositories/knowledge-base-article.repository.ts` —
  `create`/`findById`/`findMany`/`update`.
- `apps/api/src/modules/supporting-operations/knowledge-base-article.
  {service,controller,module}.ts`.
- `apps/web/app/(app)/knowledge-base/page.tsx` — list (English + Arabic
  title columns, RTL-aware inputs) + a bilingual publish form + inline
  title/titleAr edit.

## Out of scope for this file

- Any broader, company-wide read permission for the knowledge base — a
  real, documented gap; not solved here since the backlog's own
  pre-seeded grid names only `kb.publish`.
- `DocumentTemplate` (Part 11.2) itself — a separate, still-unbuilt model
  for regulator-facing bilingual formal documents, mentioned here only as
  the contrasting "mandatory-both" bilingual shape.
- This closes Domain H (#66-74) entirely — see `employee-onboarding.md`
  (#66, opens the domain), `procurement.md` (#67), `information-asset-
  inventory.md` (#69), `document-management.md` (#70),
  `vendor-management.md` (#71), and `bcp-dr-planning.md` (#72-73) for the
  rest of the domain. #68 (Internal IT) was verified-covered with no
  build and has no dedicated context file here — see `ibms-app`'s own
  README § Known gaps for that verification.
