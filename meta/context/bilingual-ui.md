# Bilingual UI (Part F, backlog Part 11)

**Last verified:** 2026-09-08 (item #7 — system-generated bilingual
documents — PARTIALLY built: complaint acknowledgement (the vertical
slice proving the FIRST document-generation infrastructure this app has
ever had — headless-Chromium HTML-to-PDF rendering, empirically verified;
the previously-dormant `DocumentTemplate` model activated; a
`@code-reviewer` pass caught and fixed 2 real deployability/reliability
BLOCKERs, and the actual Docker-build verification that followed caught
and fixed a THIRD) PLUS quotation comparison (the second document type,
reusing all of the first's shared infrastructure, promoting
`escapeHtml`/date/money formatting/CSS into a genuinely shared
`document-html.util.ts`, and adding a new customer-visibility-preserving
`ComparisonService.getByIdWithCustomer()` rather than shortcutting around
`ComparisonMatrix`'s existing per-customer access rule) — the other 4
document types remain open, documented future
work — after item #6 remainder — fuzzy transliteration matching (a
curated synonym table only; a distance-based fuzzy matcher was evaluated
and REJECTED after empirical testing), item #6 itself — bilingual
full-text search, item #4 — Arabic-first input (closed, one narrow
exception), item #5 — locale-aware number/date formatting (partial), item
#3 — bidi text handling, item #2 — full RTL layout, and item #1 — instant
language switch) · **Owner:** none named;
cross-cutting, applies to every screen.

## What this is

Part F names 8 cross-cutting tasks, each applying to every screen in the app, not a
single module:

1. Instant language switch without losing session context + a persistent per-user
   language preference — **built** (see "What item #1 covers" below).
