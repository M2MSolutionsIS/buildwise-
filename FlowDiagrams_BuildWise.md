## Sheet: Index

### BUILDWISE TRL5 — FLUXURI FUNCȚIONALE (SWIM LANE)

### M2M ERP Lite V6 — 9 fluxuri verificate cap-coadă, 0 gap-uri

| # | Flux | Actori (Swim Lanes) | Pași | Dif. ★ | Verdict |
| 1 | Lead → Client | Agent Vânzări / Sistem / Manager | 12 | 2 ★ | ✓ COMPLET |
| 2 | Oportunitate → Ofertă → Contract | Agent Vânzări / Sistem / Manager / Aprobator | 19 | — | ✓ COMPLET |
| 3 | Project Setup → Planificare | Project Manager / Sistem / Director | 12 | — | ✓ COMPLET |
| 4 | Execuție Proiect | Echipă Șantier / Project Manager / Sistem | 12 | — | ✓ COMPLET |
| 5 | Financiar | CFO / Director / Sistem / Investitor | 10 | — | ✓ COMPLET |
| 6 | Energy / AI ★ | Agent / Tehnic / Project Manager / Sistem / ML | 10 | 8 ★ | ✓ COMPLET |
| 7 | Reporting & KPI | Manager / Sistem / Echipă | 10 | — | ✓ COMPLET |
| 8 | Admin & Setup | Administrator / Sistem | 10 | — | ✓ COMPLET |
| 9 | Închidere Proiect | Project Manager / Client / Sistem | 12 | 3 ★ | ✓ COMPLET |
| TOTAL |  |  | 107 | 13 ★ | 9/9 COMPLETE |

## Sheet: 1 — Lead → Client

### FLUX 1: Lead → Client

### Achiziție & Calificare Contact

| # | AGENT VÂNZĂRI |  | SISTEM |  | MANAGER |  |
| 1 | Primesc lead (telefon/email/recomandare) | F001  [→ E-002/E-003] |  |  |  |  |
| 2 |  |  | Verificare automată duplicat | F005  [→ E-003] |  |  |
| 3 | Completez fișă: CUI, adresă, contact, fiscale | F001  [→ E-002/E-003] |  |  |  |  |
| 4 | Marchez stadiu: Prospect | F003  [→ E-003] |  |  |  |  |
| 5 | Asociez proprietate (clădirea clientului) | F010  [→ E-028] |  |  |  |  |
| 6 | ★ Completez Energy Profile: U, HVAC, suprafețe | F012  [→ E-028] |  |  |  |  |
| 7 | Programez vizită tehnică în calendar | F054  [→ E-011] |  |  |  |  |
| 8 | ★ Vizită: documentez foto + măsurători | F055  [→ E-011] |  |  |  |  |
| 9 | Loguez apel follow-up | F056  [→ E-011/E-012] |  |  |  |  |
| 10 |  |  | Actualizare automată Istoric Interacțiuni | F002  [→ E-002] |  |  |
| 11 |  |  | Trigger automat → stadiu Client Potențial | F003  [→ E-003] |  |  |
| 12 | ◇ GATE: Calificat → Handover în Pipeline | F042  [→ E-009/E-010] |  |  |  |  |
### ✓ COMPLET — 12 pași, 2 diferențiatori ★

### LEGENDĂ:

### ● Acțiune manuală

### ⚡ Automat / Sistem

### ◆ Colectare date

### ◇ Gate / Tranziție

### ⬡ Decizie / Aprobare

### ★ Diferențiator Energy/ML


## Sheet: 2 — Oport → Contract

### FLUX 2: Oportunitate → Ofertă → Contract

### Ciclu complet de vânzare

