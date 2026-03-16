# BuildWise — Context pentru Claude Code

## Ce este BuildWise

BuildWise este o platformă ERP verticală pentru eficiență energetică a clădirilor, dezvoltată de BAHN S.R.L. Platforma servește 3 prototipuri din același codebase:

- **P1 — BuildWise TRL5**: Focus pe energie + AI, pentru piața de eficiență energetică
- **P2 — BAHM Operational**: Focus pe construcții, include Resource Management complet
- **P3 — M2M ERP Lite**: Versiune SaaS generică, multi-tenant, white-label

## Cifre cheie

- **108 funcționalități** totale (82 comune = 76%, 21 doar P2+P3, 5 doar P3)
- **98 ecrane** documentate cu wireframes (71 comune + 16 P2 + 1 P3 + 10 P1)
- **6 module**: CRM (10F), Sales Pipeline (26F), PM (34F), RM (16F), BI (5F), Sistem (17F)
- **54 navigări** documentate între ecrane
- **F-codes**: Fiecare funcționalitate are un cod unic (F001-F160) trasabil între documente

## Stack Tehnologic

| Componentă | Tehnologie | Note |
|------------|-----------|------|
| Backend | FastAPI (Python 3.11+) | Async, Pydantic v2, OpenAPI auto |
| Frontend | React 19 + TypeScript 5 | Vite build, strict mode |
| UI Library | Ant Design 5 + ProComponents | ProTable, ProForm, ProLayout |
| Baza de date | PostgreSQL 16 | JSON fields pt. date flexibile |
| ORM | SQLAlchemy 2.0 + Alembic | Async sessions |
| Cache | Redis 7 | Sesiuni, cache, taskuri async |
| Auth | JWT (access + refresh) | bcrypt pentru parole |
| Email | Resend | Notificări, follow-up |
| Container | Docker Compose | PostgreSQL + Redis + FastAPI + Nginx |
| Hosting | Railway (dev) → Hetzner (prod) | Deploy automat din GitHub |

## Structura Proiectului

