# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**UNS Rirekisho Pro v26.1.4** is a Human Resource Dispatch Management System for ユニバーサル企画株式会社 (Universal Kikaku Co., Ltd.), a Japanese staffing agency specializing in foreign worker dispatch (人材派遣) and contract work (請負).

## Development Commands

```bash
# Backend (FastAPI)
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (Next.js 15)
cd frontend
npm install
npm run dev          # Development server on port 3000
npm run build        # Production build
npm run lint         # ESLint
npm run typecheck    # TypeScript type checking

# Docker (full stack)
docker compose up -d
docker compose --profile dev up -d  # Include Adminer for DB access

# Database setup (after backend is running)
cd backend
python scripts/create_admin.py   # Create initial admin user (admin/Admin@123!)
python scripts/seed_data.py      # Optional: seed sample data

# Run backend tests
cd backend
pytest
pytest tests/test_candidates.py -v  # Single test file
pytest -k "test_login" -v           # Run tests matching pattern

# Alembic migrations
cd backend
alembic upgrade head              # Apply migrations
alembic revision --autogenerate -m "description"  # Create new migration
```

## Architecture

### Backend (`/backend`)
```
app/
├── main.py           # FastAPI entry point, router registration
├── api/              # API route handlers (auth, candidates, employees, etc.)
├── core/
│   ├── config.py     # Settings via pydantic-settings (from .env)
│   ├── database.py   # Async SQLAlchemy engine & session
│   └── security.py   # JWT handling, password hashing
├── models/models.py  # SQLAlchemy ORM models (all in one file)
├── schemas/          # Pydantic request/response schemas
└── services/         # Business logic layer
scripts/              # Admin scripts (create_admin, seed_data, migrations)
alembic/              # Database migrations
```

### Frontend (`/frontend`)
```
app/
├── layout.tsx        # Root layout with providers
├── providers.tsx     # TanStack Query + context providers
├── login/page.tsx    # Login page (unauthenticated)
└── (dashboard)/      # Protected route group
    ├── layout.tsx    # Dashboard shell with sidebar
    ├── dashboard/    # Main dashboard with charts
    ├── candidates/   # Candidate list & detail [id]
    ├── applications/ # Application management
    ├── joining-notices/  # 入社連絡票 workflow
    └── employees/    # haken/, ukeoi/, [id] detail
components/
├── ui/               # shadcn/ui primitives
├── layout/           # Sidebar navigation
└── dashboard/        # Chart components (Recharts)
lib/
├── api.ts            # Axios client with JWT interceptors
├── auth.ts           # Auth state management
└── utils.ts          # Utility functions (cn, etc.)
types/index.ts        # TypeScript type definitions
```

### Key Data Flow
```
Candidate → Application → 入社連絡票 → Employee
(履歴書)    (派遣先提出)   (承認必須)    (派遣/請負)
```

## Business Rules

1. **Never delete candidates** - All records must be preserved for historical tracking
2. **入社連絡票 approval required** - Joining notice must be approved before employee creation
3. **Separate employee types**: 派遣社員 uses `haken_assignments`, 請負社員 uses `ukeoi_assignments`
4. **Housing types**: 社宅 (company), 自宅 (own), 賃貸 (rental)

## Coding Conventions

### Language Policy
- **Code/Comments**: English
- **UI Text**: Japanese (primary), Spanish (secondary)
- **Database fields**: Preserve exact Japanese column names from legacy Access/Excel

### Naming
- **Python**: `snake_case` for functions/variables, match legacy field names
- **TypeScript**: `camelCase` for functions, `PascalCase` for components
- **Database**: `snake_case` for tables/columns

### Protected Files (confirm before modifying)
- `docker-compose.yml`
- `.env` / `.env.local`
- `alembic/versions/*.py` (existing migrations)

## API Endpoints

| Prefix | Purpose |
|--------|---------|
| `/api/auth` | Login, logout, refresh, me |
| `/api/candidates` | CRUD + document upload |
| `/api/applications` | Create + record result |
| `/api/joining-notices` | Create, submit, approve/reject |
| `/api/employees` | List (haken/ukeoi), update, terminate |
| `/api/companies` | Client company master |
| `/api/apartments` | Company housing (社宅) |
| `/api/dashboard` | Stats and recent activity |

## User Roles

| Role | Can Approve 入社連絡票 |
|------|----------------------|
| `super_admin` | Yes |
| `admin` | Yes |
| `manager` | Yes |
| `staff` | No |
| `viewer` | No (read-only) |

## Environment Variables

Required in `.env`:
- `DATABASE_URL` - PostgreSQL connection (async: `postgresql+asyncpg://...`)
- `SECRET_KEY` - JWT signing key (min 32 chars, auto-generated in dev)
- `FRONTEND_URL` - For CORS in production

## Legacy Data Migration

```bash
# From Access database (T_履歴書)
python scripts/migrate_access.py --access-db "path/to/db.accdb"

# From Excel (社員台帳)
python scripts/migrate_excel.py --excel-file "path/to/社員台帳.xlsm"
```
