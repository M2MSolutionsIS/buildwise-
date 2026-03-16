# Product Owner Guide

**M2M ERP LITE**

Product Owner Guide

Ecosistem Software: BuildWise (P1) + BAHM Operational (P2) + M2M ERP
Lite SaaS (P3)

Strategie Produs \| Arhitectura \| Roadmap Dezvoltare \| Backlog
Prioritizat

**M2M Solutions Consulting SRL**

M2M Tech Solutions SRL

Botosani, Romania \| Martie 2026

Document Confidential --- Uz Intern

Cuprins

1\. Viziune Produs

1.1 Problema de piata

Companiile din constructii si servicii tehnice din Romania opereaza cu
sisteme fragmentate: CRM separat, Excel pentru devize, WhatsApp pentru
comunicare interna, dosare fizice pentru documente de proiect. Aceasta
fragmentare genereaza pierderi de informatii, decizii intarziate,
depasiri de buget nedetectate la timp si imposibilitatea de a avea o
viziune consolidata asupra performantei firmei.

In domeniul eficientei energetice a cladirilor, nu exista instrumente
software care sa conecteze datele tehnice ale cladirii (coeficienti
transfer termic, HVAC, suprafete vitrate) cu predictia consumului
energetic prin modele ML, si apoi sa valideze predictiile cu masuratori
reale post-interventie.

1.2 Solutia propusa

M2M ERP Lite este un ecosistem software modular care integreaza CRM,
Sales Pipeline, Project Management, Resource Management, Business
Intelligence si (in varianta BuildWise) motor AI/ML pentru predictie
energetica --- totul intr-o singura platforma.

Ecosistemul se manifesta prin 3 prototipuri care impartasesc un nucleu
comun (\~82 functii) si se diferentiaza prin module specifice:

  -------------- ---------------- ------------- ----------------------- ----------------------
  **Prototip**   **Focus**        **Functii**   **Diferentiator**       **Target**

  P1 ---         AI / Eficienta   82            Motor ML predictie      PoCIDIF TRL 5-7, BAHM
  BuildWise      Energetica                     consum, Technical Data  SRL
                                                Energy, Post-Execution  
                                                measurements            

  P2 --- BAHM    Resource         103           RM complet (HR,         CDI operational, BAHM
  Operational    Management /                   Echipamente,            SRL
                 Constructii                    Materiale), Import      
                                                Devize, Gantt           
                                                Dual-Layer, SdL         
                                                Generator               

  P3 --- M2M ERP SaaS Generic     108           Multi-tenancy,          Produs comercial SaaS
  Lite           Multi-Vertical                 localizare, branding    
                                                custom, vertical flex   
                                                (constructii + IT       
                                                services)               
  -------------- ---------------- ------------- ----------------------- ----------------------

1.3 Propunere unica de valoare (UVP)

**BuildWise (P1):** Singura platforma care conecteaza datele tehnice ale
cladirii cu predictia ML a consumului energetic si valideaza cu
masuratori reale --- ciclu complet date-predictie-validare-invatare.

**BAHM Operational (P2):** ERP vertical pentru constructii care
integreaza managementul resurselor (echipe, echipamente, materiale) cu
executia proiectelor intr-o singura interfata --- de la deviz la
situatie de lucrari la P&L.

**M2M ERP Lite (P3):** Platforma SaaS accesibila pentru IMM-uri care
ofera CRM + Pipeline + PM + RM + BI fara complexitatea si costul unui
ERP enterprise --- cu adaptare pe vertical (constructii, IT services,
consultanta).

2\. Arhitectura Produs

2.1 Structura modulara