```
buildwise/
├── CLAUDE.md                    # Acest fișier
├── README.md                    # Instrucțiuni quick-start
├── docker-compose.yml           # Toate serviciile: db, redis, backend, frontend, nginx
├── .env.example                 # Template variabile de mediu
├── .gitignore
│
├── backend/
│   ├── Dockerfile               # Python 3.11-slim + uvicorn
│   ├── requirements.txt         # FastAPI, SQLAlchemy, Alembic, etc.
│   ├── alembic.ini
│   ├── alembic/
│   │   ├── env.py               # Async Alembic config
│   │   ├── script.py.mako
│   │   └── versions/
│   │       └── 0001_initial_schema_all_6_modules.py  # 77 tabele
│   ├── app/
│   │   ├── main.py              # FastAPI app entry + lifespan
│   │   ├── config.py            # Settings (pydantic-settings)
│   │   ├── database.py          # SQLAlchemy async engine + sessions
│   │   ├── core/
│   │   │   ├── base_model.py    # Mixins: Timestamp, SoftDelete, Org, PKMixin, PrototypeFlags
│   │   │   ├── auth.py          # JWT, login, register (TBD)
│   │   │   ├── rbac.py          # Roluri + permisiuni middleware (TBD)
│   │   │   ├── audit.py         # Audit trail automat (TBD)
│   │   │   └── deps.py          # Dependențe comune: get_db, get_user (TBD)
│   │   ├── crm/                 # M1: Contacte, Proprietăți, Oferte — 11 tabele
│   │   │   ├── models.py        # ✅ Contact, Property, EnergyProfile, Product, Document…
│   │   │   ├── schemas.py       # (TBD)
│   │   │   ├── router.py        # (TBD)
│   │   │   └── service.py       # (TBD)
│   │   ├── pipeline/            # M2: Oportunități, Activități, Forecast — 14 tabele
│   │   │   └── models.py        # ✅ Opportunity, Milestone, Activity, Offer, Contract…
│   │   ├── pm/                  # M3: Proiecte, WBS, Gantt, Devize — 21 tabele
│   │   │   └── models.py        # ✅ Project, WBSNode, Task, DevizItem, Timesheet…
│   │   ├── rm/                  # M4: HR, Materiale, Stocuri, Alocare (P2+P3) — 10 tabele
│   │   │   └── models.py        # ✅ Employee, Equipment, MaterialStock, ResourceAllocation…
│   │   ├── bi/                  # M5: Dashboards, Reports, KPI — 9 tabele
│   │   │   └── models.py        # ✅ KPIDefinition, Dashboard, ReportDefinition, AIConversation…
│   │   └── system/              # M6: Settings, Configuratoare, Multi-tenant — 16 tabele
│   │       └── models.py        # ✅ Organization, User, Role, AuditLog, FeatureFlag…
│   └── tests/
│
├── frontend/
│   ├── Dockerfile               # Node 20-alpine + npm dev
│   ├── Dockerfile.prod          # Multi-stage build → nginx
│   ├── package.json             # React 19, Ant Design 5, TanStack Query, Zustand
│   ├── tsconfig.json
│   ├── vite.config.ts           # Alias @/, proxy /api → backend
│   ├── index.html
│   └── src/
│       ├── main.tsx             # ReactDOM entry
│       ├── App.tsx              # Router + ConfigProvider + QueryClient
│       ├── vite-env.d.ts
│       ├── routes/              # (TBD) React Router lazy routes
│       ├── layouts/
│       │   └── AppLayout.tsx    # ✅ Sidebar + Header + Content (E-027 App Shell)
│       ├── modules/
│       │   ├── crm/             # pages/, components/, hooks/, services/
│       │   ├── pipeline/        # pages/, components/, hooks/, services/
│       │   ├── pm/              # pages/, components/, hooks/, services/
│       │   ├── rm/              # pages/, components/, hooks/, services/
│       │   ├── bi/              # pages/, components/, hooks/, services/
│       │   └── system/          # pages/, components/, hooks/, services/
│       ├── components/          # Componente reutilizabile
│       ├── hooks/               # Hooks globale
│       ├── services/
│       │   └── api.ts           # ✅ Axios instance cu JWT interceptor
│       └── types/
│           └── index.ts         # ✅ ApiResponse, User, Prototype
│
├── nginx/
│   └── nginx.conf               # Reverse proxy: /api → backend, / → frontend
│
├── Centralizator_M2M_ERP_Lite.md  # ⭐ SURSA DE ADEVĂR — 108F
├── Wireframe_Masterplan.md
├── Wireframes_Faza0.md ... Faza6.md
├── FlowDiagrams_BuildWise.md
├── FlowDiagrams_BAHM.md
├── FlowDiagrams_M2M_Lite.md
├── Strategie_Dezvoltare.md
├── Cercetare_Piata.md
├── Fisa_Proiect.md
├── Product_Owner_Guide.md
├── Roadmap_TRL5_TRL7.md
├── Specificatii_TRL5.md         # Context TRL5 (referință, NU pt. implementare directă)
└── Functionalitati_TRL7.md      # Target TRL7 (VIITOR, NU implementa)
```

## Convenții Cod

### Backend (Python)
- **Modele DB**: snake_case (ex: `contact_name`, `created_at`)
- **API endpoints**: kebab-case (ex: `/api/v1/crm/contacts`, `/api/v1/pipeline/opportunities`)
- **Schemas Pydantic**: CamelCase class, snake_case fields (ex: `ContactCreate.contact_name`)
- **Pattern per modul**: models.py → schemas.py → service.py → router.py
- **Toate operațiunile CRUD**: trec prin audit trail automat
- **Responses**: mereu wrap în `{ "data": ..., "meta": { "total", "page", "per_page" } }`
- **Erori**: HTTPException cu status codes standard + detail message

### Frontend (TypeScript)
- **Componente**: PascalCase (ex: `ContactDetail.tsx`, `PipelineKanban.tsx`)
- **Hooks**: camelCase cu prefix `use` (ex: `useContacts`, `usePipelineStats`)
- **Services**: camelCase (ex: `contactService.getAll()`)
- **Module folder**: fiecare modul are `pages/`, `components/`, `hooks/`, `services/`
- **UI**: Ant Design components — ProTable pentru liste, ProForm pentru formulare
- **State**: React Query (TanStack Query) pentru server state, zustand pentru UI state
- **Routing**: React Router v6 cu lazy loading per modul

### Naming Ecrane (din Masterplan)
- **E-001 ... E-041**: ecrane principale (ex: E-002 = Contacts Lista)
- **E-003.1 ... E-003.5**: sub-ecrane / tab-uri
- **E-003.M1 ... E-003.M3**: modale
- **C-001 ... C-005**: componente globale

## Roluri Utilizatori (RBAC)

