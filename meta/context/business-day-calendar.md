# Business-day calendar (used by every SLA in pdpl-sla-timers.md)

**Last verified:** 2026-08-26 · **Owner:** DPO (role, not yet a named person)

## What this is

`meta/lex/pdpl-sla-timers.md`'s SLA registry states most of its deadlines in "business
days" (consent withdrawal: 2; DSR access/deletion: 15; DSR correction/objection: 10;
quarterly access review: 15; data sharing decision: 3 standard / 1 regulatory-channel;
DPIA screening review: 5) without ever defining what a business day is in Jordan. This
file is that definition — the one fact every business-day SLA computation across all 14
registry rows depends on, not just the ones a given engineering session happens to touch.

## The shapes

```
Jordan's weekend: Friday + Saturday (not Saturday/Sunday)
```

`ibms-app`'s `apps/api/src/common/business-days.util.ts` (backlog A.8) encodes this as
`JORDAN_WEEKEND_DAYS = [5, 6]` (`Date#getUTCDay()` numbering: 0=Sunday..6=Saturday) and
uses it as the default for `addBusinessDays()`/`applyDuration()`.

## The rules that aren't obvious

- **CORRECTED 2026-11-08 — THE CALENDAR EXISTS, AND THIS WAS THE THIRD PLACE THE SAME
  STALE SENTENCE WAS WRITTEN.** This bullet said *"No gazetted public-holiday calendar
  exists anywhere in this brain"*, and the two copies in `ibms-app`
  (`business-days.util.ts`'s top docblock and `follow-up.util.ts`'s) both cited THIS FILE
  as their authority. It was true when written and rotted in place. **Measured:**
  `model SlaHoliday` is in `packages/db/prisma/schema.prisma`, is editable over HTTP
  through `sla-timer.controller.ts`, and holds **48 rows on the dev database**. Its source
  and its cadence rule are in `apps/api/src/modules/sla/jordan-public-holidays.config.ts`
  — Jordan's Ministry of Foreign Affairs, owner-supplied 2026-09-28 — which is the "real
  holiday calendar section" the old third bullet asked for, and it carries the rule that
  matters: **the Islamic dates are entered per year from the official announcement and are
  never computed**, because the announced day can differ from any calendar conversion and
  a wrong deadline would look like arithmetic rather than a wrong input. Only the four
  fixed dates may be generated.
- **`addBusinessDays()` ALREADY TAKES A HOLIDAY LIST.** The old third bullet named that as
  the outstanding fix; `BusinessDayOptions.holidays` has shipped. **So what is left is
  WIRING, not capability, and it is a narrower and more checkable statement than the one
  this file used to make.** The util is pure and does no I/O, so each caller must pass the
  set. Measured 2026-11-08: 12 non-spec files import it, 9 evaluate a duration, and the
  holidays reach exactly ONE path — `sla-timer.service.ts:234` → `computePolicyDueAt`,
  the configured-`SlaPolicy` path.
- **Consequence, now true of SEVEN call sites rather than of every deadline.** The
  reasoning below is unchanged and still correct wherever no calendar is passed: such a
  deadline only skips Friday/Saturday, does not skip Eid al-Fitr, Eid al-Adha,
  Independence Day or any other public holiday falling on a weekday inside the window, and
  is therefore a **lower bound** — never *earlier* than the true statutory deadline, but
  possibly *later*. A system escalating on it escalates early, never in violation, and
  never exactly on time. **Do not present such a date as the legally exact deadline in a
  DPO-facing or regulator-facing report.** The seven, measured in `ibms-app`:
  `follow-up.util.ts:55`, `dsr.config.ts:95`,
  `access-recertification.controller.ts:75`, `access-recertification.scheduler.ts:40`,
  and three inside `sla-timer.service.ts` itself — `:181` the registry fallback (the only
  path on a database with no `SlaPolicy` rows), `:227` the regulatory fast track, and
  `:277` the one non-zero escalation offset (DSR's T−3-business-day DPO warning).
- **A caller whose unit is not `businessDays` is not in that set.** `calendarDays`,
  `months`, and `minutes`/`hours` without a `workingWindow` never consult
  `businessDayOptions`, so there is nothing for them to pass and passing one would be dead
  code. `CONTINUOUS_24_7` policies are holiday-blind **deliberately** — a containment
  clock does not stop for Friday — and `businessDayOptionsFor` records that at its own
  site.

## Where the code lives

- `ibms-app`'s `apps/api/src/common/business-days.util.ts` — `JORDAN_WEEKEND_DAYS`,
  `isBusinessDay()`, `addBusinessDays()`, `applyDuration()`.
- `ibms-app`'s `apps/api/src/modules/sla/sla-registry.config.ts` — the 14-entry SLA
  registry whose `businessDays`-unit durations and escalation-stage offsets are the reason
  this file exists.

## Out of scope for this file

The 14 SLA values themselves and their escalation paths — `meta/lex/pdpl-sla-timers.md`.
The retention-period-table gap (a different missing number, same missing-authoritative-
source shape) — `meta/context/data-retention-and-disposal.md`.
