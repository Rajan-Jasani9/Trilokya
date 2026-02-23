# Trilokya

A comprehensive Technology Readiness Level (TRL) monitoring and governance system built with **FastAPI**, **React**, and **PostgreSQL**, designed for DRDO-style multi‑stakeholder project oversight.

## Features

- **Multi-dimensional Readiness Tracking**: TRL today, with IRL/MRL/SRL assessment scaffolding at CTE level for future extension
- **CTE-based Assessment**: Technology readiness is tracked per Critical Technology Element (CTE), then rolled up to project level
- **Project-Level TRL Rollup**: Project TRL is computed from CTE TRLs (default `MIN(CTE TRLs)` with manual override support)
- **Target TRL Management**: Target TRL captured per CTE and aggregated to project target TRL
- **Role-Based Access Control**: Hierarchical permissions (SuperAdmin, Manager, Assistant Manager, Engineer, Scientist)
- **Approval Workflow**: Configurable multi-step approval process for TRL assessments and other actions
- **Evidence Management**: File uploads and rich text notes attached to TRL responses; evidence enforcement driven by TRL definitions
- **Admin TRL Definitions**: SuperAdmin UI to manage TRL levels, questions, evidence requirements, and weights
- **Responsive UI**: Modern, fully responsive React + Tailwind CSS frontend
- **Audit Logging**: Comprehensive audit trail for key actions (assessment, approvals, configuration changes)

## Tech Stack

### Backend
- **FastAPI (Python)**: REST API and authentication
- **PostgreSQL**: Primary data store
- **SQLAlchemy**: ORM and model layer
- **Alembic**: Database migrations
- **JWT Authentication**: Token-based auth and session management

### Frontend
- **React** (JavaScript)
- **Vite** for dev/build tooling
- **Tailwind CSS** for styling
- **React Router** for routing

---

## Setup Instructions

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file (copy from `.env.example` if present, otherwise create manually):
```bash
cp .env.example .env
```

5. Update `.env` with your database credentials:
```
DATABASE_URL=postgresql://user:password@localhost:5432/trl_monitoring
SECRET_KEY=your-secret-key-here
```

6. Run database migrations:
```bash
alembic upgrade head
```

7. Initialize database with base data (roles, org units, users, TRL definitions):
```bash
# On Linux/Mac:
python -m scripts.init_db         # Base roles, org units, users
python -m scripts.init_trl        # Default TRL levels and questions

# On Windows (from backend directory):
scripts\run_init.bat
scripts\run_init_trl.bat
```

This will create:
- All necessary roles (SuperAdmin, Manager, Assistant Manager, Engineer, Scientist)
- Sample organization units
- Default users with passwords (see script output for credentials)

**⚠️ IMPORTANT**: Change default passwords in production!

8. Start the server:
```bash
uvicorn app.main:app --reload
```

Backend will run on `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

Frontend will run on `http://localhost:3000`

---

## Project Structure

```text
backend/
├── app/
│   ├── api/
│   │   ├── routes/          # Versioned API routers (auth, projects, CTEs, TRL, admin, approvals, users, etc.)
│   │   └── deps.py          # Shared dependencies (auth, access checks)
│   ├── core/                # Security, permissions, TRL engine, file storage
│   ├── models/              # SQLAlchemy models (projects, CTEs, TRL, approvals, users, org units, etc.)
│   ├── schemas/             # Pydantic schemas for request/response
│   ├── utils/               # Helpers (Excel import, validators)
│   ├── config.py            # Settings, environment configuration
│   ├── database.py          # Session and Base
│   └── main.py              # FastAPI app entrypoint and router wiring
├── alembic/                 # Database migrations (including TRL/CTE changes)
├── scripts/                 # DB initialization helpers (init_db, init_trl)
└── uploads/                 # Evidence file storage

frontend/
├── src/
│   ├── components/
│   │   ├── auth/            # Login, protected route
│   │   ├── common/          # Layout, Navbar, Sidebar, Modal, Table, etc.
│   │   ├── projects/        # Project list/detail/forms, member assignment
│   │   ├── ctes/            # CTE list/detail/forms, TRL view
│   │   ├── approvals/       # Approval queues and actions
│   │   ├── trl/             # TRL progression workflow UI
│   │   └── admin/           # TRL definition manager and admin tools
│   ├── pages/               # Dashboard, Projects, CTEs, Approvals, Users, Admin
│   ├── services/            # API wrapper, auth, storage utilities
│   ├── context/             # Auth context and provider
│   └── styles/              # Tailwind entry styles
├── index.html               # Vite entry HTML
└── vite.config.js           # Vite configuration
```

---

## Domain & TRL Logic Overview

- **CTE-centric readiness**:
  - Each `CTE` belongs to a project and can have TRL/IRL/MRL/SRL assessment records.
  - `CTE` currently stores `target_trl` and links to TRL/IRL/MRL/SRL assessment tables.
- **TRL computation**:
  - For a given CTE, the backend computes current TRL as the **highest level** with an **approved** assessment where all required questions are satisfied (and evidence rules are met).
  - Project TRL is computed as the **minimum** of all non-zero CTE TRLs, with support for **project-level TRL overrides** by managers/superadmins.
- **Target TRL aggregation**:
  - CTEs capture `target_trl`; project target TRL is automatically updated as `MIN(target_trl of all CTEs in the project)`.
- **TRL definitions & questions**:
  - TRL levels (1–9) and their questions are configurable via admin APIs and the `TRLDefinitionManager` UI.
  - Each question has flags for `is_required`, `evidence_required`, and an optional `weight`.
