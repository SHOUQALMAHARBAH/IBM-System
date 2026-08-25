# Verification contract — what "working" means here

**Last verified:** 2026-08-24 · **Owner:** shouq

> This is the most valuable verification file in the brain. Without it, an agent invents its own standard of "done" — and it will be lower than yours.
>
> An agent will tell you the page looks great whether or not it ever rendered the page.
>
> **The rule: claims are not evidence. Exit codes, test results, API responses, database verification, and screenshots are evidence.**

A change is NOT done when the code is written. It is done when the applicable evidence below exists and is pasted or linked in the PR description.

---

## Current engineering baseline

The IBMS engineering stack is:

| Layer | Technology |
|---|---|
| Source control | GitHub |
| CI/CD | GitHub Actions |
| Frontend | Next.js + TypeScript |
| Backend | Node.js + TypeScript |
| Database | PostgreSQL |

The following are not finalized yet and must be filled in when the engineering repository is established:

| Area | Status |
|---|---|
| Frontend test framework | Vitest + Testing Library |
| Backend test framework | Vitest |
| E2E framework | Playwright |
| Accessibility tooling | axe-core |
| Database migration tooling | Prisma Migrate |
| API contract testing | OpenAPI |
| Containerization | Docker |
| Preview environment | Vercel |
| Deployment platform | none yet |

**Do not invent a command for a gate that does not exist yet.**

---

# Every change

| Gate | Command | Evidence |
|---|---|---|
| Brain health | `bash scripts/brain-doctor.sh` | exit 0 |
| No unfilled placeholders | part of brain-doctor | 0 unfilled fill-markers outside `_TEMPLATE.md` files |
| Type checking | `npm run typecheck` | exit 0 — once script exists |
| Lint | `npm run lint` | exit 0 — once script exists |
| Unit tests | `npm test` | exit 0 + test count — once script exists |
| Build | `npm run build` | exit 0 — once script exists |
| Regulatory traceability | Manual | citation present in PR/ticket description |
| Evidence generation | CI artifact | artifact exists for the commit SHA |

The exact executable commands become authoritative when the engineering repository and CI pipeline are created. If the repository uses different script names, update this contract instead of inventing aliases.

---

# Once the engineering repository exists

The first repository-creation PR must establish the real commands for:

| Gate | Required evidence |
|---|---|
| Types | exit 0 |
| Lint | exit 0 |
| Unit tests | exit 0 + test count |
| Build | exit 0 |
| Integration tests | exit 0 |
| E2E | exit 0 |
| Accessibility | 0 serious/critical violations |
| Security tests | exit 0 |
| Database migrations | exit 0 |
| Database schema tests | exit 0 |
| Smoke tests | exit 0 |

These rows must be updated in the same commit that creates the relevant engineering capability.

---

# Backend services additionally

Every backend service must eventually have:

| Gate | Command | Evidence |
|---|---|---|
| Boots | `npm run start` | service starts successfully |
| Health | `curl /health` | HTTP 200 |
| Smoke | `bash scripts/smoke.sh auth` | exit 0 + output |
| Contract | `npm run test:contract` | exit 0 |
| Security | `npm run test:security` | exit 0 |
| Integration | `npm run test:integration` | exit 0 |

**Write `scripts/smoke.sh` for each service the day services exist.**

A smoke test must assert the service's actual job. A process merely starting is not sufficient.

For IBMS, smoke coverage should eventually include at least one critical business rule, such as:

- unauthorized user cannot approve a protected workflow;
- maker cannot approve their own transaction where maker/checker separation applies;
- a shared request becomes locked where the business rule requires locking;
- a historical insurance request remains linked to its original form version.

---

# Frontend pages additionally

Every changed frontend page must eventually have:

| Gate | Command | Evidence |
|---|---|---|
| Type checking | `npm run typecheck` | exit 0 |
| Lint | `npm run lint` | exit 0 |
| Unit/component tests | npm test | exit 0 + test count |
| E2E | npx playwright test | exit 0 |
| Screenshots | Playwright screenshots | required PNG states |
| Accessibility | axe-core + manual keyboard verification | 0 serious/critical violations + keyboard checks pass |
| Production build | `npm run build` | exit 0 |

---

# Required UI states

Every page ships with all four states implemented and verified:

1. **loading**
2. **empty**
3. **error**
4. **populated**

A state with no screenshot is a state that is not implemented.

For workflow-heavy IBMS pages, additional states may be required:

- draft
- submitted
- pending approval
- approved
- rejected
- returned
- cancelled
- locked
- archived
- expired

Only applicable states need to be implemented for a specific page.

---

# IBMS frontend requirements

Every affected IBMS page must be verified in:

### English

- LTR navigation
- LTR forms
- LTR tables
- LTR filters
- LTR dialogs
- LTR charts

### Arabic

- RTL navigation
- RTL forms
- RTL tables
- RTL filters
- RTL dialogs
- RTL charts

The test must verify the actual layout, not merely the text direction.

---

# Bidirectional text

IBMS must correctly display mixed Arabic/English values.

Examples include:

- Arabic customer/company names containing English codes
- Arabic insurance names containing policy/product codes
- English reference numbers inside Arabic forms
- Arabic addresses containing Latin characters

Evidence must show that mixed-content fields remain readable and correctly positioned in both LTR and RTL contexts.

---

# Keyboard accessibility

Every interactive element must have:

- visible keyboard focus;
- logical keyboard order;
- accessible name/label;
- usable keyboard interaction.


Accessibility tooling: axe-core.
Automated accessibility checks must report 0 serious/critical violations.
Keyboard navigation and focus behavior remain manually verified where automated tooling cannot establish usability.

---

# No layout shift

Pages must not materially shift when data changes from loading to populated.

This is especially important for:

- dashboards;
- tables;
- forms;
- insurance requests;
- claims;
- collections;
- governance screens.

---

# Responsive verification

IBMS pages must eventually be verified at:

- mobile breakpoint;
- tablet breakpoint where applicable;
- desktop breakpoint.

Exact breakpoint values are **TBD** until the design system is finalized.

---

# Authentication and authorization

Any change touching authentication or authorization must verify:

- successful authentication;
- invalid credentials;
- password policy;
- session handling;
- role-based access;
- permission denial;
- server-side authorization.

Hiding an action in the frontend is not authorization.

The backend must independently reject unauthorized operations.

---

# RBAC

Changes to roles or permissions must verify:

```text
User
  ↓
Role
  ↓
Permission
  ↓
Action