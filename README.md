# BAHM Operational — ERP pentru Construcții și Eficiență Energetică

Platformă ERP verticală pentru managementul operațional al proiectelor de construcții și reabilitare energetică, dezvoltată de **BAHN S.R.L.**

**Prototip P2** — 103 funcționalități | 276 API endpoints | 77 tabele | 98 ecrane

## Module Disponibile

| Modul | Funcționalități | Descriere |
|-------|----------------|-----------|
| **CRM** | 10 | Contacte, proprietăți, profil energetic, catalog produse |
| **Sales Pipeline** | 26 | Oportunități, Kanban, oferte, contracte, activități |
| **Project Management** | 34 | WBS, Gantt, devize, pontaj, EVM, impact energetic |
| **Resource Management** | 16 | Angajați, echipamente, stocuri, alocări, analiză cost |
| **Business Intelligence** | 4 | Dashboard executiv, KPI-uri, chatbot AI |
| **Sistem** | 13 | Auth, RBAC, audit trail, configuratoare, notificări |

## Quick Start

```bash
# 1. Clone & configure
git clone <repo-url>
cd buildwise
cp .env.example .env

# 2. Start all services (5 containers)
docker-compose up --build

# 3. Access
#    App:      http://localhost
#    API Docs: http://localhost:8000/api/docs
#    Health:   http://localhost:8000/api/v1/health
```

Migrația DB rulează automat la startup. Manual: `docker-compose exec backend alembic upgrade head`

## Deploy Production (Railway)

| Serviciu | URL |
|----------|-----|
| Frontend | `https://buildwise-frontend.up.railway.app` |
| Backend API | `https://buildwise-backend.up.railway.app` |
| Swagger/OpenAPI | `https://buildwise-backend.up.railway.app/api/docs` |
| Health Check | `https://buildwise-backend.up.railway.app/api/v1/health` |

## Credențiale Demo

| Rol | Email | Parolă |
|-----|-------|--------|
| Admin | `admin@buildwise.ro` | `Admin123!` |
| Manager Vânzări | `manager@buildwise.ro` | `Manager123!` |
| Agent Comercial | `agent@buildwise.ro` | `Agent123!` |
| Tehnician | `tech@buildwise.ro` | `Tech123!` |

## Stack Tehnologic

| Layer | Tehnologie |
|-------|-----------|
| **Backend** | FastAPI + Uvicorn (Python 3.11) |
| **ORM** | SQLAlchemy 2.0 async + Alembic |
| **Baza de date** | PostgreSQL 16 |
| **Frontend** | React 19 + TypeScript 5 (Vite 6) |
| **UI** | Ant Design 5 + ProComponents |
| **State** | TanStack Query v5 + Zustand v4 |
| **Auth** | JWT (access 30min + refresh 7d, bcrypt) |
| **Cache** | Redis 7 |
| **Container** | Docker Compose (5 servicii) |
| **Hosting** | Railway (dev) → Hetzner (prod) |

## Funcționalități per Modul

### M1 — CRM (10F)

Managementul contactelor, proprietăților și catalogului de produse.

- Lista contacte cu căutare, filtrare, import/export CSV
- Detalii contact: info, persoane, interacțiuni, proprietăți
- Proprietăți asociate cu profil energetic complet (U-values, HVAC, consum)
- Catalog produse și servicii (categorii, prețuri, unități)

### M2 — Sales Pipeline (26F)

Ciclul complet de vânzare: de la lead la contract semnat.

- Oportunități cu Kanban board (drag & drop între stadii)
- Calificare automată, scoring, probabilitate
- Oferte: builder cu line items, versioning, PDF, aprobare
- Contracte: generare din ofertă, semnare, tracking termen
- Activități: apeluri, vizite tehnice, email-uri, follow-up automat
- Forecast și pipeline analytics

### M3 — Project Management (34F)

Managementul complet al proiectelor de construcții și reabilitare.

- WBS Editor (arbore ierarhic 3 nivele: capitol → subcapitol → articol)
- Gantt Chart cu dependențe și dual-layer (P2)
- Deviz/Budget: estimat vs. real, variante
- Pontaj/Timesheet cu aprobare
- Consum materiale, subcontractori, rapoarte zilnice
- Monitorizare progres: S-Curve, EVM (CPI/SPI)
- Situații de lucrări (SdL Generator)
- Recepție + Punch List + Garanții
- Impact energetic: PRE/POST kWh, CO₂, clase energetice
- Company Capacity Dashboard (F130)

### M4 — Resource Management (16F)

