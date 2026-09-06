# Human Resources / Employee Onboarding (Process 66)

**Last verified:** 2026-09-17 · **Owner:** System Security Administrator,
Branch/Department Manager (roles, not yet named people)

## What this is

Backlog Part C #66 — **opens Domain H, Supporting Operations (#66-74)**.
Two checkboxes: an employee record + licensing/certification tracking for
regulated staff + training records; an automated access de-provisioning
checklist on an employment-status change (same business day). `Employee`,
`SecurityAwarenessTraining`, and `AccessDeprovisioningChecklist` all
pre-exist in the core schema (Part 8.2) with zero prior application code —
this is their first real consumer, the exact "dormant model, first real
writer" shape #58-65 repeatedly found in Domain G.

## Licensing/certification tracking maps to existing flat fields

The backlog says "licensing/certification tracking for regulated staff."
No separate `Certification`/`License` child table exists in the schema —
`Employee.licensedRole` (free text), `confidentialityAgreementSignedAt`,
and `backgroundCheckCompletedAt` are the schema's OWN complete design for
this (Part 8.2). No new table was invented; these three flat fields ARE
the tracking.

## `terminate()` is the first real caller of an already-registered SLA

The backlog's "automated access de-provisioning checklist... same business
day" is not a new SLA decision — `pdpl-sla-timers.md`'s own registry
already has a sourced row: **"Termination access revocation (M05) | Same
business day | Critical alert to IT management if still open after 24h."**
The machine-readable `SLA_REGISTRY` (`sla-registry.config.ts`) already
transcribes this as `termination_access_revocation` — `duration: { value:
0, unit: 'hours' }` (the "same business day as trigger" reading: due AT
the trigger instant, not "end of day" — a deliberate simplification
avoiding a whole new `SlaDurationUnit`), one escalation stage at `+24
hours` to `'IT_MANAGEMENT'`. **Zero prior caller existed for this entry**
— `EmployeeService.terminate()` is the first. No new SLA design work was
needed; only wiring `SlaTimerService.startTimer()`/`.resolve()` to the
real termination/completion events.

## Termination is a stamp+create transaction, not a status enum

`Employee` has no `status`/`EmploymentStatus` enum — the "employment-status
change" that triggers de-provisioning is `terminationDate` going from
`null` to a real date. `EmployeeRepository.terminate()` stamps
`terminationDate` and creates the `AccessDeprovisioningChecklist` row in
ONE interactive `$transaction` — the
`retention-case.repository.ts#escalateAndCreateRetentionCase` shape (a
deliberate, precedented local exception to this codebase's no-`$transaction`
convention): the stamp's `where` re-asserts `terminationDate: null`
(race-safe-invariants.md), so a second concurrent termination attempt
gets a clean `null` result (409) instead of racing into a duplicate
checklist or a raw unique-constraint error.

## `systemAccessRevoked` has a real effect, not just a timestamp

Ticking `systemAccessRevoked: true` on the checklist does more than record
`systemAccessRevokedAt` — if the employee has a linked `User` account
(`User.employeeId`), the service:
1. Sets `user.isActive = false` (blocks future logins).
2. Calls `SessionService.revokeAllForUser(userId, 'admin_revoked')` —
   killing every live session immediately. `JwtStrategy.validate()` calls
   `SessionService.validateAndTouch()` on EVERY authenticated request, so
   a revoked session fails the very next call with that access token —
   proven end-to-end in `test/employee.e2e-spec.ts` (a real linked user's
   own bearer token gets a 401 immediately after the tick).

This was a deliberate design choice beyond the checklist's own literal
field list: a de-provisioning checklist whose "system access revoked" box
can be ticked with no actual access-control effect would satisfy the
letter of Part 8.2 while missing its entire point (PRIV-STD-02,
PRIV-SOP-01/02/03 — the same citation the SLA registry entry already
uses).

## `User.employeeId` — #61's dormant FK gets its first real writer too

`EmployeePerformanceRecord` (#61) needs `Employee -> User` via
`User.employeeId`, but nothing before this process ever set it (#61's own
context file: "no linked User means nothing to compute"). `POST
/employees` accepts an optional `userId`; if given, the service verifies
the user exists (404) and isn't already linked to a DIFFERENT employee
(409 — `User.employeeId` is `@unique`, so a naive attempt would otherwise
surface as a raw Prisma constraint error), then links it. This is a
minimal, deliberate scope addition beyond the backlog's own two checkboxes
— not required by #66's text, but a natural, tiny completion of what an
"employee record" already implies, and it makes #61's dormant metric
usable for the first time.

## Permission split — termination sits behind the NARROWER permission

`employee.manage` (`[SYSTEM_SECURITY_ADMINISTRATOR, BRANCH_DEPARTMENT_
MANAGER]`) gates the general record + training surface. `deprovisioning.
execute` (`[SYSTEM_SECURITY_ADMINISTRATOR]` ONLY, narrower) gates BOTH
`POST /employees/:id/terminate` and every checklist action — terminating
IS the "employment-status change" the checklist's own schema doc comment
names as its trigger, so it sits behind the same narrow permission as
executing the checklist itself, not the broader `employee.manage` a
Branch/Department Manager also holds. Both permissions were pre-seeded
ahead of time — zero seed change, the Domain G "seed before code" pattern
extended to Domain H.

## Encryption follows the Customer precedent exactly

`Employee.nationalIdEnc` was already registered in `ENCRYPTED_FIELDS`
(`encrypted-fields.ts`) with zero prior consumer. `EmployeeService` mirrors
`CustomerService` field-for-field: masked-by-default (`toMasked()` via
`decryptEntityFields` + `SensitiveFieldRevealService.mask()`), full reveal
only via a justified `POST /employees/:id/reveal-field` (min. 10-character
reason, Part 10.6), and the list view STRIPS the encrypted field entirely
rather than decrypting-then-masking N times (the `CustomerService.list()`
precedent — a list of many employees is exactly the "bulk decrypt" shape
Part 10.3's anomaly detector watches for).

## Where the code lives

- `apps/api/src/modules/supporting-operations/employee.
  {config,service,controller,module}.ts` + `dto/`.
- `apps/api/src/repositories/employee.repository.ts`.
- `apps/web/app/(app)/employees/` — a list+create page and a `[id]` detail
  page (profile + reveal, training, and the de-provisioning checklist).

## Out of scope for this file

#67-74 (Procurement, Internal IT, Cybersecurity, Document Management,
Vendor Management, BCP/DR, Knowledge Management) — the remaining Domain H
items, not yet built. A true HR onboarding/offboarding WORKFLOW with
approval stages — #66 is a flat CRUD + one guarded transition
(terminate), not a multi-step workflow needing the full
`WorkflowTransitionService` engine (there is no multi-state enum to
transition through).
