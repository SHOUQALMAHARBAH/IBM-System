# Bilingual UI (Part F, backlog Part 11)

**Last verified:** 2026-09-07 (item #4 — Arabic-first input — CLOSED: Arabic
keyboards confirmed clear + Jordanian national-ID-convention name-splitting
built for Customer/Employee/UltimateBeneficialOwner; `InsuredPerson`
deliberately excluded, it has zero CRUD anywhere yet — after item #5 —
locale-aware number/date formatting (partial), item #3 — bidi text
handling, item #2 — full RTL layout, and item #1 — instant language
switch) · **Owner:** none named; cross-cutting, applies to every screen.

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
6. Full-text search across Arabic and English with fuzzy transliteration matching — not
   started.
7. System-generated bilingual documents (quotation comparison, recommendation report,
   policy schedule, invoices, certificates, complaint acknowledgements) — not started;
   no document-generation infrastructure (PDF or otherwise) exists anywhere in this app
   yet — `Document` (Process #70) is version/classification METADATA tracking, not a
   generator.
8. Four-state (loading/empty/error/populated) screenshot evidence per screen — a
   verification DISCIPLINE overlay on 1-7, not a separate build item.

Worked one item at a time, the Part D/E pacing convention — this file now covers
items #1-5 (item #4 CLOSED with one narrow, documented exception; item #5
PARTIAL, by explicit user scoping decision). Items #6-8 are unbuilt; do not
assume they are covered by any earlier item's own infrastructure without
checking each item's own "does NOT cover" section below.

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

## Next

**Item #4 is now CLOSED**, with one narrow, documented exception:
`InsuredPerson` name-splitting, deferred until that model gets real CRUD
(see "What item #4 does NOT cover" above) — this is a pre-existing gap this
item did not create and is not blocking on. Item #5 remains PARTIALLY
complete — number/date formatting only; Hijri calendar and multi-currency
(reinsurance) remain open, documented future work (see "What item #5 does
NOT cover" above). Do not assume a future session can mark item #5 fully
closed without addressing its own deferred scope. Wait for the user's
explicit go-ahead before resuming item #5's remaining scope, starting item
#6 (bilingual full-text search), or any other Part F item — do not
self-select. Items #6-7 each look like their own multi-session effort (item
#7 in particular has no document-generation infrastructure to build on at
all yet); item #8 (the 4-state screenshot discipline) is a verification
overlay on whichever of #6-7 land, not a standalone build.