| # | AGENT VÂNZĂRI |  | SISTEM |  | MANAGER / APROBATOR |  |
| 1 |  |  | Auto-creare oportunitate la Handover | F042→F050  [→ E-009 | E-009/E-010] |  |  |
| 2 | Văd oportunitatea pe Kanban: stadiu NOU | F050  [→ E-009] |  |  |  |  |
| 3 | Drag → CALIFICAT (validare automată) | F051  [→ E-009] |  |  |  |  |
| 4 | Încarc template milestone din bibliotecă | F048  [→ E-010] |  |  |  |  |
| 5 | Ajustez milestone-uri: durate, secvențe | F043-F047  [→ E-010] |  |  |  |  |
| 6 | Predimensionez: resurse + costuri estimate | F045  [→ E-010] |  |  |  |  |
| 7 | Aloc sarcini pe responsabili | F046  [→ E-010] |  |  |  |  |
| 8 | Drag → OFERTARE | F051  [→ E-009] |  |  |  |  |
| 9 | Offer Builder: wizard complet | F019  [→ E-005] |  |  |  |  |
| 10 | Preview ofertă + Export PDF/DOC | F023  [→ E-005] |  |  |  |  |
| 11 | ◇ GATE: Submit la aprobare | F028  [→ E-006] |  |  |  |  |
| 12 |  |  |  |  | ⬡ DECIZIE: Review → Approve / Reject | F028  [→ E-006] |
| 13 |  |  | Snapshot v1 imutabil | F026  [→ E-005] |  |  |
| 14 | Trimit ofertă la client | F027  [→ E-006] |  |  |  |  |
| 15 | ◇ GATE: Ofertă ACCEPTATĂ | F027  [→ E-006] |  |  |  |  |
| 16 | Contract Builder (din ofertă) | F031  [→ E-007] |  |  |  |  |
| 17 | Preview + Export contract | F033  [→ E-007] |  |  |  |  |
| 18 |  |  | Auto-generare grafic facturare | F035  [→ E-007] |  |  |
| 19 |  |  | ⚡ Contract Semnat → Trigger Project Setup | F031→F063  [→ E-007 | E-014] |  |  |
### ✓ COMPLET — 19 pași, nicio ruptură

### LEGENDĂ:

### ● Acțiune manuală

### ⚡ Automat / Sistem

### ◆ Colectare date

### ◇ Gate / Tranziție

### ⬡ Decizie / Aprobare

### ★ Diferențiator Energy/ML


## Sheet: 3 — Project Setup

### FLUX 3: Project Setup → Planificare

### Inițializare & Structurare Proiect

| # | PROJECT MANAGER |  | SISTEM |  | DIRECTOR |  |
| 1 |  |  | Auto-creare proiect la semnare contract | F063  [→ E-014] |  |  |
| 2 | Completez checklist kickoff | F063  [→ E-014] |  |  |  |  |
| 3 |  |  | Import automat milestone-uri din Deal Scoping | F063  [→ E-014] |  |  |
| 4 |  |  | Sync automat date client din CRM | F066  [→ E-014] |  |  |
| 5 | Import deviz extern (Intersoft/eDevize/Excel) | F123  [→ E-037] |  |  |  |  |
| 6 | Vizualizez deviz: arbore ierarhic | F125  [→ E-017] |  |  |  |  |
| 7 | Creez WBS din structura devizului | F069  [→ E-015] |  |  |  |  |
| 8 | Generez Gantt cu dependențe | F070  [→ E-015] |  |  |  |  |
| 9 | Completez deviz estimativ | F071  [→ E-015/E-016] |  |  |  |  |
| 10 | Identific riscuri → Risk Register RIEM | F084  [→ E-016] |  |  |  |  |
| 11 | Setez buget per capitol WBS | F080  [→ E-020/E-021] |  |  |  |  |
| 12 | Proiect vizibil în Portfolio | F101  [→ E-013] |  |  |  |  |
### ✓ COMPLET — 12 pași, nicio ruptură

### LEGENDĂ:

### ● Acțiune manuală

### ⚡ Automat / Sistem

### ◆ Colectare date

### ◇ Gate / Tranziție

### ⬡ Decizie / Aprobare

### ★ Diferențiator Energy/ML


## Sheet: 4 — Execuție

### FLUX 4: Execuție Proiect

### Operațiuni zilnice șantier

| # | ECHIPĂ ȘANTIER |  | PROJECT MANAGER |  | SISTEM |  |
| 1 | Loguiesc ore efective pe task-uri | F072  [→ E-018] |  |  |  |  |
| 2 | Setez status task: InProgress/Blocat/Done | F073  [→ E-018] |  |  |  |  |
| 3 | Înregistrez consum materiale per WBS | F074  [→ E-017/E-019] |  |  |  |  |
| 4 | Documentez Raport Zilnic Șantier (RZS) | F077  [→ E-017] |  |  |  |  |
| 5 | Înregistrez cantități realizate pe deviz | F125  [→ E-017] |  |  |  |  |
| 6 |  |  |  |  | ⚡ Auto-update Gantt dual-layer | F070  [→ E-015] |
| 7 |  |  | Verific avansare proiect: % fizic vs plan | F078  [→ E-017] |  |  |
| 8 |  |  | Urmăresc subcontractori: valori, % | F075  [→ E-019] |  |  |
| 9 |  |  | Generez Situație de Lucrări lunară | F079  [→ E-017/E-039] |  |  |
| 10 |  |  | ◇ GATE: Link direct → Emite factură | F079→F035  [→ E-007 | E-017/E-039] |  |  |
| 11 |  |  | Verific buget: alocat vs realizat | F080  [→ E-020/E-021] |  |  |
| 12 |  |  | Atașez documente în Wiki proiect | F144-F145  [→ E-023] |  |  |
### ✓ COMPLET — 12 pași, nicio ruptură