| Rol | Permisiuni |
|-----|-----------|
| Admin | Tot — CRUD complet, setări, audit, management utilizatori |
| Manager Vânzări | CRM + Pipeline + Rapoarte + Dashboard-uri (read PM) |
| Agent Comercial | CRM + Pipeline propriu + Activități (nu vede alte pipeline-uri) |
| Tehnician | PM + Execuție + Recepție + Măsurători (read-only CRM) |

## Flags Prototip

Funcționalitățile specifice per prototip sunt controlate prin flags:
- **Comun (P1+P2+P3)**: 82 funcționalități — mereu active
- **P2+P3 only**: 21 funcționalități — modulul RM complet, Gantt dual-layer, Financial Planning
- **P3 only**: 5 funcționalități — multi-tenant, white-label, Reports Builder, multi-limbă

La nivel de cod, folosim un enum `Prototype` (P1, P2, P3) și feature flags per organizație.

## Parametri Critici de Business

- **Coeficient U sticlă tratată termic BAHM**: 0.3 W/m²K — parametru fundamental în calculele energetice
- **Tipologii fond construit românesc**: bloc panou prefabricat, bloc cărămidă, casă interbelică, casă post-1990, spațiu industrial, clădire comercială, clădire publică
- **Pipeline stages default**: Identificare Nevoie → Evaluare Tehnică → Ofertă → Negociere → Contract → Execuție → Post-vânzare
- **EVM indicators**: CPI (Cost Performance Index), SPI (Schedule Performance Index) — obligatorii în modulul PM

## Documentație de Referință

### SURSA DE ADEVĂR PENTRU IMPLEMENTARE (folosește DOAR acestea pentru cod):

- **Ce funcționalități implementez?** → `Centralizator_M2M_ERP_Lite.md` ⭐ FIȘIERUL MASTER — 108F cu F-codes, P1/P2/P3 mapping, priorități, user stories. ACEASTA e singura sursă de adevăr pentru ce se implementează.
- **Ce ecrane construiesc?** → `Wireframe_Masterplan.md` (98 ecrane cu prioritate și complexitate)
- **Cum arată ecranele?** → `Wireframes_Faza0.md` până la `Faza6.md` (wireframes detaliate)
- **Care e fluxul utilizatorului?** → `FlowDiagrams_BuildWise.md` / `_BAHM.md` / `_M2M_Lite.md`

### CONTEXT STRATEGIC (NU pentru implementare directă — doar pentru înțelegere):

- `Specificatii_TRL5.md` — Descrieri detaliate ale funcțiunilor existente la BAHM + ce date generează pentru ML. Util ca referință, dar NU e specificație de cod. Dacă există contradicții cu Centralizatorul, Centralizatorul câștigă.
- `Functionalitati_TRL7.md` — Target TRL7 cu module AI/ML (Serviciu Informare, Serviciu Învățare, Monitorizare). NU implementa nimic din acest fișier decât dacă ți se cere explicit. Acesta descrie VIITORUL, nu ce construim acum.
- `Strategie_Dezvoltare.md` — Strategia completă: arhitectură, roadmap, plan financiar
- `Cercetare_Piata.md` — Cercetarea de piață, competitori, gap-uri
- `Product_Owner_Guide.md` — Ghidul Product Owner

## Docker & Development

```bash
# Start all services
cp .env.example .env
docker-compose up --build

# Access points
#   App (via nginx):   http://localhost
#   Backend API:       http://localhost:8000/api/docs
#   Frontend (direct): http://localhost:5173
#   PostgreSQL:        localhost:5432
#   Redis:             localhost:6379

# Run Alembic migration
docker-compose exec backend alembic upgrade head

# Create a new migration
docker-compose exec backend alembic revision --autogenerate -m "description"
```

## Reguli Importante

1. **Audit trail**: FIECARE operațiune CRUD se loghează (cine, ce, când, valorile vechi/noi)
2. **GDPR**: Consimțământ explicit, drept ștergere, export date portabil
3. **RBAC**: Verificare permisiuni pe FIECARE endpoint, nu doar pe frontend
4. **Multi-tenant** (P3): Izolare completă date între organizații — NICIODATĂ query fără org_id
5. **Migrații**: Nu modifica niciodată migrații existente — creează migrații noi
6. **Teste**: Fiecare endpoint API trebuie să aibă cel puțin un test
7. **Validare**: Pydantic pe backend, Ant Design Form rules pe frontend — validare pe ambele părți
