# Lex: Backup RPO/RTO

**Enforcement level: mandatory — no exceptions.**

## Rule

Every production database must have encrypted, scheduled backups, and the
restore path must be exercised end-to-end — not merely assumed to work —
at least as often as the RTO target below, and reviewed at least annually.
Recovery Point Objective (RPO): **24 hours** — daily backups, so at most a
day of data can be lost. Recovery Time Objective (RTO): **15 minutes**
(900 seconds) — a restore from backup, verified, must complete within that
window. These are draft targets (no production deployment target exists yet
— see `ibms-app/README.md` § Deployment), not yet signed off by the
business-continuity owner named in Part 10.4/10.5 — treat them as the
number currently being tested, confirm them the day a real production
database exists.

## What triggers this rule

- Any production (or would-be-production) PostgreSQL database
- A change to the backup schedule, encryption method, or restore procedure
- The annual RPO/RTO review coming due

## What does NOT trigger this rule

- The `db-test`/`db-uat` local docker-compose databases outside of using
  them as the drill target for testing the *mechanism* itself — the rule is
  about protecting real data, not about every database that happens to run
  Postgres
- A schema migration (that's `meta/lex/workflow-state-transitions.md`'s and
  the ordinary migration-review process's concern, not this one)

## How it is enforced

**CI check:** `Backup restore drill` (`ibms-app/.github/workflows/backup-drill.yml`)
— runs weekly (more often than the annual minimum, so a broken restore path
is caught in days, not up to a year later) and on manual dispatch, driving
`ibms-app/scripts/backup-restore-drill.sh`. The script dumps a database,
encrypts the dump (AES-256-CBC), decrypts and restores it into a throwaway
database, verifies the restored row count matches the original, and fails
the run if the whole cycle exceeds the RTO target (`RTO_TARGET_SECONDS`,
default 900) — this is what "actually-tested," not "backup-only assurance,"
means concretely. Today the CI workflow and a manual
`bash scripts/backup-restore-drill.sh` run only ever target `db-test` — no
production database exists yet for this to protect. Wire it at a real
database the day one exists, and update the RPO/RTO numbers above with
whatever the business actually commits to instead of the draft figures.

## Rationale

Part 10.4/10.5 requires disaster-recovery capability, and a backup that has
never been restored is not a verified capability — it is an assumption that
happens to be encrypted. Making the restore drill a script with a real
pass/fail (row-count parity + a timed RTO check) rather than a checklist
item is the same "claims are not evidence" posture as
`meta/context/verification-contract.md` — an exit code, not someone
remembering to test it once a year.