Platforma este construita pe principiul modularitatii: un nucleu comun
(Core) pe care se suprapun module specifice per prototip. Aceasta
arhitectura permite dezvoltarea incrementala si reutilizarea maxima a
codului.

  ----------- ---------------- ---------------- ---------------- -----------------
  **Modul**   **Core (comun)** **P1 Extensii**  **P2 Extensii**  **P3 Extensii**

  CRM         Contacte,        Technical Data   ---              Multi-currency,
              Catalog, Oferte, Energy, Asset                     Branding custom
              Contracte        Energy Class                      

  Sales       Kanban Board,    ---              ---              Oferte
  Pipeline    Opportunities,                                     multilingve
              Activities,                                        
              Analytics                                          

  PM          Projects, WBS,   Post-Execution   Import Engine,   ---
              Gantt, Deviz,    Energy, Energy   SdL Generator,   
              Timesheet, Fise  Measurements     Gantt            
              Consum,                           Dual-Layer, Work 
              Reporting                         Tracker          

  RM          --- (nu in P1    ---              HR, Echipamente, RM complet (din
              core)                             Materiale,       P2)
                                                Stocuri, Company 
                                                Capacity,        
                                                Financial        
                                                Planning         

  BI          Executive        Data-\>ML (4     ---              KPI Builder,
              Dashboard        modele), AI                       Reports Builder
                               Assistant                         
                               Predictive                        

  Sistem      Settings, Users, ---              ---              Multi-tenancy,
              Permissions,                                       Localization,
              Notifications,                                     Tenant Setup
              Search, App                                        Wizard
              Shell, Wiki                                        
  ----------- ---------------- ---------------- ---------------- -----------------

2.2 Tech Stack recomandat

Recomandarea se bazeaza pe ecosistemul React/Node --- matur, cu
comunitate mare, potrivit pentru SaaS B2B cu interfete complexe (Gantt,
Kanban, tabele editabile, dashboards).

  ------------ ----------------------- ---------------------------------------
  **Layer**    **Tehnologie**          **Motivatie**

  Frontend     React 18+ cu            Ecosistem matur, componente complexe
               TypeScript, Tailwind    (Gantt, Kanban), dark theme nativ,
               CSS, Zustand (state),   TypeScript pentru safety
               TanStack Table/Query    

  Backend      Node.js cu Fastify sau  Acelasi limbaj frontend/backend,
               NestJS, TypeScript,     performanta I/O, Prisma pentru
               Prisma ORM              type-safe DB access

  Database     PostgreSQL 16+ cu       Robust, open-source, JSON support,
               extensii (pg_trgm       full-text search nativ, scalabil
               pentru search,          
               timescaledb optional    
               pentru time-series)     

  Auth         NextAuth.js sau Clerk,  4 roluri predefinite (Admin, Sales, PM,
               JWT + refresh tokens,   Viewer), permisiuni per modul x actiune
               RBAC (Role-Based Access 
               Control)                

  File Storage S3-compatible (MinIO    Documente, fotografii punch list,
               self-hosted sau AWS S3) PDF-uri generate, import devize

  PDF          Puppeteer + Handlebars  Oferte, contracte, SdL, rapoarte ---
  Generation   templates               template-uri configurabile din Settings

  Real-time    WebSocket (Socket.io    Notificari push, Kanban live updates,
               sau ws) pentru          Gantt collaboration
               notificari, updates     
               live                    

  ML/AI (P1)   Python FastAPI          Modele predictie energetica separate de
               microservice,           aplicatia principala, API REST
               scikit-learn/XGBoost,   
               PostgreSQL ML data      
               store                   

  Deployment   Docker + Docker Compose Containerizat, reproducibil, scalabil
               (dev/staging),          orizontal pentru multi-tenancy
               Kubernetes (productie   
               P3 SaaS)                

  CI/CD        GitHub Actions sau      Build automat, teste, deploy pe merge
               GitLab CI, ESLint,      to main
               Vitest, Playwright E2E  
  ------------ ----------------------- ---------------------------------------

2.3 Arhitectura deployment

P1 (BuildWise) si P2 (BAHM) --- Single Tenant

Instanta dedicata per client. Deployment: Docker Compose pe VPS sau
server client. Database PostgreSQL dedicata. Simplu, predictibil,
control total asupra datelor.

P3 (M2M ERP Lite SaaS) --- Multi-Tenant

Strategie multi-tenancy: schema-per-tenant in PostgreSQL (fiecare client
are schema proprie, izolare completa a datelor). Shared infrastructure:
un singur cluster aplicatie, routing pe baza subdomain-ului
(client1.m2merp.ro). Avantaje: cost eficient, deploy o singura data,
fiecare tenant izolat.

2.4 API Design

REST API cu conventii consistente. Toate endpoint-urile sub /api/v1/.
Autentificare: Bearer JWT token. Rate limiting: 100 req/min per user.
Paginare: cursor-based (nu offset). Format raspuns: {data, meta,
errors}. Versionare: URL-based (/v1/, /v2/).

