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
  remarks: string?              # OFAC "Remarks", or UN "COMMENTS1" — PUBLIC government
                                 # text, not IBMS customer data
  syncRunId: string              # which WatchlistSyncRun last confirmed this row

WatchlistSyncRun
  source: WatchlistSource
  status: "running" | "succeeded" | "failed"
  recordCount: int?
  errorMessage: string?
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

## Where the code lives

- `packages/db/prisma/schema.prisma` — `WatchlistSource`, `WatchlistEntry`,
  `WatchlistSyncRun` (search "Process 49").
- `packages/db/prisma/migrations/20260904140000_add_watchlist_sync/`.
- `apps/api/src/modules/compliance-risk/` — `watchlist-sync.config.ts` (pure:
  `normalizeWatchlistName`, `parseCsvLine`/`parseOfacSdnCsv`, `parseUnConsolidatedXml`,
  the two cron constants), `watchlist-fetchers.ts` (the network boundary),
  `watchlist-sync.service.ts` (fetch→parse→upsert→prune orchestration),
  `watchlist-sync.controller.ts`, `watchlist-sync.scheduler.ts` (12h).
- `apps/api/src/repositories/watchlist-entry.repository.ts`.
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
