# BuildWise — Plan de Dezvoltare Software Complet
## 3 Prototipuri | 108 Funcționalități | 98 Ecrane | Claude Code | Deploy Continuu

BAHN S.R.L.
BUILDWISE
PLAN DE DEZVOLTARE SOFTWARE COMPLET
3 Prototipuri | 108 Funcționalități | 98 Ecrane | Claude Code | Deploy Continuu
1. CE ESTE CLAUDE CODE
Claude Code este secțiunea </> Code din sidebar-ul Claude. Se conectează direct la GitHub, scrie cod, rulează comenzi și creează automat pull request-uri.
2. DEPLOY CONTINUU PE MODULE
Fiecare merge pe GitHub = deploy automat pe Railway în 2-3 minute. Nu aștepți să fie totul gata:
3. CELE 3 PROTOTIPURI
Strategie: 82 funcționalități (76%) sunt comune. Construim nucleul comun o singură dată, apoi adăugăm specific P2 și P3.
4. HOSTING + STACK
5. CUM ÎNCARȚI DOCUMENTAȚIA ÎN CLAUDE CODE
Pas critic: Claude Code nu citește .xlsx/.docx nativ. Documentația trebuie convertită în Markdown și urcată în repo.
Cum faci: Eu (aici în Chat) convertesc totul în Markdown + generez CLAUDE.md. Îți dau un .zip. Tu dezarhivezi și urci pe GitHub. Gata.
6. CE AI NEVOIE ÎNAINTE DE TASK-UL 1
7. PAȘII DE IMPLEMENTARE — 35 TASK-URI
Organizate în 7 faze. Fazele 0-3 = nucleu comun (82 funcționalități). Fazele 4-5 = specific P2+P3. Faza 6 = integrare finală.
8. SUMAR EFORT
Estimare la 14-16 ore/zi: 5-6 task-uri pe zi. ~7 zile calendaristice de la zero la 3 prototipuri live pe URL public. Prima zi e setup + fundație; din ziua 2 ai deja CRM funcțional pe care îl poți arăta.
9. URMATORUL PAS CONCRET
Pașii sunt: (1) convertim documentația → (2) urci pe GitHub → (3) Claude Code → Task 1

## PAȘII DE IMPLEMENTARE — 35 TASK-URI

Produs | BuildWise — Platforma AI verticală
Prototipuri | P1: BuildWise | P2: BAHM Op. | P3: M2M Lite
Funcționalități | 108 total (82 comune + 21 P2+P3 + 5 P3)
Ecrane | 98 (71 comune + 16 P2 + 1 P3 + 10 P1)
Module | 6: CRM + Pipeline + PM + RM + BI + Sistem
Stack | FastAPI + React/TS + Ant Design + PostgreSQL
Dezvoltare | Claude Code (claude.ai/code)
Task-uri estimate | 35 task-uri | ~7 zile la 14-16h/zi
Versiune | 1.0 | Martie 2026

PASUL 1 | PASUL 2 | PASUL 3 | PASUL 4
Alegi repo-ul GitHub
Deschizi Claude Code, selectezi repository-ul buildwise. | Descrii ce vrei
Claude Code planifică, scrie codul, testează. | Claude face push + PR
Creează branch, push pe GitHub, Pull Request. | Deploy automat
Merge PR → Railway deploy-ează. Aplicație live.

Ziua | Ce faci merge | Ce e live pe URL
1 | Task 1-3: Fundația + Auth | Login screen + structura goală
2 | Task 4-8: CRM | CRM complet funcțional
3 | Task 9-12: Pipeline | CRM + Pipeline cu Kanban
4-5 | Task 13-21: PM + Integrare | P1 complet: CRM+Pipeline+PM
5-6 | Task 22-28: RM + P2 extras | P2 complet: + RM + Gantt dual
6-7 | Task 29-35: P3 + Final | Toate 3 prototipurile live

 | P1 — BuildWise | P2 — BAHM Op. | P3 — M2M Lite