Pattern-uri cheie: GET /api/v1/{entity} (lista cu filtre + paginare),
GET /api/v1/{entity}/:id (detail), POST (create), PATCH (update
partial), DELETE (soft delete cu confirmare). Nested resources:
/api/v1/projects/:id/wbs, /budget, /timesheets etc.

2.5 Structura database (conceptuala)

Entitati principale: contacts, contact_persons, properties,
property_technical_data (P1), products, offers, offer_items,
offer_versions, contracts, contract_milestones, opportunities,
activities, projects, wbs_nodes, budget_items, timesheets,
consumption_records, energy_measurements (P1), ml_models (P1),
ml_datasets (P1), staff (P2), equipment (P2), materials (P2),
material_orders (P2), sdl_documents (P2), wiki_articles, wiki_versions,
notifications, users, roles, permissions, settings, custom_fields,
audit_log.

Relatii cheie: Contact -\> Properties -\> Technical Data (P1);
Opportunity -\> Offer -\> Contract -\> Project; Project -\> WBS -\>
Budget Items; Project -\> Timesheets + Consumption; Project -\> Energy
Measurements (P1) -\> ML Datasets (P1).

3\. Strategie Dezvoltare

3.1 Principii

**Core First:** Dezvoltam mai intai nucleul comun (82 functii) care
serveste toate 3 prototipurile. Apoi adaugam extensii P1/P2/P3
incremental.

**Vertical Slice:** Fiecare sprint livreaza un flux complet end-to-end
(ex: de la creare contact pana la generare oferta), nu module izolate.

**Design System First:** Inainte de orice ecran, construim componenta
library (butoane, tabele, carduri, modale, toast-uri) ---
wireframe-urile Faza 6 sunt blueprint-ul.

**API-First:** Backend-ul expune API-ul complet inainte ca frontend-ul
sa inceapa consumul. Contract API documentat cu OpenAPI/Swagger.

**Test-Driven pe fluxuri critice:** E2E tests pe: creare contact -\>
oferta -\> contract -\> proiect (fluxul principal de business).

3.2 Faze de dezvoltare

  ------------- ------------ ------------------ --------------------- ----------------------
  **Faza**      **Durata**   **Livrabil**       **Module (FE paralel  **Criterii
                                                cu BE)**              acceptanta**

  Faza 0 ---    S1 (5 zile)  Infrastructura +   Repo, CI/CD, Docker,  Build trece, deploy pe
  Setup                      API Contract +     DB schema, Auth       staging, login
                             Design System      (JWT+RBAC), Component functional, sidebar
                                                Library (C-001 la     navigabil, Swagger UI
                                                C-005), App Shell     cu toate
                                                (E-027).              endpoint-urile
                                                OpenAPI/Swagger       
                                                contract complet      
                                                intre FE si BE.       

  Faza 1 ---    S2-S3 (10    CRM complet +      FE: Contacts (E-002,  Flux
  CRM +         zile)        Pipeline           E-003 + tabs),        lead-\>oportunitate
  Pipeline                   functional         Products (E-004),     functional. CRUD
                                                Kanban (E-009),       contacte cu search +
                                                Opportunities         filtre + duplicate
                                                (E-010), Activities   guard. Kanban
                                                (E-011). BE: API      drag&drop.
                                                contacts CRUD,        
                                                search, duplicate     
                                                guard, pipeline,      
                                                drag&drop,            
                                                activities.           

  Faza 2 ---    S3-S4 (10    Ciclu complet      FE: Offer Builder     Flux complet:
  Oferte +      zile)        vanzare            (E-005 + steps),      oportunitate -\>
  Contracte +                                   Offer Lifecycle       oferta -\> PDF generat
  Dashboard                                     (E-006), Contract     -\> contract -\>
                                                Builder (E-007),      aprobare. Dashboard cu
                                                Contracts Pipeline    KPIs reali.
                                                (E-008), Analytics    
                                                (E-012), Dashboard    
                                                (E-001). BE: Offer    
                                                CRUD + versioning,    
                                                PDF generation,       
                                                contract approval     
                                                workflow, analytics.  

  Faza 3 --- PM S4-S6 (12    Project Management FE: Projects (E-013), Auto-creare proiect la
  Complet       zile)        end-to-end         Project Hub (E-014 +  semnare contract. WBS
                                                tabs), WBS (E-015),   -\> Gantt -\> Deviz
                                                Gantt (E-016), Deviz  functional. EV
                                                (E-017), Timesheet    calculat. TrueCast.
                                                (E-018), Fise Consum  Receptie cu punch
                                                (E-019), Reporting    list.
                                                (E-020), Receptie     
                                                (E-021). BE: WBS      
                                                tree, Gantt engine +  
                                                critical path, deviz  
                                                tracker, timesheet    
                                                approval, Earned      
                                                Value, TrueCast,      
                                                receptie + punch      
                                                list.                 

  Faza 4 ---    S6-S7 (8     Diferentiatori per P1: Technical Data    P1: predictie
  Extensii P1 + zile)        prototip           (E-028 + tabs),       energetica
  P2                                            Post-Exec (E-029),    functionala, eroare
                                                Data-\>ML (E-030), AI \<15%. P2: matrice
                                                Assistant (E-031).    resurse, conflict
                                                P2: Resource          detection, import
                                                Dashboard (E-032), HR deviz, SdL PDF
                                                (E-033), Echipamente  generat.
                                                (E-034), Materiale    
                                                (E-035), Capacity     
                                                (E-036), Import       
                                                (E-037), Gantt Dual   
                                                (E-038), SdL (E-039), 
                                                Fin. Planning         
                                                (E-040). Dev FE pe    
                                                P1, dev BE pe P2      
                                                simultan.             

  Faza 5 ---    S7-S8 (10    Admin complet +    FE: BI Dashboard      KPI dashboard. Wiki cu
  BI + System + zile)        Testare + Lansare  (E-022), Wiki         versionare. Permisiuni
  QA                                            (E-023), Settings     complete. Notificari
                                                (E-024 + sub-ecrane), real-time. Zero
                                                Notifications         critical bugs. Deploy
                                                (E-025), Search       productie.
                                                (E-026). BE: KPI      
                                                aggregation, wiki +   
                                                versionare,           
                                                permissions matrix,   
                                                WebSocket notif.,     
                                                FTS. QA: E2E pe       
                                                fluxuri critice,      
                                                performance,          
                                                security, bug fixing. 
  ------------- ------------ ------------------ --------------------- ----------------------

