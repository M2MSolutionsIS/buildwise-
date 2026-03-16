## Sheet: Masterplan V4 Complet

| ID | Modul | Nume | Nivel | Scope | P1 | P2 | P3 | Tip Ecran | Parent | F-codes | Nr.F | Complexitate | Status WF | Prioritate | Note Developer |
| E-001 | CRM | Dashboard Principal | Ecran | Comun | ✓ | ✓ | ✓ | Dashboard | — | F133, F135 | 2 | Ridicată | ✓ | P0 | Widgets diferite per prototip |
| E-002 | CRM | Contacts — Lista | Ecran | Comun | ✓ | ✓ | ✓ | List+Filters | — | F001, F002, F003, F004, F005 | 5 | Medie | ✓ | P0 | Duplicate Guard badge |
| E-003 | CRM | Contact — Detail | Ecran | Comun | ✓ | ✓ | ✓ | Detail+Tabs | — | F001, F003, F004, F005, F010, F012 | 6 | Ridicată | ✓ | P0 | Header persistent, 5 tab-uri |
| E-003.1 | CRM | Tab: Date Generale | Sub-ecran (tab) | Comun | ✓ | ✓ | ✓ | Form/Cards | E-003 | F001, F003, F004 | 3 | Medie | ✓ | P0 | Grid 2col: info companie + sumar |
| E-003.2 | CRM | Tab: Istoric Interacțiuni | Sub-ecran (tab) | Comun | ✓ | ✓ | ✓ | Timeline | E-003 | F005 | 1 | Medie | ✓ | P1 | Timeline cronologică, filtre tip |
| E-003.3 | CRM | Tab: Proprietăți | Sub-ecran (tab) | Comun | ✓ | ✓ | ✓ | List/Cards | E-003 | F010, F012, F016, F018 | 4 | Medie | ✓ | P1 | Lista proprietăți + badge energie (P1) |
| E-003.4 | CRM | Tab: Documente | Sub-ecran (tab) | Comun | ✓ | ✓ | ✓ | Grid/Upload | E-003 | F005 | 1 | Medie | ✓ | P1 | Grid docs, drag&drop, categorii |
| E-003.5 | CRM | Tab: Oferte & Contracte | Sub-ecran (tab) | Comun | ✓ | ✓ | ✓ | Tables | E-003 | F019, F031 | 2 | Scăzută | ✓ | P1 | 2 tabele linkate |
| E-003.M1 | CRM | Modal: Adaugă Persoană | Modal / Overlay | Comun | ✓ | ✓ | ✓ | Form modal | E-003 | F003 | 1 | Scăzută | ✓ | P1 | Nume, rol, telefon, email |
| E-003.M2 | CRM | Modal: Duplicate Guard | Modal / Overlay | Comun | ✓ | ✓ | ✓ | Diff modal | E-003 | F004 | 1 | Medie | ✓ | P1 | Side-by-side diff, merge |
| E-003.M3 | CRM | Modal: Upload Document | Modal / Overlay | Comun | ✓ | ✓ | ✓ | Upload modal | E-003 | F005 | 1 | Scăzută | ✓ | P2 | Drag&drop, categorie, progress |
| E-004 | CRM | Products & Services | Ecran | Comun | ✓ | ✓ | ✓ | List+CRUD | — | F007 | 1 | Scăzută | ✓ | P1 | Sidebar categorii + tabel |
| E-004.M1 | CRM | Modal: Produs Detail | Modal / Overlay | Comun | ✓ | ✓ | ✓ | Form modal | E-004 | F007 | 1 | Scăzută | ✓ | P1 | Edit complet + istoric prețuri |
| E-005 | CRM | Offer Builder — Wizard | Ecran | Comun | ✓ | ✓ | ✓ | Wizard | — | F019, F023, F026, F027 | 4 | Ridicată | ✓ | P0 | 5 steps, Step 3 wireframe-at |
| E-005.S1 | CRM | Step 1: Selectare Client | Sub-ecran (tab) | Comun | ✓ | ✓ | ✓ | Form | E-005 | F019 | 1 | Scăzută | ✓ | P1 | Search client + selectare proprietate |
| E-005.S2 | CRM | Step 2: Line Items | Sub-ecran (tab) | Comun | ✓ | ✓ | ✓ | Table+Picker | E-005 | F023 | 1 | Medie | ✓ | P1 | Tabel editabil + picker catalog |
| E-005.S4 | CRM | Step 4: T&C | Sub-ecran (tab) | Comun | ✓ | ✓ | ✓ | Editor | E-005 | F026 | 1 | Scăzută | ✓ | P2 | Template editabil din Settings |
| E-005.S5 | CRM | Step 5: Preview & Generare | Sub-ecran (tab) | Comun | ✓ | ✓ | ✓ | Preview | E-005 | F027, F028 | 2 | Medie | ✓ | P1 | Preview PDF + generare |
| E-005.M1 | CRM | Modal: Product Picker | Modal / Overlay | Comun | ✓ | ✓ | ✓ | Search modal | E-005 | F007, F023 | 2 | Medie | ✓ | P1 | Search catalog, click → add |
| E-006 | CRM | Offer — Lifecycle | Ecran | Comun | ✓ | ✓ | ✓ | Detail+Timeline | — | F027, F028, F029, F049 | 4 | Medie | ✓ | P1 | Status pipeline + versiuni |
| E-006.M1 | CRM | Modal: Version Diff | Modal / Overlay | Comun | ✓ | ✓ | ✓ | Diff modal | E-006 | F029 | 1 | Medie | ✓ | P1 | Side-by-side diff v1/v2 |
| E-007 | CRM | Contract Builder | Ecran | Comun | ✓ | ✓ | ✓ | Wizard/Form | — | F031, F033, F035, F037 | 4 | Medie | ✓ | P1 | Billing schedule + aprobare |
| E-007.M1 | CRM | Modal: Aprobare Contract | Modal / Overlay | Comun | ✓ | ✓ | ✓ | Workflow | E-007 | F035 | 1 | Medie | ✓ | P1 | Status aprobatori + acțiune |
| E-008 | CRM | Contracts — Pipeline | Ecran | Comun | ✓ | ✓ | ✓ | Board+List | — | F031, F033, F035, F037 | 4 | Scăzută | ✓ | P2 | Pattern Kanban reutilizat |
| E-009 | Sales Pipeline | Pipeline Board — Kanban | Ecran | Comun | ✓ | ✓ | ✓ | Kanban | — | F042, F050, F051, F052, F053 | 5 | Ridicată | ✓ | P0 | Drag&drop, stagnare |
| E-009.M1 | Sales Pipeline | Slide-over: Quick Opportunity | Modal / Overlay | Comun | ✓ | ✓ | ✓ | Slide-over | E-009 | F042, F050 | 2 | Medie | ✓ | P1 | KPIs + quick actions fără părăsi board |
| E-010 | Sales Pipeline | Opportunity — Detail | Ecran | Comun | ✓ | ✓ | ✓ | Detail+Tabs | — | F042, F043, F044, F045, F046, F047, F048 | 7 | Medie | ✓ | P1 | Scoring + activity log |
| E-010.1 | Sales Pipeline | Tab: Activități Oportunitate | Sub-ecran (tab) | Comun | ✓ | ✓ | ✓ | Timeline | E-010 | F043, F045, F047 | 3 | Medie | ✓ | P1 | Timeline completă + filtre |
| E-010.M1 | Sales Pipeline | Modal: Won/Lost Reason | Modal / Overlay | Comun | ✓ | ✓ | ✓ | Form modal | E-010 | F046 | 1 | Scăzută | ✓ | P2 | Motiv dropdown + text liber |
| E-011 | Sales Pipeline | Activity Planner | Ecran | Comun | ✓ | ✓ | ✓ | Calendar+List | — | F054, F055, F056, F058 | 4 | Medie | ✓ | P1 | Calendar + templates |
| E-011.M1 | Sales Pipeline | Modal: Activitate Nouă | Modal / Overlay | Comun | ✓ | ✓ | ✓ | Form modal | E-011 | F054 | 1 | Medie | ✓ | P1 | Tip, dată, durată, link client |
| E-012 | Sales Pipeline | Pipeline — Analytics | Ecran | Comun | ✓ | ✓ | ✓ | Dashboard | — | F056, F058 | 2 | Medie | ✓ | P2 | Funnel + agent perf |
| E-013 | PM | Projects — Lista | Ecran | Comun | ✓ | ✓ | ✓ | List+Filters | — | F101, F130 | 2 | Scăzută | ✓ | P2 | Pattern reutilizat E-002 |
| E-014 | PM | Project — Detail Hub | Ecran | Comun | ✓ | ✓ | ✓ | Detail+Tabs | — | F063, F066, F069, F070, F071, F091 | 6 | Foarte ridicată | ✓ | P0 | 8 tab-uri, cel mai complex |
| E-014.1 | PM | Tab: Overview | Sub-ecran (tab) | Comun | ✓ | ✓ | ✓ | Dashboard mini | E-014 | F063, F091, F095, F100 | 4 | Medie | ✓ | P0 | KPIs EV + Gantt mini |
| E-014.2 | PM | Tab: WBS (→E-015) | Sub-ecran (tab) | Comun | ✓ | ✓ | ✓ | Ref E-015 | E-014 | F069, F070, F071 | 3 | — | ✓ | P0 | Embedded E-015 |
| E-014.3 | PM | Tab: Gantt (→E-016/038) | Sub-ecran (tab) | Comun | ✓ | ✓ | ✓ | Ref E-016 | E-014 | F069, F083, F084 | 3 | — | ✓ | P0 | E-016 comun, E-038 P2 |
| E-014.4 | PM | Tab: Deviz (→E-017) | Sub-ecran (tab) | Comun | ✓ | ✓ | ✓ | Ref E-017 | E-014 | F074, F077, F078, F079, F125 | 5 | — | ✓ | P0 | Embedded E-017 |
| E-014.5 | PM | Tab: Execuție | Sub-ecran (tab) | Comun | ✓ | ✓ | ✓ | Ref E-018/019 | E-014 | F072, F073, F074, F075 | 4 | — | ✓ | P1 | Toggle: Timesheet / Fișe Consum |
| E-014.6 | PM | Tab: Post-Exec Energy | Sub-ecran (tab) | Specific P1 | ✓ |  |  | Ref E-029 | E-014 | F086, F088, F090, F105, F161 | 5 | — | ✓ | P0 | Doar P1 |
| E-014.7 | PM | Tab: RM Proiect | Sub-ecran (tab) | Specific P2 |  | ✓ |  | Mini dashboard | E-014 | F117, F118, F119, F120 | 4 | Medie | ✓ | P1 | Doar P2. Resurse alocate proiect |
| E-014.8 | PM | Tab: Raportare (→E-020) | Sub-ecran (tab) | Comun | ✓ | ✓ | ✓ | Ref E-020 | E-014 | F091, F092, F093, F094, F095, F100, F140 | 7 | — | ✓ | P1 | Embedded E-020 |
| E-014.M1 | PM | Modal: Schimbare Status Proiect | Modal / Overlay | Comun | ✓ | ✓ | ✓ | Confirm | E-014 | F063 | 1 | Scăzută | ✓ | P1 | Confirmare + comentariu opțional |
| E-015 | PM | WBS Editor | Ecran | Comun | ✓ | ✓ | ✓ | Tree+Table | — | F069, F070, F071 | 3 | Ridicată | ✓ | P0 | Arbore 3 niveluri, drag |
| E-015.M1 | PM | Modal: Adaugă Nod WBS | Modal / Overlay | Comun | ✓ | ✓ | ✓ | Form modal | E-015 | F069 | 1 | Scăzută | ✓ | P1 | Tip, denumire, responsabil, durată, cost |
| E-016 | PM | Gantt Chart | Ecran | Comun | ✓ | ✓ | ✓ | Gantt | — | F083, F084 | 2 | Foarte ridicată | ✓ | P0 | Target vs realizat, critical path |
| E-017 | PM | Deviz — Editor & Tracker | Ecran | Comun | ✓ | ✓ | ✓ | Table edit | — | F074, F077, F078, F079, F123, F125 | 6 | Ridicată | ✓ | P0 | Estimat vs realizat, SdL (P2) |
| E-017.M1 | PM | Modal: Adaugă Articol Deviz | Modal / Overlay | Comun | ✓ | ✓ | ✓ | Form modal | E-017 | F074 | 1 | Scăzută | ✓ | P1 | Articol, UM, cant, preț, WBS |
| E-018 | PM | Timesheet | Ecran | Comun | ✓ | ✓ | ✓ | Grid | — | F072, F073 | 2 | Medie | ✓ | P1 | Grid ore/zi, aprobare PM |
| E-019 | PM | Fișe Consum Materiale | Ecran | Comun | ✓ | ✓ | ✓ | Table | — | F075 | 1 | Medie | ✓ | P1 | Planificat vs consumat |
| E-019.M1 | PM | Modal: Înregistrare Consum | Modal / Overlay | Comun | ✓ | ✓ | ✓ | Form modal | E-019 | F075 | 1 | Scăzută | ✓ | P1 | Material, cantitate, dată |
| E-020 | PM | Project Reporting 3-in-1 | Ecran | Comun | ✓ | ✓ | ✓ | Report | — | F080, F091, F092, F093, F094, F095, F100, F103, F140 | 9 | Ridicată | ✓ | P1 | EV + P&L + CF + TrueCast |
| E-021 | PM | Recepție & Punch List | Ecran | Comun | ✓ | ✓ | ✓ | Checklist | — | F080, F103 | 2 | Medie | ✓ | P2 | Checklist + defecte |
| E-021.M1 | PM | Modal: Adaugă Defect | Modal / Overlay | Comun | ✓ | ✓ | ✓ | Form modal | E-021 | F103 | 1 | Medie | ✓ | P2 | Defect, severitate, responsabil, foto |
| E-022 | BI | BI — Executive Dashboard | Ecran | Comun | ✓ | ✓ | ✓ | Dashboard | — | F101, F130, F133, F135, F148, F152 | 6 | Medie | ✓ | P2 | KPIs cross-module |
| E-023 | PM | Wiki — Documentație | Ecran | Comun | ✓ | ✓ | ✓ | Tree+Content | — | F144, F145, F146 | 3 | Medie | ✓ | P2 | Sidebar + WYSIWYG + versiuni |
| E-023.M1 | PM | Modal: Istoric Versiuni | Modal / Overlay | Comun | ✓ | ✓ | ✓ | Diff modal | E-023 | F145 | 1 | Medie | ✓ | P2 | Lista versiuni + diff vizual |
| E-024 | Sistem | Settings | Ecran | Comun | ✓ | ✓ | ✓ | Settings | — | F039, F040, F041, F061, F106, F131, F136, F137, F138, F139, F141, F142, F143, F160 | 14 | Medie | ✓ | P2 | Sidebar categorii |
| E-024.1 | Sistem | Settings: Utilizatori & Roluri | Sub-ecran (tab) | Comun | ✓ | ✓ | ✓ | Table+CRUD | E-024 | F131 | 1 | Medie | ✓ | P2 | Tabel useri, role assignment |
| E-024.2 | Sistem | Settings: Permisiuni | Sub-ecran (tab) | Comun | ✓ | ✓ | ✓ | Matrix | E-024 | F131 | 1 | Medie | ✓ | P2 | Matrice modul × acțiune × rol |
| E-024.3 | Sistem | Settings: Template-uri | Sub-ecran (tab) | Comun | ✓ | ✓ | ✓ | Editor | E-024 | F106 | 1 | Medie | ✓ | P2 | Editor cu placeholders |
| E-024.4 | Sistem | Settings: Câmpuri Custom | Sub-ecran (tab) | Comun | ✓ | ✓ | ✓ | CRUD+Config | E-024 | F039, F061 | 2 | Medie | ✓ | P2 | Definire câmpuri per entitate |
| E-024.5 | Sistem | Settings: Pipeline Stadii | Sub-ecran (tab) | Comun | ✓ | ✓ | ✓ | Drag list | E-024 | F040 | 1 | Scăzută | ✓ | P2 | Drag reorder stadii |
| E-024.M1 | Sistem | Modal: Invită Utilizator | Modal / Overlay | Comun | ✓ | ✓ | ✓ | Form modal | E-024 | F131 | 1 | Scăzută | ✓ | P2 | Email, rol, mesaj |
| E-025 | Sistem | Notifications Center | Ecran | Comun | ✓ | ✓ | ✓ | List+Settings | — | F141 | 1 | Scăzută | ✓ | P2 | Feed + preferences |
| E-025.1 | Sistem | Notifications: Preferences | Sub-ecran (tab) | Comun | ✓ | ✓ | ✓ | Matrix | E-025 | F141 | 1 | Scăzută | ✓ | P2 | Matrice eveniment × canal |
| E-026 | Sistem | Global Search | Ecran | Comun | ✓ | ✓ | ✓ | Modal | — | F142 | 1 | Scăzută | ✓ | P2 | Cmd+K, rezultate grupate |
| E-027 | Sistem | App Shell | Ecran | Comun | ✓ | ✓ | ✓ | Layout | — | F157, F158 | 2 | Medie | ✓ | P0 | Sidebar + header, responsive |
| E-028 | CRM | Technical Data — Energy | Ecran | Specific P1 | ✓ |  |  | Detail+Tabs | — | F010, F012, F016, F018 | 4 | Ridicată | ✓ | P0 | Diferențiator #1 |
| E-028.1 | CRM | Tab: Parametri Energetici | Sub-ecran (tab) | Specific P1 | ✓ |  |  | Form | E-028 | F012, F016 | 2 | Medie | ✓ | P0 | U-value, consum estimat |
| E-028.2 | CRM | Tab: HVAC | Sub-ecran (tab) | Specific P1 | ✓ |  |  | Form | E-028 | F016 | 1 | Medie | ✓ | P1 | Tip, capacitate, eficiență |
| E-028.3 | CRM | Tab: Calculator Suprafețe | Sub-ecran (tab) | Specific P1 | ✓ |  |  | Calculator | E-028 | F018 | 1 | Medie | ✓ | P1 | Niveluri × suprafață dinamice |
| E-028.4 | CRM | Tab: Istoric Măsurători | Sub-ecran (tab) | Specific P1 | ✓ |  |  | Timeline | E-028 | F010, F086 | 2 | Medie | ✓ | P1 | PRE/POST per parametru |
| E-029 | PM | Post-Execution — Energy | Ecran | Specific P1 | ✓ |  |  | Form+Dashboard | — | F086, F088, F090, F105, F161 | 5 | Ridicată | ✓ | P0 | PRE/POST + ML dataset |
| E-030 | BI | Data → ML | Ecran | Specific P1 | ✓ |  |  | Dashboard | — | F132 | 1 | Ridicată | ✓ | P0 | Status modele + mapare |
| E-030.M1 | BI | Modal: Detalii Model ML | Modal / Overlay | Specific P1 | ✓ |  |  | Detail | E-030 | F132 | 1 | Medie | ✓ | P1 | Parametri, istoric, grafic eroare |
| E-031 | BI | AI Assistant | Ecran | Specific P1 | ✓ |  |  | Chat+Cards | — | F132 | 1 | Ridicată | ✓ | P2 | Chat + carduri vizuale |
| E-032 | RM | Resource Dashboard | Ecran | Specific P2 |  | ✓ |  | Dashboard | — | F117, F118, F119, F120, F121, F122 | 6 | Ridicată | ✓ | P0 | Semafoare, matrice, conflicte |
| E-032.M1 | RM | Modal: Rezolvare Conflict | Modal / Overlay | Specific P2 |  | ✓ |  | Action | E-032 | F118 | 1 | Medie | ✓ | P1 | Opțiuni: re-alocare, amânare |
| E-033 | RM | HR — Echipe & Personal | Ecran | Specific P2 |  | ✓ |  | List+Detail | — | F107, F108, F109, F110, F111 | 5 | Medie | ✓ | P1 | Personal, competențe, alocare |
| E-033.M1 | RM | Modal: Fișă Angajat | Modal / Overlay | Specific P2 |  | ✓ |  | Detail | E-033 | F107, F109 | 2 | Medie | ✓ | P1 | Date + calendar + istoric |
| E-034 | RM | Echipamente & Utilaje | Ecran | Specific P2 |  | ✓ |  | List+Detail | — | F110, F111 | 2 | Medie | ✓ | P1 | Status, alocare, mentenanță |
| E-034.M1 | RM | Modal: Echipament Detail | Modal / Overlay | Specific P2 |  | ✓ |  | Detail | E-034 | F110 | 1 | Scăzută | ✓ | P1 | Istoric + mentenanță |
| E-035 | RM | Materiale & Stocuri | Ecran | Specific P2 |  | ✓ |  | List+Detail | — | F112, F113, F114 | 3 | Medie | ✓ | P1 | Stocuri, alertă, comenzi |
| E-035.M1 | RM | Modal: Comandă Rapidă | Modal / Overlay | Specific P2 |  | ✓ |  | Form | E-035 | F113 | 1 | Scăzută | ✓ | P1 | Material, cantitate, furnizor |
| E-036 | RM | Company Capacity | Ecran | Specific P2 |  | ✓ |  | Dashboard | — | F121, F122 | 2 | Ridicată | ✓ | P0 | Heatmap, simulare what-if |
| E-037 | PM | Import Engine — Devize | Ecran | Specific P2 |  | ✓ |  | Wizard | — | F123 | 1 | Ridicată | ✓ | P0 | 4 steps |
| E-037.S1 | PM | Import: Step 1 Sursă | Sub-ecran (tab) | Specific P2 |  | ✓ |  | Selector | E-037 | F123 | 1 | Scăzută | ✓ | P1 | Intersoft / eDevize / CSV |
| E-037.S2 | PM | Import: Step 2 Upload | Sub-ecran (tab) | Specific P2 |  | ✓ |  | Upload+Table | E-037 | F123 | 1 | Medie | ✓ | P1 | Upload + preview + erori |
| E-038 | PM | Gantt Dual-Layer | Ecran | Specific P2 |  | ✓ |  | Gantt+RM | — | F083, F084, F117, F118 | 4 | Foarte ridicată | ✓ | P0 | Toggle resurse ON/OFF |
| E-039 | PM | SdL Generator | Ecran | Specific P2 |  | ✓ |  | Wizard+Table | — | F078, F079 | 2 | Medie | ✓ | P1 | Articole, cantități, PDF |
| E-040 | RM | Financial Planning RM | Ecran | Specific P2 |  | ✓ |  | Dashboard | — | F115, F116 | 2 | Medie | ✓ | P1 | Cost RM per proiect |
| E-041 | BI | Reports Builder | Ecran | Specific P3 |  |  | ✓ | Builder | — | F148, F152 | 2 | Ridicată | ✓ | P2 | Drag & drop, templates |
| C-001 | Sistem | Confirmare Ștergere | Component | Comun | ✓ | ✓ | ✓ | Confirm | Global | — | 0 | Scăzută | ✓ | P1 | Pattern reutilizat: Ești sigur? |
| C-002 | Sistem | Toast Notifications | Component | Comun | ✓ | ✓ | ✓ | Toast | Global | — | 0 | Scăzută | ✓ | P1 | 4 variante: success/error/warn/info |
| C-003 | Sistem | Empty State Pattern | Component | Comun | ✓ | ✓ | ✓ | Empty state | Global | — | 0 | Scăzută | ✓ | P2 | Icon + mesaj + CTA |
| C-004 | Sistem | Skeleton Loader | Component | Comun | ✓ | ✓ | ✓ | Skeleton | Global | — | 0 | Scăzută | ✓ | P2 | Shimmer: card, row, KPI |
| C-005 | Sistem | PDF Preview Modal | Component | Comun | ✓ | ✓ | ✓ | Preview | Global | — | 0 | Medie | ✓ | P1 | Iframe PDF + download/print |

