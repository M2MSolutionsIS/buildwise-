# BuildWise ERP Platform

Platformă ERP verticală pentru eficiență energetică a clădirilor, dezvoltată de **BAHN S.R.L.**

## Prototipuri

Același codebase servește 3 prototipuri, controlate prin PrototypeSwitcher:

| Prototip | Focus | Funcționalități |
|----------|-------|-----------------|
| **P1 — BuildWise TRL5** | Energie + AI | 82 comune |
| **P2 — BAHM Operational** | Construcții + Resource Management | 82 comune + 21 P2+P3 |
| **P3 — M2M ERP Lite** | SaaS multi-tenant, white-label | 82 comune + 21 P2+P3 + 5 P3 |

## Deploy Production (Railway)

| Serviciu | URL |
|----------|-----|
| Frontend | `https://buildwise-frontend.up.railway.app` |
| Backend API | `https://buildwise-backend.up.railway.app` |
| Swagger/OpenAPI | `https://buildwise-backend.up.railway.app/api/docs` |
| ReDoc | `https://buildwise-backend.up.railway.app/api/redoc` |
| OpenAPI JSON | `https://buildwise-backend.up.railway.app/api/openapi.json` |
| Health Check | `https://buildwise-backend.up.railway.app/api/v1/health` |

## Credențiale Demo

| Rol | Email | Parolă |
|-----|-------|--------|
| Admin | `admin@buildwise.ro` | `Admin123!` |
| Manager Vânzări | `manager@buildwise.ro` | `Manager123!` |
| Agent Comercial | `agent@buildwise.ro` | `Agent123!` |
| Tehnician | `tech@buildwise.ro` | `Tech123!` |

> Conturile demo sunt create automat la prima migrare. Parolele sunt hash-uite cu bcrypt.

## Quick Start (Local Development)

```bash
# 1. Clone & configure
git clone <repo-url>
cd buildwise
cp .env.example .env

# 2. Start all services (5 containers)
docker-compose up --build

# 3. DB migration runs automatically at startup
# Manual: docker-compose exec backend alembic upgrade head
```

## Access Points (Local)

| Service | URL | Description |
|---------|-----|-------------|
| App (nginx) | http://localhost | Frontend via reverse proxy |
| API Docs | http://localhost:8000/api/docs | Swagger UI — 276 endpoints |
| ReDoc | http://localhost:8000/api/redoc | API documentation alternativă |
| Frontend | http://localhost:5173 | Vite dev server (HMR) |
| Health | http://localhost:8000/api/v1/health | Backend status + DB + Redis |

## Stack Tehnologic

| Layer | Tehnologie | Versiune |
|-------|-----------|----------|
| **Backend** | FastAPI + Uvicorn | Python 3.11 |
| **ORM** | SQLAlchemy 2.0 (async) + Alembic | PostgreSQL 16 |
| **Frontend** | React 19 + TypeScript 5 | Vite 6 |
| **UI** | Ant Design 5 + ProComponents | Dark theme |
| **State** | TanStack Query (server) + Zustand (UI) | v5 / v4 |
| **Auth** | JWT (access 30min + refresh 7d) | bcrypt |
| **Cache** | Redis 7 | Sessions + async tasks |
| **Container** | Docker Compose | 5 services |
| **Hosting** | Railway (dev) → Hetzner (prod) | Auto-deploy |

## Module și Funcționalități (108 total)

### M1 — CRM (10 funcționalități)

| Cod | Funcționalitate | Ecran |
|-----|----------------|-------|
| F001 | Lista contacte cu căutare și filtrare | E-002 |
| F002 | Creare contact (validare duplicat) | E-003 |
| F003 | Detalii contact (tabs: info, persoane, interacțiuni) | E-003 |
| F004 | Persoane de contact multiple per companie | E-003.1 |
| F005 | Istoric interacțiuni (timeline) | E-003.2 |
| F006 | Proprietăți asociate contactului | E-003.3 |
| F007 | Import contacte din CSV/Excel | E-002.M1 |
| F008 | Export contacte | E-002 |
| F009 | Merge contacte duplicate | E-002.M2 |
| F017 | Catalog produse și servicii (CRUD) | E-004 |

### M2 — Sales Pipeline (26 funcționalități)

| Cod | Funcționalitate | Ecran |
|-----|----------------|-------|
| F018–F025 | Oportunități: creare, editare, Kanban, calificare | E-005, E-006 |
| F026–F031 | Oferte: builder, versioning, PDF, aprobare | E-007, E-008 |
| F032–F037 | Contracte: generare, semnare, tracking | E-009 |
| F038–F043 | Activități, follow-up, calendar, dashboard | E-010, E-011 |