- **TRL progression workflow (UI)**:
  - From a CTE detail view, users can advance from current TRL `N` to `N+1` by:
    - Fetching TRL questions for the target level.
    - Answering required questions and providing evidence (text + optional file upload).
    - Submitting responses, then calling the backend to validate and mark the assessment as approved.
  - Successful progression updates the CTE’s effective TRL and the project’s rolled-up TRL.
- **Future IRL/MRL/SRL integration**:
  - Models and relationships for `CTEIRLAssessment`, `CTEMRLAssessment`, and `CTESRLAssessment` are already present.
  - Additional engines/routes can follow the TRL pattern to compute and aggregate IRL/MRL/SRL once business rules are finalized.

---

## API Overview (Selected)

All routes are rooted under `/api` in production (depending on your deployment proxy).

- **Authentication**
  - `POST /api/auth/login` – Login with username/password and receive JWT tokens
  - `POST /api/auth/refresh` – Refresh access token
  - `GET /api/auth/me` – Get current user profile and roles

- **Projects**
  - `GET /api/projects` – List projects accessible to current user (RBAC and org-unit aware)
  - `POST /api/projects` – Create project (Manager or above)
  - `GET /api/projects/{id}` – Get project (includes org units, members, current/target TRL, overrides)
  - `PATCH /api/projects/{id}` – Update project metadata and org units
  - `POST /api/projects/{id}/members` – Add project members
  - `DELETE /api/projects/{id}/members/{member_id}` – Remove project members
  - `POST /api/projects/{id}/trl-override` – Override project TRL (Manager/SuperAdmin)

- **CTEs**
  - `GET /api/ctes/projects/{project_id}/ctes` – List CTEs for a project
  - `POST /api/ctes/projects/{project_id}/ctes` – Create CTE (with optional target TRL)
  - `GET /api/ctes/{id}` – Get CTE details

- **TRL Assessments**
  - `GET /api/trl/ctes/{id}/trl-assessments` – List TRL assessments for a CTE
  - `POST /api/trl/ctes/{id}/trl-assessments/{level}` – Start a new TRL assessment at given level
  - `GET /api/trl/ctes/{id}/trl-assessments/{level}/questions` – Get configured questions for a TRL level
  - `POST /api/trl/ctes/{id}/trl-assessments/{level}/responses` – Submit/update response for a question
  - `POST /api/trl/ctes/{id}/trl-assessments/{level}/submit` – Submit assessment for approval (where approval workflow is used)
  - `GET /api/trl/ctes/{id}/current-trl` – Get computed current TRL for a CTE
  - `POST /api/trl/ctes/{id}/advance-trl` – Validate required responses/evidence and mark level as approved

- **Admin – TRL Definitions & Workflow**
  - `GET /api/admin/trl-definitions` – List active TRL definitions (SuperAdmin)
  - `POST /api/admin/trl-definitions` – Create TRL definition
  - `PATCH /api/admin/trl-definitions/{id}` – Update TRL definition (except level)
  - `DELETE /api/admin/trl-definitions/{id}` – Delete TRL definition
  - `POST /api/admin/trl-definitions/upload` – Bulk import TRL definitions/questions from Excel
  - `POST /api/admin/trl-questions` – Create TRL question
  - `PATCH /api/admin/trl-questions/{id}` – Update TRL question
  - `DELETE /api/admin/trl-questions/{id}` – Delete TRL question
  - `GET /api/admin/workflow-config` / `POST /api/admin/workflow-config` – Manage approval workflow configuration

- **Evidence**
  - `POST /api/evidence/upload` – Upload evidence file and link to a TRL response
  - `POST /api/evidence/link` – Add an external evidence link
  - `GET /api/evidence/{id}/download` – Download stored evidence

- **Approvals**
  - `GET /api/approvals/pending` – List pending approvals for current user
  - `POST /api/approvals/{id}/approve` – Approve
  - `POST /api/approvals/{id}/reject` – Reject

---

## Frontend Application Flow

- **Authentication & Layout**
  - `App.jsx` wires React Router with guarded routes via `ProtectedRoute` and global auth via `AuthProvider`.
  - After login, users are redirected into a shell layout (`Layout`) with a sidebar, navbar, and content area.

- **Dashboard**
  - Fetches all accessible projects and computes:
    - Total projects
    - Active CTEs (via `/ctes/projects/{id}/ctes`)
    - Total users (via `/users` or `/users/accessible` depending on role)
  - Displays a project summary list with current and target TRL badges.

- **Projects & CTEs**
  - `ProjectsPage` and `CTEsPage` provide table/grid views, search, and forms for create/edit.
  - Selecting a project or CTE drills into detail views (`ProjectDetail`, `CTEDetail`) showing TRL info and related entities.

- **TRL Progression**
  - `TRLProgression` component handles:
    - Fetching questions for the next TRL level.
    - Capturing answers, notes, and evidence uploads per question.
    - Submitting responses and calling backend to advance TRL.

- **Admin**
  - `AdminPage` hosts tools for TRL configuration and (optionally) other admin functions.
  - `TRLDefinitionManager` lets SuperAdmins manage TRL levels, descriptions, evidence rules, and questions.

---

## Mobile Responsive Design

The frontend is fully responsive with Tailwind CSS:
- **Mobile**: < 640px (base styles)
- **Tablet**: 640px - 768px (`sm:` prefix)
- **Desktop**: 768px - 1024px (`md:` prefix)
- **Large**: 1024px+ (`lg:` prefix)

All components adapt their layout, visibility, and interactions based on screen size.

## Security

- JWT token-based authentication
- Role-based access control (RBAC)
- HTTPS/TLS enforced in production
- File upload validation
- SQL injection prevention (SQLAlchemy ORM)
- XSS prevention (React auto-escaping)

## License

This project is proprietary software for DRDO.