### LEGENDĂ:

### ● Acțiune manuală

### ⚡ Automat / Sistem

### ◆ Colectare date

### ◇ Gate / Tranziție

### ⬡ Decizie / Aprobare

### ★ Diferențiator Energy/ML


## Sheet: 5 — Financiar

### FLUX 5: Financiar

### Director / CFO — Raportare financiară

| # | CFO / DIRECTOR |  | SISTEM |  | INVESTITOR |  |
| 1 |  |  | ⚡ Alimentare automată P&L din surse | F091  [→ E-020] |  |  |
| 2 | P&L per proiect: venituri vs costuri | F091  [→ E-020] |  |  |  |  |
| 3 | Cash Flow per proiect | F092  [→ E-020] |  |  |  |  |
| 4 | P&L consolidat companie (per ani fiscali) | F093  [→ E-020] |  |  |  |  |
| 5 | Cash Flow consolidat companie | F094  [→ E-020] |  |  |  |  |
| 6 | TrueCast: Actual vs Forecast cross-module | F140  [→ E-020] |  |  |  |  |
| 7 | Verific facturi restante + alerte | F066  [→ E-014] |  |  |  |  |
| 8 | Grafic facturare: ce facturi urmează | F035  [→ E-007] |  |  |  |  |
| 9 | Export rapoarte financiare | F142  [→ E-026] |  |  |  |  |
| 10 |  |  |  |  | Dashboard investitor (acces extern) | F100  [→ E-020/E-022] |
### ✓ COMPLET — 10 pași, nicio ruptură

### LEGENDĂ:

### ● Acțiune manuală

### ⚡ Automat / Sistem

### ◆ Colectare date

### ◇ Gate / Tranziție

### ⬡ Decizie / Aprobare

### ★ Diferențiator Energy/ML


## Sheet: 6 — Energy AI ★

### FLUX 6: Energy / AI ★

### Diferențiatorul BuildWise — Ciclu date → ML

| # | AGENT / TEHNIC |  | PROJECT MANAGER |  | SISTEM / ML |  |
| 1 | ★ Property Profile: clădire, materiale | F010  [→ E-028] |  |  |  |  |
| 2 | ★ Energy Profile: coef U, HVAC, suprafețe | F012  [→ E-028] |  |  |  |  |
| 3 | ★ Calculator suprafețe → input ML | F012  [→ E-028] |  |  |  |  |
| 4 | ★ Vizită: foto + măsurători reale | F055  [→ E-011] |  |  |  |  |
| 5 |  |  | Execuție proiect: montaj sticlă tratată | Flux 4 |  |  |
| 6 |  |  | ★ Măsurători kWh pre/post montaj | F088  [→ E-029] |  |  |
| 7 |  |  | ★ Raport: estimat vs real, economii, CO₂ | F088  [→ E-029] |  |  |
| 8 |  |  | Arhivare completă date proiect | F090  [→ E-029] |  |  |
| 9 |  |  |  |  | ★ Mapare Date → Modele ML TRL7 | F105  [→ E-029] |
| 10 |  |  |  |  | ★ ENERGY PORTFOLIO: impact agregat | F161  [→ E-029] |
### ✓ COMPLET — 10 pași, 8 diferențiatori ★

### LEGENDĂ:

### ● Acțiune manuală

### ⚡ Automat / Sistem

### ◆ Colectare date

### ◇ Gate / Tranziție

### ⬡ Decizie / Aprobare

### ★ Diferențiator Energy/ML


## Sheet: 7 — Reporting KPI

### FLUX 7: Reporting & KPI

### Management — Monitorizare performanță