### M3 — Project Management (34 funcționalități)

| Cod | Funcționalitate | Ecran |
|-----|----------------|-------|
| F063 | Lista proiecte cu filtrare | E-014 |
| F069 | WBS Editor (arbore ierarhic 3 nivele) | E-015 |
| F070 | Gantt Chart (drag & drop, dependențe) | E-016 |
| F071 | Deviz/Budget Editor (estimat vs real) | E-017 |
| F072–F073 | Timesheet / Pontaj | E-018 |
| F074 | Consum materiale | E-019 |
| F075 | Subcontractori | E-020 |
| F077 | Rapoarte zilnice | E-021 |
| F078 | Monitorizare progres (S-Curve, EVM) | E-022 |
| F079 | Situații de lucrări (SdL Generator) | E-023 |
| F080 | Registru riscuri | E-024 |
| F081–F082 | Recepție + Punch List | E-025 |
| F086 | Garanții post-recepție | E-026 |
| F088 | Impact energetic | E-030 |

### M4 — Resource Management (16F, doar P2+P3)

| Cod | Funcționalitate | Ecran |
|-----|----------------|-------|
| F096–F100 | Angajați: CRUD, disponibilitate, planificare HR | E-031 |
| F101–F104 | Echipamente: CRUD, mentenanță | E-032 |
| F105–F108 | Materiale: stoc, aprovizionare | E-033 |
| F109–F111 | Alocare resurse, buget, analiză cost | E-034 |

### M5 — Business Intelligence (5F)

| Cod | Funcționalitate | Ecran |
|-----|----------------|-------|
| F112 | Dashboard executiv cu KPI-uri | E-035 |
| F113 | KPI Dashboard configurabil | E-036 |
| F114 | KPI Builder | E-037 |
| F115 | Reports Builder (doar P3) | E-038 |
| F116 | AI Assistant + ML Forecast | E-039 |

### M6 — System (17F)

| Cod | Funcționalitate | Ecran |
|-----|----------------|-------|
| F040 | Configurator Pipeline | E-040 |
| F136 | Multi-tenant izolat (doar P3) | — |
| F137 | White-label branding | E-041 |
| F138 | i18n bilingv (RO + EN) | — |
| F155 | Auth (JWT login/register) | E-001 |
| F156 | User management + RBAC | E-042 |
| F157 | Căutare globală (Ctrl+K) | C-001 |
| F158 | App shell: sidebar, header, breadcrumbs | E-027 |
| F160 | Tenant setup wizard (doar P3) | E-043 |

## API Documentation (276 endpoints)

Swagger UI disponibil la `/api/docs` — toate endpoint-urile sunt documentate cu:
- OpenAPI 3.1 tags per modul
- Request/Response schemas (Pydantic v2)
- Authentication (JWT Bearer token)
- Example payloads

| Modul | Prefix | Endpoints | Tag |
|-------|--------|-----------|-----|
| Health | `/api/v1/health` | 1 | Health |
| Auth | `/api/v1/auth` | 5 | Auth |
| Users | `/api/v1/users` | 8 | Users |
| System | `/api/v1/system` | 28 | System |
| CRM | `/api/v1/crm` | 39 | CRM |
| Pipeline | `/api/v1/pipeline` | 56 | Sales Pipeline |
| PM | `/api/v1/pm` | 80 | Project Management |
| RM | `/api/v1/rm` | 37 | Resource Management |
| BI | `/api/v1/bi` | 21 | Business Intelligence |
| Search | `/api/v1/search` | 1 | Search |

## Ecrane Frontend (98 ecrane)

| Categoria | Ecrane | Status |
|-----------|--------|--------|
| CRM | E-002, E-003, E-003.1–3.5, E-004 | Implementate |
| Pipeline | E-005–E-013 | Implementate |
| PM | E-014–E-030 | Implementate |
| RM | E-031–E-034 | Implementate |
| BI | E-035–E-039 | Implementate |
| System | E-040–E-043, E-027 | Implementate |
| Dashboard | E-001 (Home) | Implementat |
| Global | C-001–C-005 | Integrate |

## Componente Globale (C-001 — C-005)