## Sheet: Navigare & Flow

| De la | Acțiune / Trigger | Către | Tip Navigare | Scope | Condiție |
| E-001 Dashboard | Click card Pipeline | E-009 Pipeline Kanban | Navigate | Comun |  |
| E-001 Dashboard | Click card Proiecte | E-013 Projects Lista | Navigate | Comun |  |
| E-001 Dashboard | Click widget energie | E-029 Post-Exec Energy | Navigate | P1 only | Widget vizibil doar P1 |
| E-001 Dashboard | Click widget RM | E-032 Resource Dashboard | Navigate | P2 only | Widget vizibil doar P2 |
| E-002 Contacts Lista | Click rând | E-003 Contact Detail | Navigate | Comun |  |
| E-002 Contacts Lista | Click '+ Contact' | E-003 (create mode) | Navigate | Comun | Formular gol |
| E-003 Contact Detail | Tab Proprietăți → click | E-028 Technical Data | Navigate | P1 only |  |
| E-003 Contact Detail | Tab Oferte → click ofertă | E-006 Offer Detail | Navigate | Comun |  |
| E-003 Contact Detail | '+ Ofertă nouă' | E-005 Offer Builder | Navigate | Comun | Pre-selectează client |
| E-003 Contact Detail | '+ Persoană' | E-003.M1 Modal Persoană | Modal | Comun |  |
| E-003 Contact Detail | 'Compară & Merge' | E-003.M2 Modal Duplicate | Modal | Comun | Doar dacă duplicat detectat |
| E-003 Contact Detail | 'Upload document' | E-003.M3 Modal Upload | Modal | Comun |  |
| E-005 Offer Builder | Step 2 → '+ Produs' | E-005.M1 Product Picker | Modal | Comun |  |
| E-005 Offer Builder | Step 5 → Generează | E-006 Offer Detail | Navigate | Comun | Creează oferta |
| E-006 Offer Detail | 'Compară versiuni' | E-006.M1 Version Diff | Modal | Comun |  |
| E-006 Offer Detail | 'Convertește → Contract' | E-007 Contract Builder | Navigate | Comun | Pre-populat |
| E-007 Contract Builder | 'Workflow aprobare' | E-007.M1 Modal Aprobare | Modal | Comun |  |
| E-007 Contract Builder | Semnare finalizată | E-014 Project Detail | Nav+Create | Comun | Auto-creare proiect |
| E-009 Pipeline Kanban | Click card | E-009.M1 Slide-over Quick | Slide-over | Comun |  |
| E-009 Pipeline Kanban | Double-click card | E-010 Opportunity Detail | Navigate | Comun |  |
| E-009 Pipeline Kanban | Drag card | E-009 (self) | Update | Comun | Status + timestamp |
| E-010 Opportunity Detail | 'Creează ofertă' | E-005 Offer Builder | Navigate | Comun | Pre-select client |
| E-010 Opportunity Detail | Mutare Won/Lost | E-010.M1 Won/Lost Reason | Modal | Comun | Motiv obligatoriu |
| E-011 Activity Planner | '+ Activitate' | E-011.M1 Modal Activitate | Modal | Comun |  |
| E-013 Projects Lista | Click proiect | E-014 Project Detail | Navigate | Comun |  |
| E-014 Project Detail | Tab WBS | E-015 WBS Editor | Tab switch | Comun | Lazy loaded |
| E-014 Project Detail | Tab Gantt | E-016 / E-038 | Tab switch | Comun/P2 | P2=Dual-Layer |
| E-014 Project Detail | Tab Deviz | E-017 Deviz Tracker | Tab switch | Comun |  |
| E-014 Project Detail | Tab Execuție | E-018/E-019 | Tab switch | Comun | Toggle Timesheet/Consum |
| E-014 Project Detail | Tab Post-Exec | E-029 Post-Exec Energy | Tab switch | P1 only | Doar P1 |
| E-014 Project Detail | Tab RM | E-014.7 Mini RM | Tab switch | P2 only | Doar P2 |
| E-014 Project Detail | Tab Raportare | E-020 Reporting | Tab switch | Comun |  |
| E-014 Project Detail | Schimbare status | E-014.M1 Confirm Status | Modal | Comun |  |
| E-014 Project Detail | 'Recepție' | E-021 Recepție | Navigate | Comun | Status=Post-Exec |
| E-015 WBS Editor | '+ Nod' | E-015.M1 Modal WBS | Modal | Comun |  |
| E-017 Deviz Tracker | '+ Articol' | E-017.M1 Modal Articol | Modal | Comun |  |
| E-017 Deviz Tracker | 'Import deviz' | E-037 Import Engine | Modal/Wizard | P2 only | Buton doar P2 |
| E-017 Deviz Tracker | 'Generează SdL' | E-039 SdL Generator | Modal/Wizard | P2 only | Buton doar P2 |
| E-019 Fișe Consum | '+ Înregistrare' | E-019.M1 Modal Consum | Modal | Comun |  |
| E-021 Recepție | '+ Defect' | E-021.M1 Modal Defect | Modal | Comun |  |
| E-023 Wiki | 'Istoric versiuni' | E-023.M1 Modal Versiuni | Modal | Comun |  |
| E-024 Settings | '+ Invită user' | E-024.M1 Modal Invită | Modal | Comun |  |
| E-029 Post-Exec | 'Adaugă la ML' | E-030 Data→ML | Navigate | P1 only |  |
| E-030 Data→ML | Click model | E-030.M1 Modal Model | Modal | P1 only | Expand detalii |
| E-032 Resource Dash | Click conflict | E-032.M1 Rezolvare | Modal | P2 only |  |
| E-032 Resource Dash | Click echipă | E-033 HR | Navigate | P2 only |  |
| E-032 Resource Dash | Click echipament | E-034 Echipamente | Navigate | P2 only |  |
| E-032 Resource Dash | Click stoc | E-035 Materiale | Navigate | P2 only |  |
| E-033 HR | Click angajat | E-033.M1 Fișă Angajat | Modal | P2 only |  |
| E-034 Echipamente | Click echipament | E-034.M1 Detail | Modal | P2 only |  |
| E-035 Materiale | 'Comandă rapidă' | E-035.M1 Modal Comandă | Modal | P2 only |  |
| E-027 App Shell | Cmd+K | E-026 Global Search | Modal | Comun |  |
| E-027 App Shell | Click notification bell | E-025 Notifications | Dropdown | Comun | Badge count |
| E-027 App Shell | Sidebar click modul | Ecranul principal modul | Navigate | Comun | Meniu diferit/prototip |

