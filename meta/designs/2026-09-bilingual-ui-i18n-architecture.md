# Design: Part F bilingual UI — a hand-rolled context, not a locale-routing i18n library

**Status:** accepted · **Date:** 2026-09-07 · **Author:** shouq (via Claude Code) · **Service:** apps/web

## Context

Backlog Part F (Part 11, "Bilingual UI Requirements") names 8 cross-cutting tasks
applying to every screen: instant language switch + a persistent per-user preference,
full RTL layout, bidi text handling, Arabic-first input, locale-aware formatting,
bilingual full-text search, system-generated bilingual documents, and a four-state
screenshot discipline. This is the first Part F work — no i18n infrastructure of any
kind existed before it: `apps/web` had zero i18n dependencies, `app/layout.tsx`
hardcoded `<html lang="en">` with no `dir` attribute, and the App Router has no
`[locale]`-segment routing.

The schema, however, already carried dormant infrastructure: `User.languagePreference`
and `Customer.languagePreference` (`LanguagePreference` enum: `AR`/`EN`, `@default(AR)`)
both existed since the initial migration, read at signup/creation and returned by
`GET /auth/me` — but never *updatable* after the fact, and never actually applied to
any rendering. A real, if half-wired, foundation to build item #1 on, not a blank
schema.

The literal backlog wording for item #1 — "**instant** language switch **without
losing session context**" — is itself a technical constraint, not just a nice-to-have:
it describes a client-side, no-navigation toggle, not a page reload or URL change.

## Decision

Build a hand-rolled `LanguageProvider` React context (`apps/web/lib/i18n/
language-context.tsx`) rather than adopting a locale-routing i18n framework
(`next-intl` or similar). It:

- Initializes from `localStorage` synchronously (a fast, per-device, pre-auth GUESS —
  `AR`, matching the schema default) for the least-bad first paint before the account
  loads.
- Syncs to the ACCOUNT's own `User.languagePreference` (via `useAuth()`) exactly ONCE
  per session load, then treats local state as authoritative for the rest of the
  session — a manual mid-session switch is never silently overwritten by a stale
  re-render of the same already-fetched `user` object.
- On every switch, updates React state AND `document.documentElement.lang`/`dir`
  synchronously (client-side DOM mutation, the same shape the pre-existing
  `suppressHydrationWarning` on `<html>` already anticipated for exactly this kind of
  post-hydration correction) — genuinely instant, no navigation, no URL change, no lost
  session context. Persistence to the account (`PATCH /auth/me/language`, new) fires in
  the background, best-effort — the `SlaTimerService.startTimer` "local action already
  succeeded, remote persistence failure is logged not surfaced" shape used everywhere
  else in this codebase.
- A small, real (not stubbed) translation dictionary (`translations.ts`) backs a `t()`
  hook — deliberately scoped to the switcher control itself + the nav shell's account
  footer for this item, proving the mechanism round-trips end to end. Translating the
  other ~80 screens is items #2-5's own, much larger scope (RTL layout, bidi text,
  Arabic-first input, locale formatting) — not attempted here.

Login/signup screens (outside the authenticated `AppNav` shell) are NOT wired to the
switcher in this pass — a `languagePreference` has nowhere to persist against before an
account exists, and a pre-login toggle would only affect ephemeral local state. A real,
documented gap, not silently dropped: see `meta/context/bilingual-ui.md`.

## Alternatives considered

| Option | Why it lost |
|---|---|
| `next-intl` (or similar) with `app/[locale]/` routing | The standard App Router integration path changes the URL on every switch (`/en/leads` ↔ `/ar/leads`) — directly contradicting "instant... without losing session context," which reads as a same-URL, client-only toggle. Migrating ~80 existing routes under a new dynamic segment is also a large, invasive restructure disproportionate to item #1 alone; a real routing-based library is worth revisiting once items #2-5 (full-app translation) are actually underway and the migration cost is amortized across real content, not paid up front for a bare switch. |
| A cookie + middleware-based SSR locale (correct `<html>` on first paint, no client flash) | Solves a real but secondary problem (a brief LTR-then-RTL flash on first load for an AR-preferring user) at the cost of a new `middleware.ts` and a locale cookie contract this app doesn't have yet. The client-only correction is simpler, ships today, and the flash is bounded to first load only — a documented, accepted limitation, not silently ignored. |
| Store the preference ONLY in `localStorage`, skip the `PATCH` endpoint entirely | Fails the backlog's own explicit second half — "a **persistent per-user** language preference" reads as account-level (follows the user across devices/sessions), not device-level. `User.languagePreference` already existed for exactly this; leaving it write-once-at-signup-only would waste a field the schema had already reserved for this. |
| Translate the whole nav (`AppNav`'s ~80 links) as part of item #1, since the dictionary mechanism was being built anyway | Item #1's own bullet is about the SWITCH, not the content; the other ~80 screens' worth of translation belongs to items #2-5 (RTL layout, bidi, Arabic-first input, formatting) by the backlog's own structure. Doing it now would blur the item boundary this whole project's pacing convention depends on (one checklist item verified and shipped at a time) and multiply this single item's review surface by roughly the size of the entire rest of the app. |

## Consequences

**Accepted costs:** a brief English/LTR flash on first load for an Arabic-preferring
user is possible (client-only correction, no SSR locale awareness) — acceptable for
item #1, worth fixing if/when a real cookie-based SSR locale scheme is built. Only the
language switcher control + the nav shell's account footer are actually bilingual today;
the rest of the app remains English-only text (though now RTL-container-aware at the
`<html>` level once Arabic is selected — individual screens have not been laid out for
RTL yet, which is item #2). Login/signup have no switcher at all yet.

**Revisit if:** items #2-5 begin (full-app translation, RTL layout polish, Arabic-first
input, locale formatting) — at that point, re-evaluate whether the dictionary should
grow in place or whether the accumulated translation surface finally justifies migrating
to a routing-based i18n library instead of continuing to hand-roll it. Also revisit if a
real SSR locale-cookie/middleware need emerges (e.g. a public-facing, pre-auth bilingual
page is added) — today's design deliberately defers that.
