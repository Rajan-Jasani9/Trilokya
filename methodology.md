# Project Methodology — DRDO Project Monitoring System (Trilokya)

This document describes **how this system is conceived, structured, and evolved**: architectural choices, domain rules (TRL governance), delivery practices, and operational assumptions. It complements `README.md` (setup, API surface, and file layout) with **methodological** guidance for contributors and reviewers.

---

## 1. Purpose and scope

- **Goal**: Support **multi-stakeholder project oversight** in a DRDO-style context by tracking **Technology Readiness Level (TRL)** and related readiness dimensions at the **Critical Technology Element (CTE)** level, with roll-up to projects, **evidence**, **approvals**, and **role-based access**.
- **Product name in codebase**: The application is referred to as **Trilokya** in frontend packaging; the repository and domain documentation use **DRDO Project Monitoring System** / TRL monitoring language interchangeably.
- **Out of scope (unless extended)**: Full IRL/MRL/SRL business rules are **scaffolded** in models and APIs; methodology for those should mirror the TRL pattern once requirements are fixed (see §7).

---

## 2. Development methodology

### 2.1 Iterative delivery

- Features are delivered in **vertical slices**: API routes → core engine / permissions → persistence → UI pages and components.
- **Configuration-first readiness**: TRL levels, questions, evidence rules, and workflow settings are **admin-configurable** rather than hard-coded-only, so methodology changes (within TRL 1–9) can be reflected without redeploying code in many cases.

### 2.2 Environment and reproducibility

- **Backend**: Python virtual environment, `requirements.txt` for dependencies, `.env` for secrets and `DATABASE_URL`, **Alembic** for schema history.
- **Frontend**: Node.js, `npm` for dependencies, **Vite** for dev server and production builds.
- **Bootstrap**: Database is brought to a known state via **migrations** (`alembic upgrade head`) and **initialization scripts** (roles, org units, users, TRL definitions, optional seed data). New environments should follow `README.md` end-to-end to avoid drift.

### 2.3 Documentation hierarchy

| Artifact | Role |
|----------|------|
| `README.md` | Setup, structure, domain summary, API overview |
| `methodology.md` (this file) | How we build, govern data, and reason about TRL/process |
| Inline code | Authoritative for behavior; update when behavior changes |

---

## 3. Architectural methodology

### 3.1 Backend (FastAPI)

- **Layered design**:
  - **Routers** under `app/api/routes/` expose versioned REST endpoints.
  - **Pydantic schemas** under `app/schemas/` define request/response contracts and validation.
  - **SQLAlchemy models** under `app/models/` own persistence and relationships.
  - **Core** (`app/core/`) holds cross-cutting concerns: security, permissions, TRL/readiness engines, file storage.
- **Shared dependencies** (e.g. current user, DB session) live in `app/api/deps.py` for consistent injection and testing hooks.
- **Migrations** are the single source of truth for schema evolution; application code assumes the DB matches **Alembic head**.

### 3.2 Frontend (React + Vite)

- **SPA routing** with **React Router**: public routes (e.g. login, landing) vs. **`/app/*`** behind **`ProtectedRoute`** and **`AuthProvider`**.
- **Layout shell** (`Layout`, sidebar, navbar) wraps authenticated pages for consistent navigation and role-appropriate menus.
- **Service layer** (`src/services/`) centralizes HTTP calls (e.g. Axios) and auth token handling; pages stay thin and delegate data access and mutations.
- **Styling**: **Tailwind CSS** with **responsive breakpoints** (mobile-first); components avoid one-off inline styles where utility classes preserve consistency.

### 3.3 Integration contract

- The frontend consumes **REST + JWT**: login yields tokens; subsequent requests send the access token; refresh flows are supported per API design in `README.md`.
- API paths are rooted under `/api` in production depending on the reverse proxy; local development should mirror that contract to avoid environment-specific bugs.

---

## 4. Domain methodology (TRL, CTEs, projects)

### 4.1 Entity relationships

- **Project** aggregates **CTEs**. Each **CTE** carries **target TRL** and links to TRL (and optionally IRL/MRL/SRL) assessment records.
- **Organization units and membership** scope who sees which projects and actions.

### 4.2 Readiness computation (high level)

- **CTE current TRL**: Derived from **approved** assessments—the effective level respects **question completion**, **evidence rules**, and configured definitions (not a single numeric field in isolation).
- **Project TRL roll-up**: Default aggregation uses the **minimum** of participating CTE TRLs (weakest link), reflecting governance risk; **project-level TRL overrides** exist for controlled exceptions (manager/super-admin capabilities per README).
- **Target TRL**: CTEs store targets; project target TRL aggregates (e.g. **minimum of CTE targets**) so planning and gap analysis stay aligned.

### 4.3 Workflow and evidence

- **Progression** follows: fetch questions for target level → answer → attach **notes and evidence** (files/links as supported) → submit → **approval** when the workflow requires it.
- **TRL definitions** (levels, questions, required flags, evidence requirements, weights) are managed through **admin APIs** and the **TRL definition UI**, keeping methodology adjustments traceable and auditable.

### 4.4 Governance and audit

- **Role-based access control (RBAC)** restricts create/read/update paths by role and org context.
- **Audit logging** captures material actions (assessments, approvals, configuration), supporting accountability in a multi-stakeholder setting.

---

## 5. Security methodology

- **Authentication**: JWT access (and refresh) tokens; tokens stored and attached per frontend auth utilities.
- **Authorization**: Centralized permission checks in the backend; UI hides or disables actions where possible but **server rules are authoritative**.
- **Input and storage**: Pydantic validation on inputs; ORM for SQL safety; uploads validated and stored via dedicated file handling; production assumes **HTTPS/TLS**.

---

## 6. Quality and change management

### 6.1 Testing (recommended practice)

- The repository prioritizes **documentation and working integration paths**; automated test suites are a **recommended next step** for regression safety (API tests for TRL engine edge cases, RBAC matrix checks, and critical UI flows).

### 6.2 Schema and data changes

- **Additive-first migrations** when possible to support rolling updates.
- **Seed and init scripts** should remain idempotent or clearly documented if destructive, so staging and production refreshes stay predictable.

### 6.3 Frontend quality

- Prefer **accessible patterns** (semantic HTML, keyboard-friendly controls) alongside responsive layout.
- Reuse **common components** (tables, modals, toasts) before adding new primitives.

---

## 7. Future extensions

- **IRL / MRL / SRL**: Models and routes exist as scaffolding; methodology should **reuse the TRL progression + evidence + approval** template once business rules are defined.
- **Technology foresight / catalog** (where present in backend data and scripts): treat as **reference or seed content**, not a substitute for project-specific TRL assessments unless product requirements say otherwise.

---

## 8. Deployment notes

- **Backend**: `uvicorn` ASGI server; configure `DATABASE_URL`, `SECRET_KEY`, and CORS for the frontend origin.
- **Frontend**: `npm run build` produces static assets; deploy behind a static host or CDN (e.g. **Vercel** configuration exists in `frontend/vercel.json`).
- **Operations**: Rotate secrets between environments; **change default seeded passwords** before any shared or production use.

---

## Summary

This project follows a **layered API + SPA** pattern with **CTE-centric TRL tracking**, **configurable definitions**, **approval workflows**, **evidence**, and **RBAC**. Development is **migration-driven** and **script-assisted** for reproducible environments; extend **IRL/MRL/SRL** using the same procedural template when requirements stabilize.