| ID | Component | Utilizare |
|----|-----------|-----------|
| C-001 | ToastNotifications | Feedback utilizator (success/error/warning) |
| C-002 | EmptyState | State vid pentru liste/tabele fără date |
| C-003 | SkeletonLoaders | Loading placeholders (cards, rows, KPI, page) |
| C-004 | PDFPreviewModal | Preview documente PDF (oferte, contracte, SdL) |
| C-005 | ConfirmDelete | Dialog confirmare ștergere cu danger styling |

## RBAC (Role-Based Access Control)

| Rol | Permisiuni |
|-----|-----------|
| **Admin** | Tot — CRUD complet, setări, audit, management utilizatori |
| **Manager Vânzări** | CRM + Pipeline + Rapoarte + Dashboards (read-only PM) |
| **Agent Comercial** | CRM + Pipeline propriu + Activități (nu vede alte pipeline-uri) |
| **Tehnician** | PM + Execuție + Recepție + Măsurători (read-only CRM) |

## Multi-Tenant Isolation (P3)

- Fiecare query include `WHERE organization_id = :org_id`
- Middleware RBAC verifică `org_id` pe fiecare request
- Date complet izolate între organizații
- Tenant setup wizard la prima autentificare (F160)
- White-label: logo, culori, nume custom per organizație

## Baza de Date (77 tabele, 6 module)

```
CRM:      11 tabele  — Contact, Property, EnergyProfile, Product, Document...
Pipeline: 14 tabele  — Opportunity, Milestone, Activity, Offer, Contract...
PM:       21 tabele  — Project, WBSNode, Task, DevizItem, Timesheet...
RM:       10 tabele  — Employee, Equipment, MaterialStock, ResourceAllocation...
BI:        9 tabele  — KPIDefinition, Dashboard, ReportDefinition, AIConversation...
System:   16 tabele  — Organization, User, Role, AuditLog, FeatureFlag...
```

Migrații gestionate cu Alembic — rulează automat la startup.

## Docker Services

| Service | Image | Port | Health Check |
|---------|-------|------|-------------|
| `db` | postgres:16-alpine | 5432 | `pg_isready` |
| `redis` | redis:7-alpine | 6379 | `redis-cli ping` |
| `backend` | python:3.11-slim | 8000 | `/api/v1/health` |
| `frontend` | node:20-alpine | 5173 | — |
| `nginx` | nginx:alpine | 80 | depends on all |

## Environment Variables

```bash
# Database
DATABASE_URL=postgresql+asyncpg://buildwise:buildwise@db:5432/buildwise

# Redis
REDIS_URL=redis://redis:6379/0

# JWT Auth
JWT_SECRET_KEY=your-secret-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# App
APP_ENV=production          # development | staging | production
APP_DEBUG=false             # true enables extra logging
DEFAULT_PROTOTYPE=P1        # P1 | P2 | P3

# Email
RESEND_API_KEY=re_xxx

# Frontend
VITE_API_URL=/api/v1
```

## Development Commands

```bash
# Start all services
docker-compose up --build

# Rebuild single service
docker-compose up --build backend

# View logs
docker-compose logs -f backend

# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "description"

# Run migration
docker-compose exec backend alembic upgrade head

# Stop everything
docker-compose down

# Reset DB (caution: destroys data)
docker-compose down -v
```

## Build Optimizat (Production)

Frontend build cu Vite + Terser:
- Code splitting: vendor-react, vendor-antd, vendor-query, vendor-utils
- Tree shaking + dead code elimination
- Console/debugger drops in production
- Source maps disabled

```bash
cd frontend && npm run build
# Output: dist/ (~800KB gzipped)
```

## Documentație de Referință

> **Sursa de adevăr**: `Centralizator_M2M_ERP_Lite.md` — 108 funcționalități cu F-codes

| Document | Conținut |
|----------|---------|
| `Centralizator_M2M_ERP_Lite.md` | 108 funcționalități, F-codes, P1/P2/P3 mapping |
| `Wireframe_Masterplan.md` | 98 ecrane cu priorități și complexitate |
| `Wireframes_Faza0.md` — `Faza6.md` | Wireframes detaliate per fază |
| `FlowDiagrams_*.md` | Fluxuri utilizator per prototip |
| `BuildWise_Plan_Dezvoltare_Complet.md` | 35 task-uri, 7 faze, plan complet |
| `CLAUDE.md` | Convenții dezvoltare și context tehnic |

---

**BuildWise ERP v1.0.0** — Dezvoltat de BAHN S.R.L. | 108 funcționalități | 276 API endpoints | 77 tabele | 98 ecrane