3.3 Timeline estimativa

Total estimat: 8 saptamani (\~2 luni) cu o echipa de 2 developeri
full-time: 1 frontend (React/TypeScript) + 1 backend (Node/PostgreSQL).
Dezvoltare paralela: frontend-ul construieste interfetele pe baza
wireframe-urilor cu date mock, backend-ul construieste API-ul si logica
de business. Integrare continua prin contract API (OpenAPI/Swagger)
definit in Faza 0. Faza 4 permite paralelism maxim: un developer pe P1,
celalalt pe P2.

Nota: timeline-ul de 8 saptamani este realizabil --- documentatia
completa este livrata. Conditii: (1) contract API definit in S1, (2)
zero scope creep, (3) Product Owner disponibil zilnic. Daca echipa e
noua pe domeniu, se adauga 1 saptamana ramp-up.

4\. Backlog Prioritizat

4.1 Epics

  ---------------- ------------------------- ----------------- --------- --------------
  **Epic**         **Descriere**             **Ecrane**        **Story   **Prototip**
                                                               Points    
                                                               est.**    

  EP-01            Setup repo, CI/CD,        E-027, C-001 la   21        Core
  Infrastructure   Docker, DB, Auth, Design  C-005                       
                   System                                                

  EP-02 CRM        Contacts CRUD, Persons,   E-002, E-003      34        Core
                   Properties, Documents,    (+tabs), E-004              
                   Custom Fields, Duplicate                              
                   Guard                                                 

  EP-03 Sales      Kanban, Opportunities,    E-009, E-010,     34        Core
  Pipeline         Activities, Scoring,      E-011, E-012                
                   Analytics                                             

  EP-04 Offer      Offer Builder wizard,     E-005 (+steps),   21        Core
  Lifecycle        Versioning, Lifecycle,    E-006                       
                   PDF Generation                                        

  EP-05 Contracts  Contract Builder, Billing E-007, E-008      21        Core
                   Schedule, Approval                                    
                   Workflow, Pipeline                                    

  EP-06 PM Core    Projects, WBS, Gantt,     E-013, E-014,     55        Core
                   Deviz Tracker             E-015, E-016,               
                                             E-017                       

  EP-07 PM         Timesheet, Fise Consum,   E-018, E-019,     34        Core
  Execution        Reporting, TrueCast,      E-020, E-021                
                   Receptie                                              

  EP-08 Energy AI  Technical Data,           E-028 (+tabs),    34        P1 only
                   Post-Exec, ML Pipeline,   E-029, E-030,               
                   AI Chat                   E-031                       

  EP-09 Resource   HR, Echipamente,          E-032, E-033,     34        P2 only
  Mgmt             Materiale, Alocare,       E-034, E-035,               
                   Capacity                  E-036, E-040                

  EP-10            Import Devize, Gantt RM,  E-037, E-038,     21        P2 only
  Construction Ops SdL Generator             E-039                       

  EP-11 BI + Admin Dashboard BI, Wiki,       E-022, E-023,     34        Core
                   Settings, Notifications,  E-024 (+sub),               
                   Search                    E-025, E-026                

  EP-12 SaaS       Multi-tenancy,            E-041, F160       21        P3 only
  Platform         Localization, Reports                                 
                   Builder, Tenant Wizard                                
  ---------------- ------------------------- ----------------- --------- --------------

