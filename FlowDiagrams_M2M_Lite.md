## Sheet: Index

### M2M ERP LITE — FLUXURI FUNCȚIONALE (SWIM LANE)

Produs SaaS generic V6 — 7 fluxuri: onboarding, business, analytics, admin, vertical flex, integrare

| # | Flux | Actori (Swim Lanes) | Frecvență | Pași | SaaS P3 | Verdict |
| 1 | Tenant Onboarding — Client SaaS Nou | Client Admin / Sistem | PER CLIENT NOU | 15 | 10 | ✓ COMPLET |
| 2 | Ciclu Complet Vânzare (cu features SaaS) | Agent Vânzări / Client / Sistem | PER DEAL | 13 | 5 | ✓ COMPLET |
| 3 | Ciclu Proiect cu Analytics & Predictive | Project Manager / BI / Management / Sistem | PER PROIECT | 15 | 1 | ✓ COMPLET |
| 4 | Resource Management — Ciclu Complet | HR / Achiziții / Director Operațiuni / Sistem | CONTINUU | 14 | — | ✓ COMPLET |
| 5 | Administrare Platformă SaaS | Administrator / Sistem | PERIODIC | 11 | 5 | ✓ COMPLET |
| 6 | Adaptare Verticală — Construcții vs IT Services | Vertical Construcții / Vertical IT Services / Platformă (comun) | PER VERTICAL | 15 | 6 | ✓ COMPLET |
| 7 | Data Lifecycle — De la CRM la Predictive Analytics | Utilizator / Modul curent / Date propagate | TEST INTEGRARE | 21 | 1 | ✓ COMPLET |
| TOTAL |  |  |  | 104 | 28 | 7/7 COMPLETE |
⚠ OBSERVAȚIE: 14 funcții au încă terminologie construcții în descriere (WBS, deviz, RZS, șantier). Descrierile P3 includ varianta generică „Construcții: X. Generic: Y." dar funcționalitățile (F069, F071, F077, F079) ar beneficia de redenumire în P3.  [→ E-015 | E-015/E-016 | E-017 | E-017/E-039]


## Sheet: 1 — Tenant Onboarding

### FLUX 1: Tenant Onboarding — Client SaaS Nou

### Self-service — prima conectare la platformă  ⏱ PER CLIENT NOU

| # | CLIENT ADMIN |  | SISTEM |  |
| 1 | Accesează platforma — prima autentificare | F160  [→ E-024] |  |  |
| 2 |  |  | Wizard Step 1: date companie (denumire, CUI, adresă) | F160  [→ E-024] |
| 3 | Wizard Step 2: alege branding (logo, culori) | F137  [→ E-024] |  |  |
| 4 | Wizard Step 3: alege limba principală | F138  [→ E-024] |  |  |
| 5 | Wizard Step 4: configurează monede | F139  [→ E-024] |  |  |
| 6 | Wizard Step 5: creează utilizatori + roluri | F040  [→ E-024] |  |  |
| 7 | Wizard Step 6: selectează module active | F136  [→ E-024] |  |  |
| 8 |  |  | Generare automată: navigation, sidebar, dashboard | F157+F158  [→ E-027] |
| 9 | Configurez stadii pipeline (CRM) | F039  [→ E-024] |  |  |
| 10 | Configurez tipuri proiect (PM) | F106  [→ E-024] |  |  |
| 11 | Configurez categorii resurse (RM) | F131  [→ E-024] |  |  |
| 12 | Configurez stadii pipeline (Sales) | F061  [→ E-024] |  |  |
| 13 |  |  | Notificări active, audit log pornit, sync activ | F141+F041+F143  [→ E-024 | E-025] |
| 14 | Import contacte existente (CSV/Excel) | F004  [→ E-003] |  |  |
| 15 | ◇ Onboarding complet — platforma e live | — |  |  |
### ✓ COMPLET — 15 pași, 10 SaaS-specifice

### SCOP: Verifică: F160 + toată infrastructura SaaS funcționează  [→ E-024]

### LEGENDĂ:

### ● Acțiune manuală

### ⚡ Automat / Sistem

### ◆ Colectare date

### ◇ Gate / Tranziție

### ⬡ Decizie

### ◆ SaaS-specific (P3)


## Sheet: 2 — Ciclu Vânzare SaaS

### FLUX 2: Ciclu Complet Vânzare (cu features SaaS)

### Lead → Contract cu oferte multilingve, multivalută, branding custom  ⏱ PER DEAL

