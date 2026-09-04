# Sanctions & PEP Screening (Process 49)

**Last verified:** 2026-09-05 · **Owner:** Compliance Officer (role, not yet a named person)

## What this is

Backlog Part C #49 has one checkbox: "Screen at onboarding + on any material change + a
recurring batch against updated lists." The onboarding and material-change checks were
already built under #3-4 (`ScreeningService.run()`); this process finishes the third leg
— "against **updated** lists" — by giving the recurring batch two things it didn't have
before: real list data (two free, publicly published sanctions lists, not a fictional
fixture) and a cadence tied to how often those lists actually change, instead of an
unsourced monthly guess.

`ScreeningService` (Process 3.1/47/49, `apps/api/src/modules/customer/`) now checks
every subject name (`Customer.legalName` + every `UltimateBeneficialOwner.fullName`)
against **two** sources: `sample-watchlist.ts` (a fictional, dev/test-only fixture,
disabled in production — unchanged, see that file's own header) and the real,
locally-cached `WatchlistEntry` table this process adds — populated by
`WatchlistSyncService` (`apps/api/src/modules/compliance-risk/`) fetching OFAC SDN and
the UN Security Council Consolidated List directly. The real check runs in every
environment, including production; the fixture never does.

## The shapes

```
WatchlistSource: OFAC_SDN | UN_CONSOLIDATED

WatchlistEntry
  source: WatchlistSource
  sourceRecordId: string        # OFAC ent_num, or UN DATAID — the upsert/prune key
  fullName: string
  normalizedName: string        # normalizeWatchlistName(fullName) — see below
  listProgram: string?          # OFAC "Program", or UN "UN_LIST_TYPE (REFERENCE_NUMBER)"
  remarks: string?              # OFAC "Remarks", or UN "COMMENTS1" — classified
                                 # HIGHLY_CONFIDENTIAL by default (see BLOCKER 4 below);
                                 # can carry a real individual's DOB + alleged conduct
  classification: DataClassification  # @default(HIGHLY_CONFIDENTIAL) — a review
                                       # BLOCKER; see below
  syncRunId: string              # which WatchlistSyncRun last confirmed this row

WatchlistSyncRun
  source: WatchlistSource
  status: "running" | "succeeded" | "failed"
  recordCount: int?
  errorMessage: string?
  # a hand-authored partial UNIQUE(source) WHERE status='running' — a review BLOCKER;
  # see below
```

`ScreeningBatchScheduler` (unchanged file, `apps/api/src/modules/customer/`) now runs
every 4 hours instead of the drafted-monthly cadence #3-4 shipped with, delegating to
`ScreeningService.runRecurringBatch()` (moved out of the scheduler and into the service,
so `POST /screening/recurring-batch` can call the identical logic on demand).
`WatchlistSyncScheduler` runs every 12 hours, delegating to
`WatchlistSyncService.runSync()`.

## The rules that aren't obvious

- **Both source URLs are real and were verified reachable, live, on 2026-09-05**:
  `https://www.treasury.gov/ofac/downloads/sdn.csv` (302-redirects to
  `sanctionslistservice.ofac.treas.gov`; ~19,000 records) and
  `https://scsanctions.un.org/resources/xml/en/consolidated.xml` (~1,000 records). No
  API key, no paid provider — genuinely different from `sample-watchlist.ts`'s own
  header, which says "no real sanctions/PEP/AML data provider exists or is obtainable in
  this environment." That was true when #3-4 shipped; it no longer is, for these two
  specific free lists.
- **Matching is exact-on-a-canonical-form, not fuzzy.** `normalizeWatchlistName`
  (`watchlist-sync.config.ts`) uppercases, strips everything but letters/digits/
  whitespace, and sorts the whitespace-split tokens — applied identically at ingestion
  time (`WatchlistEntry.normalizedName`) and at match time (a customer/UBO name). This
  buys tolerance for name-order and punctuation differences (OFAC formats
  "LASTNAME, Firstname"; a customer record might store "Firstname Lastname" — both
  reduce to the same sorted token string) at effectively no engineering cost. It does
  **not** buy tolerance for spelling variants, transliteration differences, honorifics
  ("Dr.", "Sheikh"), or a missing/extra middle name — a real sanctions screening product
  uses phonetic or edit-distance algorithms this module does not implement. Documented
  as a limitation, not silently assumed to be "good enough."
- **The parsers are hand-rolled, not a new dependency** — a general quoted-CSV-field
  parser (`parseCsvLine`) for OFAC's mixed quoted/unquoted 12-column format, and a
  scoped regex block/tag extractor for the UN XML (safe specifically because every tag
  this module reads — `DATAID`, `FIRST_NAME`, `SECOND_NAME`, `THIRD_NAME`,
  `FOURTH_NAME`, `UN_LIST_TYPE`, `REFERENCE_NUMBER`, `COMMENTS1` — is a flat,
  single-occurrence leaf directly inside `<INDIVIDUAL>`/`<ENTITY>`, verified against the
  real, live document; none collide with a same-named tag nested inside a sibling
  structure like `ENTITY_ALIAS`). Both are unit-tested against real captured sample
  lines/blocks, not synthetic ones. Aliases are not matched — primary name only, the
  same scope limit `sample-watchlist.ts` already had.
- **The network boundary is two tiny injectable classes** (`OfacSdnFetcher`,
  `UnConsolidatedFetcher`, `watchlist-fetchers.ts`) so `WatchlistSyncService` never calls
  `fetch()` directly. Neither the unit suite nor the e2e suite calls the real endpoints —
  the e2e spec (`test/watchlist-sync.e2e-spec.ts`) stubs `globalThis.fetch` with fixture
  CSV/XML content and drives the real `POST /watchlist-sync/run` endpoint through the
  full Nest app, proving the whole fetch→parse→upsert→prune pipeline without depending
  on an external government server's uptime during CI. A scheduled background sync must
  never make automated tests flaky, slow, or offline-broken.
- **Upsert-then-prune, not a transaction, and chunked with bounded concurrency.**
  `WatchlistEntryRepository.upsertMany` stamps every parsed record with the current
  `WatchlistSyncRun.id`; `pruneStale` then deletes every row of that source NOT stamped
  with it — i.e. every entry the source list dropped since the last sync. Two passes,
  not one `$transaction`: this is a cache refresh from an external, non-transactional
  source, not a financial or workflow write (`race-safe-invariants.md` guards against a
  *stranded invariant*, e.g. a `Refund` created with no matching stamp — a sync that dies
  partway just leaves a mix of old and new rows, which the next sync or `POST
  /watchlist-sync/run` supersedes). Upserts run in chunks of 100 with bounded
  `Promise.all` concurrency, not a raw-SQL bulk upsert — OFAC alone is ~19,000 rows; a
  fully sequential await-per-row loop would take unnecessarily long for a background job
  nobody is waiting on, but 19,000 fully concurrent connections would be worse.
- **`WatchlistEntryRepository` is provided twice, deliberately, not exported/imported.**
  `ComplianceRiskModule` (owns the sync) and `CustomerModule` (`ScreeningService` reads
  it) each list it directly in their own `providers: []`. It is a stateless
  `PrismaService` wrapper — two independent instances still operate on the same rows —
  so this avoids a `ComplianceRiskModule` <-> `CustomerModule` dependency in either
  direction for a single narrow read.
- **`sanctions-pep.screen` gates three endpoints, not one**: `POST /watchlist-sync/run`,
  `GET /watchlist-sync/status`, and `POST /screening/recurring-batch` — the seeded
  permission's own description ("Run recurring sanctions/PEP screening batches") covers
  both halves of the mechanism (refreshing the lists, and re-checking customers against
  them), and there is only one permission provisioned for this backlog item.
- **The 12h/4h cadence is a real, sourced ratio, not an arbitrary pair.** The two source
  lists refresh roughly every 12 hours in the real world; re-screening customers twice
  within that window (every 4 hours) keeps the gap between "the list changed" and "we
  checked again" bounded to at most one sync interval plus one screening interval. Still
  **DRAFTED** in the sense that no OFAC/UN SLA document commits to exactly 12h — but it
  is an observed publication cadence, not a guess, the same status
  `kyc-aml-sla-timers.md`'s two figures have.

## `@code-reviewer` findings (resolved) — read this before touching the sync job again

The first pass shipped without any of the four things below. All four are now fixed;
this section exists because each one is a mistake an agent re-implementing "a scheduled
external sync + cache refresh" elsewhere in this codebase is likely to repeat.

- **BLOCKER 1 — no concurrency guard.** Nothing stopped a manual `POST
  /watchlist-sync/run` from firing while the 12-hourly scheduler was already mid-run for
  the same source (or two manual triggers overlapping). Two concurrent syncs of the same
  source interleave their `pruneStale` calls — one run's prune can delete rows the
  *other* run just (re-)wrote under a different `syncRunId`, silently dropping a
  currently-sanctioned entry from the cache until the next sync happens to re-add it.
  **Fixed**: a hand-authored partial `UNIQUE (source) WHERE status='running'` on
  `WatchlistSyncRun` (`race-safe-invariants.md`'s shape — Prisma cannot express the
  `WHERE` predicate in `@@unique`, so this lives only in the migration SQL, not the
  schema's `@@unique` block). `createSyncRun`'s resulting P2002 is caught in
  `WatchlistSyncService.syncSource` and mapped to a `'skipped'` outcome, not an
  unhandled rejection.
- **BLOCKER 2 — no plausibility check before pruning.** A 200 response carrying the
  wrong content (a WAF/interstitial page, a captcha, a changed redirect target) parses
  to zero or near-zero records without ever throwing an error — nothing distinguished
  that from OFAC/UN genuinely, drastically shrinking their list (which doesn't happen in
  practice), so `pruneStale` would happily wipe out the *entire* prior cache for that
  source on the strength of a bad fetch. **Fixed**: before committing anything,
  `WatchlistSyncService` compares the freshly parsed count against
  `WatchlistEntryRepository.findLastSuccessfulRun`'s `recordCount` — the new count must
  be at least `WATCHLIST_MIN_ACCEPTABLE_RATIO = 0.5` (drafted) of it, or at least
  `WATCHLIST_MIN_ABSOLUTE_RECORDS = 10` (drafted) if there's no prior successful sync at
  all. Failing the floor routes into the existing failure path (`status: 'failed'`,
  cache untouched) — no new plumbing needed.
- **BLOCKER 3 — an ASCII-only normalizer is a false-positive-wildcard generator.**
  `normalizeWatchlistName`'s original character class was `[^A-Z0-9\s]` — anything not
  ASCII letters/digits/whitespace got stripped. Applied to a name written **entirely** in
  a non-Latin script (Arabic, for this Jordan-based broker, whose
  `Customer.languagePreference` defaults to `AR`), that strips every character, leaving
  `""`. An empty `normalizedName` is not "no match" — it is a universal collision key:
  every empty-string customer/UBO name would match every empty-string watchlist entry.
  **Fixed** two ways, deliberately redundant: (1) the character class became
  Unicode-aware — `\p{L}`/`\p{N}` with the `u` regex flag — so Arabic/Cyrillic/CJK/etc.
  letters survive as real, distinguishing tokens instead of vanishing; (2) an empty
  `normalizedName` is refused outright at **three** points — ingestion
  (`WatchlistSyncService` filters such a record out before `upsertMany`, logged, not
  silently dropped), match time (`ScreeningService.findRealWatchlistHit` skips a subject
  name that normalizes to `""` before ever calling the repository, both correctness and
  a wasted-query avoidance for a Jordan-market customer base), and the repository itself
  (`WatchlistEntryRepository.findByNormalizedName` returns `null` immediately for an
  empty string — belt-and-suspenders, since it has no other caller to lean on that). The
  Unicode fix narrows but does not eliminate the empty-string risk — a name of pure
  punctuation/whitespace still normalizes to `""`, which is why all three refusals stay
  in place rather than relying on the character-class fix alone. **A related, accepted
  MINOR, not fixed**: a real UN entity is listed under the single token "ADF" — any
  customer/UBO whose legal name normalizes to exactly one short token collides on an
  exact match the same way a longer name would, with no lower-confidence tier in between
  (`ScreeningOutcome.PENDING_INVESTIGATION` exists on the model but this module does not
  use it).
- **BLOCKER 4 — `classification` was reasoned in a code comment, not cited.** The first
  pass shipped `WatchlistEntry` with no `DataClassification` field at all, on the
  reasoning (in a comment, not a citation) that OFAC/UN list content is "public
  government text, not IBMS customer data." `meta/designs/2026-08-pcms-source-of-truth.md`
  is explicit that IBMS code must never re-derive a privacy/compliance classification —
  it must defer to PCMS (`PRIV-STD-*`/`PRIV-SOP-*`) or flag the determination as open,
  never assert it inline. **Fixed**: `classification DataClassification
  @default(HIGHLY_CONFIDENTIAL)` added to the model — a conservative default pending an
  actual PCMS/`PRIV-STD-02` determination, not a claim that the determination is already
  made. `remarks` (OFAC "Remarks" / UN "COMMENTS1") is exactly why "public" was never the
  same question as "unclassified": it can carry a real, named individual's DOB and
  alleged-conduct text verbatim.
- **3 MINORs, also fixed**: `parseCsvLine` silently merged every field after an
  unterminated quote into one garbled value instead of rejecting the line — a stray `"`
  in a hand-typed name/remarks field (this is government-published text about people,
  not machine-generated data) would corrupt that row rather than being caught; it now
  returns `null` for such a line, treated as unparseable exactly like a blank one
  (`parseOfacSdnLine` already had that fallback for blank lines). `ScreeningService.
  runRecurringBatch`'s catch block gained a comment explaining *why* logging
  `(err as Error).message` verbatim is safe here — every failure this loop can actually
  reach is keyed on `customer.id`, never built from a matched name or list content — so a
  future reader doesn't have to re-derive that safety argument from scratch. The
  single-short-token collision risk (BLOCKER 3's accepted MINOR, above) is now explicit
  in the code, not an implicit gap.

## Where the code lives

- `packages/db/prisma/schema.prisma` — `WatchlistSource`, `WatchlistEntry`,
  `WatchlistSyncRun` (search "Process 49").
- `packages/db/prisma/migrations/20260904140000_add_watchlist_sync/`.
- `apps/api/src/modules/compliance-risk/` — `watchlist-sync.config.ts` (pure:
  `normalizeWatchlistName`, `parseCsvLine`/`parseOfacSdnCsv`, `parseUnConsolidatedXml`,
  the two cron constants), `watchlist-fetchers.ts` (the network boundary),
  `watchlist-sync.service.ts` (fetch→parse→upsert→prune orchestration),
  `watchlist-sync.controller.ts`, `watchlist-sync.scheduler.ts` (12h).
- `apps/api/src/repositories/watchlist-entry.repository.ts` — including
  `findLastSuccessfulRun` (the plausibility-floor baseline, BLOCKER 2 above).
- `apps/api/src/modules/customer/screening.service.ts` — `findRealWatchlistHit`
  (the match call) and `runRecurringBatch` (moved here from the scheduler).
- `apps/api/src/modules/customer/screening-batch.scheduler.ts` — now a thin 4-hourly
  delegator.
- `apps/api/src/modules/customer/screening.controller.ts` — `POST
  /screening/recurring-batch`, the on-demand trigger.
- `apps/web/app/(app)/watchlist-sync/page.tsx` +
  `apps/web/lib/compliance-risk/watchlist-sync-api.ts`.

## Out of scope for this file

Building an actual production-grade fuzzy/phonetic name-matching algorithm — this module
is explicit that it does not have one. Any *paid* sanctions/PEP/AML data provider — #49's
scope is specifically the free lists a broker can use with no procurement decision.
Screening any entity type beyond `Customer`/`UltimateBeneficialOwner` (an
`InsuredPerson`/`Employee`/`ThirdPartyClaimant` name is not checked — no module writes
those tables yet either). Domain F's other processes — see
`meta/context/transaction-monitoring.md` (#48) for the "Out of scope" list covering
#50-57.