Total estimat: \~384 story points. Cu velocity 48 SP/saptamana (2 devs x
24 SP), estimam \~8 saptamani. Velocity agresiva presupune wireframes si
specificatii complete (livrate), zero scope creep, PO disponibil zilnic.

4.2 Prioritizare MoSCoW

  ---------------- ------------------------ -------- ------------------------------
  **Prioritate**   **Epics**                **SP**   **Motivatie**

  **Must Have      EP-01 + EP-02 + EP-03 +  220      Fluxul complet de business:
  (MVP)**          EP-04 + EP-05 + EP-06 +           contact -\> oferta -\>
                   EP-07                             contract -\> proiect -\>
                                                     raport. Fara acestea, produsul
                                                     nu are sens.

  **Should Have**  EP-08 (P1) SAU           89-110   Diferentiatorii per prototip +
                   EP-09+EP-10 (P2) + EP-11          admin. Depinde de prioritatea
                                                     clientului: BuildWise sau
                                                     BAHM.

  **Could Have**   EP-12 (P3 SaaS)          21       Multi-tenancy. Dezvoltat doar
                                                     daca se confirma modelul SaaS
                                                     comercial.

  **Won\'t Have    Mobile app, Integrare    ---      Amanate post-lansare. Se pot
  (v1)**           contabilitate, API                adauga in v2 pe baza
                   publica                           feedback-ului.
  ---------------- ------------------------ -------- ------------------------------

5\. Documentatie Existenta --- Index