| # | AGENT VÂNZĂRI |  | CLIENT |  | SISTEM |  |
| 1 | Creez contact + asociez active (Asset Data) | F001+F010  [→ E-002/E-003 | E-028] |  |  |  |  |
| 2 | Calific → Handover → Pipeline Board | F003→F042→F050  [→ E-003 | E-009 | E-009/E-010] |  |  |  |  |
| 3 | Deal Scoping: milestone-uri + predimensionare | F043-F048  [→ E-010] |  |  |  |  |
| 4 | Offer Builder: estimări în EUR + RON simultan | F019  [→ E-005] |  |  |  |  |
| 5 |  |  |  |  | Sistem aplică cursul de schimb configurat | F139  [→ E-024] |
| 6 | Preview ofertă: layout + logo din branding custom | F023  [→ E-005] |  |  |  |  |
| 7 | ◇ Aprobare ofertă | F028  [→ E-006] |  |  |  |  |
| 8 | Export ofertă PDF — cromatică Private Label | F023  [→ E-005] |  |  |  |  |
| 9 |  |  | Client primește oferta branded | — |  |  |
| 10 | Ofertă acceptată → Contract Builder | F031  [→ E-007] |  |  |  |  |
| 11 | Contract bilingv (RO + EN) din template | F033  [→ E-007] |  |  |  |  |
| 12 |  |  |  |  | Auto-generare grafic facturare multivalută | F035  [→ E-007] |
| 13 |  |  |  |  | ⚡ Contract Semnat → Trigger Project Setup | F031→F063  [→ E-007 | E-014] |
### ✓ COMPLET — 13 pași, 5 SaaS-specifice

### SCOP: Verifică: Multi-language + multi-currency funcționează în fluxul de vânzare

### LEGENDĂ:

### ● Acțiune manuală

### ⚡ Automat / Sistem

### ◆ Colectare date

### ◇ Gate / Tranziție

### ⬡ Decizie

### ◆ SaaS-specific (P3)


## Sheet: 3 — Proiect + BI

### FLUX 3: Ciclu Proiect cu Analytics & Predictive

### Execuție proiect cu KPI monitoring și previziuni ML  ⏱ PER PROIECT

| # | PROJECT MANAGER |  | BI / MANAGEMENT |  | SISTEM |  |
| 1 |  |  |  |  | Auto-creare proiect + import milestones | F063  [→ E-014] |
| 2 | Planificare: WBS → Gantt → Buget | F069+F070+F080  [→ E-015 | E-020/E-021] |  |  |  |  |
| 3 | Alocare resurse din RM | F083  [→ E-016] |  |  |  |  |
| 4 | Execuție zilnică: ore, consum, status task-uri | F072-F074  [→ E-017/E-019 | E-018] |  |  |  |  |
| 5 | Generez Situație → Emit factură | F079→F035  [→ E-007 | E-017/E-039] |  |  |  |  |
| 6 |  |  |  |  | P&L automat: surse venituri + costuri | F091  [→ E-020] |
| 7 |  |  | Creez KPI custom: rată avansare proiect | F148  [→ E-022] |  |  |
| 8 |  |  | Setez praguri: Slab / Bun / Excelent | F148  [→ E-022] |  |  |
| 9 |  |  |  |  | KPI Dashboard: gauge + trend + ranking | F152  [→ E-022] |
| 10 |  |  | Drill-down: lunar, trimestrial | F152  [→ E-022] |  |  |
| 11 |  |  | Project Reports: schedule + financial 3-in-1 | F095  [→ E-020] |  |  |
| 12 |  |  | Executive Dashboard: cross-module agregat | F133  [→ E-022] |  |  |
| 13 |  |  | ★ Predictive Analytics: ML pe date istorice | F135  [→ E-022] |  |  |
| 14 |  |  | Dashboard investitor: subset read-only | F100  [→ E-020/E-022] |  |  |
| 15 | Closeout + arhivare → date alimentează ML | F086+F090  [→ E-029] |  |  |  |  |
### ✓ COMPLET — 15 pași, 1 SaaS-specifice

### SCOP: Verifică: PM + BI + Predictive funcționează integrat

### LEGENDĂ:

### ● Acțiune manuală

### ⚡ Automat / Sistem

### ◆ Colectare date

### ◇ Gate / Tranziție

### ⬡ Decizie

### ◆ SaaS-specific (P3)


## Sheet: 4 — RM Full Cycle

### FLUX 4: Resource Management — Ciclu Complet

### HR → Alocare → Consum → Rapoarte → Planificare Financiară  ⏱ CONTINUU

