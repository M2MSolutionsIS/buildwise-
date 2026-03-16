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
├── docker-compose.yml
├── .env.example
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry
│   │   ├── config.py            # Settings (pydantic-settings)
│   │   ├── database.py          # SQLAlchemy engine + sessions
│   │   ├── core/
│   │   │   ├── auth.py          # JWT, login, register
│   │   │   ├── rbac.py          # Roluri + permisiuni middleware
│   │   │   ├── audit.py         # Audit trail automat
│   │   │   └── deps.py          # Dependențe comune (get_db, get_user)
│   │   ├── crm/                 # M1: Contacte, Proprietăți, Oferte
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── router.py
│   │   │   └── service.py
│   │   ├── pipeline/            # M2: Oportunități, Activități, Forecast
│   │   │   └── (same pattern)
│   │   ├── pm/                  # M3: Proiecte, WBS, Gantt, Devize, Consum
│   │   │   └── (same pattern)
│   │   ├── rm/                  # M4: HR, Materiale, Stocuri, Alocare (P2+P3)
│   │   │   └── (same pattern)
│   │   ├── bi/                  # M5: Dashboards, Reports Builder (P3)
│   │   │   └── (same pattern)
│   │   └── system/              # M6: Settings, Configuratoare, Multi-tenant
│   │       └── (same pattern)
│   ├── alembic/                 # Migrații DB
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── routes/
│   │   ├── modules/
│   │   │   ├── crm/             # Ecrane CRM
│   │   │   ├── pipeline/        # Ecrane Pipeline
│   │   │   ├── pm/              # Ecrane PM
│   │   │   ├── rm/              # Ecrane RM (P2+P3)
│   │   │   ├── bi/              # Ecrane BI
│   │   │   └── system/          # Ecrane System
│   │   ├── components/          # Componente reutilizabile
│   │   ├── layouts/             # App Shell, Sidebar, Header
│   │   ├── hooks/
│   │   ├── services/            # API client (axios/fetch)
│   │   └── types/               # TypeScript interfaces
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── Dockerfile
├── nginx/
│   └── nginx.conf
└── docs/                        # Documentația completă (markdown)
    ├── README.md                # Index documentație
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
    └── context/                 # NU pentru implementare directă
        ├── Specificatii_TRL5.md     # Descrieri TRL5 + date ML (referință)
        └── Functionalitati_TRL7.md  # Target TRL7 (VIITOR, nu implementa)
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

- **Ce funcționalități implementez?** → `docs/Centralizator_M2M_ERP_Lite.md` ⭐ FIȘIERUL MASTER — 108F cu F-codes, P1/P2/P3 mapping, priorități, user stories. ACEASTA e singura sursă de adevăr pentru ce se implementează.
- **Ce ecrane construiesc?** → `docs/Wireframe_Masterplan.md` (98 ecrane cu prioritate și complexitate)
- **Cum arată ecranele?** → `docs/Wireframes_Faza0.md` până la `Faza6.md` (wireframes detaliate)
- **Care e fluxul utilizatorului?** → `docs/FlowDiagrams_BuildWise.md` / `_BAHM.md` / `_M2M_Lite.md`

### CONTEXT STRATEGIC (NU pentru implementare directă — doar pentru înțelegere):

- `docs/context/Specificatii_TRL5.md` — Descrieri detaliate ale funcțiunilor existente la BAHM + ce date generează pentru ML. Util ca referință, dar NU e specificație de cod. Dacă există contradicții cu Centralizatorul, Centralizatorul câștigă.
- `docs/context/Functionalitati_TRL7.md` — Target TRL7 cu module AI/ML (Serviciu Informare, Serviciu Învățare, Monitorizare). NU implementa nimic din acest fișier decât dacă ți se cere explicit. Acesta descrie VIITORUL, nu ce construim acum.
- `docs/Strategie_Dezvoltare.md` — Strategia completă: arhitectură, roadmap, plan financiar
- `docs/Cercetare_Piata.md` — Cercetarea de piață, competitori, gap-uri
- `docs/Product_Owner_Guide.md` — Ghidul Product Owner

## Reguli Importante

1. **Audit trail**: FIECARE operațiune CRUD se loghează (cine, ce, când, valorile vechi/noi)
2. **GDPR**: Consimțământ explicit, drept ștergere, export date portabil
3. **RBAC**: Verificare permisiuni pe FIECARE endpoint, nu doar pe frontend
4. **Multi-tenant** (P3): Izolare completă date între organizații — NICIODATĂ query fără org_id
5. **Migrații**: Nu modifica niciodată migrații existente — creează migrații noi
6. **Teste**: Fiecare endpoint API trebuie să aibă cel puțin un test
7. **Validare**: Pydantic pe backend, Ant Design Form rules pe frontend — validare pe ambele părți