Pachetul complet de documentatie pentru echipa de dezvoltare cuprinde
urmatoarele fisiere:

  ---------------------------------------- ---------------------------- -------------------------
  **Fisier**                               **Continut**                 **Utilizare**

  M2M_ERP_Lite_Centralizator_V7.xlsx       108 functii detaliate pe 3   Sursa de adevar pentru ce
                                           prototipuri, cu user         trebuie construit.
                                           stories, prioritati,         Fiecare functie are ID
                                           comparabilitate piata        unic (F-code).

  BuildWise_Wireframe_Masterplan_V4.xlsx   98 itemi (41 ecrane + 30     Harta completa a
                                           sub-ecrane + 22 modale + 5   interfetei. Fiecare item
                                           componente) cu F-codes       are ID (E-xxx), parent,
                                           exacte, scope, prioritati,   F-codes mapate din
                                           note developer               centralizator.

  BuildWise_Wireframes_Faza0.docx          9 ecrane principale ---      Referinta vizuala pentru
                                           screenshot dark theme +      ecranele core: Dashboard,
                                           specificatii + stari + note  Contacts, Offer Builder,
                                           dev                          Pipeline Kanban, Project
                                                                        Hub, Gantt, Technical
                                                                        Data, Post-Exec Energy,
                                                                        Data-\>ML

  BuildWise_Wireframes_Faza1.docx          8 ecrane P0 critice ---      Ecranele fara care
                                           Contact Detail, WBS, Deviz,  produsul nu poate
                                           App Shell + 4 P2 (RM         functiona
                                           Dashboard, Company Capacity, 
                                           Import Engine, Gantt         
                                           Dual-Layer)                  

  BuildWise_Wireframes_Faza2.docx          13 ecrane P1 importante ---  Al doilea val de ecrane
                                           Catalog, Offer Lifecycle,    necesare pentru produs
                                           Contract Builder,            complet
                                           Opportunity, Activity        
                                           Planner, Timesheet, Fise     
                                           Consum, Reporting + 6 P2     
                                           (HR, Echipamente, Materiale, 
                                           SdL, Financial Planning)     

  BuildWise_Wireframes_Faza3.docx          11 ecrane P2 utile ---       Ecrane care completeaza
                                           Contracts Pipeline,          experienta
                                           Analytics, Projects Lista,   
                                           Receptie, BI Dashboard,      
                                           Wiki, Settings,              
                                           Notifications, Search, AI    
                                           Assistant (P1), Reports      
                                           Builder (P3)                 

  BuildWise_Wireframes_Faza4.docx          22 sub-ecrane --- tab-uri    Layout-ul fiecarui tab
                                           individuale pentru Contact   --- developerul stie
                                           Detail (4), Offer Builder    exact ce apare pe fiecare
                                           (4), Opportunity (1),        
                                           Project RM (1), Settings     
                                           (5), Notifications (1),      
                                           Technical Data (4), Import   
                                           Engine (2)                   

  BuildWise_Wireframes_Faza5.docx          22 modale si overlay-uri --- Toate interactiunile
                                           form modals, diff modals,    modale ale aplicatiei
                                           workflow modals, detail      
                                           modals, slide-over, upload   
                                           modal, product picker        

  BuildWise_Wireframes_Faza6.docx          5 componente globale ---     Design patterns
                                           Confirmare Stergere (3       reutilizabile pe toata
                                           variante), Toast (4          aplicatia
                                           variante), Empty State (4    
                                           variante), Skeleton Loader   
                                           (6 variante), PDF Preview    

  BuildWise_FlowDiagrams_V2.xlsx           9 fluxuri swim-lane P1 cu    Parcursul utilizatorului
                                           referinte E-xxx per pas      prin aplicatie --- de la
                                                                        lead la inchidere proiect

  BAHM_Op_FlowDiagrams_V2.xlsx             8 fluxuri swim-lane P2 cu    Fluxuri specifice BAHM:
                                           referinte E-xxx per pas      configurare,
                                                                        aprovizionare, operatiuni
                                                                        zilnice, ciclu lunar,
                                                                        resurse multi-proiecte

  M2M_Lite_FlowDiagrams_V2.xlsx            7 fluxuri swim-lane P3 cu    Fluxuri SaaS: tenant
                                           referinte E-xxx per pas      onboarding, ciclu vanzare
                                                                        SaaS, vertical flex, data
                                                                        lifecycle
  ---------------------------------------- ---------------------------- -------------------------

6\. Metrici Produs si KPIs

6.1 KPIs de adoptie

  ---------------------- ------------ ------------------------------------
  **KPI**                **Target v1  **Cum masuram**
                         (6 luni)**   

  Nr. contacte create    \>20         COUNT contacts WHERE created_at \>
  per user/luna                       30 days per user

  Oferte generate / luna \>10         COUNT offers per month

  Rata conversie oferta  \>25%        COUNT contracts / COUNT offers
  -\> contract                        

  Proiecte active        \>3          COUNT projects WHERE status = active
  simultam                            

  Deviatia buget         \>90% din    Alerte budget triggered / actual
  detectata \<24h        cazuri       deviations

  Predictie energetica   \<15%        AVG(abs(predicted - actual) /
  eroare (P1)                         actual) per model S1
  ---------------------- ------------ ------------------------------------

6.2 KPIs tehnici

  ---------------------- ------------------ ------------------------------
  **KPI**                **Target**         **Tool**

  Time to first          \<2s               Lighthouse
  meaningful paint                          

  API response time      \<500ms            APM (Datadog/NewRelic)
  (p95)                                     

  Uptime                 \>99.5%            UptimeRobot

  Test coverage          \>70% (unit) +     Vitest + Playwright
                         \>50% (E2E pe      
                         fluxuri critice)   

  Zero critical security 0                  OWASP ZAP, Snyk
  vulnerabilities                           

  Deploy frequency       \>2x / saptamana   CI/CD metrics
  ---------------------- ------------------ ------------------------------