| # | HR / ACHIZIȚII |  | DIRECTOR OPERAȚIUNI |  | SISTEM |  |
| 1 | CRUD angajați + salarizare + competențe | F107-F111  [→ E-033 | E-034] |  |  |  |  |
| 2 | Calendar: disponibilitate, concedii | F109  [→ E-033] |  |  |  |  |
| 3 | Achiziții: comandă → NIR → factură → stoc | F112-F114  [→ E-035] |  |  |  |  |
| 4 |  |  | Alocă angajați + materiale pe proiecte | F117  [→ E-032] |  |  |
| 5 |  |  |  |  | Sync RM↔PM bidirecțional | F083+F143  [→ E-016 | E-024] |
| 6 |  |  |  |  | Consum real: ore (timesheet) + materiale (fișe) | F072+F074  [→ E-017/E-019 | E-018] |
| 7 |  |  | Urmărire consum vs alocare real-time | F118  [→ E-032] |  |  |
| 8 |  |  | Rebalansare resurse între proiecte | F117  [→ E-032] |  |  |
| 9 |  |  | Rapoarte utilizare per angajat/material/proiect | F121  [→ E-036] |  |  |
| 10 |  |  | Evaluare eficiență: plan vs real | F119  [→ E-032] |  |  |
| 11 |  |  | Planificare financiară: bugete per centru cost | F115  [→ E-040] |  |  |
| 12 |  |  | Analiză costuri reale vs bugetate | F116  [→ E-040] |  |  |
| 13 |  |  |  |  | Global P&L + Cash Flow consolidat | F093+F094  [→ E-020] |
| 14 |  |  | TrueCast: Actual vs Forecast | F140  [→ E-020] |  |  |
### ✓ COMPLET — 14 pași

### SCOP: Verifică: întregul modul RM funcționează cap-coadă cu PM + Finance

### LEGENDĂ:

### ● Acțiune manuală

### ⚡ Automat / Sistem

### ◆ Colectare date

### ◇ Gate / Tranziție

### ⬡ Decizie

### ◆ SaaS-specific (P3)


## Sheet: 5 — Platform Admin

### FLUX 5: Administrare Platformă SaaS

### Branding, localizare, roluri, sync — operațiuni platformă  ⏱ PERIODIC

| # | ADMINISTRATOR |  | SISTEM |  |
| 1 | Modifică branding: logo nou, palete culori | F137  [→ E-024] |  |  |
| 2 |  |  | Preview: toate documentele reflectă noul branding | F023+F033  [→ E-005 | E-007] |
| 3 | Adaugă limbă nouă (ex: FR pe lângă RO+EN) | F138  [→ E-024] |  |  |
| 4 | Adaugă valută nouă (ex: GBP) | F139  [→ E-024] |  |  |
| 5 | Creez rol nou: „Supervizor Șantier" | F040  [→ E-024] |  |  |
| 6 | Setez permisiuni granulare per modul | F040  [→ E-024] |  |  |
| 7 | Configurez notificări per rol + triggers | F141  [→ E-025] |  |  |
| 8 |  |  | Audit log: verifică cine ce a modificat | F041  [→ E-024] |
| 9 |  |  | Sync engine: verifică integritate cross-module | F143  [→ E-024] |
| 10 | Export global: backup configurație | F142  [→ E-026] |  |  |
| 11 | AI Assistant: activez chatbot pentru utilizatori | F132  [→ E-031] |  |  |
### ✓ COMPLET — 11 pași, 5 SaaS-specifice

### SCOP: Verifică: infrastructura SaaS se administrează coerent

### LEGENDĂ:

### ● Acțiune manuală

### ⚡ Automat / Sistem

### ◆ Colectare date

### ◇ Gate / Tranziție

### ⬡ Decizie

### ◆ SaaS-specific (P3)


## Sheet: 6 — Vertical Flex

### FLUX 6: Adaptare Verticală — Construcții vs IT Services

### Același produs, configurație diferită — SaaS multi-vertical  ⏱ PER VERTICAL

