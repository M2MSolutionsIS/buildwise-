# BuildWise ERP Platform

Platformă ERP verticală pentru eficiență energetică a clădirilor, dezvoltată de BAHN S.R.L.

3 prototipuri din același codebase:
- **P1 — BuildWise TRL5**: Energie + AI
- **P2 — BAHM Operational**: Construcții + Resource Management
- **P3 — M2M ERP Lite**: SaaS generic, multi-tenant, white-label

## Quick Start

```bash
# 1. Clone & configure
git clone <repo-url>
cd buildwise
cp .env.example .env        # Edit .env if needed

# 2. Start all services
docker-compose up --build

# 3. Run database migration
docker-compose exec backend alembic upgrade head
```

## Access Points

| Service | URL | Description |
|---------|-----|-------------|
| App (nginx) | http://localhost | Frontend via reverse proxy |
| API Docs | http://localhost:8000/api/docs | Swagger UI |
| Frontend (direct) | http://localhost:5173 | Vite dev server |
| Health Check | http://localhost:8000/api/v1/health | Backend status |

## Services

| Service | Technology | Port |
|---------|-----------|------|
| `db` | PostgreSQL 16 | 5432 |
| `redis` | Redis 7 | 6379 |
| `backend` | FastAPI (Python 3.11) | 8000 |
| `frontend` | React 19 + Vite | 5173 |
| `nginx` | Nginx (reverse proxy) | 80 |

## Stack

- **Backend**: FastAPI, SQLAlchemy 2.0 (async), Alembic, Pydantic v2
- **Frontend**: React 19, TypeScript 5, Ant Design 5, TanStack Query, Zustand
- **Database**: PostgreSQL 16 (77 tables, 6 modules)
- **Cache**: Redis 7
- **Auth**: JWT (access + refresh tokens)
- **Container**: Docker Compose

## Project Structure

```
buildwise/
├── docker-compose.yml         # 5 services: db, redis, backend, frontend, nginx
├── .env.example               # All environment variables
├── backend/                   # FastAPI + SQLAlchemy
│   ├── app/
│   │   ├── main.py            # App entry point
│   │   ├── config.py          # pydantic-settings
│   │   ├── database.py        # Async SQLAlchemy engine
│   │   ├── core/              # Shared: base models, auth, RBAC, audit
│   │   ├── crm/               # M1: Contacts, Properties, Products (10F)
│   │   ├── pipeline/          # M2: Opportunities, Offers, Contracts (26F)
│   │   ├── pm/                # M3: Projects, WBS, Gantt, Budget (34F)
│   │   ├── rm/                # M4: HR, Materials, Allocation (16F, P2+P3)
│   │   ├── bi/                # M5: KPIs, Dashboards, Reports (5F)
│   │   └── system/            # M6: Users, Roles, Settings (17F)
│   └── alembic/               # DB migrations
├── frontend/                  # React 19 + Vite
│   └── src/
│       ├── modules/           # Mirror backend: crm, pipeline, pm, rm, bi, system
│       ├── layouts/           # App shell
│       ├── services/          # API client (axios)
│       └── types/             # TypeScript interfaces
└── nginx/
    └── nginx.conf             # /api → backend, / → frontend
```

## Development

```bash
# Rebuild a single service
docker-compose up --build backend

# View logs
docker-compose logs -f backend

# Run alembic migration
docker-compose exec backend alembic upgrade head

# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "description"

# Stop everything
docker-compose down

# Stop and remove volumes (reset DB)
docker-compose down -v
```

## Documentation

> **Source of truth**: `Centralizator_M2M_ERP_Lite.md` — 108 functionalities with F-codes

| Document | Content |
|----------|---------|
| `Centralizator_M2M_ERP_Lite.md` | 108 functionalities, F-codes, P1/P2/P3 mapping |
| `Wireframe_Masterplan.md` | 98 screens with priorities |
| `Wireframes_Faza0.md` — `Faza6.md` | Detailed wireframes |
| `FlowDiagrams_*.md` | User flows per prototype |
| `CLAUDE.md` | Development conventions and context |
