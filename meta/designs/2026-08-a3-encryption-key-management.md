# Design: A.3 field-level encryption + centralized key management, built ahead of any consumer

**Status:** accepted · **Date:** 2026-08-26 · **Author:** shouq · **Service:** ibms-app — apps/api

## Context

Backlog item A.3 (Part 10.2) requires four things: (1) a field-level encryption service applied
to every `-- ENCRYPT` schema field, (2) encryption at rest for the database and the document
store, (3) mandatory TLS on all traffic, (4) centralized key management — restricted
key-custodian access, a rotation policy, logging of every key use.

Two constraints shaped how this landed:

- `MfaCredential.secretEnc`/`webauthnPublicKeyEnc` already had a working, tested field-level
  encryption implementation (`apps/api/src/common/crypto.util.ts`, single `MFA_ENCRYPTION_KEY`
  env var, AES-256-GCM) before this task started.
- The other five `-- ENCRYPT` fields this task names — `Customer.nationalIdEnc/
  contactPhoneEnc/contactEmailEnc`, `UltimateBeneficialOwner.nationalIdEnc`,
  `InsuredPerson.nationalIdEnc`, `Employee.nationalIdEnc`, `ThirdPartyClaimant.
  contactDetailsEnc` — exist only in the schema. No CRM/HR/Claims module reads or writes them
  yet (Part C's business modules aren't built) — the same situation A.2's permission grid
  was built into ahead of any consumer (see `2026-08-*` RBAC work; no design doc filed for that
  one, but the reasoning is identical and recorded in project memory).
- `ibms-app`'s deployment platform is still **TBD** (`meta/context/verification-contract.md`) —
  there is no concrete cloud provider or managed Postgres/object-store instance to point a
  disk-encryption-at-rest setting at yet.

## Decision

**1. One new centralized service, not a retrofit of the MFA path.** `apps/api/src/modules/
security/` adds `KeyRegistryService` (versioned key material, env-driven, purpose-scoped) and
`EncryptionService` (AES-256-GCM encrypt/decrypt, ciphertext format `keyId:iv:authTag:
ciphertext` so the embedded key id makes rotation possible) for a new `'pii'` purpose. It does
**not** touch `crypto.util.ts` — MFA secrets keep their own single-key pool
(`MFA_ENCRYPTION_KEY`). Two independent key pools give blast-radius isolation: a compromised PII
key does not expose auth secrets and vice versa. `EncryptionService`'s design (purpose-scoped,
versioned registry) is generic enough for `crypto.util.ts` to adopt later without a redesign —
see Revisit.

**2. Infrastructure built ahead of the consumer, scoped to a service + a field map, not full
repositories.** `apps/api/src/modules/security/encrypted-fields.ts` declares the exact five-entity
field map from the schema's `-- ENCRYPT` comments and exposes `encryptEntityFields`/
`decryptEntityFields` generic helpers. No `CustomerRepository`/`EmployeeRepository`/etc. were
added — those entities have no controller, service, or DTO yet, and guessing their CRUD shape
ahead of the real CRM/HR module would be speculative business logic, not infrastructure (unlike
the RBAC permission grid, which had nowhere else to attach). Whichever module creates
`Customer`/`UltimateBeneficialOwner`/`InsuredPerson`/`Employee`/`ThirdPartyClaimant` rows calls
these helpers and gets compliant field-level encryption by construction.

**3. Every key use is logged, not just encryption calls in aggregate.** A new `AuditAction.
ENCRYPTION_KEY_USED` value records `{ keyId, purpose, field, operation }` (never plaintext or
ciphertext) on every single `encrypt`/`decrypt` call, attributed to the acting user, with
`isSensitiveDataAccess: true` on decrypt (Part 10.3 — reads of Sensitive Personal Data must be
logged, not just writes).

**4. Key-custodian access is a role, not a new access model.** `SYSTEM_SECURITY_ADMINISTRATOR`
(the existing RBAC role closest to a security-operations function) is the sole role granted the
new `encryption-key.read` permission, gating `GET /security/encryption-keys`
(`EncryptionKeysController`) — which returns key ids and active/retired status only. Key
material never leaves process memory/env config; there was nothing to add beyond "who may see
even the metadata."

**5. Rotation policy is the versioned-registry mechanism, not a scheduled job.**
`PII_ENCRYPTION_KEYS` holds every key version still needed for decrypt; `PII_ENCRYPTION_
ACTIVE_KEY_ID` picks which one encrypts new writes. Operator rotates by adding a new id,
flipping the active id, then retiring the old id once every row encrypted under it has been
re-encrypted. No automated re-encryption sweep exists — there is no data yet for it to sweep
(see Consequences).