| # | VERTICAL CONSTRUCȚII |  | VERTICAL IT SERVICES |  | PLATFORMĂ (COMUN) |  |
| 1 |  |  |  |  | Tenant Onboarding: wizard identic ambele | F160  [→ E-024] |
| 2 | Asset Data = Property Profile (clădiri, energie) | F010+F012  [→ E-028] |  |  |  |  |
| 3 |  |  | Asset Data = Client Systems (servere, licențe) | F010  [→ E-028] |  |  |
| 4 | Products = sticlă tratată, tâmplărie PVC | F007  [→ E-004] |  |  |  |  |
| 5 |  |  | Products = implementare ERP, consultanță, SLA | F007  [→ E-004] |  |  |
| 6 | Import Engine = devize Intersoft, eDevize | F123  [→ E-037] |  |  |  |  |
| 7 |  |  | Import Engine = project plan CSV, Jira export | F123  [→ E-037] |  |  |
| 8 | Work Tracker = deviz cu articole + cantități | F125  [→ E-017] |  |  |  |  |
| 9 |  |  | Work Tracker = tasks cu ore + cost per sprint | F125  [→ E-017] |  |  |
| 10 | Site Ops = RZS, consum materiale, subcontractori | F077+F074+F075  [→ E-017 | E-017/E-019 | E-019] |  |  |  |  |
| 11 |  |  | Site Ops = daily standup log, ore remote, vendors | F077+F072+F075  [→ E-017 | E-018 | E-019] |  |  |
| 12 |  |  |  |  | Pipeline, Offers, Contracts — IDENTICE | F050+F019+F031  [→ E-005 | E-007 | E-009] |
| 13 |  |  |  |  | Time Tracking, Budget, KPIs — IDENTICE | F072+F080+F148  [→ E-018 | E-020/E-021 | E-022] |
| 14 |  |  |  |  | P&L, Cash Flow, Reporting — IDENTICE | F091+F092+F095  [→ E-020] |
| 15 |  |  |  |  | Concluzie: 85% platformă identică, 15% config | — |
### ✓ COMPLET — 15 pași, 6 SaaS-specifice

### SCOP: Verifică: Asset Data, Import Engine, Work Tracker se adaptează per industrie

### LEGENDĂ:

### ● Acțiune manuală

### ⚡ Automat / Sistem

### ◆ Colectare date

### ◇ Gate / Tranziție

### ⬡ Decizie

### ◆ SaaS-specific (P3)


## Sheet: 7 — Data Lifecycle

### FLUX 7: Data Lifecycle — De la CRM la Predictive Analytics

### Un singur data point traversează toate 6 modulele  ⏱ TEST INTEGRARE

| # | UTILIZATOR |  | MODUL CURENT |  | DATE PROPAGATE |  |
| 1 | Agent creează contact „Firma ABC" în CRM | F001  [→ E-002/E-003] |  |  |  |  |
| 2 |  |  | CRM: contact salvat cu Asset Data | CRM |  |  |
| 3 | Agent califică → Handover → oportunitate | F042  [→ E-009/E-010] |  |  |  |  |
| 4 |  |  | Sales Pipeline: oportunitate cu link la contact | Pipeline |  |  |
| 5 | Deal Scoping: 10 milestone-uri, buget 50K€ | F043-F048  [→ E-010] |  |  |  |  |
| 6 |  |  |  |  | Date propagate: contact + milestone-uri + buget | CRM→Pipeline |
| 7 | Offer Builder preia milestone-uri + prețuri | F019  [→ E-005] |  |  |  |  |
| 8 | Contract semnat → Trigger proiect | F031→F063  [→ E-007 | E-014] |  |  |  |  |
| 9 |  |  |  |  | Date propagate: client + contract + milestones → PM | Pipeline→PM |
| 10 |  |  | PM: proiect creat cu WBS + Gantt + buget | PM |  |  |
| 11 | RM alocă 3 angajați pe proiect | F117  [→ E-032] |  |  |  |  |
| 12 |  |  |  |  | Date propagate: angajați + rate orare → PM | RM→PM |
| 13 | Echipa loguiește 160h în luna 1 | F072  [→ E-018] |  |  |  |  |
| 14 |  |  |  |  | Date propagate: ore × rată → cost personal → P&L | PM→Finance |
| 15 | PM creează KPI „Cost per oră efectivă" | F148  [→ E-022] |  |  |  |  |
| 16 |  |  |  |  | Date propagate: timesheet + salarizare → KPI Engine | PM+RM→BI |
| 17 |  |  | BI: KPI Dashboard afișează trend | BI |  |  |
| 18 | Executive Dashboard: agregare cross-module | F133  [→ E-022] |  |  |  |  |
| 19 |  |  |  |  | Date propagate: CRM+Pipeline+PM+RM → Dashboard | ALL→BI |
| 20 | Predictive: ML estimează cost final proiect | F135  [→ E-022] |  |  |  |  |
| 21 |  |  |  |  | ✓ Data point „Firma ABC" a traversat 6 module | CRM→Pipe→PM→RM→BI→Sistem |
### ✓ COMPLET — 21 pași, 1 SaaS-specifice

### SCOP: Verifică: datele curg fără ruptură prin CRM → Pipeline → PM → RM → BI → Sistem

### LEGENDĂ:

### ● Acțiune manuală

### ⚡ Automat / Sistem

### ◆ Colectare date

### ◇ Gate / Tranziție

### ⬡ Decizie

### ◆ SaaS-specific (P3)