Destinație | Eficiență energetică + AI | Construcții & operațional | SaaS generic multi-tenant
Funcționalități | 82 | 103 | 108
Module | CRM+Pipeline+PM+BI | +RM complet | +RM+Sistem avansat
Specific | Energy Profile, AI predictions | HR, Materiale, Gantt dual | Multi-tenant, white-label
Ecrane | 81 | 97 | 98

Componentă | Tehnologie | Rol
Backend | FastAPI (Python) | API REST, logică business, pregătit pentru ML la TRL7
Frontend | React + TypeScript | Componentizare, type safety, 98 ecrane
UI Library | Ant Design + ProComponents | Tabele enterprise, formulare, wizard, Kanban, dashboards
Bază de date | PostgreSQL | Relații complexe, JSON fields, full-text search
Cache | Redis | Sesiuni, cache, cozi taskuri
Hosting | Railway (→ Hetzner) | ~5$/lună, deploy automat din GitHub
Dezvoltare | Claude Code | Secțiunea </> Code, scrie direct în GitHub

Ce | Detaliu
A) Folder /docs
documentația completă | Toate cele 19 fișiere convertite în Markdown. Tabele, funcționalități, specificații, wireframes, flow diagrams — păstrate integral. Claude Code le citește când referențiezi „citește docs/Specificatii_TRL5_M1_CRM.md”.
B) CLAUDE.md
citit AUTOMAT | Fișier în root-ul repo-ului, citit automat la fiecare sesiune. Context proiect, stack, convenții cod, schema DB rezumată, link-uri spre /docs. Inclusiv: care funcționalități sunt comune și care sunt specifice P2/P3.

Nr. | Ce | Cum
1 | Cont GitHub (gratuit) | github.com → Sign up → creezi repository „buildwise”
2 | Cont Railway (~5$/lună) | railway.app → Sign up cu GitHub
3 | Conectează GitHub la Claude | Deschizi </> Code → selectezi repo → autorizare
4 | Documentația în repo | Convertim în Markdown, urci în /docs + CLAUDE.md

FAZA 0 — Fundația (Task 1-3) | Ziua 1

1 | Schema bazei de date completă (toate 3 prototipurile)
Toate tabelele pentru 6 module: CRM, Pipeline, PM, RM, BI, Sistem. Include flag-uri per prototip (is_p1, is_p2, is_p3) pentru funcționalități specifice. 108 funcționalități acoperite. | Migrații + modele SQLAlchemy
Task 1

2 | Scaffolding proiect complet
Docker Compose, structura foldere (6 module backend + 6 module frontend), CLAUDE.md, Dockerfile-uri, nginx.conf. Configurare multi-prototip. | docker-compose up funcțional
Task 2

3 | Core: Auth + RBAC + Audit Trail + Multi-tenant base
JWT, 4 roluri, middleware RBAC, audit trail automat. Baza pentru multi-tenant P3: model Organization, izolare date. | Auth + audit + tenant base
Task 3

FAZA 1 — Modulul CRM — Comun (Task 4-8) | Ziua 2

4 | Backend CRM: Contacte + Proprietăți + Asset Data
API CRUD: contacte, tipologie client, Property Profile, Energy Profile, parametri sticlă U=0.3 W/m²K, clasificare fond construit. 10 funcționalități (F001-F018). | API endpoints CRM
Task 4

5 | Frontend CRM: Lista (E-002) + Detail (E-003)
Lista contacte cu filtre multi-criteriu, căutare, paginare. Contact Detail cu 5 tab-uri. Header persistent. Duplicate Guard. | 2 ecrane end-to-end
Task 5

6 | Oferte: Builder (E-005) + Versionare
Wizard 5 steps, calculator suprafețe, parametri sticlă, versionare cu comparare automată. Offer Detail (E-006). | Wizard oferte complet
Task 6

7 | Pipeline vânzări CRM + Dashboard KPI
Status pipeline, segmentare clienți, rapoarte comerciale, dashboard KPI per agent (E-001 parțial). | Pipeline tracking + KPI
Task 7

