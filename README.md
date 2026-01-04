# UNS Rirekisho Pro v26.1.4

人材派遣管理システム for ユニバーサル企画株式会社 (Universal Kikaku Co., Ltd.)

## Overview

UNS Rirekisho Pro is a comprehensive Human Resource Dispatch Management System designed for Japanese staffing agencies. It manages the full lifecycle from candidate registration (履歴書/Rirekisho) to employee dispatch (派遣) and contract work (請負).

## Features

- **Candidate Management (候補者管理)**
  - Register and manage 履歴書 (CV/Resume)
  - Upload documents (photos, residence cards, licenses)
  - Track candidate status through workflow

- **Application Workflow (申請ワークフロー)**
  - Present candidates to 派遣先 (client companies)
  - Record acceptance/rejection results
  - Full history tracking

- **入社連絡票 (Joining Notices)**
  - Create joining notifications for accepted candidates
  - Multi-level approval process
  - Automatic employee creation upon approval

- **Employee Management (社員管理)**
  - Separate views for 派遣社員 (dispatch) and 請負社員 (contract)
  - Complete tracking of financial, insurance, and visa information
  - Housing (社宅) management

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 16
- **ORM**: SQLAlchemy 2.0 (async)
- **Auth**: JWT with role-based access control

### Frontend
- **Framework**: Next.js 15 (React 19)
- **Styling**: Tailwind CSS 4
- **State**: TanStack Query + Zustand
- **UI Components**: shadcn/ui

### Infrastructure
- **Container**: Docker + Docker Compose
- **Cache**: Redis

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 20+ (for local development)
- Python 3.11+ (for local development)

### Using Docker (Recommended)

```bash
# Clone the repository
cd UNSRireki-Prov26.1.4

# Copy environment file
cp .env.example .env

# Edit .env with your settings
# Change SECRET_KEY and DB_PASSWORD!

# Start all services
docker compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/api/docs
# Adminer (DB): http://localhost:8080 (dev profile only)
```

### Local Development

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (in another terminal)
cd frontend
npm install
npm run dev
```

## Project Structure

```
UNSRireki-Prov26.1.4/
├── backend/
│   ├── app/
│   │   ├── api/           # API endpoints
│   │   ├── core/          # Config, security, database
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   └── services/      # Business logic
│   ├── alembic/           # Database migrations
│   └── scripts/           # Migration scripts
├── frontend/
│   ├── app/               # Next.js pages
│   ├── components/        # React components
│   ├── lib/               # Utilities, API client
│   └── types/             # TypeScript types
├── docs/                  # Documentation
├── docker-compose.yml
└── CLAUDE.md              # AI assistant context
```

## Data Migration

### From Access Database (T_履歴書)

```bash
cd backend
python scripts/migrate_access.py \
  --access-db "path/to/database.accdb" \
  --output-dir "./exports" \
  --extract-attachments
```

### From Excel (社員台帳)

```bash
cd backend
python scripts/migrate_excel.py \
  --excel-file "path/to/社員台帳.xlsm" \
  --output-dir "./exports"
```

## API Documentation

Interactive API documentation is available at:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## User Roles

| Role | Description | Permissions |
|------|-------------|-------------|
| super_admin | Full system access | All |
| admin | Administrative access | All except system config |
| manager | Can approve 入社連絡票 | CRUD + approvals |
| staff | Office personnel | CRUD candidates/applications |
| viewer | Read-only access | View only |

## Business Flow

```
Candidate Registration
        ↓
Application to 派遣先
        ↓
    Accept/Reject
        ↓
入社連絡票 Creation (if accepted)
        ↓
Manager Approval
        ↓
Employee Creation
  ├── 派遣社員 (Dispatch)
  └── 請負社員 (Contract)
```

## Company Information

**ユニバーサル企画株式会社 (Universal Kikaku Co., Ltd.)**
〒461-0025 愛知県名古屋市東区徳川2丁目18番18号
TEL: 052-938-8840 / FAX: 052-938-8841

## License

Proprietary - All rights reserved
