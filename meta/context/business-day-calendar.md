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

- **No gazetted public-holiday calendar exists anywhere in this brain.** This is the same
  class of gap already recorded in `meta/context/data-retention-and-disposal.md` for the
  `PRIV-STD-03` retention-period table: engineering has never been handed the actual list
  of Jordanian public holidays (fixed-date national holidays plus the lunar-calendar
  Islamic holidays whose Gregorian dates shift year to year and are only confirmed a few
  weeks ahead by royal decree) to exclude from a business-day count.
- **Consequence:** any business-day SLA deadline computed today — e.g.
  `ibms-app`'s `addBusinessDays()` — only skips Friday/Saturday. It does not skip Eid
  al-Fitr, Eid al-Adha, Independence Day, or any other public holiday that falls on a
  weekday within the SLA window. That makes every computed deadline a **lower bound**: the
  true statutory/contractual deadline (which does exclude public holidays) is never
  *earlier* than the computed one, but may be *later* — so a system that escalates on the
  computed date escalates conservatively (early), never in violation of the real deadline,
  but also never exactly on time. Do not present a business-day-computed date as the
  legally exact deadline in any DPO-facing or regulator-facing report until a real holiday
  calendar is supplied.
- **The fix is the same as the retention-period gap**: someone with the authority to
  supply an authoritative Jordanian public-holiday source (DPO/Compliance/Legal, or HR's
  existing annual holiday circular if one exists) needs to hand it over. At that point this
  file should gain a real "The holiday calendar" section (a source, an update cadence for
  the lunar holidays, and how far ahead it's confirmed) and
  `business-days.util.ts`/`addBusinessDays()` should take a holiday list, not just a
  weekend-days set.

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