8 | Documente + Import/Export + Notificări
Upload/download documente, import/export CSV/Excel, notificări automate follow-up. | Document mgmt + import
Task 8

FAZA 2 — Modulul Pipeline — Comun (Task 9-12) | Ziua 3

9 | Backend Pipeline: Oportunități + Scoring
Oportunități comerciale, etape configurabile, probabilitate câștig, valoare ponderată, motive pierdere. 26 funcționalități (F019-F068). | API endpoints Pipeline
Task 9

10 | Frontend Kanban Board (E-009) + Opportunity Detail (E-010)
Drag & drop între etape, filtre per agent/valoare, scorare vizuală, modal detaliu oportunitate. | Kanban interactiv
Task 10

11 | Activități: Planificator + Vizite + Log
Activity Planner (E-011), vizite tehnice cu fotografii, log apeluri, urmărire email-uri, raport activitate. | Activity planner complet
Task 11

12 | Analytics: Dashboard + Funnel + Forecast
Dashboard comercial (E-012), analiză funnel, forecast vânzări, raport performanță agent, analiză mix produse. | Dashboard analytics
Task 12

FAZA 3 — Modulul PM — Comun (Task 13-18) | Zilele 4-5

13 | Backend PM: Proiecte + WBS + Devize
Creare proiecte din oportunitate, WBS ierarhic, deviz estimativ și de execuție. 34 funcționalități (F069-F106). | API endpoints PM
Task 13

14 | Gantt Chart (E-016) + Alocare Resurse
Gantt cu dependențe (FS, SS, FF, SF), cale critică, alocare resurse, vizualizare încărcare. Versiunea standard (P1). | Gantt interactiv
Task 14

15 | Execuție: Fișe Consum + Pontaj + Livrări
Fișe consum (E-019), pontaj (E-018), subcontractori, livrări materiale, raport zilnic șantier. | Module execuție
Task 15

16 | Monitorizare: Avansare + Buget EVM + Riscuri
Avansare % (S-curve), control buget CPI/SPI, situații de lucrări, registru riscuri. | Dashboard monitorizare
Task 16

17 | Recepție + Garanție + Măsurători Energetice
Recepție lucrări (E-021), punch list, PV, garanție, măsurători consum energetic pre/post. | Flux recepție
Task 17

18 | Rapoarte PM + Arhivă Proiecte Finalizate
Raport impact energetic, bază de date proiecte finalizate, export PDF/Excel. | Rapoarte + arhivă
Task 18

19 | App Shell (E-027) + Navigare + Search Global
Sidebar, breadcrumbs, notificări (E-025), search global (E-026). Layout responsive. | Aplicație unificată
Task 19

20 | Integrare P1 End-to-End
Flux: Client → Oportunitate → Proiect → Execuție → Recepție → Raport impact. Testare completă. | P1 BuildWise funcțional
Task 20

21 | Deploy P1 Production
Docker production build, configurare Railway (PostgreSQL + Redis + Backend + Frontend), verificare live. | P1 live pe URL public
Task 21

FAZA 4 — Modulul RM + Extras P2 (Task 22-28) | Zilele 5-6

22 | Backend RM: HR Management
CRUD angajați (F107), planificare angajări (F108), concedii/disponibilitate (F109), competențe (F110), salarizare + rată orară (F111). | API endpoints HR
Task 22

23 | Backend RM: Materiale + Stocuri + Financiar
Planificare achiziții (F112), facturi/NIR/bonuri (F113), stocuri cu alerte (F114), planificare financiară (F115), analiză costuri (F116). | API endpoints Materials+Finance
Task 23

24 | Backend RM: Alocare Resurse pe Proiecte
Alocare angajați+materiale+buget (F117), urmărire consum real-time (F118), eficiență per proiect (F119), resurse externe (F120), rapoarte (F121-F122). | API endpoints Allocation
Task 24