| # | MANAGER |  | SISTEM |  | ECHIPĂ |  |
| 1 | Creez KPI custom: formulă drag-block | F148  [→ E-022] |  |  |  |  |
| 2 | Setez praguri: Slab / Bun / Excelent | F148  [→ E-022] |  |  |  |  |
| 3 | Atribui KPI pe agenți / echipă | F148  [→ E-022] |  |  |  |  |
| 4 | Dashboard KPI: grid + gauge + trend | F152  [→ E-022] |  |  |  |  |
| 5 | Drill-down: lunar / trimestrial / anual | F152  [→ E-022] |  |  |  |  |
| 6 | Raport schedule: Gantt actual vs forecast | F095  [→ E-020] |  |  |  |  |
| 7 | Raport financiar per proiect | F095  [→ E-020] |  |  |  |  |
| 8 | Sales Dashboard: funnel + pipeline value | F058  [→ E-011] |  |  |  |  |
| 9 | Export orice raport: Excel / PDF | F142  [→ E-026] |  |  |  |  |
| 10 |  |  |  |  | Ranking angajați per categorie KPI | F152  [→ E-022] |
### ✓ COMPLET — 10 pași, nicio ruptură

### LEGENDĂ:

### ● Acțiune manuală

### ⚡ Automat / Sistem

### ◆ Colectare date

### ◇ Gate / Tranziție

### ⬡ Decizie / Aprobare

### ★ Diferențiator Energy/ML


## Sheet: 8 — Admin Setup

### FLUX 8: Admin & Setup

### Configurare inițială platformă

| # | ADMINISTRATOR |  | SISTEM |  |
| 1 | Deschid aplicația: Home Dashboard | F157  [→ E-027] |  |  |
| 2 | Navigare cu sidebar contextual | F158  [→ E-027] |  |  |
| 3 | Configurez companie + utilizatori | F136  [→ E-024] |  |  |
| 4 | Setez roluri: Admin/Manager/Agent/Tehnic | F040  [→ E-024] |  |  |
| 5 | Configurez monede: RON + EUR | F139  [→ E-024] |  |  |
| 6 | Configurez stadii pipeline | F039  [→ E-024] |  |  |
| 7 | Template ofertă: logo, layout, clauze | F039  [→ E-024] |  |  |
| 8 | Configurez tipuri proiect + checklist | F106  [→ E-024] |  |  |
| 9 | Setez notificări per rol + triggers | F141  [→ E-025] |  |  |
| 10 |  |  | ⚡ Audit log activ pe toate acțiunile | F041  [→ E-024] |
### ✓ COMPLET — 10 pași, nicio ruptură

### LEGENDĂ:

### ● Acțiune manuală

### ⚡ Automat / Sistem

### ◆ Colectare date

### ◇ Gate / Tranziție

### ⬡ Decizie / Aprobare

### ★ Diferențiator Energy/ML


## Sheet: 9 — Închidere

### FLUX 9: Închidere Proiect

### Finalizare, Recepție & Arhivare

| # | PROJECT MANAGER |  | CLIENT |  | SISTEM |  |
| 1 | Recepție lucrări la obiectiv | F086  [→ E-029] |  |  |  |  |
| 2 | Punch list: lista remedieri | F086  [→ E-029] |  |  |  |  |
| 3 |  |  | ⬡ DECIZIE: PV recepție semnat | F086  [→ E-029] |  |  |
| 4 | Activez garanția post-execuție | F086  [→ E-029] |  |  |  |  |
| 5 | ★ Măsor consum energetic post-montaj | F088  [→ E-029] |  |  |  |  |
| 6 | ★ Generez raport impact energetic | F088  [→ E-029] |  |  |  |  |
| 7 |  |  |  |  | ⚡ Arhivare automată date proiect | F090  [→ E-029] |
| 8 |  |  |  |  | ★ Mapare Date → ML TRL7 | F105  [→ E-029] |
| 9 | Verific: toate facturile încasate? | F066  [→ E-014] |  |  |  |  |
| 10 | P&L final: profit sau pierdere | F091  [→ E-020] |  |  |  |  |
| 11 | ◇ GATE: Închid formal (grație 30z) | F103  [→ E-021] |  |  |  |  |
| 12 |  |  |  |  | ⚡ Status → FINALIZAT pe Portfolio | F101  [→ E-013] |
### ✓ COMPLET — 12 pași, 3 diferențiatori ★

### LEGENDĂ:

### ● Acțiune manuală

### ⚡ Automat / Sistem

### ◆ Colectare date

### ◇ Gate / Tranziție

### ⬡ Decizie / Aprobare

### ★ Diferențiator Energy/ML