7\. Riscuri si Mitigare

  ---------------- ------------------- ------------ ----------------------------------------
  **Risc**         **Probabilitate**   **Impact**   **Mitigare**

  Complexitatea    Ridicata            Ridicat      Evalueaza DHTMLX Gantt (comercial) vs
  Gantt interactiv                                  implementare custom. Buget 2 saptamani
  depaseste                                         extra pentru Gantt.
  estimarile                                        

  ML pipeline (P1) Medie               Ridicat      Dezvolta cu date sintetice. Structureaza
  necesita date                                     pipeline-ul sa functioneze cu min 50
  reale care nu                                     datasets. Primul model = linear
  exista inca                                       regression simplu.

  Import Intersoft Medie               Mediu        Parser configurabil (nu hardcodat).
  (P2) --- format                                   Schema de validare separata. Fallback la
  XML se schimba                                    CSV manual.

  Echipa dev nu    Ridicata            Mediu        Sesiuni de knowledge transfer (2-3 zile)
  are experienta                                    la inceputul proiectului. Flow
  cu domeniul                                       diagrams-urile ca material de training.
  constructii                                       

  Scope creep ---  Ridicata            Ridicat      Backlog-ul prioritizat ca referinta.
  cereri noi in                                     Orice adaugare trece prin Product Owner.
  timpul                                            Sprint planning strict.
  dezvoltarii                                       

  Multi-tenancy    Medie               Ridicat      Arhitectura multi-tenant de la inceput
  (P3) adauga                                       (schema-per-tenant) chiar daca P3 se
  complexitate                                      dezvolta mai tarziu. Migrari de schema
  neasteptata                                       automatizate.
  ---------------- ------------------- ------------ ----------------------------------------

8\. Criterii de Acceptanta Globale

Fiecare functionalitate livrata trebuie sa indeplineasca:

**Functional:** Implementeaza toate starile documentate in wireframe
(empty, loading, error, success, variante per prototip). Respecta
specificatiile din note developer.

**Vizual:** Respecta design system-ul dark theme din wireframes.
Responsive pe 3 breakpoints (desktop \>1200px, tablet 768-1200px, mobile
\<768px).

**Permisiuni:** Respecta matricea de permisiuni (Admin/Sales/PM/Viewer).
Viewer nu poate edita. Sales nu poate accesa PM. Admin are acces
complet.

**Navigare:** Toate tranzitiile din Masterplan V4 sheet Navigare & Flow
sunt implementate. Back button functioneaza corect. Deep links
functioneaza.

**Performanta:** Lista/tabel cu 1000 itemi se incarca in \<2s. Dashboard
cu 10 widget-uri in \<3s. Gantt cu 100 activitati fluent la scroll/zoom.

**Date:** Nicio pierdere de date la save/navigate/refresh. Auto-save pe
formulare lungi (Offer Builder, Contract Builder). Undo disponibil pe
operatii distructive.

9\. Glosar

  --------------- -------------------------------------------------------
  **Termen**      **Definitie**

  F-code          ID unic al unei functionalitati din Centralizatorul V7
                  (ex: F042 = Qualify & Handover)

  E-xxx           ID unic al unui ecran/sub-ecran/modal din Masterplan V4
                  (ex: E-003.2 = Tab Istoric Interactiuni)

  P1 / BuildWise  Prototipul cu focus pe AI/Energie --- 82 functii ---
                  PoCIDIF TRL 5-7

  P2 / BAHM       Prototipul cu focus pe Resource Management/Constructii
  Operational     --- 103 functii

  P3 / M2M ERP    Prototipul SaaS generic --- 108 functii --- produs
  Lite            comercial

  Core            Functionalitati comune tuturor celor 3 prototipuri
                  (\~82 functii)

  WBS             Work Breakdown Structure --- descompunerea ierarhica a
                  proiectului in faze, activitati, sub-activitati

  SdL             Situatie de Lucrari --- document lunar de decontare in
                  constructii

  TrueCast        Proiectia P&L si Cash Flow la finalizarea proiectului
                  pe baza tendintelor curente (EAC/VAC)

  Earned Value    Metoda de masurare performanta proiect: SPI (schedule),
                  CPI (cost), EV, EAC

  U-value         Coeficient transfer termic (W/m2K) --- cu cat mai mic,
                  cu atat mai buna izolatie termica

  ML Pipeline     Fluxul de date de la colectare la antrenare model la
                  predictie: CRM data -\> Training -\> Model -\>
                  Prediction

  Sprint          Perioada de dezvoltare de 2 saptamani cu livrabil
                  demonstrabil

  Story Point     Unitate relativa de efort estimare (1=trivial,
                  3=simplu, 5=mediu, 8=complex, 13=foarte complex)
  --------------- -------------------------------------------------------