25 | Frontend RM: Dashboard + HR + Materiale
Resource Dashboard (E-032), HR Echipe (E-033), Echipamente (E-034), Materiale & Stocuri (E-035), modale aferente. | 4 ecrane RM funcționale
Task 25

26 | Frontend RM: Company Capacity + Financial Planning
Company Capacity Dashboard (E-036): angajați, proiecte, load factor. Financial Planning (E-040): bugete, previziuni. | 2 dashboard-uri RM
Task 26

27 | Gantt Dual-Layer (E-038) + SdL Generator (E-039)
Gantt cu 2 straturi (planificat vs. real + resurse). Generator Situații de Lucrări automat din deviz. | Gantt avansat + SdL
Task 27

28 | Import Engine (E-037) + Integrare P2
Wizard import devize externe (2 steps). Integrare RM ↔ PM (sync resurse). Tab RM în Project Hub (E-014.7). Deploy P2. | P2 BAHM complet + live
Task 28

FAZA 5 — Specific P3: SaaS + Multi-tenant (Task 29-33) | Zilele 6-7

29 | Multi-tenant complet + Tenant Setup Wizard (F160)
Izolare date între clienți enterprise. Wizard onboarding: configurare companie, utilizatori, module active, branding. | Multi-tenant funcțional
Task 29

30 | Configuratoare avansate: Pipeline (F061) + RM (F131)
Configurator Pipeline: stadii custom, reguli avansare automată, alertă stagnare. Configurator RM: categorii resurse, unități, praguri. | Configuratoare funcționale
Task 30

31 | Reports Builder (E-041) + Executive Dashboard (F133)
Builder rapoarte custom drag & drop. Dashboard executiv cross-module CRM+Pipeline+PM+RM. | Reports Builder + BI
Task 31

32 | Multi-limbă (F138) + White-label (F137)
Suport bilingv (RO+EN) pentru oferte/contracte. Personalizare crematică: logo, culori, fonturi per tenant. | i18n + branding
Task 32

33 | AI Assistant (E-031) + Previziuni (F135)
Chatbot integrat: asistență, FAQ, navigare, sugestii. Placeholder pentru previziuni ML (implementare reală la TRL7). | AI Assistant + ML placeholder
Task 33

FAZA 6 — Integrare Finală + Deploy (Task 34-35) | Ziua 7

34 | Integrare End-to-End toate 3 prototipurile
Testare flux complet pe fiecare prototip. Verificare izolare multi-tenant. Switch între prototipuri. Componente globale (C-001 la C-005): Toast, Empty State, Skeleton, PDF Preview. | Toate 3 prototipurile validate
Task 34

35 | Deploy Final Production
Build optimizat, Railway production, verificare performanță, documentare endpoints API (OpenAPI/Swagger), README final. | Aplicație completă live
Task 35

Fază | Task-uri | Ziua | Scope | Livrabil
Faza 0 — Fundația | 1-3 | 1 | Core | Proiect + auth + DB
Faza 1 — CRM | 4-8 | 2 | Comun | CRM complet (10 F)
Faza 2 — Pipeline | 9-12 | 3 | Comun | Pipeline complet (26 F)
Faza 3 — PM + P1 | 13-21 | 4-5 | Comun+P1 | PM + P1 live deployat
Faza 4 — RM + P2 | 22-28 | 5-6 | P2 | RM + BAHM live
Faza 5 — SaaS P3 | 29-33 | 6-7 | P3 | Multi-tenant + SaaS
Faza 6 — Final | 34-35 | 7 | All | Tot live și testat
TOTAL | 35 | ~7 zile | 108 F | 3 prototipuri live

Pas | Ce faci
1 | Cere-mi să convertesc documentația (toate 19 fișiere) în Markdown + CLAUDE.md. Îți dau un .zip.
2 | Creezi cont GitHub + repository „buildwise”. Urci conținutul din .zip.
3 | Creezi cont Railway. Conectezi la GitHub.
4 | Deschizi </> Code din sidebar Claude. Selectezi repo-ul buildwise. Scrii Task 1.
