# CLAUDE.md — UNS Rirekisho Pro v26.1.4

## Project Overview

**UNS Rirekisho Pro** is a modern Human Resource Dispatch Management System for ユニバーサル企画株式会社 (Universal Kikaku Co., Ltd.), a Japanese staffing agency specializing in foreign worker dispatch (人材派遣) and contract work (請負).

### Business Domain
- **Candidate Registration**: Register applicants with 履歴書 (CV/Resume)
- **Application Workflow**: Present candidates to 派遣先 (client companies)
- **入社連絡票**: Process joining notices for approved candidates
- **Employee Management**: Manage 派遣社員 (dispatch) and 請負社員 (contract) workers
- **Housing Management**: Track 社宅 (company housing) assignments

## Tech Stack

### Backend (`/backend`)
- **Framework**: FastAPI 0.115+ (Python 3.11+)
- **Database**: PostgreSQL 16 with SQLAlchemy 2.0 (async)
- **Migrations**: Alembic
- **Authentication**: JWT with role-based access control
- **Validation**: Pydantic v2

### Frontend (`/frontend`)
- **Framework**: Next.js 15 (App Router)
- **UI**: React 19 + Tailwind CSS 4 + shadcn/ui
- **State**: TanStack Query v5 + Zustand
- **Tables**: AG Grid or TanStack Table
- **Forms**: React Hook Form + Zod

### Infrastructure
- **Container**: Docker + Docker Compose
- **Storage**: Supabase Storage / AWS S3
- **Cache**: Redis (optional)

## Development Commands

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev

# Docker (full stack)
docker compose up -d
```

## Key Business Rules

### Entity Flow (STRICT)
```
Candidate → Application → 入社連絡票 → Employee
   ↓           ↓              ↓           ↓
履歴書DB    派遣先結果     承認プロセス   社員台帳
```

### Critical Rules
1. **Never delete candidates** - All records are historical
2. **Approval required** - 入社連絡票 must be approved before creating employee
3. **Separate employee types**:
   - 派遣社員 (haken_assignments table)
   - 請負社員 (ukeoi_assignments table)
4. **Housing tracking** - 社宅/自宅/賃貸 status required

### Data Source Mapping
| Legacy Source | New Table |
|---------------|-----------|
| Access T_履歴書 | candidates |
| Excel DBStaffX | employees |
| Excel DBGenzaiX | haken_assignments |
| Excel DBUkeoiX | ukeoi_assignments |

## API Structure

```
/api/auth/*           - Authentication (login, refresh, logout)
/api/candidates/*     - Candidate CRUD + documents
/api/applications/*   - Application workflow
/api/joining-notices/*- 入社連絡票 management
/api/employees/*      - Employee master data
/api/haken/*          - 派遣社員 assignments
/api/ukeoi/*          - 請負社員 assignments
/api/apartments/*     - 社宅 management
/api/companies/*      - 派遣先 companies
```

## Database Schema Overview

### Core Tables
- `users` - System users with roles
- `candidates` - Applicant/CV records (履歴書)
- `candidate_documents` - Files (photos, PDFs)
- `applications` - Presentation to 派遣先
- `joining_notices` - 入社連絡票
- `employees` - Master employee records
- `haken_assignments` - 派遣社員 work details
- `ukeoi_assignments` - 請負社員 work details
- `company_apartments` - 社宅 properties
- `client_companies` - 派遣先/請負先

## Coding Conventions

### Language Policy
- **Code/Comments**: English
- **User Interface**: Japanese (primary), Spanish (secondary)
- **Domain Data**: Japanese field names preserved

### Protected Files (DO NOT MODIFY without confirmation)
- `docker-compose.yml`
- `.env` / `.env.local`
- `alembic/versions/*.py` (existing migrations)

### Naming Conventions
- **Python**: snake_case for functions/variables
- **TypeScript**: camelCase for functions, PascalCase for components
- **Database**: snake_case for tables/columns
- **Japanese fields**: Use exact column names from Excel/Access

## Security Notes

- Store sensitive data (API keys) in environment variables
- Never commit `.env` files
- All API routes require authentication except `/api/auth/login`
- Rate limiting enabled on all endpoints
