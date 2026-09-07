# Bilingual UI (Part F, backlog Part 11)

**Last verified:** 2026-09-07 (item #1 — instant language switch + persistent
per-user language preference — built and verified) · **Owner:** none named;
cross-cutting, applies to every screen.

## What this is

Part F names 8 cross-cutting tasks, each applying to every screen in the app, not a
single module:

1. Instant language switch without losing session context + a persistent per-user
   language preference — **built, this entry**.
2. Full RTL layout for Arabic and LTR for English (navigation, forms, tables, charts
   genuinely mirrored, not just mirrored text) — not started.
3. Bidirectional (bidi) text handling for mixed-content fields — not started (though
   Notices/`PrivacyNoticeDisplay`, Part D, already renders `textAr`/`textEn` side by
   side with `dir="rtl"` on the Arabic paragraph — a CONTENT-level bidi display, not
   the mixed-content-in-one-field case this bullet actually names).
4. Arabic-first input (Arabic keyboards, national-ID-convention name fields, correct
   Arabic sorting) — not started.
5. Locale-aware number/date/currency formatting (Gregorian + optional Hijri, JOD base +
   multi-currency for reinsurance) — not started.
6. Full-text search across Arabic and English with fuzzy transliteration matching — not
   started.
7. System-generated bilingual documents (quotation comparison, recommendation report,
   policy schedule, invoices, certificates, complaint acknowledgements) — not started;
   no document-generation infrastructure (PDF or otherwise) exists anywhere in this app
   yet — `Document` (Process #70) is version/classification METADATA tracking, not a
   generator.
8. Four-state (loading/empty/error/populated) screenshot evidence per screen — a
   verification DISCIPLINE overlay on 1-7, not a separate build item.

Worked one item at a time, the Part D/E pacing convention — this file covers item #1
only. Items #2-8 are unbuilt; do not assume they are covered by item #1's own
infrastructure without checking this file's own "What item #1 does NOT cover" section
below.

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
- **No RTL layout polish anywhere** (item #2) — mirrored nav/forms/tables/charts is
  entirely separate, unbuilt work; `dir="rtl"` alone does not achieve "genuinely
  mirrored, not just mirrored text" for a component that was never built RTL-aware.
- **No bidi mixed-content handling** (item #3), Arabic input/sorting (item #4), locale
  formatting (item #5), bilingual search (item #6), or document generation (item #7).

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

## A real regression caught while verifying this item

Playwright's `page.route("**/leads**", ...)` in the new spec's first draft ALSO matched
the page's own navigation request (`page.goto("/leads")`) — a bare glob with no host
matches everything containing the substring, including the app's own HTML document
request, not just XHR/fetch calls to the api. The page rendered literal `[]` text
instead of the real shell. Fixed by scoping to the api origin explicitly
(`http://localhost:4000/leads**`), the convention every other spec in this codebase
already follows — re-confirmed by grepping for the pattern rather than assuming this
spec's own mistake was novel.

## Verification

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

## Next

Wait for the user's explicit go-ahead before starting item #2 (full RTL layout) or any
other Part F item — do not self-select. Item #2 is a substantially larger undertaking
than item #1 (every existing screen's layout needs RTL-aware review, not just one new
control), and should very likely be its own multi-session effort, possibly broken down
further rather than attempted as one unit.