2. Full RTL layout for Arabic and LTR for English (navigation, forms, tables, charts
   genuinely mirrored, not just mirrored text) — **built** (see "What item #2
   covers" below).
3. Bidirectional (bidi) text handling for mixed-content fields — **built, this
   entry.** Distinct from Notices/`PrivacyNoticeDisplay` (Part D), which renders
   `textAr`/`textEn` side by side with `dir="rtl"` on the Arabic paragraph — a
   CONTENT-level bidi display of two whole, separate fields, not the
   mixed-content-in-one-field case this item actually names.
4. Arabic-first input (Arabic keyboards, national-ID-convention name fields, correct
   Arabic sorting) — **CLOSED, this entry.** All three sub-problems are now
   addressed: Arabic sorting (built earlier — `'ar'` locale collation); Arabic
   keyboards (verified CLEAR — no code change needed, see "What item #4 covers"
   below); national-ID-convention name fields (built — a real schema migration
   splitting `Customer`/`Employee`/`UltimateBeneficialOwner` names into the
   Jordanian given/father's/grandfather's/family-name convention).
   `InsuredPerson` (the 4th model with a national ID field) is the one
   deliberate exception — it has zero CRUD anywhere in this app yet, so
   splitting its name now would be schema-only busywork; revisit once its CRUD
   exists (see "What item #4 does NOT cover" below).
5. Locale-aware number/date/currency formatting (Gregorian + optional Hijri, JOD base +
   multi-currency for reinsurance) — **PARTIALLY built, this entry: number/date
   formatting only.** Hijri calendar and multi-currency (reinsurance) support are
   explicitly deferred as future work (see "What item #5 covers/does NOT cover"
   below) — a user scoping decision: this bullet bundles three sub-problems of very
   different size ("optional" per the bullet's own wording for Hijri), and the user
   confirmed fixing only number/date formatting for now.
6. Full-text search across Arabic and English with fuzzy transliteration matching —
   full-text search **built** (see "What item #6 covers" below); fuzzy
   transliteration matching **PARTIALLY built, this entry: a curated synonym table
   only** (see "What item #6 remainder covers" below) — a distance-based fuzzy
   matcher (the other real way to do this) was evaluated and REJECTED after
   empirical testing against this Postgres install showed an unacceptable
   false-positive rate, not merely deferred for later. Same-script typo tolerance
   (`pg_trgm`) remains explicitly deferred as future work. `Insurer` remains excluded
   from the entity scope — it has no dedicated module or web list page anywhere in
   this app (only narrow lookups inside RFQ/commission), so adding search to it would
   mean building its first browse screen from scratch.
7. System-generated bilingual documents (quotation comparison, recommendation report,
   policy schedule, invoices, certificates, complaint acknowledgements) — **PARTIALLY
   built, this entry: complaint acknowledgement only**, the vertical slice chosen (via
   `AskUserQuestion`) to prove the shared rendering pipeline before extending to the
   other 5. `Document` (Process #70) is version/classification METADATA tracking, not a
   generator — this item builds the FIRST real document-generation infrastructure this
   app has ever had (see "What item #7 covers" below), including activating the
   previously-dormant `DocumentTemplate` model (Part 11.2).
8. Four-state (loading/empty/error/populated) screenshot evidence per screen — a
   verification DISCIPLINE overlay on 1-7, not a separate build item.

Worked one item at a time, the Part D/E pacing convention — this file now covers
items #1-7 (item #4 CLOSED with one narrow, documented exception; items #5, #6, and #7
PARTIAL, by explicit user scoping decision). Item #8 is unbuilt; do not
assume it is covered by any earlier item's own infrastructure without
checking that item's own "does NOT cover" section below.

## What item #1 covers

**The switch itself, not app translation.** `User.languagePreference` (`LanguagePreference`
enum: `AR`/`EN`, `@default(AR)`) pre-existed in the schema, readable via `GET /auth/me`,
but write-once-at-signup only — no update path, and nothing on the frontend ever
applied it to rendering. This item:

- Adds `PATCH /auth/me/language` (`auth.controller.ts`) — every authenticated user
  manages their own preference, no permission beyond being signed in (the `GET
  /auth/me` shape), no maker/checker (a personal UI preference, not a business
  decision). Returns the fresh `me()` shape.
- `UserRepository.updateLanguagePreference()` — the `setMfaEnabled`/`updatePassword`
  self-service-update shape.
- `apps/web/lib/i18n/language-context.tsx` — a `LanguageProvider` (wraps `AuthProvider`'s
  children in `app/layout.tsx`) exposing `language`, `setLanguage()`, `t()`. See
  `meta/designs/2026-09-bilingual-ui-i18n-architecture.md` for the full "why a hand-rolled
  context, not next-intl" reasoning — the short version: "instant... without losing
  session context" reads as a same-URL, client-only toggle, which a locale-routing
  library's default App Router integration does not give you for free.
- `apps/web/lib/i18n/translations.ts` — a small, real (not stubbed) dictionary + `t()`
  lookup, scoped ONLY to the switcher control and the `AppNav` account footer (signed-in-as
  / role / sign-out) for this item.
- A switcher (two toggle buttons, `aria-pressed`, always showing "العربية"/"English" —
  the TARGET language's own name, never translated based on current state, the
  conventional language-switcher UX) mounted in `AppNav`'s footer — visible on every
  authenticated screen, since `AppNav` wraps the whole `(app)` route group.
- `<html lang>`/`<html dir>` set reactively client-side on every switch — `dir="rtl"`
  for AR, `"ltr"` for EN. This is a REAL, functional RTL trigger at the document level
  (the browser's own bidi/RTL layout engine responds to it immediately), but individual
  screens have not been LAID OUT with RTL in mind — that polish is item #2.

## What item #1 does NOT cover (read before assuming otherwise)

- **The ~80 other screens' text is still English-only.** Only the switcher control and
  the `AppNav` footer are bilingual. Do not assume `t()`/`translations.ts` covers any
  page content — check `translations.ts`'s own key list directly.
- **No SSR-aware initial locale.** `app/layout.tsx` still hardcodes `<html lang="en">`
  for the FIRST server-rendered paint (no locale cookie/middleware exists) — the
  correct `dir`/`lang` is applied client-side, after hydration, via `LanguageProvider`'s
  own `useEffect`. An Arabic-preferring user can see a brief LTR flash on first load.
  Documented, accepted limitation (design doc's own "Consequences").
- **Login/signup have no switcher.** Both live outside `AppLayout`/`AppNav` (the
  authenticated shell) — a `languagePreference` has nowhere to persist against before
  an account exists. Not wired in this pass.
- **No bidi mixed-content handling** (item #3), Arabic input/sorting (item #4), locale
  formatting (item #5), bilingual search (item #6), or document generation (item #7).

## What item #2 covers

**Structural layout mirroring, not translation.** Item #2 is scoped to the
mechanism — does the LAYOUT of nav/forms/tables/charts genuinely flip sides
under `dir="rtl"` — not to translating the ~80 still-English screens (that
remains unbuilt, exactly as item #1 left it; see "What item #2 does NOT
cover" below). Two techniques, chosen per-surface rather than one blanket
approach:

- **CSS logical properties, everywhere a physical direction was previously
  hardcoded.** Every `textAlign: 'left'/'right'` → `'start'/'end'`,
  `marginLeft/Right` → `marginInlineStart/End`, `borderLeft/Right` →
  `borderInlineStart/End`, `paddingLeft/Right` → `paddingInlineStart/End`
  across all `apps/web/components/**/*.styles.ts` shared style modules and
  every page that inlines a style object — a mechanical, one-for-one
  substitution (60 files, ~110 lines), verified by a whole-codebase grep
  confirming **zero remaining physical-direction CSS properties anywhere in
  `apps/web`** after the change. Because these are LOGICAL values, they read
  back unchanged in both directions (`getComputedStyle().textAlign` still
  reports `"start"` whether the page is AR or EN) — proving the mirroring
  actually happened requires a real bounding-box assertion, not a
  computed-style check (see `apps/web/e2e/rtl-layout.spec.ts`).
- **Free mirroring from existing `display: flex`/`flexDirection: row` +
  `dir` cascading.** The app shell's sidebar (`components/app/app.styles.ts`
  `shellStyle`) already used plain `flexDirection: 'row'` — once `dir="rtl"`
  cascades from `<html>` (item #1's own mechanism), the browser mirrors flex
  item order for free with NO CSS change needed; the sidebar's separator
  border was the one thing that needed converting (`borderRight` →
  `borderInlineEnd`, so it stays on the edge touching the content column,
  not the outer edge, in both directions).
- **Native `<table>` column mirroring is a plain browser default once
  `direction` inherits as `rtl`** — no CSS or markup change needed at all.
  57 files use a native `<table>` element; none needed touching for this
  item. Verified directly (bounding-box comparison of the first vs. last
  column header) on one representative page
  (`apps/web/app/(app)/watchlist-sync/page.tsx`) rather than assumed for all
  57 — the mechanism is a browser universal, not a per-page CSS concern, so
  one proof stands for all of them.
- **Charts: N/A, not silently skipped.** Grepped the whole `apps/web` tree
  for `recharts`, `chart.js`, `d3`, `<canvas>`, `<svg>` — this app has NO
  chart/graph visualization anywhere (dashboards render numbers/tables, not
  visual charts; the only real `<svg>` files are Next.js's own boilerplate
  `public/*.svg` assets). The "charts genuinely mirrored" sub-requirement is
  vacuously satisfied today — there is nothing to mirror — and this is
  worth re-checking the day this app's first real chart component lands,
  since SVG/canvas do NOT inherit CSS logical-property mirroring the way
  flex/table layout does; a future chart will need its own RTL treatment,
  not a free ride from this item's work.

## What item #2 does NOT cover (read before assuming otherwise)

- **Translation of the ~80 still-English screens** — completely unchanged
  from item #1. A screen's LAYOUT now mirrors correctly under `dir="rtl"`,
  but its text is exactly as English as it was before this item. Hardcoded
  English prose containing a directional character (e.g. "New → Contacted →
  Qualified" in `leads/page.tsx`) stays exactly as written — that is a
  translation/bidi-text concern (items #3-8's OWN later scope, not this
  one), not a layout-mirroring bug.
- **No SSR-aware initial `dir`** — unchanged from item #1's own documented
  gap; the brief LTR flash on first load for an Arabic-preferring user is
  still present.
- **No new component library or per-component RTL audit was needed** —
  this app has no shared Table/Card/Modal component (reuse happens via
  shared `*.styles.ts` constant modules), so centralizing the fix in those
  ~18 shared modules plus a mechanical per-page sweep covered the whole
  surface in one pass; there was no separate "component-by-component RTL
  audit" step to do.
- **Forms**: covered structurally (shared `formRowStyle`/`checkboxRowStyle`
  in `lead.styles.ts` and `inputStyle`/`labelStyle` in
  `auth-form.styles.ts` were already direction-agnostic flex layouts with no
  physical properties) — not a separate build step, a confirmation that the
  existing shared primitives already had zero RTL debt.

## What item #3 covers

**A single field/string that may itself mix Arabic and Latin script** — e.g.
an Arabic customer/company legal name, an Arabic insurance-line label sitting
next to a Latin policy number, an Arabic address containing a Latin building
number, a person's name typed in either script. This is distinct from item
#2 (whole-SCREEN layout mirroring) and distinct from `PrivacyNoticeDisplay`'s
`textAr`/`textEn` (two whole, separate single-language fields shown
together, not one field mixing scripts). Per `verification-contract.md`'s own
"Bidirectional text" section, the four named categories are: Arabic
customer/company names containing English codes, Arabic insurance names
containing policy/product codes, English reference numbers inside Arabic
forms, Arabic addresses containing Latin characters — no concrete field list
existed anywhere in the brain beyond these four categories; a codebase survey
(schema + render-site grep) identified the real fields at risk.

Two native, zero-JS-logic HTML/CSS mechanisms cover this, applied at ~30
files:

- **Display**: every dynamically-rendered value from an at-risk field is
  wrapped in a native `<bdi>` element — `<bdi>{value}</bdi>`. `<bdi>`
  isolates the value's bidi runs from surrounding text and auto-detects its
  own base direction from content — the exact mechanism the HTML spec
  designed for "third-party/user-generated content of unknown
  directionality." Where two independently-directioned values are joined by
  a literal separator (e.g. `PolicySection.tsx`'s
  `insuranceLine · policyNumber`, `ClaimSection.tsx`'s claim-number line and
  `causeOfLoss — lossLocation`), each value is wrapped SEPARATELY — `` <bdi>
  {a}</bdi> · <bdi>{b}</bdi> `` — so the separator glyph sits between two
  isolated runs and stays stable, rather than one wrapper around the whole
  concatenated string. Fixed once at the shared `ProfileField` primitive
  (`customers/[id]/page.tsx`, `prospects/[id]/page.tsx`) rather than
  per-call-site, the same "fix the shared primitive once" precedent item #2
  used for `app.styles.ts`.
- **Form inputs**: `dir="auto"` added to every `<input>`/`<textarea>`
  capturing a field that may be typed in either script (name, address,
  free-text description, insurance-line filter) — the browser then sets
  caret/alignment direction from the first strong character typed, instead
  of inheriting a fixed direction from the page.
- Fields NOT touched: dedicated single-language pairs (`titleAr`/`bodyAr`/
  `textAr`/`nameAr`) — already correctly handled via hardcoded `dir="rtl"`
  from earlier work, not a mixed-content case; enum/status/id fields
  (ASCII-only, no bidi ambiguity); `WatchlistEntry`/`ScreeningResult` fields
  (confirmed via grep — never rendered on the frontend at all, a
  backend-only model; screening logs counts/listSource only, per
  `sensitive-data-handling.md`, so there is genuinely nothing to fix there).

## What item #3 does NOT cover (read before assuming otherwise)

- **No visual/pixel proof that bidi rendering "looks right"** — the
  browser's own Unicode Bidirectional Algorithm (UAX #9) implementation is
  not under test here (that's a browser-vendor concern); the new
  `apps/web/e2e/bidi-text.spec.ts` proves only that OUR markup applies the
  isolation mechanism (a genuine `<bdi>` tag around the value, a real
  `dir="auto"` on the input) — a structural claim, not a rendering one. This
  mirrors item #2's own "prove the mechanism, not just that text is
  present" testing philosophy.
- **Translation of the ~80 still-English screens** — unchanged from items
  #1-2; this item is about mixed-SCRIPT isolation within a field, not about
  which language the field's own label/surrounding prose is written in.
- **Arabic-first input or national-ID-convention name fields** (item #4,
  still deferred as of that item's own partial build) — a `dir="auto"` input
  still accepts whatever the OS keyboard sends; it does not add an Arabic
  keyboard or a national-ID-convention name-field layout anywhere. (Arabic
  sorting/collation itself WAS added later, in item #4's own partial build —
  see "What item #4 covers" below; this bullet is intentionally narrower now
  than when item #3 first wrote it.)
- **Locale-aware number/date/currency formatting** (item #5) — untouched.
- **System-generated bilingual documents** (item #7) — untouched; no
  document-generation infrastructure exists in this app yet regardless.
- **Not every string field in the schema** — only fields a real user would
  plausibly type bilingual/mixed content into (names, addresses, product/
  line labels, free-text descriptions, reference numbers shown adjacent to
  those). Pure numeric/enum/id fields were deliberately left untouched.

## What item #4 covers (CLOSED — all three sub-problems addressed)

Item #4's own bullet bundles three sub-problems of very different size.
This entry closes all three: Arabic sorting was built first (see below);
Arabic keyboards were investigated and confirmed clear (no code change
needed); national-ID-convention name-splitting was scoped with the user via
`AskUserQuestion` (which models, and whether to keep the flat display field
as computed) and then built as a real, if narrow, schema migration.

- **Correct Arabic sorting**: every `localeCompare(x, 'en')` call sorting a
  genuinely bilingual name/label field switched to `localeCompare(x, 'ar')`
  — `finance.config.ts` (customer legal name, insurer name ×2, insurance-line/
  segment key), `loss-ratio.config.ts` (customer/insurer/insurance-line
  label), `profitability-analysis.config.ts` (insurance-line/segment key).
  Two DB-level sorts using plain Postgres collation
  (`commission.repository.ts`'s `listInsurers()`,
  `rfq.repository.ts`'s `findSelectableInsurers()`, both sorting
  `Insurer.name`) were converted from Prisma `orderBy` to a fetch-then-JS-sort
  with the same `'ar'` comparator — no DB-level ICU collation migration
  needed, since both are small, unpaginated lookup lists.
- **`'ar'` is HARDCODED, not the calling user's own language preference** — a
  second explicit user scoping decision (asked directly, confirmed). A
  future item could thread the actual caller's `languagePreference` through
  instead; not attempted here.
- **Deliberately NOT touched — two sites where the sorted value is a fixed,
  always-English constant, not user content**: `sla-dashboard.config.ts`'s
  `label` (a hardcoded SLA-workflow name — "DSR — Access / Deletion", etc. —
  from `sla-registry.config.ts`, never Arabic) and
  `role.repository.ts`'s `Role.name` (a `RoleName` enum —
  `SALES_RELATIONSHIP_OFFICER`, etc.). Changing these would have been WRONG,
  not a fix — confirmed by reading each field's actual source before
  deciding, not assumed from the field name alone.
- A genuine, empirically-verified test proves the mechanism: `"إبراهيم
  للتأمين"` sorts BEFORE `"أحمد للتجارة"` under `'ar'` collation but AFTER it
  under `'en'` (verified directly against Node's ICU, not assumed) — a real
  divergence, not an artificial fixture, locked in as a regression test in
  `finance.config.spec.ts`.
- **Arabic keyboards — confirmed CLEAR, no code change needed.** The one
  keyboard-adjacent risk flagged (but not checked) when Arabic sorting
  shipped was finally investigated: grepped all 67 `@Matches` validators
  across every api DTO — none restrict any name field to Latin-only
  characters (all are money/date/score/account-number/currency-code
  patterns); grepped every web `pattern=` attribute — only 3 exist, all on
  6-digit MFA code inputs, unrelated to names; `@Length`/`@MinLength` on
  name fields count JS string length correctly for Arabic script (no
  surrogate-pair miscount, since Arabic sits in the Basic Multilingual
  Plane). Nothing in this codebase blocks or miscounts Arabic input
  anywhere — a real finding, not an assumption, closing this sub-problem
  with no code change.
- **National-ID-convention name-splitting — built.** The Jordanian
  convention (given name + father's name + grandfather's name + family
  name, the four parts on a Jordanian national ID card) is now a real
  schema migration on the 3 models that have BOTH a genuine CRUD surface
  AND an existing `nationalIdEnc` field to verify a split name against:
  `Customer` (`INDIVIDUAL` type only — `CORPORATE.legalName` is a company
  name, untouched), `Employee`, `UltimateBeneficialOwner`. Each gained 4
  new nullable columns (`givenName`, `fatherName`, `grandfatherName`,
  `familyName`) via migration
  `20260917120000_add_national_id_name_parts`; the existing flat field
  (`Customer.legalName`/`Employee.fullName`/`UltimateBeneficialOwner.
  fullName`) stays as a computed/denormalized display string, auto-joined
  server-side from the 4 parts by one new shared helper,
  `apps/api/src/common/person-name.util.ts`'s `composeFullName()` — so
  every existing consumer (Arabic sorting above, `<bdi>` display, search,
  audit logs, exports) keeps working unchanged against the same field
  name. `givenName`/`familyName` are required whenever the split applies
  (the two universally-present anchors of a name); `fatherName`/
  `grandfatherName` are optional — a judgment call made in the absence of
  any stricter sourced rule, flagged to the user rather than silently
  assumed. No backfill: historical rows keep only their flat name with all
  4 parts NULL — inventing a split for text no one actually entered that
  way would be fabricating data.
- **`InsuredPerson` deliberately excluded** — the 4th model with a
  `nationalIdEnc` field, but confirmed via grep to have ZERO CRUD anywhere
  in this app (no controller/service/repository ever creates or updates
  one) — splitting its name now would be schema-only busywork with nothing
  to exercise it. Revisit once its CRUD exists (a separate, pre-existing
  gap already documented in `meta/context/consent-management.md`).
- **`'ar'` is HARDCODED for sorting, not the calling user's own language
  preference** — a second explicit user scoping decision from when sorting
  was built (asked directly, confirmed). Name-splitting, by contrast, is
  NOT locale-hardcoded — it threads real user input through, the same as
  any other captured field.

## What item #4 does NOT cover (read before assuming otherwise)

- **`InsuredPerson` name-splitting** — deliberately excluded, see above;
  revisit once `InsuredPerson` CRUD exists.
- **Caller-aware sort locale** — `'ar'` is hardcoded for the Arabic-sorting
  sub-problem specifically (see above); no code reads `languagePreference`
  to pick a sort locale dynamically. This is UNRELATED to name-splitting,
  which is not locale-gated at all.
- **Editing an existing name** — no `update-*.dto.ts` exists for `Customer`/
  `Employee`/`UltimateBeneficialOwner` names today (confirmed by grep before
  starting), so this item only touches CREATE paths; an edit form was never
  in scope to begin with, not a gap this item introduced.
- **A dedicated on-screen Arabic virtual keyboard widget** — "Arabic
  keyboards" was interpreted as "does the app block or mis-handle Arabic
  input," per the backlog bullet's own framing (grouped with a Latin-only
  regex risk and name-field length limits, not with an IME/virtual-keyboard
  feature) — confirmed clear above. Building an actual on-screen keyboard
  widget was never implied by that framing and was not built.

## What item #5 covers (PARTIAL — a deliberate user scoping decision)

Item #5's own bullet bundles three sub-problems: number/date formatting,
Hijri calendar support ("optional" per the bullet's own wording), and
multi-currency for reinsurance. Presented with that breakdown ahead of
implementation, the user explicitly chose: **fix #1 (locale-aware
number/date formatting) now; Hijri calendar and multi-currency remain
deferred future work.**

- **One shared formatting utility, `apps/web/lib/i18n/format.ts`**
  (`formatMoney`/`formatDate`/`formatDateTime`), replacing ~9 duplicated
  local `money()`/`fmtMoney()`/`fmtDateTime()` implementations across
  `apps/web/components/**` and `apps/web/app/(app)/**/page.tsx` — the same
  "fix the shared primitive once" precedent items #2/#3 already established
  (`app.styles.ts`, `ProfileField`). Every duplicate's exact null/non-finite
  fallback behavior (an em dash for `null`, the raw value with a currency
  prefix for a non-numeric string) was preserved byte-for-byte — a
  behavior-preserving consolidation, not a new contract.
- **Driven by the SAME live `useLanguage()` context item #1 already ships**
  — every call site threads the current `language` (`'AR'`/`'EN'`) through,
  either via the hook directly (inside a component) or as an explicit
  `language: Language` parameter threaded into a plain helper function that
  cannot call a hook itself (e.g. `coverageLabel(c, language)` in
  `ClaimSection.tsx`, `oldest(daysOverdue, dueDate, language)` in
  `client-accounting`/`insurer-accounting`).
- **Locale tags were empirically verified against Node's own ICU before
  being chosen, not assumed** — the specific risk: an Arabic REGION tag
  (`'ar-JO'`) silently switches to Eastern Arabic-Indic numerals
  (`١٬٢٣٤٫٥٠٠` instead of `1,234.500`), which nothing in this codebase or
  brain ever asked for and would be a confusing surprise for JOD amounts.
  Bare `'ar'` (no region) keeps Western Arabic numerals while still
  formatting the DATE in genuine Arabic-locale order (`D/M/YYYY`, no
  leading zeros, with invisible RTL direction marks between components) —
  confirmed via `node -e` scripts calling `toLocaleDateString`/
  `toLocaleString` directly, the same "prove it against real ICU, don't
  assume" discipline item #4's sorting fix used. English uses `'en-GB'`
  (`DD/MM/YYYY`), matching the existing backend precedent in
  `audit-anomaly-detection.service.ts` — not bare `'en'`, which would read
  as US-style `MM/DD/YYYY`.
- **User confirmed the locale-tag choice directly** — presented with the
  empirical divergence above via `AskUserQuestion`, the user selected
  `'ar'` + `'en-GB'` over the alternative of a region-qualified Arabic tag.
- **Full mechanical sweep, not a sample** — every `.toLocaleString()`/
  `.toLocaleDateString()`/`.toLocaleString()`-as-datetime call site and
  every duplicated `money()`-shaped helper across `apps/web` was converted;
  confirmed via a whole-codebase grep showing zero remaining
  `toLocaleString`/`toLocaleDateString` calls and zero remaining local
  `money`/`fmtMoney`/`fmtDateTime` function definitions anywhere in
  `apps/web` afterward — the same "grep to confirm zero remaining" bar
  items #2/#3 held themselves to.

## What item #5 does NOT cover (read before assuming otherwise — explicitly deferred future work)

- **Hijri calendar** — out of scope by user decision; every date renders
  Gregorian regardless of language, even though the backlog bullet marks
  Hijri as merely "optional" (not mandatory) rather than unstated.
- **Multi-currency for reinsurance** — out of scope by user decision.
  `formatMoney()` takes a `currency` parameter (defaulting to `'JOD'`) and
  every call site already passes the record's own actual currency where one
  exists, but nothing in this pass added multi-currency SUPPORT beyond what
  already existed (e.g. no currency-conversion, no reinsurance-specific
  formatting rule) — it is the same single-currency-per-record display this
  codebase always had, just locale-aware now.
- **Caller-aware locale IS honored here** (unlike item #4's hardcoded
  `'ar'`) — this item threads the real `useLanguage()` value throughout, not
  a hardcoded constant. Worth noting as a DIFFERENCE from item #4's own
  scoping decision, not an inconsistency: item #4's sort locale lives in a
  backend config with no request-scoped user language available the same
  way; item #5's formatting lives entirely in `apps/web` components that
  already have the hook in scope.
- **Locale-aware number/date formatting elsewhere in the STACK** — this item
  only touches display formatting in `apps/web`. No backend DTO, PDF/export,
  or Prisma-level formatting was touched; `git diff --stat` confirms this
  item's entire diff is `apps/web/**` (plus its own new `e2e`/`lib` test
  files).

## What item #6 covers (PARTIAL — a deliberate user scoping decision)

Item #6's own bullet bundles two sub-problems of very different size.
Presented with that ahead of implementation, the user explicitly chose:
**fix real full-text search now; defer fuzzy transliteration matching AND
same-script typo tolerance as future work.**

- **Entity scope, also confirmed with the user**: `Customer`, `Prospect`,
  `Vendor` — the only 3 entities with BOTH a genuinely bilingual name field
  AND an existing list endpoint + web list page. `Insurer` was considered
  and explicitly EXCLUDED after a follow-up finding, not an oversight: it
  has no dedicated module anywhere (no `insurer.controller.ts`/`.service.ts`
  — only narrow lookups embedded inside RFQ's/commission's own pickers) and
  no `/insurers` web list page at all (only `insurer-accounting`/
  `insurer-performance`, which are per-insurer REPORTS, not a browse
  screen) — the same class of gap item #4 hit with `InsuredPerson`.
- **Mechanism — empirically verified against the actual running Postgres
  (18-alpine), not assumed**: this install ships a real built-in `'arabic'`
  text-search configuration (genuine stemming — verified
  `to_tsvector('arabic', 'شركة الأفق للتأمين')` → `'افق':2 'تام':3
  'شرك':1`, definite articles/prefixes stripped) alongside `'english'`.
  Bilingual documents are built by CONCATENATING both configs' tsvectors —
  `to_tsvector('arabic', text) || to_tsvector('english', text)` — verified
  each config tokenizes text from the OTHER script without erroring
  (passes it through largely unstemmed rather than dropping it), so the
  combined vector matches BOTH a real Arabic stem and an English word from
  the same field. The query side uses `websearch_to_tsquery` (never raw
  `to_tsquery`) against both configs, OR'd — verified empty/punctuation-only
  input degrades to an empty tsquery (a harmless NOTICE, no crash), and an
  injection-shaped test string (`"Ahmad' OR 1=1; --"`) is parsed entirely
  within tsquery's own mini-language when passed through Prisma's
  PARAMETERIZED tagged-template `$queryRaw` — never `$queryRawUnsafe`, never
  string concatenation — confirmed not a real SQL-injection vector this way.
- **One new `GENERATED ALWAYS ... STORED` tsvector column + GIN index per
  model**, computed by Postgres itself (never written to by the app):
  `Customer.searchVector` from `legalName` ONLY —
  `contactPhoneEnc`/`contactEmailEnc` are Highly Confidential -- ENCRYPT
  fields and must never be indexed in plaintext
  (`sensitive-data-handling.md`); `Prospect.searchVector` from
  `companyName` + `contactPerson`; `Vendor.searchVector` from `name`. No
  backfill needed — the generated column computes for every existing row
  the moment it's added.
- **The raw query resolves ids only, never duplicates filter logic**: each
  repository's new `searchIds(term)` returns matching ids via `$queryRaw`;
  the SAME existing Prisma `findMany()` then filters by `id: { in: ids }`
  alongside its existing filters (`ownerUserId`/`status`,
  `salesOwnerUserId`, `vendorType`) — avoids re-implementing any filter in
  raw SQL, the raw query's only job is turning free text into ids.
- **An empty search box means "show everything," not "search for an empty
  string"** — verified empirically that an empty-string tsquery matches
  NOTHING (not everything), so `emptyStringToUndefined` on the DTO's
  `search` field (the same transform this codebase already uses for every
  other optional filter) is load-bearing here, not cosmetic: it turns an
  empty search box into "no filter" before the query ever runs.
- **Two tests per entity prove REAL stemming, not substring luck**: an
  English term that is a Porter-stem of a stored word but never a literal
  substring of it (searching `"trade"` finds a stored `"...Trading Co."`),
  and an Arabic SINGULAR search term that matches a stored PLURAL form via
  a shared stem (searching `"سيارة"` finds a stored `"...للسيارات..."`) —
  both verified directly against this Postgres build before writing the
  assertions, not assumed.
- **This is the first real use of `$queryRaw` with user input anywhere in
  this codebase** — the one pre-existing use (`app.controller.ts`'s health
  check) is a literal `SELECT 1`.

## What item #6 does NOT cover (read before assuming otherwise — explicitly deferred future work)

- **Fuzzy transliteration matching** — PARTIALLY addressed since this was
  first written; see "What item #6 remainder covers"/"does NOT cover"
  below for the curated-synonym-table build and its own, separate,
  documented coverage limit. This bullet is left here as a pointer, not
  duplicated.
- **Same-script typo tolerance** — also out of scope by user decision,
  deferred alongside transliteration rather than built separately.
  `pg_trgm`/`unaccent`/`fuzzystrmatch` are available on this Postgres
  install (confirmed via `pg_available_extensions`) but NOT installed — a
  small misspelling within the same script (e.g. a typo in an English or
  Arabic name) will not match today.
- **`Insurer` search** — out of scope; no dedicated module or web list
  page exists for it at all (see "What item #6 covers" above). Building
  search for it now would mean building its first-ever browse screen from
  scratch, not adding search to an existing one.
- **Search on any field beyond the ones named above** — `Customer`'s
  encrypted contact fields, `Prospect`'s `sector`/`activity`/`location`,
  `Vendor`'s `vendorType`, and every OTHER entity in this app (Policy,
  Claim, Employee, etc.) have no search capability added by this item.
- **Search-as-you-type** — the web search input is submit-triggered (Enter
  key or a "Search" button), not instant/debounced-as-you-type. This app
  has no debounce utility anywhere; introducing one for a first pass was
  judged disproportionate.
- **A relevance-ranked or highlighted result** — `ts_rank`/`ts_headline`
  were not added; results are returned in each entity's own existing sort
  order (`createdAt desc`), a plain filter, not a ranked search experience.

## What item #6 remainder covers (curated synonym table — a deliberate rejection of distance-based fuzzy matching)

Before building anything, two real mechanisms were evaluated empirically
against this actual Postgres install (18-alpine), not assumed:

- **Distance-based fuzzy matching — evaluated and REJECTED as a primary
  match rule.** The `transliteration` npm package (real, maintained) was
  installed and run against common Arabic given names — it outputs a
  Buckwalter-style consonant skeleton (`محمد` → `mHmd`, `أحمد` → `'Hmd`).
  Reducing a natural Latin spelling the same way (strip vowels, fold case)
  and comparing via `pg_trgm` similarity / `fuzzystrmatch`'s `levenshtein()`
  (both installed on `db-test` for this spike, then dropped again
  afterward — this was a research spike, not a build) produced a genuine,
  measured problem: true-positive pairs like "Yousef"/"يوسف" (Levenshtein 1,
  trigram 0.29) scored in the SAME range as a real false positive — "Khaled"
  against a stored "Khalil," a different person (Levenshtein 1, trigram
  0.43). No threshold separates the two. This is the same known collision
  problem Soundex/Metaphone have on short English names, applied to short
  3-5-letter Arabic name skeletons — inherent to phonetic-key matching on a
  small alphabet, not an artifact of this specific normalization; a
  hand-rolled Arabic phonetic key would hit the identical ceiling for more
  build cost. A customer/prospect/vendor search surfacing a different
  person's record on a common name was judged worse than the bounded
  coverage below — presented to the user with the measured numbers via
  `AskUserQuestion` before choosing a direction, not assumed.
- **ICU's Transliterator / commercial transliteration APIs — ruled out
  structurally**, not tested: `Intl` (Node's only ICU surface) exposes
  formatting, not the general Transliterator class, and no well-maintained
  npm binding for it exists; a commercial API would mean sending
  customer/prospect names to a third party — a real PDPL data-residency
  question for identity-adjacent data, plus a new external dependency this
  app has never taken on, disproportionate for a search box.
- **`pg_trgm`/`fuzzystrmatch` alone — ruled out structurally**: they compare
  character sequences within one alphabet; an Arabic string and a Latin
  string share zero characters, so similarity is always ~0 regardless of
  how similar the names actually sound. They can only help AFTER something
  transliterates one side into the other's alphabet — which is exactly the
  mechanism tested and rejected above.

**What was built instead — a curated synonym table**, extending item #6's
existing `searchIds()`/`websearch_to_tsquery` mechanism rather than adding
new fuzzy-matching machinery or a schema migration:

- `apps/api/src/common/name-transliteration.config.ts` — ~50 groups of
  KNOWN equivalent spellings for common Jordanian/Arab given names across
  both scripts (e.g. `['mohammed', 'muhammad', 'mohamed', ..., 'محمد']`),
  including the hamza-dropped Arabic spelling where that's commonly typed
  casually (`أحمد`/`احمد`). `expandSearchTerms(term)` tokenizes the query on
  whitespace and returns every OTHER spelling in any group a token
  exactly (case-insensitively, diacritic-stripped) matches — never a
  distance-based guess, so the false-positive problem above does not
  apply here: this is an exact/stemmed lookup on a literal known term, the
  same guarantee item #6's own tsvector search already gives.
- Each of the 3 repositories' `searchIds(term)` now ORs the original
  `term` with every string `expandSearchTerms(term)` returns, each still
  its own parameterized `websearch_to_tsquery(...)` call via Prisma's
  `Prisma.sql`/`Prisma.join` (no string concatenation — the same
  SQL-injection guarantee as the single-term case). **No schema migration,
  no new column** — this only expands the QUERY side; the existing
  `searchVector` generated column from item #6 is untouched.
- Entity scope is IDENTICAL to item #6 itself (`Customer`, `Prospect`,
  `Vendor`) — this reuses the same `searchIds()` method those repositories
  already had, so there was no separate scoping decision to make here.

## What item #6 remainder does NOT cover (read before assuming otherwise)

- **Any name not in the curated table** — coverage is bounded to the ~50
  groups built (the most common Jordanian/Arab given names), not a
  linguistically authoritative or complete list. An uncommon name gets no
  variant-matching at all; extend the table as real gaps surface.
- **Family-name/surname components** (e.g. "Al-"/"El-" prefixes,
  compound surnames) — deliberately excluded; they compose with far more
  variation than a fixed-group table can safely represent without
  reintroducing false-positive risk.
- **Same-script typo tolerance** — still fully deferred, unchanged from
  item #6's own original scope (see "What item #6 does NOT cover" above).
- **`Insurer` search** — still excluded, unchanged from item #6's own
  original scope (no dedicated module or web list page exists for it).
- **A distance-based/probabilistic fuzzy matcher** — deliberately NOT
  built, for the false-positive reason measured and documented above. A
  future session revisiting this should re-read that finding before
  re-attempting a fuzzy-distance design; the ceiling is inherent to the
  algorithm class, not this implementation.

## What item #7 covers (PARTIAL — complaint acknowledgement + quotation comparison, 2 of 6 document types)

Item #7's own bullet names 6 document types of very different data
richness. Presented with a research spike's findings before implementing,
the user chose: headless-Chromium rendering (empirically tested, not
assumed — see below), generate-on-demand with no persistence (this app has
NO real object storage anywhere — `Document.storageRef` is an opaque
string the CALLER already has to have gotten from somewhere; nothing ever
writes real bytes to real storage), derive "certificate" from
`Policy`+`PolicySchedule` when that type is eventually built (deferred,
not built this pass), and **complaint acknowledgement as the first
document type** — simplest real data, lowest risk way to prove the
pipeline end-to-end.

- **Rendering mechanism — empirically tested against real bilingual
  content, not assumed.** A real HTML page containing Arabic (with an
  RTL table, embedded LTR numbers, mixed-script content) and English was
  rendered to PDF using the headless Chromium already cached locally via
  this repo's own Playwright install (`apps/web`'s e2e-test browser
  binary), then visually inspected: Arabic contextual letter shaping, RTL
  table/paragraph direction, and embedded LTR numbers inside RTL text all
  rendered correctly. A JS-native PDF library (pdfkit/pdfmake) was
  considered and rejected — neither shapes Arabic script itself, and
  there is no well-maintained library to do that reshaping first, a real
  correctness risk for what is now this system's PRIMARY language.
- **`playwright-core` (not `@playwright/test`) — a new `apps/api`
  production dependency.** The browser-automation library alone, without
  the test runner `apps/web`'s e2e suite uses it for; reuses the SAME
  cached Chromium revision rather than triggering an independent
  download. `PdfRendererService` (`apps/api/src/modules/
  document-generation/pdf-renderer.service.ts`) launches ONE shared
  browser for the process lifetime (a fresh browser per request would
  cost ~1-2s of cold-start on every document) and a fresh `page` per
  render, closed immediately after.
- **`DocumentTemplate` (Part 11.2) activated for the first time.**
  Schema-only before this item — no repository/service/controller ever
  read or wrote it at runtime; the only seeded rows were 4 unrelated
  `proposal_form_*` templates (Part B). New
  `DocumentTemplateRepository.findByType()` (a `findFirst`, matching the
  model's own no-unique-constraint shape the seed script's
  `ensureDocumentTemplates()` already established) resolves the ONE new
  real row (`templateType: 'complaint_acknowledgement'`) for its EDITABLE
  boilerplate prose (`bodyEn`/`bodyAr`) — Compliance/Customer Service can
  revise the wording without a code change, the same shape the seeded
  `proposal_form_*` rows already established. Structured, per-instance
  facts (reference, dates, category, SLA due date) are NOT stored in the
  template — real domain data (`Complaint`, its `Customer`, its
  `SlaTimer.dueAt`), merged in by
  `complaint-acknowledgement.template.ts` around the boilerplate text,
  never string-replaced into it. `ComplaintAcknowledgementService` falls
  back to built-in default text (byte-identical to the real seed row's
  wording) when no `DocumentTemplate` row exists yet — generation must
  not hard-fail over a missing editable-prose row.
- **Language selection**: `GET /complaints/:id/acknowledgement?language=
  AR|EN|DUAL` — omitted defaults to the customer's own
  `languagePreference` (the backlog's "client's preferred language"),
  matching item #5's own "thread the real preference through" precedent
  rather than a hardcoded default. `DUAL` renders BOTH languages in one
  PDF as two full sections separated by a page break — **Arabic section
  first, English second**, since Arabic is this system's PRIMARY
  language (a user decision, this session) — not a side-by-side/
  interleaved layout, which would be visually messy mixing two opposite
  reading directions on one line.
- **Generate-on-demand, not persisted** — a deliberate user scoping
  decision given the no-object-storage gap above. `GET /complaints/:id/
  acknowledgement` generates the PDF fresh on every call and streams it
  back (Nest's `StreamableFile`) — no `Document` row is created, no bytes
  are written anywhere. Same `complaint.log` permission as reading a
  complaint (`ComplaintController.get()`) — generating an acknowledgement
  is a read, not a new capability.
- **A genuinely new injection-risk shape, closed deliberately, not
  assumed safe.** `Complaint.issue` is customer-supplied free text
  (`CreateComplaintDto.issue`), and this is the FIRST time this codebase
  renders any user-influenced string inside a REAL browser engine — an
  unescaped `<script>`/`<iframe>` would not be a cosmetic HTML-injection
  bug, it would EXECUTE inside that page context (a real SSRF-shaped risk
  via a headless browser reachable from wherever the api container
  runs). Every interpolated value in `complaint-acknowledgement.
  template.ts`'s `renderSection()` goes through a local `escapeHtml()`
  first — verified via a dedicated unit test injecting a literal
  `<script>` string and asserting it comes out escaped, not executable.
- **Web**: the `/complaints` list page (no separate detail page existed
  or was added) gained one "Download acknowledgement (PDF)" button per
  row, visible to anyone holding `complaint.log` regardless of the
  complaint's status. This is the FIRST binary (non-JSON) download
  anywhere in `apps/web` — a new `apiFetchBlob()` primitive
  (`lib/auth/api-client.ts`, mirrors `apiFetch()`'s own 401-retry-once
  shape but resolves a `Blob`) triggers a browser download via an
  object-URL + synthetic `<a download>` click, since a plain `<a href>`
  cannot carry the `Authorization` bearer header this app's auth strategy
  needs.

## What item #7 does NOT cover (read before assuming otherwise — explicitly deferred future work)

- **The other 4 document types** — recommendation report, policy
  schedule summary, invoice, certificate. Each has real underlying data
  to build from (`Recommendation`; `Policy`+`PolicySchedule`; `Invoice`;
  `Policy`+`PolicySchedule` again for certificate, no dedicated
  certificate data model exists) — the SHARED infrastructure this item
  built (`PdfRendererService`, `DocumentTemplateRepository`,
  `DocumentGenerationModule`, and now `document-html.util.ts`'s
  `escapeHtml`/`formatDocumentDate`/`formatDocumentMoney`/
  `DOCUMENT_BASE_CSS`/`DocumentLanguage` — promoted to shared the moment
  the SECOND document type needed them, per a `@code-reviewer` MINOR
  finding on the first) is reusable for all 4, but none has its own HTML
  template, `DocumentTemplate` seed row, endpoint, or web entry point
  yet.
- **Persistence / a `Document` audit trail for a generated file** — out
  of scope by user decision. This app has no real object storage
  anywhere; building one was judged a separate, larger gap than this
  item's own ask. A generated document is NOT retrievable later except
  by generating it again.
- **`Insurer` documents / any document type for an entity with no browse
  screen** — not applicable to either document type built so far
  (Complaints and RFQs both have real list/detail pages), but will recur
  for any future document type tied to an entity in the same gap class
  item #4/#6 already hit.
- **A picker in the web UI for language/dual mode** — both download
  buttons always request the customer's own default language; `DUAL` is
  only reachable by calling the api directly (e.g. `?language=DUAL`) for
  now, not from a UI control.
- **Hijri dates, multi-currency** — unrelated, still item #5's own
  deferred scope; every document's dates are Gregorian and every amount
  stays in its own record's actual currency, matching every other date/
  amount in this app today.
- **A dedicated Process 14 e2e file auditing the pre-existing `POST
  /comparison-matrices` build endpoint or `GET` read endpoints** —
  `comparison.e2e-spec.ts` (new, this entry) is scoped to what THIS
  item's own `GET :id/document` endpoint needs exercised (including
  comparison's pre-existing visibility rule, which the document endpoint
  had to inherit correctly); it is not a retroactive audit of Process 14
  itself, which had zero e2e coverage of its own before this item and
  still has none beyond what this item incidentally exercises as setup.

## What item #7's quotation-comparison slice covers

The second document type, chosen next by the user. Reuses ALL of the
first document type's shared infrastructure unchanged
(`PdfRendererService`, `DocumentTemplateRepository`,
`DocumentGenerationModule`) — no new rendering mechanism, no new
production dependency. Two things this slice added that the first one
didn't need:

- **Shared HTML-template utilities promoted out of `complaint-
  acknowledgement.template.ts`** into a new `apps/api/src/modules/
  document-generation/document-html.util.ts` — `escapeHtml`,
  `formatDocumentDate`, a NEW `formatDocumentMoney` (mirrors `apps/web/
  lib/i18n/format.ts#formatMoney()`'s exact null/non-finite contract and
  `'ar'`/`'en-GB'` locale tags, the api-side equivalent since
  `apps/api` cannot import `apps/web`'s own utility), `DOCUMENT_BASE_CSS`,
  and the `DocumentLanguage` type — plus a shared `DocumentLanguageQueryDto`
  (`document-generation/dto/`) replacing the complaint-specific one. This
  is the exact moment a `@code-reviewer` MINOR finding on the FIRST
  document type anticipated ("promote shared pieces before a second
  template forks its own copy") — done proactively here, not after a
  divergence was found. `complaint-acknowledgement.template.ts` was
  refactored to import from the shared file; its own 8 unit tests were
  re-run afterward and still pass byte-for-byte, confirming the
  extraction changed nothing observable.
- **`ComparisonService.getByIdWithCustomer()` — a NEW, security-relevant
  method, not a shortcut around the existing service.** Unlike
  `Complaint` (whose `complaint.log` permission is genuinely flat/
  unscoped — confirmed by re-reading `ComplaintService.get()` before
  copying its shortcut pattern), `ComparisonMatrix` access already
  enforces real per-customer visibility (`assertCustomerVisible` — the
  matrix inherits its RFQ's Opportunity's Customer's ownership rule; a
  Sales Officer can only reach a comparison for a customer they own,
  unless they hold a cross-owner role). Generating a document from the
  bare `ComparisonRepository` (the complaint precedent's own shortcut)
  would have SKIPPED this check entirely — a real access-control
  regression, not a hypothetical one. `getByIdWithCustomer()` goes
  through the SAME private `loadVisibleRfq()` helper `getById()` already
  used (extended to also return `customerId`, an addition with zero
  behavior change for existing callers) — the document endpoint has
  IDENTICAL visibility to the existing read endpoint, verified directly:
  a Sales Officer who does not own the customer gets 404 from the new
  `GET :id/document` endpoint despite holding `comparison.read`, while a
  Branch/Department Manager (a cross-owner role) reaches it regardless of
  ownership.
- **Table columns mirror `apps/web/components/comparison/
  ComparisonSection.tsx`'s own existing columns exactly** (Insurer /
  Premium / Deductible / Liability limit / BI period / Commission % /
  Quality / Service / Exclusions & conditions) — that screen already
  established which dimensions matter for this app's "never price alone"
  rule (`ibms-brain/meta/context/policy-lifecycle.md`); the PDF is a
  printable rendering of the SAME data, not a second, independently
  chosen column set. `Quotation.limits` (a free-form JSON field) is
  deliberately NOT rendered, for the same reason the web screen already
  omits it — no established convention anywhere in this app for
  displaying arbitrary JSON.
- **Missing/declined insurer callouts** — the same two buckets
  `ComparisonSection.tsx` already surfaces (shortlisted insurers with no
  current quote, and insurers that declined) appear in the document too,
  bilingual, below the comparison table.
- **Web**: the RFQ detail page's existing "Comparison" section
  (`apps/web/components/comparison/ComparisonSection.tsx`) gained a
  "Download comparison (PDF)" button, visible once a matrix has been
  built, reusing `apiFetchBlob()` from item #7's first slice.

## Where the code lives

- `packages/db/prisma/schema.prisma` — `User.languagePreference` (line ~149) and the
  `LanguagePreference` enum (line ~65) both pre-existed; no migration needed for item #1.
- `apps/api/src/modules/auth/dto/update-language-preference.dto.ts` — `@IsEnum(['AR','EN'])`.
- `apps/api/src/modules/auth/auth.controller.ts` — `PATCH auth/me/language`
  (`@SkipMfaRequired()`, `@CurrentUser()`, no separate permission).
- `apps/api/src/modules/auth/services/auth.service.ts` — `updateLanguagePreference()`,
  right after `me()`.
- `apps/api/src/repositories/user.repository.ts` — `updateLanguagePreference()`.
- `apps/api/test/auth.e2e-spec.ts` — the new test walks default-AR → PATCH to EN →
  persisted (re-`GET /auth/me` confirms) → 400 on an invalid value → 401 unauthenticated.
  No dedicated `AuthService` unit spec exists (none did before this item either — its
  login/MFA/session orchestration is verified via e2e, the established pattern for this
  class).
- `apps/web/lib/i18n/language-context.tsx` — `LanguageProvider`/`useLanguage()`.
- `apps/web/lib/i18n/translations.ts` — the dictionary + `translate()`, unit-tested in
  `translations.test.ts` (the `privacy-by-default.test.ts` precedent — pure logic gets a
  vitest unit test; React component/context behavior is verified via Playwright instead,
  since this web app has no React-Testing-Library-style component test precedent at all).
- `apps/web/lib/auth/auth-api.ts` — `updateLanguagePreference()` client function.
- `apps/web/app/layout.tsx` — `LanguageProvider` wraps `AuthProvider`'s children (must be
  a DESCENDANT of `AuthProvider`, since it reads `useAuth()` internally to sync from the
  account).
- `apps/web/components/app/AppNav.tsx` — the switcher UI + `t()` applied to the footer.
- `apps/web/e2e/language-switcher.spec.ts` — instant-switch-no-reload, persistence
  round-trip, default-from-account, a11y.

**Item #2** — no backend files, no migration, no new permission:

- `apps/web/components/app/app.styles.ts` — `sidebarStyle`'s `borderInlineEnd`
  (was `borderRight`); the app-shell choke point for the nav mirroring proof.
- 59 other page/component files across every feature folder — the mechanical
  logical-property sweep (see "What item #2 covers" above); no single file
  worth naming individually beyond the shell.
- `apps/web/e2e/rtl-layout.spec.ts` — new. Two tests asserting REAL bounding-box
  mirroring (not computed-style keywords, which read back unchanged in both
  directions for a logical value): the sidebar nav hugs the opposite screen
  edge in AR vs. EN, and a table's column order visually reverses (native
  browser behavior) while DOM order stays identical.

**Item #3** — no backend files, no migration, no new permission:

- `apps/web/components/customer/CustomerOnboardingWizard.tsx` — the shared
  Customer/UBO onboarding form; `dir="auto"` on legal name, registration
  number, address, nature of business, tax registration number, UBO full
  name; `<bdi>` around every legal-name mention in the review/confirmation
  prose.
- `apps/web/app/(app)/customers/[id]/page.tsx` — the shared `ProfileField`
  primitive gained `<bdi>` around its rendered value (covers registered
  address/registration number/tax registration number/national ID/contact
  fields for free); the `legalName` `<h1>` wrapped directly.
  `apps/web/app/(app)/prospects/[id]/page.tsx`'s own local `ProfileField`
  got the identical fix.
- `apps/web/components/policy/PolicySection.tsx` /
  `apps/web/components/policy/ClaimSection.tsx` — the two confirmed
  concatenation risk sites (`insuranceLine · policyNumber`, claim number,
  `causeOfLoss — lossLocation`, third-party/adjuster name) — each value
  wrapped in its OWN `<bdi>`, not one wrapper around the joined string;
  `dir="auto"` added to the adjuster name/firm and cause-of-loss/location/
  third-party-name inputs.
- ~25 other page/component files across customers, prospects, vendors,
  insurers (accounting/commission/financial-report/RFQ/operational-PI-risk
  pages), complaints, and the management-reporting dashboards/analytics
  breakdown tables — the mechanical `<bdi>`/`dir="auto"` sweep (see "What
  item #3 covers" above); no single file worth naming individually beyond
  the primitives above.
- `apps/web/e2e/bidi-text.spec.ts` — new. Three tests: a customer legal name
  (and, via the shared `ProfileField`, its registered address) each render
  inside a genuine `<bdi>` element; a policy number sitting next to an
  Arabic insurance-line label are each their OWN isolate (an exact-text
  match against either value alone would fail if a single shared wrapper
  held both); a mixed-content capture input (`vendors` create form) carries
  `dir="auto"`.

**Item #4 — Arabic sorting** (built earlier this session) — api-only, no web
files, no migration, no new permission:

- `apps/api/src/modules/finance/finance.config.ts` — 4 `localeCompare`
  tie-breakers (customer legal name, insurer name ×2, insurance-line/segment
  key) switched `'en'` → `'ar'`; the `buildReceivablesAgeing` docstring
  updated to match.
- `apps/api/src/modules/loss-ratio/loss-ratio.config.ts` — the
  customer/insurer/insurance-line label tie-breaker switched to `'ar'`.
- `apps/api/src/modules/management-reporting/profitability-analysis.config.ts`
  — the insurance-line/segment key tie-breaker switched to `'ar'`.
- `apps/api/src/repositories/commission.repository.ts` /
  `apps/api/src/repositories/rfq.repository.ts` — `listInsurers()`/
  `findSelectableInsurers()` converted from a Prisma `orderBy` (plain
  Postgres collation) to a fetch-then-JS-sort with the same `'ar'`
  comparator.
- Deliberately UNCHANGED: `apps/api/src/modules/sla-dashboard/
  sla-dashboard.config.ts` (a fixed, always-English workflow-name label) and
  `apps/api/src/repositories/role.repository.ts` (`Role.name`, a fixed
  enum) — both confirmed by reading the actual field source, not assumed.
- `apps/api/src/modules/finance/finance.config.spec.ts` — new test proving
  the mechanism empirically: `"إبراهيم للتأمين"` sorts before `"أحمد
  للتجارة"` under `'ar'` but after it under `'en'` (verified directly
  against Node's ICU before writing the assertion, not assumed).

**Item #4 remainder — Arabic keyboards (verified clear) + national-ID-convention
name-splitting** (this entry) — schema migration + api + web, no new permission:

- `packages/db/prisma/schema.prisma` — 4 new nullable `String?` columns
  (`givenName`, `fatherName`, `grandfatherName`, `familyName`) on
  `Customer`, `Employee`, `UltimateBeneficialOwner`.
  `packages/db/prisma/migrations/20260917120000_add_national_id_name_parts/
  migration.sql` — new, hand-authored (see the note below on why).
- `apps/api/src/common/person-name.util.ts` — new. `composeFullName()`,
  the one shared join used identically by all 3 services.
  `person-name.util.spec.ts` — 5 new unit tests.
- `apps/api/src/modules/customer/dto/create-customer.dto.ts` — `legalName`
  now `@ValidateIf(CORPORATE)` (was unconditionally required); new
  `givenName`/`familyName` (required-if-`INDIVIDUAL`) and `fatherName`/
  `grandfatherName` (optional); `CustomerTypeFieldCoherence` extended to
  reject the 4 new fields on a CORPORATE submission and `legalName` on an
  INDIVIDUAL one, the same mutual-exclusion rigor it already enforced for
  `nationalId`/`registrationNumber`.
  `apps/api/src/modules/customer/dto/create-ubo.dto.ts` — `fullName`
  replaced with the 4 parts (UBO is always an individual, no branching
  needed).
  `apps/api/src/modules/supporting-operations/dto/create-employee.dto.ts` —
  same replacement as UBO.
- `apps/api/src/modules/customer/customer.service.ts` — `create()`/
  `addUbo()` compute `legalName`/`fullName` via `composeFullName()`;
  `MaskedCustomer`'s explicit field list (built via `Omit<Customer,...>`,
  so the 4 new fields flow through automatically) and its 2 hand-built
  call sites (`toMasked()`, `list()`'s per-row map) updated;
  `toMaskedUbo()` needed NO change — it spreads `{...rest}` from the raw
  UBO row, so the new fields already flowed through.
  `apps/api/src/modules/supporting-operations/employee.service.ts` —
  `create()` computes `fullName`.
  `apps/api/src/modules/supporting-operations/employee.config.ts` — the 4
  fields added to `MaskedEmployee`/`EmployeeListRow` and their 2 builder
  functions (this module, unlike Customer's, hand-builds every response
  shape explicitly).
- `apps/api/src/repositories/customer.repository.ts` /
  `apps/api/src/repositories/employee.repository.ts` — the 4 new optional
  fields added to `CreateCustomerInput`/`CreateUboInput`/
  `CreateEmployeeInput`; no other repository logic changed, since all 3
  `create()` methods already pass their input straight into `prisma.
  client.<model>.create({ data: input })`.
- `apps/web/lib/customer/customer-api.ts` / `apps/web/lib/supporting-
  operations/employee-api.ts` — the 4 fields added to every response/input
  type; `legalName`/`fullName` became optional on the create-input types
  (required only for CORPORATE/never-accepted-directly, respectively).
- `apps/web/components/customer/CustomerOnboardingWizard.tsx` — the
  profile step's INDIVIDUAL branch and the UBO mini-form each replaced
  their single name input with 4 (`dir="auto"` on each, matching every
  other mixed-script input in this file); the review step switched from a
  local `legalName` state (which no longer represents an individual's name
  after the split) to `customer.legalName` (the server-computed value,
  already available and never masked either way).
- `apps/web/app/(app)/employees/page.tsx` / `employees/[id]/page.tsx` /
  `apps/web/app/(app)/customers/[id]/page.tsx` — the same 4-input
  create-form treatment; 4 new read-only display rows for the split parts
  (a KYC reviewer needs to see them separately to verify against a
  physical/scanned national ID, not just have them stored); 3 genuine
  pre-existing item #3 (`<bdi>`) gaps found and fixed while reading these
  exact files — `employees/page.tsx`'s list-table name cell,
  `employees/[id]/page.tsx`'s detail heading, and `customers/[id]/page.tsx`'s
  UBO list row, none of which had been wrapped in `<bdi>` despite being
  genuinely bilingual name fields.
- **A hand-authored migration, not `prisma migrate dev`-generated**: this
  repo's dev/test Postgres containers have a known, pre-existing checksum
  drift on 3 unrelated already-applied migrations (documented in this
  session's own memory as a recurring gotcha) that makes `migrate dev`
  refuse to run without a full `migrate reset` (which would drop all local
  data) — worked around the same non-destructive way as before: hand-write
  the migration SQL, apply it directly via `docker exec ... psql -f
  /dev/stdin`, then `prisma migrate resolve --applied` to register it
  without a shadow-database diff. Confirmed via `prisma migrate status`
  ("Database schema is up to date!") on both `db` and `db-test` afterward.
- **Every existing e2e fixture that POSTs to `/customers`, `/customers/:id/
  ubos`, or `/employees` with a `legalName`/`fullName` literal updated for
  the new contract** — `customer.e2e-spec.ts`'s own `createIndividualCustomer()`
  helper (and `employee.e2e-spec.ts`'s new local `splitName()`) split a
  single display-name string on its first space into givenName/familyName,
  so `composeFullName()` rejoins it back to the BYTE-IDENTICAL original
  string — every existing assertion (including the EDD watchlist-match
  test's exact-string match against a sample sanctioned name) keeps passing
  unchanged. 6 other e2e files that create a Customer purely as setup data
  for an unrelated feature (`crm`, `cross-sell`, `insurance-program`,
  `needs-assessment`, `risk-profile`, `up-sell`) needed the same fix — none
  of them assert on the resulting `legalName`, confirmed by grep before
  changing them.

**Item #5 (partial)** — web-only, no backend files, no migration, no new
permission:

- `apps/web/lib/i18n/format.ts` — new. `formatMoney(value, language,
  currency = 'JOD')`, `formatDate(value, language)`,
  `formatDateTime(value, language)` — the shared utility, `'ar'`/`'en-GB'`
  locale tags baked in as an internal `LOCALE_BY_LANGUAGE` map.
- `apps/web/lib/i18n/format.test.ts` — new. 7 vitest tests, including an
  empirically-verified Arabic-vs-English date-format divergence assertion
  (stripping the invisible LRM/RLM direction-control codepoints ICU inserts
  before comparing visible digits, rather than asserting the exact byte
  sequence).
- 9 `components/**` files (`ClaimSection`, `PolicySection`,
  `CommissionSection`, `FinanceSection`, `EndorsementSection`,
  `ComparisonSection`, `QuotationsSection`, `RecommendationSection`,
  `ClientDecisionSection`) — each had its own local `money()`/`fmtMoney()`/
  `fmtDateTime()` removed and replaced with the shared import; a plain
  helper function that cannot call `useLanguage()` itself (e.g.
  `coverageLabel()`) gained an explicit `language: Language` parameter
  instead.
- 16 `app/(app)/**/page.tsx` files (`claims-analytics`, `client-accounting`,
  `crm`, `cross-sell` + `cross-sell/[id]`, `financial-report`,
  `insurance-programs`, `insurer-accounting`, `needs-assessments`,
  `opportunities` + `opportunities/[id]`, `rfqs` + `rfqs/[id]`,
  `settings/security`, `up-sell` + `up-sell/[id]`) — the same sweep applied
  to page-level components and their local sub-components.
  `client-accounting`'s and `insurer-accounting`'s own local `oldest()`
  helpers (displaying a raw `dueDate.slice(0, 10)`/`collectedAt.slice(0,
  10)` ISO fragment — not originally a `toLocaleString`/`toLocaleDateString`
  call, but still a raw, non-locale-aware date display) were judged in
  scope and converted to call `formatDate()` too.
- `apps/web/e2e/locale-formatting.spec.ts` — new. Drives the real, live
  `useLanguage()` switcher (the same mechanism `language-switcher.spec.ts`
  exercises) against a real page (`client-accounting`): asserts a rendered
  date genuinely changes from `en-GB` to `ar` formatting on switch, while
  the SAME money cell's rendered digits stay byte-identical across the
  switch — the specific end-to-end proof that the `'ar'`-not-`'ar-JO'`
  locale-tag choice holds in a real rendered page, not just in the unit
  test's isolated function calls.

**Item #6 (partial)** — schema migration + api + web, no new permission:

- `packages/db/prisma/schema.prisma` — one new
  `searchVector Unsupported("tsvector")?` field on `Customer`, `Prospect`,
  `Vendor` (Prisma's documented mechanism for a DB column type it can't
  model in its own query API — the column exists and is queryable via
  `$queryRaw`, excluded from the generated Client's normal type-safe
  methods, which is correct since nothing should ever WRITE to it —
  Postgres computes it).
  `packages/db/prisma/migrations/20260918120000_add_search_vectors/
  migration.sql` — new, hand-authored (same pre-existing, unrelated
  checksum-drift workaround as item #4's own migration).
- `apps/api/src/repositories/customer.repository.ts` /
  `prospect.repository.ts` / `vendor.repository.ts` — each gained a
  `searchIds(term): Promise<string[]>` method (the first real use of
  `$queryRaw` with user input anywhere in this codebase) and an optional
  `id?: string[]` field on its own `Filter` interface, applied as
  `id: filter.id ? { in: filter.id } : undefined` in `findMany()` — the
  same `undefined`-means-"don't filter" pattern every other field in
  these interfaces already uses.
- `apps/api/src/modules/customer/dto/list-customers-query.dto.ts` /
  `apps/api/src/modules/prospect/dto/list-prospects-query.dto.ts` /
  `apps/api/src/modules/supporting-operations/dto/list-vendors-query.dto.ts`
  — each gained an optional `search` field
  (`@Transform(emptyStringToUndefined)`, the load-bearing behavior
  documented above).
- `apps/api/src/modules/customer/customer.service.ts` /
  `apps/api/src/modules/prospect/prospect.service.ts` /
  `apps/api/src/modules/supporting-operations/vendor.service.ts` — each
  `list()` calls `searchIds()` when `query.search` is present, then passes
  the resulting ids into the existing `findMany()` filter object
  unchanged otherwise (`ProspectService.list()`/`VendorService.list()`
  became `async`; `CustomerService.list()` already was).
- `apps/web/lib/customer/customer-api.ts` / `prospect-api.ts` /
  `supporting-operations/vendor-api.ts` — each gained a `search` field/
  parameter and querystring wiring (`listVendors()` gained a second
  positional `search?: string` parameter rather than an options object,
  matching its own existing single-positional-parameter shape).
- `apps/web/app/(app)/customers/page.tsx` / `prospects/page.tsx` /
  `vendors/page.tsx` — none of these 3 pages had ANY existing filter UI
  before this item (confirmed by reading each — every one called its
  `list*()` function with no arguments on mount). Each gained one
  `<input dir="auto">` + `<form onSubmit>` (submit-triggered, not
  search-as-you-type — see "What item #6 does NOT cover" above) and an
  empty-state message that distinguishes "no results for your search"
  from "none exist yet."
- `apps/api/test/customer.e2e-spec.ts` / `prospect.e2e-spec.ts` /
  `vendor.e2e-spec.ts` — 4 new tests each (English stemming proof, Arabic
  stemming proof, empty-search-shows-everything proof, nonsense-term-
  matches-nothing proof) — 12 new tests total, all against the real
  `db-test` Postgres (no repository in this codebase has a unit-test
  precedent that mocks Prisma raw SQL, and faking tsvector behavior would
  prove nothing).
- `apps/web/e2e/customers.spec.ts` / `prospects.spec.ts` / `vendors.spec.ts`
  — one new Playwright test each, proving the WIRING (search input →
  correct querystring → re-rendered filtered list) against a mocked api,
  not re-testing real Postgres FTS itself (that is the api e2e tests' own
  job) — the same web-proves-wiring/api-proves-behavior split this
  session has used throughout Part F.

**Item #6 remainder (curated synonym table)** — api-only, no migration, no
new permission, no web files touched (confirmed via `git diff --stat`):

- `apps/api/src/common/name-transliteration.config.ts` — new.
  `NAME_TRANSLITERATION_GROUPS` (~50 groups) + `expandSearchTerms(term)`.
  `name-transliteration.config.spec.ts` — 9 new unit tests (case
  insensitivity, hamza-dropped Arabic spelling, diacritic-stripping,
  multi-word terms expanding only the matching word, no variant for an
  unknown name, no duplicate variants).
- `apps/api/src/repositories/customer.repository.ts` /
  `prospect.repository.ts` / `vendor.repository.ts` — each `searchIds()`
  now builds `[term, ...expandSearchTerms(term)]` and ORs a
  `websearch_to_tsquery(...)` check per term via `Prisma.sql`/
  `Prisma.join` (previously a single fixed query per call). `Prisma` was
  already imported as a TYPE in 2 of the 3 files (for `Prisma.Decimal`) —
  switched to a value import (`import { Prisma } from '@ibms/db'`) since
  `Prisma.sql`/`Prisma.join` are runtime functions, not types.
- `apps/api/test/customer.e2e-spec.ts` / `prospect.e2e-spec.ts` /
  `vendor.e2e-spec.ts` — 2 new tests each (6 total): a Latin search term
  finding a record whose name field contains ONLY the Arabic spelling
  (never the Latin form anywhere in the document), and the reverse — both
  prove the base bilingual tsvector query alone could NOT have found the
  match (the two scripts share no tokens), so only the variant expansion
  explains the result.

**Item #7 (partial — complaint acknowledgement only)** — no schema
migration (the `DocumentTemplate` model already existed), no new
permission, first `apps/api` production dependency added this whole Part
F effort:

- `apps/api/package.json` — new `playwright-core` dependency, pinned to
  the exact version already resolved/cached locally via `apps/web`'s
  `@playwright/test` install.
- `apps/api/src/repositories/document-template.repository.ts` — new.
  `findByType()`, the first-ever runtime access to `DocumentTemplate`.
- `apps/api/src/modules/document-generation/pdf-renderer.service.ts` —
  new. `PdfRendererService`, the shared Chromium wrapper (one browser for
  the process lifetime, `OnModuleDestroy` closes it).
  `document-generation.module.ts` — new. Exports `PdfRendererService` +
  `DocumentTemplateRepository`; no controller, no document-type-specific
  logic — every future document type imports this module the same way
  `CustomerServiceModule` does.
- `apps/api/src/modules/customer-service/complaint-acknowledgement.
  template.ts` — new (later refactored, see the quotation-comparison
  listing below, to import `escapeHtml`/`formatDocumentDate`/
  `DOCUMENT_BASE_CSS` from the shared `document-html.util.ts` instead of
  its own private copies). Pure function,
  `buildComplaintAcknowledgementHtml()`.
  `complaint-acknowledgement.template.spec.ts` — 7 new unit tests
  (AR-only, EN-only, DUAL-both-Arabic-first, category translation +
  unknown-category fallback, SLA-due-date omission when no timer exists,
  HTML-injection escaping); re-run unchanged (still 7/7) after the later
  refactor.
- `apps/api/src/modules/customer-service/complaint-acknowledgement.
  service.ts` — new. `ComplaintAcknowledgementService.generate()` —
  loads the `Complaint` (existing `ComplaintRepository`), its `Customer`
  (existing `CustomerRepository`, imported via `CustomerModule`), the
  `DocumentTemplate` row (or the built-in fallback), builds the HTML,
  renders it via `PdfRendererService`.
- `apps/api/src/modules/customer-service/dto/
  generate-complaint-acknowledgement-query.dto.ts` — new, then DELETED
  once the quotation-comparison slice promoted an identical shared
  `DocumentLanguageQueryDto` (see below) — `complaint.controller.ts`
  imports the shared one now.
- `apps/api/src/modules/customer-service/complaint.controller.ts` — new
  `GET :id/acknowledgement` route, `complaint.log` permission, returns a
  `StreamableFile`. `customer-service.module.ts` — imports `CustomerModule`
  + `DocumentGenerationModule`, registers `ComplaintAcknowledgementService`.
- `packages/db/prisma/seed-data/document-templates.ts` — new
  `complaint_acknowledgement` row (5th template overall, first of the 6
  real item #7 types) — seeded to both `db` and `db-test`.
- `apps/api/test/complaint.e2e-spec.ts` — 1 new test (multiple
  assertions): permission-gated (403), 404 on an unknown complaint,
  AR-customer default, EN-customer default, an explicit `?language=AR`
  override on an EN customer, DUAL producing a genuinely LARGER PDF than
  either single-language document (a real byte-size proof), and 400 on an
  invalid `language` value — every PDF check verifies the real `%PDF-`
  magic bytes, not just a 200 status.
- `apps/web/lib/auth/api-client.ts` — new `apiFetchBlob()`, the first
  binary-response primitive in this app.
  `apps/web/lib/customer-service/complaint-api.ts` — new
  `downloadComplaintAcknowledgement()`.
  `apps/web/app/(app)/complaints/page.tsx` — new "Download acknowledgement
  (PDF)" button per row, triggers a real browser download via an
  object-URL + synthetic `<a download>` click.
- `apps/web/e2e/complaints.spec.ts` — 1 new Playwright test, proving the
  WIRING (button click -> real api call -> a real browser `download`
  event with the expected filename) against a mocked api response — this
  item's own "web proves wiring, api proves behavior" split, the same one
  item #6 used.

**Item #7's quotation-comparison slice** — no schema migration, no new
permission, no new production dependency (reuses `playwright-core` from
the first slice):

- `apps/api/src/modules/document-generation/document-html.util.ts` — new.
  `escapeHtml`, `formatDocumentDate`, `formatDocumentMoney`,
  `DOCUMENT_BASE_CSS`, `DocumentLanguage` — promoted out of
  `complaint-acknowledgement.template.ts` (see above). `document-html.
  util.spec.ts` — 7 new unit tests.
  `apps/api/src/modules/document-generation/dto/
  document-language-query.dto.ts` — new, shared `language?: 'AR'|'EN'|
  'DUAL'`, superseding the complaint-specific DTO.
- `apps/api/src/modules/comparison/comparison.service.ts` — `loadVisibleRfq()`
  (private) extended to also return `customerId` (zero behavior change
  for `build()`/`get()`/`getById()`, its existing callers); new
  `getByIdWithCustomer()` — the SAME visibility rule as `getById()` plus
  the resolved `Customer` row, the one and only authorization gate for
  the new document endpoint.
- `apps/api/src/modules/comparison/quotation-comparison.template.ts` —
  new. Pure function, `buildQuotationComparisonHtml()`.
  `quotation-comparison.template.spec.ts` — 10 new unit tests (AR-only,
  EN-only, DUAL-both-Arabic-first, JOD money formatting, superseded-quote
  tagging, null-field em-dashes, missing/declined insurer lists +
  their omission when empty, HTML-injection escaping on both exclusions/
  conditions AND an insurer name).
- `apps/api/src/modules/comparison/quotation-comparison-document.
  service.ts` — new. `QuotationComparisonDocumentService.generate()` —
  calls `ComparisonService.getByIdWithCustomer()` (never
  `ComparisonRepository` directly), the `DocumentTemplate` row (or the
  built-in fallback), builds the HTML, renders it via
  `PdfRendererService`.
- `apps/api/src/modules/comparison/comparison.controller.ts` — new
  `GET :id/document` route, `comparison.read` permission, returns a
  `StreamableFile`. `comparison.module.ts` — imports
  `DocumentGenerationModule`, registers
  `QuotationComparisonDocumentService`.
- `packages/db/prisma/seed-data/document-templates.ts` — new
  `quotation_comparison` row (6th template overall, second of the 6 real
  item #7 types) — seeded to both `db` and `db-test`.
- `apps/api/test/comparison.e2e-spec.ts` — new file (Process 14 had none
  before this item). 1 test (multiple assertions): permission-gated
  (403), 404 on an unknown comparison, 404 for a Sales Officer who does
  NOT own the customer despite holding `comparison.read` (the visibility
  proof), 200 for a cross-owner Manager regardless of ownership,
  AR/EN-customer defaults, an explicit override, DUAL producing a
  genuinely LARGER PDF, and 400 on an invalid `language` value — every
  PDF check verifies the real `%PDF-` magic bytes.
- `apps/web/lib/comparison/comparison-api.ts` — new
  `downloadComparisonDocument()`.
  `apps/web/components/comparison/ComparisonSection.tsx` — new "Download
  comparison (PDF)" button, same object-URL + synthetic `<a download>`
  pattern `complaints/page.tsx` already established.
- `apps/web/e2e/rfq.spec.ts` — 1 new Playwright test, proving the WIRING
  against a mocked api — registers a MORE SPECIFIC route
  (`comparison-matrices/*/document**`) after the file's existing shared
  `mockRfqApi()` helper's own broader route, relying on Playwright's
  last-registered-wins route precedence rather than modifying that large
  shared helper.

## A real regression caught while verifying item #1

Playwright's `page.route("**/leads**", ...)` in the new spec's first draft ALSO matched
the page's own navigation request (`page.goto("/leads")`) — a bare glob with no host
matches everything containing the substring, including the app's own HTML document
request, not just XHR/fetch calls to the api. The page rendered literal `[]` text
instead of the real shell. Fixed by scoping to the api origin explicitly
(`http://localhost:4000/leads**`), the convention every other spec in this codebase
already follows — re-confirmed by grepping for the pattern rather than assuming this
spec's own mistake was novel.

## Verification — item #1

+1 api unit is not applicable (no dedicated `AuthService` spec, per precedent above);
+1 new api e2e test in `auth.e2e-spec.ts` (12/12 total, was 11); +3 web unit tests
(`translations.test.ts`, new file); +3 new Playwright tests
(`language-switcher.spec.ts`, new file) — full suite **287/287** (was 283, split
221 non-`@a11y` + 66 `@a11y`, all green; 4 unrelated specs
(`information-assets`/`insurance-programs`) flaked once under a concurrent-process
memory-pressure episode caused by running an api unit suite alongside the Playwright
run — re-confirmed clean in isolation, not a regression). Full api unit suite
2316/2316 confirmed green. Full 62-file api e2e suite green across all 8 foreground
batches; the chronic `rbac.e2e-spec.ts` flake needed its established
`--testTimeout=180000` re-run to confirm clean (individual tests now taking 65-75s
against the very large cumulative `db-test` this project's long history has
accumulated). `npm run typecheck`/`lint`/`build` (api + web) OK.

## Verification — item #2

No backend gate applies (web-only change) — the api suite was re-run anyway as a
sanity baseline (2320/2320 unit, confirmed unrelated to this item) rather than
assumed unaffected. +1 new Playwright spec (`rtl-layout.spec.ts`, 2 tests) — full
web suite **224/224** non-`@a11y` + **66/66** `@a11y` green (one `rfq.spec.ts` test
hit a transient `write UNKNOWN` — a broken-pipe/process-contention error, not an
assertion failure — under full-suite parallel load; re-run in isolation 27/27
clean, not a regression). `npm run typecheck`/`lint`/`build`/`test` (web) OK. This
item's own diff was reviewed file-by-file in full (60 files, ~110 lines) before
being trusted — every change is the same mechanical physical-to-logical property
swap, confirmed by a whole-codebase grep showing zero remaining physical-direction
CSS properties anywhere in `apps/web` afterward.

**A genuine process note, not a code finding:** this item's actual implementation
work (the 60-file conversion + the new `rtl-layout.spec.ts`) was already sitting
uncommitted in the working tree when this session started — done in an earlier
session that never finished verifying, documenting, or committing it, despite this
very file and `CLAUDE.md` both still saying item #2 was "not started" and to "wait
for the user's explicit go-ahead." The work itself held up under a full review (no
mistakes found across all 60 files) — this entry is what closes the gap between
"code exists on disk" and "verified, documented, and committed," which is the
actual bar for "done" per `verification-contract.md`. Worth remembering: a
context file's "not started" claim is only as current as the last session that
wrote it — check the working tree itself, not just the doc, before assuming a
backlog item's real state.

## Verification — item #3

No backend gate applies (web-only change, confirmed via `git diff --stat` before
commit) — the full web suite was still run in full rather than assumed
unaffected. +1 new Playwright spec (`bidi-text.spec.ts`, 3 tests) — full web
suite **227/227** non-`@a11y` + **66/66** `@a11y` green. `npm run
typecheck`/`lint`/`build`/`test` (web) OK. Field survey (schema + render-site
grep) done before the sweep, not sampled after — ~30 files touched across every
model field identified as a genuine mixed-content risk (customer/prospect/
vendor/UBO names, addresses, registration numbers, policy numbers, insurance
lines, claim numbers/cause-of-loss/loss-location, adjuster/third-party names,
complaint issue/resolution, dashboard breakdown labels); confirmed via grep
that `WatchlistEntry`/`ScreeningResult` fields (also schema-level risks) are
never rendered on the frontend at all, so genuinely nothing to fix there.

A build-cache gotcha caught while verifying: the new spec's first run found
zero `<bdi>` elements at all, even though the source edits were correct —
Playwright's `webServer` reuses an existing `next start` process
(`reuseExistingServer: !process.env.CI`) serving the LAST `npm run build`
output, not live source; every source edit needs a fresh `npm run build`
before the next Playwright run picks it up. The exact same class of gotcha
item #2's own Claims-consent-widget fix hit once already ("a leftover
port-3000 server from before my edit") — worth checking `.next/`'s build
recency, not just the source diff, before trusting an e2e failure.

## Verification — item #4, Arabic sorting (built earlier this session)

Pure api change (no web files touched, confirmed via `git diff --stat`) — no
Playwright/a11y gate applies. +1 new unit test (`finance.config.spec.ts`,
proving `'ar'` vs `'en'` collation genuinely diverges for a real Arabic name
pair) → api unit **2321/2321** (from 2320). Targeted + adjacent e2e green:
`commission` (1/1), plus a broader sweep of every e2e file touching a
changed config module — `claim` (10/10, exercises loss-ratio recompute),
`financial-dashboard` (5/5), `sla-dashboard` (1/1, confirms the
DELIBERATELY-unchanged workflow-label sort still passes), `claims-dashboard`
(5/5), `profitability-analysis` (3/3) — 24/24 total. No existing test
asserted an exact insurer/name ordering that the locale switch could have
broken (confirmed by reading each assertion before relying on a green run,
not just trusting the exit code) — the one existing tie-break test in
`finance.config.spec.ts` uses ASCII-only fixture names, unaffected either
way. `npm run typecheck`/`lint`/`test` (api) OK.

## Verification — item #4 remainder, Arabic keyboards (verified clear) + name-splitting (this entry)

Touches `packages/db` (1 migration), `apps/api`, and `apps/web` — the first
Part F item since #1 to touch all three, confirmed via `git diff --stat`
before closing out. +5 new unit tests (`person-name.util.spec.ts`) → api
unit **2326/2326** (from 2321). Every existing unit-test fixture
constructing a raw `Customer`/`Employee`/`UltimateBeneficialOwner` Prisma
object literal needed the 4 new fields added to compile (Prisma's generated
types require a nullable column's key present as `null`, not merely
omittable) — the expected ripple this session's own `LegalHold`
precedent predicted, not a surprise. Full 62-file api e2e suite: **293/293**
(292 green + 1 transient MFA/TOTP-timing flake in `employee.e2e-spec.ts`'s
shared `makeUser()` setup helper — unrelated to this item's own logic,
re-confirmed clean in isolation, `--testTimeout=180000` per this suite's
own established chronic-flake precedent). `npm run typecheck`/`lint`/`test`
(api) OK.

Web: `npm run typecheck`/`lint`/`build`/`test` OK — web unit stays
**16/16** (no new web unit test for this item; the web-side change is
forms/display, verified via Playwright, this codebase's established split).
Fixed 2 existing Playwright specs whose accessible-name queries depended on
the now-replaced single name input (`customers.spec.ts`'s
`getByLabel("Full name")` → `getByLabel("Given name")` +
`getByLabel("Family name")`) and updated both files' fixture objects to
carry the 4 new fields. Full web suite: **228/228** non-`@a11y` (224 +
4 tests that flaked once under full-suite parallel load, all 4
re-confirmed clean in isolation — the same transient-flake class this
session has hit before, not a regression) + **66/66** `@a11y`.

**A real migration-tooling blocker, not a code problem**: Docker Desktop's
engine was unresponsive (500s from its own API) for a large stretch of this
session — root-caused by checking its own log
(`com.docker.backend.exe.log`), which showed a background software update
in progress, and confirmed via `Get-Process` that the actual backend
process had NOT restarted despite an apparent app relaunch (same PID,
3-day-old start time) until the user did a full quit from the system tray.
Once genuinely restarted, both `db` and `db-test` came up healthy and the
migration applied cleanly.

## Verification — item #5 (partial)

Web-only change (no backend files, no migration, no new permission,
confirmed via `git diff --stat`: 25 files, all under `apps/web`) — no api
gate applies, but the full web suite was still run in full rather than
assumed unaffected. +7 new web unit tests (`format.test.ts`, new file) → web
unit **16/16** (from 9). +1 new Playwright spec (`locale-formatting.spec.ts`)
— full web suite **294/294** (from 287, split 228 non-`@a11y` + 66 `@a11y`,
all green, no flakes this run). `npm run typecheck`/`lint`/`build`/`test`
(web) OK. A whole-codebase grep after the sweep confirmed zero remaining
`toLocaleString`/`toLocaleDateString` calls and zero remaining local
`money`/`fmtMoney`/`fmtDateTime` function definitions anywhere in
`apps/web` — the exhaustive-sweep bar, not a sampled subset. Locale tags
(`'ar'`/`'en-GB'`) were empirically verified against Node's own ICU via
`node -e` scripts before being chosen (see "What item #5 covers" above),
and the choice itself was confirmed with the user directly via
`AskUserQuestion` rather than assumed.

## Verification — item #6 (partial)

Touches `packages/db` (1 migration), `apps/api`, and `apps/web` — the
second Part F item since #1 to touch all three (item #4 was the first),
confirmed via `git diff --stat`. No new unit tests (this needs a real
Postgres to exercise `$queryRaw`/tsvector — no repository in this codebase
mocks Prisma raw SQL, so a unit test would prove nothing) — api unit stays
**2326/2326** (unchanged). +12 new api e2e tests (4 per entity ×
`Customer`/`Prospect`/`Vendor`: English-stemming proof, Arabic-stemming
proof, empty-search-shows-everything proof, nonsense-term-matches-nothing
proof) — targeted `customer`/`prospect`/`vendor` e2e: **43/43**. Full
62-file api e2e suite: **305/305** (from 293). Web: +3 new Playwright
tests (one per entity, proving the search-input-to-querystring wiring
against a mocked api) — full web suite **297/297** (from 294, split 231
non-`@a11y` + 66 `@a11y`, no flakes this run). `npm run
typecheck`/`lint`/`build`/`test` (api + web) OK. Migration applied to both
`db` and `db-test` via the established hand-authored-migration-plus-
`migrate resolve` workaround; smoke-tested directly against real existing
rows in `db` (`SELECT legalName, searchVector FROM "Customer"`) before
trusting the e2e suite, confirming the generated column populated
correctly on data that predates this migration, not just on new inserts.

## Verification — item #6 remainder

Pure api change — no migration, no web files touched, confirmed via `git
diff --stat`. A research spike preceded the build: `pg_trgm`/
`fuzzystrmatch` were installed on `db-test` and the `transliteration` npm
package was installed locally purely to measure the false-positive rate
documented above — both reverted (extensions dropped, npm package never
added to any `package.json`) before any code was written, so neither
appears in this item's diff. +9 new unit tests
(`name-transliteration.config.spec.ts`) → api unit **2335/2335** (from
2326). +6 new api e2e tests (2 per entity × `Customer`/`Prospect`/`Vendor`:
Latin-query-finds-Arabic-only-stored-name, and the reverse) — targeted
`customer`/`prospect`/`vendor` e2e: **49/49**. Full 62-file api e2e suite:
**311/311** (from 305) — 307 passed on the first full-suite run, the
remaining 4 (`rbac.e2e-spec.ts` ×3, `up-sell.e2e-spec.ts` ×1) hit the
30-second default test timeout under full-suite parallel load; re-run in
isolation with this suite's own established `--testTimeout=180000`
precedent, all 4 passed cleanly (`rbac.e2e-spec.ts` is *ALREADY* documented
in this codebase's own history as a chronic timeout flake under full-suite
load, unrelated to this item; `up-sell.e2e-spec.ts` timing out here is the
same transient full-suite-contention class, not a repeat offender).
`npm run typecheck`/`lint`/`test` (api) OK; no `build`/web gate applies
(pure backend change).

## Verification — item #7 (partial — complaint acknowledgement only)

Touches `apps/api`, `apps/web`, `packages/db` (seed data only, no
migration), `.github/workflows/ci.yml`, and `apps/api/Dockerfile` — the
first Part F item to touch CI/deployment config, confirmed via `git diff
--stat`. +8 new api unit tests (7 in `complaint-acknowledgement.
template.spec.ts` + 1 added during review for single-quote escaping) → api
unit **2343/2343** (from 2335). +1 new api e2e test (multiple assertions:
permission/404/400 gating, AR/EN customer defaults, an explicit override,
and DUAL producing a genuinely larger PDF, every case verified via the
real `%PDF-` magic bytes) → full 62-file api e2e suite **312/312** (from
311) — 307 passed on the first full-suite run; the other 5
(`rbac.e2e-spec.ts` ×3 — the already-chronic flake, `audit.e2e-spec.ts`
×1, `privacy-notice.e2e-spec.ts` ×1) hit timeout/MFA-timing issues under
this session's own severe memory pressure (as low as 351-694MB free RAM
on an 8GB machine, confirmed via `systeminfo`) and were re-confirmed clean
in isolation. +1 new Playwright test (`complaints.spec.ts`, proving the
download-button-to-real-browser-download wiring against a mocked api) →
full web suite **298/298** (from 297, 232 non-`@a11y` + 66 `@a11y`). `npm
run typecheck`/`lint`/`build`/`test` (api + web) OK.

**A mandatory `@code-reviewer` pass caught 2 real BLOCKERs before this was
considered done** — both fixed, not merely noted:

1. **The feature was not actually deployable as first written.**
   `playwright-core` has no browser-download step of its own (that
   belongs to the separate `playwright` package); CI's `backend` job had
   no Chromium install step at all (only the unrelated `frontend` job
   did, on a separate runner); `apps/api/Dockerfile`'s runtime stage was
   Alpine-based, and Playwright's bundled Chromium does not support musl
   libc. Fixed: `.github/workflows/ci.yml`'s `backend` job gained an
   `npx playwright-core install --with-deps chromium` step before
   Integration tests; `apps/api/Dockerfile`'s `runner` stage switched
   from Alpine to `node:20.19.0-slim` (glibc) with the same install
   command run as root before `USER nestjs`. The rendering *mechanism*
   had been verified empirically (see "What item #7 covers" above); the
   *deployment* of that mechanism had not — a real gap the review
   process, not the implementation process, caught.
2. **`PdfRendererService` had no recovery path after a browser launch
   failure or crash** — `browserPromise` cached a rejected promise or a
   disconnected `Browser` forever, wedging every future document request
   in the process behind the same stale failure. Fixed: both a failed
   `chromium.launch()` and a live browser's `'disconnected'` event now
   reset `browserPromise` to `null` (guarded by reference identity so a
   late event from an already-replaced browser can't clobber a fresh
   one), so the next call retries a genuine new launch.

4 MINOR findings also fixed: `escapeHtml()` was missing a single-quote
replacement (added, with a new regression test); `apiFetchBlob()`
duplicated `apiFetch()`'s entire retry/error-handling block instead of
sharing it (extracted into `fetchWithRetry()`); `categoryLabel()`'s
"no category" branch had a dead `lang === 'en' ? '—' : '—'` conditional
(simplified); `PdfRendererService.renderHtmlToPdf()` had no structural
defense against a FUTURE document template introducing an external
resource reference, which combined with `--no-sandbox` would be a real
SSRF path — added `page.route('**/*', ...)` aborting every non-`data:`
request, closing the class of risk before a second document type can
introduce it, not just documenting the risk. One NIT (`@Header()`
potentially leaking `Content-Type: application/pdf` onto an error
response body) was read and judged genuinely cosmetic, left as-is.

The review also POSITIVELY confirmed (not just silence): `escapeHtml()`
coverage was already complete for every customer-controlled value before
the review, verified via the dedicated injection unit test; no live SSRF
path existed in the current template (no external references anywhere in
it, checked directly); `Customer.classification` defaults to
`CONFIDENTIAL` not `HIGHLY_CONFIDENTIAL`, and `Complaint.issue` is already
shown unmasked on the existing `/complaints` list page to the same
`complaint.log`-holding roles — this PDF download exposes nothing beyond
what those roles already see on screen, so `sensitive-data-handling.md`'s
watermarking/DLP triggers (scoped to Highly Confidential fields) do not
apply; `DocumentTemplate` fallback text is byte-identical to the real
seeded row, so a missing-row environment renders identically to a seeded
one; the concurrency shape of the shared browser instance was sound
(only the no-retry-after-failure half was not).

**The Docker deployment fix IS independently verified — and verification
caught a SECOND real bug the build alone did not.** Once memory pressure
eased, `docker build -f apps/api/Dockerfile .` succeeded — but launching
Chromium inside the built container as the unprivileged `nestjs` runtime
user failed: `Executable doesn't exist at /nonexistent/.cache/
ms-playwright/...`. Root cause: Playwright resolves its browser cache
under `$HOME`, which differs between the ROOT user the Dockerfile's
`RUN npx playwright-core install` step executes as and the unprivileged
`nestjs` user `CMD` actually runs as (an `adduser --system` account has
no real home directory — `$HOME` resolves to `/nonexistent`) — so the
browser installed during the build was genuinely invisible at runtime.
Fixed: `ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright` pins the cache to a
fixed, absolute path before the install step, plus a `chown -R
nestjs:nodejs /ms-playwright` afterward so the unprivileged user (which
did not do the install) can still read/execute it. Re-verified after the
fix: rebuilt the image (a genuinely fresh Chromium download, not a stale
cached layer — the earlier broken layer was invalidated by the Dockerfile
edit) and directly launched Chromium inside the running container as
`nestjs`, rendering a real bilingual PDF (`docker run --rm <image> node
-e "..."`, verified `%PDF-` magic bytes on the output). This is exactly
why "the build succeeded" and "the feature works in production" are
different claims — a passing `docker build` proves the image compiles,
not that a headless browser can actually launch as the unprivileged user
CMD runs as.

## Verification — item #7's quotation-comparison slice

Touches `apps/api` and `apps/web` only — no migration, no CI/Dockerfile
change (reuses the first slice's `playwright-core` dependency and its CI/
Docker fixes unchanged), confirmed via `git diff --stat`. +18 new api
unit tests (8 in `document-html.util.spec.ts` — 7 plus 1 added during
review for HTML-escaping the money formatter's non-finite branch; 10 in
`quotation-comparison.template.spec.ts`) → api unit **2361/2361** (from
2343). +1 new api e2e test (`comparison.e2e-spec.ts`, the FIRST e2e
coverage Process 14 has ever had — multiple assertions: permission/404/
400 gating, a genuine visibility-scoping proof — a non-owning Sales
Officer holding `comparison.read` still gets 404, a cross-owner Manager
gets 200 regardless of ownership — AR/EN customer defaults, an explicit
override, and DUAL producing a genuinely larger PDF, every case verified
via real `%PDF-` magic bytes) → full 63-file api e2e suite **313/313**
(from 312) — 307 passed on the first full-suite run; the other 6, spread
across `rbac.e2e-spec.ts` (×3, the already-chronic flake),
`audit.e2e-spec.ts` (×1), `dsr.e2e-spec.ts` (×1, a genuine assertion
failure — 400 instead of 201 — not a bare timeout, but in a PDPL/Legal
Hold test file with zero relation to this item's own changes), and
`up-sell.e2e-spec.ts` (×1), all re-confirmed clean in isolation
(19/19, `--testTimeout=180000`) under this session's own sustained,
severe resource pressure (RBAC's own 3 tests took 135s/114s/118s in
isolation — genuinely slow, not hanging, on a machine that had already
run this same 63-file suite 6+ times in one day). +1 new Playwright test
(`rfq.spec.ts`) → full web suite **299/299** (from 298, 233 non-`@a11y` +
66 `@a11y`). `npm run typecheck`/`lint`/`build`/`test` (api + web) OK.

**A second `@code-reviewer` pass — this time on the visibility-preserving
read path specifically — found 0 BLOCKERs, 3 MINORs, all 3 fixed:**
`formatDocumentMoney()`'s non-finite branch was interpolating its `raw`/
`currency` arguments without escaping them (not currently exploitable —
every real caller's amount is `MONEY_STRING`-regex-validated before ever
becoming a `Prisma.Decimal` — but this is now shared infrastructure, so
fixed anyway, with a new regression test); a doc comment claiming "no
document type needs money formatting server-side" went stale in the SAME
commit that added `formatDocumentMoney` (removed); and
`getByIdWithCustomer()` was fetching the same `Customer` row twice (once
inside the existing `assertCustomerVisible` visibility check, once again
immediately after) — fixed by having `assertCustomerVisible`/
`loadVisibleRfq` return the already-fetched row instead of a second,
redundant query. The review's own primary focus — whether the new
`getByIdWithCustomer()` could be used to bypass `ComparisonMatrix`'s
existing per-customer visibility rule — traced every code path from the
controller down to the database read and found no bypass, corroborated
by `comparison.e2e-spec.ts`'s own real, non-owning-Sales-Officer-gets-404
proof against a live app, not just a code-reading claim.

## Next

**Item #4 is now CLOSED**, with one narrow, documented exception:
`InsuredPerson` name-splitting, deferred until that model gets real CRUD
(see "What item #4 does NOT cover" above) — this is a pre-existing gap this
item did not create and is not blocking on. **Item #6 remains PARTIALLY
built, now on BOTH sub-problems**: full-text search itself is done; fuzzy
transliteration matching now has a curated synonym table (bounded coverage,
see "What item #6 remainder does NOT cover" above) rather than nothing at
all — a distance-based fuzzy matcher was evaluated and deliberately
REJECTED, not merely deferred, so do not re-attempt one without re-reading
that finding first. Same-script typo tolerance and `Insurer` search remain
open, documented future work. Item #5 remains PARTIALLY complete —
number/date formatting only; Hijri calendar and multi-currency
(reinsurance) remain open, documented future work (see "What item #5 does
NOT cover" above). **Item #7 is now also PARTIALLY built, on 2 of 6
document types** — complaint acknowledgement, then quotation comparison,
which reused the first's shared rendering infrastructure
(`PdfRendererService`, `DocumentTemplateRepository`,
`DocumentGenerationModule`) unchanged and additionally promoted
`escapeHtml`/date+money formatting/base CSS into a genuinely shared
`document-html.util.ts` (a `@code-reviewer` MINOR finding on the first
slice, acted on proactively rather than after a third document type
forked its own copy). The other 4 (recommendation report, policy
schedule summary, invoice, certificate) remain open, documented future
work — each has real underlying data to build from (see "What item #7
does NOT cover" above), but none has its own HTML template, seed row,
endpoint, or web entry point yet. A real lesson from the comparison
slice worth re-reading before building any of the remaining 4: **check
whether the underlying entity already enforces per-customer visibility
beyond a flat permission** (`Complaint` does not; `ComparisonMatrix`
does) — the document endpoint must inherit that check via the entity's
own service, never by querying its repository directly, or a real
access-control regression follows. Persistence (a real `Document` audit
trail for a generated file) remains explicitly out of scope — this app
has no object storage anywhere, a separate, larger gap than this item's
own ask. Do not assume a future session can mark item #5, #6, or #7
fully closed without addressing its own deferred scope. Wait for the
user's explicit go-ahead before resuming any of item #5/#6/#7's
remaining scope, or starting any other Part F item — do not self-select.
Item #8 (the 4-state screenshot discipline) is a verification overlay on
whichever of #5-7 land, not a
standalone build.

Item #7's `apps/api/Dockerfile` fix (Alpine → `node:20.19.0-slim` for the
Chromium runtime stage) is now independently verified end-to-end — a real
container build PLUS a real Chromium launch as the unprivileged runtime
user, not just a successful `docker build`. That verification caught and
fixed a second real bug (`PLAYWRIGHT_BROWSERS_PATH` — see "Verification —
item #7" above) that the build alone did not surface; a future session
touching this Dockerfile again should re-verify the SAME way (build, then
actually launch Chromium inside the running container as `nestjs`), not
just confirm the build exits 0.