**6. TLS is enforced at the app layer plus a fail-fast boot check, not a new reverse-proxy
config this repo doesn't own.** `apps/api/src/common/security-headers.middleware.ts` sets HSTS
and rejects any request that did not arrive over HTTPS (checked via `X-Forwarded-Proto`,
since a reverse proxy — not this app — terminates TLS), gated on `NODE_ENV=production` so local
dev/CI are unaffected. `main.ts`'s `assertDatabaseTls()` refuses to boot in production unless
`DATABASE_URL` sets `sslmode=require`/`verify-ca`/`verify-full`. Third-party/server-to-server
integrations don't exist yet (no Insurer/vendor HTTP client is built) — there is nothing to
enforce TLS on yet; noted here so it isn't forgotten when one lands.

**7. Encryption at rest (DB + document store) is recorded as a deferred operational
requirement, not simulated with application code.** There is no chosen deployment platform and
no document-store integration yet (`Document.storageRef` has no upload service behind it). This
is genuinely an infra-provisioning decision (a managed Postgres/object-store's encryption-at-rest
setting, or self-hosted disk encryption) that cannot be wired to a real target today. Recorded
here and in `README.md` so it is a tracked gap, not a silently-dropped checklist item.

## Alternatives considered

| Option | Why it lost |
|---|---|
| Migrate `MfaCredential` onto the new `EncryptionService`/`KeyRegistryService` in the same change | Working, tested code with a passing round-trip/tamper spec; the existing 3-part ciphertext format (`iv:authTag:ciphertext`) would need to become 4-part (`keyId:...`) to fit the shared format, a breaking change to already-committed logic with no compliance benefit today — MFA secrets were never in scope of this backlog item's field list. Isolating the two pools is arguably the *better* security posture anyway (see Decision §1), so there's no pressure to unify beyond code tidiness. |
| Build full `CustomerRepository`/`UltimateBeneficialOwnerRepository`/etc. now, encryption wired in | Would require inventing create/update/find method shapes for a CRM/HR module that doesn't exist, guessing at a contract the real module might not match — dead code that goes stale, and scope creep on a task titled "Encryption & Key Management," not "Customer module." |
| A Prisma Client Extension (`$extends`) that transparently encrypts/decrypts by field name on every `create`/`update`/`find*` call, applied once in `packages/db` | Would auto-apply to `MfaCredential` too without an opt-out, forcing the MFA-pool-isolation question immediately; also silently intercepts every query against these models with async crypto + a DB write (the audit log) per field, which is much harder to reason about/test than an explicit service call at the point a repository is written. An explicit `encryptEntityFields`/`decryptEntityFields` call is one line for a future repository to add and is visible in code review — worth the small ergonomic cost. |
| Real KMS/HSM integration (AWS KMS, Azure Key Vault, HashiCorp Vault) for key storage | No cloud provider is chosen yet (deployment platform TBD). `KeyRegistryService`'s env-var-backed, purpose-scoped, versioned-key interface is deliberately the shape a real KMS-backed implementation would have (`getActiveKey()`/`getKey(id)`/`listKeyMetadata()`) — swapping the env-var loader for a KMS client call is a contained, later change, not a redesign. |
| Skip the encryption-at-rest and TLS rows entirely since neither has a concrete deployment target | Leaving a mandatory-rule checklist item silently unaddressed is worse than recording it as a known, tracked gap — a reviewer citing this design doc can see exactly what's done (app-layer TLS enforcement + DB connection check) versus deferred (disk/object-store encryption, pending a platform choice) instead of assuming either "not started" or "silently done." |

## Consequences

**Accepted costs:** two key pools to operate instead of one (MFA vs. PII) until/unless they're
unified; no automated re-encryption sweep on rotation (an operator must re-encrypt existing rows
by hand once real data exists, before retiring an old key id); encryption-at-rest for the
database and document store remains undone at the infrastructure level — this design doc and
`README.md` are the tracking mechanism until a deployment platform exists to configure it on.

**Revisit if:** (a) a deployment platform is chosen — wire real disk/object-store
encryption-at-rest and replace `assertDatabaseTls()`'s regex check with whatever connection
config that platform's managed Postgres actually requires; (b) the first Customer/UBO/
InsuredPerson/Employee/ThirdPartyClaimant-creating module is built — confirm
`encryptEntityFields`/`decryptEntityFields` fits its repository shape rather than assuming it
does; (c) a real key-rotation event happens with production data present — build the
re-encryption sweep then, informed by actual row counts/volume, instead of speculatively now;
(d) MFA and PII key management visibly diverge in a way that causes real operational confusion —
migrate `crypto.util.ts` onto `KeyRegistryService`/`EncryptionService` at that point.