## Sheet: Statistici V3

| Metric | Total | Ecrane | Sub-ecrane | Modale | Componente | Done | De făcut |
| Total itemi masterplan | 98 | 41 | 30 | 22 | 5 | 49 | 49 |
| Scope Comun | 71 | 27 | 22 | 17 | 5 |  |  |
| Scope Specific P1 | 10 | 4 | 5 | 1 | 0 |  |  |
| Scope Specific P2 | 16 | 9 | 3 | 4 | 0 |  |  |
| Scope Specific P3 | 1 | 1 | 0 | 0 | 0 |  |  |
| Prioritate P0 | 24 |  |  |  |  |  |  |
| Prioritate P1 | 49 |  |  |  |  |  |  |
| Prioritate P2 | 25 |  |  |  |  |  |  |
| Navigări documentate | 54 |  |  |  |  |  |  |
| Ecrane per prototip P1 (Comun+P1) | 81 |  |  |  |  |  |  |
| Ecrane per prototip P2 (Comun+P2) | 87 |  |  |  |  |  |  |
| Ecrane per prototip P3 (Comun+P3) | 72 |  |  |  |  |  |  |

## Sheet: Roadmap Wireframes

| Faza | Itemi | Tip | Nr. | Efort | Dependențe | Observații |
| Faza 0
(DONE) | E-001 Dashboard
E-002 Contacts Lista
E-003 Contact Detail (Tab 1)
E-005 Offer Builder (Step 3)
E-009 Pipeline Kanban
E-014 Project Hub (Overview)
E-016 Gantt
E-028 Technical Data (Tab 1)
E-029 Post-Exec Energy
E-030 Data→ML | Ecrane
principale | 9 | Completat | — | Wireframe-uri V1. Unele au doar 1 tab vizibil. |
| Faza 1
(DONE) | E-003 Contact Detail (completare)
E-015 WBS Editor
E-017 Deviz Tracker
E-027 App Shell
E-032 Resource Dashboard (P2)
E-036 Company Capacity (P2)
E-037 Import Engine (P2)
E-038 Gantt Dual-Layer (P2) | Ecrane
principale | 8 | Completat | Faza 0 | Ecrane P0 critice comune + P2. |
| Faza 2
(DONE) | E-004 Catalog · E-006 Offer Lifecycle · E-007 Contract Builder
E-010 Opportunity Detail · E-011 Activity Planner
E-018 Timesheet · E-019 Fișe Consum · E-020 Reporting
E-033 HR · E-034 Echipamente · E-035 Materiale
E-039 SdL Generator · E-040 Financial Planning | Ecrane
principale | 13 | Completat | Faza 1 | Ecrane P1 importante comune + P2. |
| Faza 3
(DONE) | E-008 Contracts Pipeline · E-012 Analytics · E-013 Projects Lista
E-021 Recepție · E-022 BI Dashboard · E-023 Wiki
E-024 Settings · E-025 Notifications · E-026 Search
E-031 AI Assistant (P1) · E-041 Reports Builder (P3) | Ecrane
principale | 11 | Completat | Faza 2 | Ecrane P2 utile + specifice P1/P3. |
| Faza 4
(NEXT) | Sub-ecrane tab-uri: E-003.2–.5, E-005.S1/S2/S4/S5
E-010.1, E-014.7, E-024.1–.5, E-025.1
E-028.1–.4, E-037.S1/S2 | Sub-ecrane
(tab-uri) | 21 | ~4-5 ore | Faza 3 | Tab-uri individuale cu layout propriu |
| Faza 5 | Modale: E-003.M1–M3, E-004.M1, E-005.M1, E-006.M1
E-007.M1, E-009.M1, E-010.M1, E-011.M1, E-014.M1
E-015.M1, E-017.M1, E-019.M1, E-021.M1, E-023.M1
E-024.M1, E-030.M1, E-032.M1, E-033.M1, E-034.M1
E-035.M1 | Modale &
Overlay-uri | 21 | ~3-4 ore | Faza 4 | Pattern-uri reutilizabile, multe similare |
| Faza 6 | C-001 Confirmare Ștergere · C-002 Toast · C-003 Empty State
C-004 Skeleton Loader · C-005 PDF Preview | Componente
globale | 5 | ~1-2 ore | Faza 5 | Design tokens + variante |