Modulul complet de resurse — specific P2.

- **HR**: Angajați CRUD, competențe, calificări, certificări, salarizare
- **HR Planning**: Calendar angajări/rezilieri, disponibilitate, concedii
- **Materiale**: Stocuri cu alerte minim, aprovizionare, documente (facturi, NIR, bonuri consum)
- **Echipamente**: CRUD, program mentenanță, disponibilitate
- **Alocare**: Resurse pe proiecte (angajați + echipamente + materiale), conflicte
- **Financiar**: Bugete per centru cost, analiză cost plan vs. real
- **Rapoarte**: Utilizare resurse, analiză comparativă

### M5 — Business Intelligence (4F)

Dashboard-uri și KPI-uri pentru decizii informate.

- Dashboard executiv cross-module (CRM + Pipeline + PM + RM)
- KPI Dashboard configurabil cu threshold-uri și trend
- KPI Builder: formule custom, drill-down, roluri
- Chatbot AI integrat: asistență, navigare, sugestii

### M6 — Sistem (13F)

Configurare, securitate și administrare platformă.

- Autentificare JWT (login, register, forgot password)
- RBAC: 4 roluri predefinite, permisiuni granulare
- Audit trail complet (cine, ce, când, valori vechi/noi)
- Căutare globală (Ctrl+K) cross-module
- Notificări in-app + email
- Configurator RM (categorii resurse, unități, praguri stoc)
- GDPR: consimțământ, export date, drept ștergere

## RBAC (Role-Based Access Control)

| Rol | Permisiuni |
|-----|-----------|
| **Admin** | Tot — CRUD complet, setări, audit, management utilizatori |
| **Manager Vânzări** | CRM + Pipeline + Rapoarte + Dashboards (read-only PM) |
| **Agent Comercial** | CRM + Pipeline propriu + Activități |
| **Tehnician** | PM + Execuție + Recepție + Măsurători (read-only CRM) |

## API Endpoints (276 total)

| Modul | Prefix | Endpoints |
|-------|--------|-----------|
| Health | `/api/v1/health` | 1 |
| Auth | `/api/v1/auth` | 5 |
| Users | `/api/v1/users` | 8 |
| System | `/api/v1/system` | 28 |
| CRM | `/api/v1/crm` | 39 |
| Pipeline | `/api/v1/pipeline` | 56 |
| PM | `/api/v1/pm` | 80 |
| RM | `/api/v1/rm` | 37 |
| BI | `/api/v1/bi` | 21 |
| Search | `/api/v1/search` | 1 |

## Baza de Date (77 tabele)

```
CRM:      11 tabele — Contact, Property, EnergyProfile, Product, Document...
Pipeline: 14 tabele — Opportunity, Milestone, Activity, Offer, Contract...
PM:       21 tabele — Project, WBSNode, Task, DevizItem, Timesheet...
RM:       10 tabele — Employee, Equipment, MaterialStock, ResourceAllocation...
BI:        9 tabele — KPIDefinition, Dashboard, ReportDefinition, AIConversation...
System:   16 tabele — Organization, User, Role, AuditLog, FeatureFlag...
```

## Environment Variables

```bash
DATABASE_URL=postgresql+asyncpg://buildwise:buildwise@db:5432/buildwise
REDIS_URL=redis://redis:6379/0
JWT_SECRET_KEY=your-secret-key-min-32-chars
APP_ENV=production
DEFAULT_PROTOTYPE=P2
RESEND_API_KEY=re_xxx
VITE_API_URL=/api/v1
```

## Docker Services

| Service | Image | Port |
|---------|-------|------|
| `db` | postgres:16-alpine | 5432 |
| `redis` | redis:7-alpine | 6379 |
| `backend` | python:3.11-slim | 8000 |
| `frontend` | node:20-alpine | 5173 |
| `nginx` | nginx:alpine | 80 |

## Development Commands

```bash
docker-compose up --build          # Start all
docker-compose logs -f backend     # View logs
docker-compose exec backend alembic revision --autogenerate -m "desc"  # New migration
docker-compose down                # Stop
docker-compose down -v             # Reset DB
```

## Scripts Utilitare

```bash
python scripts/seed_demo_data.py      # Seed date demo (toate modulele)
python scripts/cleanup_duplicates.py   # Curăță proiecte duplicate
python scripts/agent_audit.py          # Audit API complet (6 module + E2E)
```

---

**BAHM Operational v1.0.0** — Dezvoltat de BAHN S.R.L. | 103 funcționalități | 6 module | P2
