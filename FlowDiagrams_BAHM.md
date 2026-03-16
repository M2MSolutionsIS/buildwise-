## Sheet: Index

### BAHM OPERATIONAL — FLUXURI FUNCȚIONALE (SWIM LANE)

### M2M ERP Lite V6 — P2 BAHM Op. Prototype — 8 fluxuri naturale, 0 gap-uri

| # | Flux | Actori (Swim Lanes) | Frecvență | Pași | BAHM P2 | Verdict |
| 1 | Configurare Inițială | Administrator / HR / Resp. Achiziții / Sistem | O SINGURĂ DATĂ | 15 | 7 spec. | ✓ COMPLET |
| 2 | Achiziție Client → Contract Semnat | Agent Vânzări / Sistem / Manager | PER CLIENT NOU | 13 | — | ✓ COMPLET |
| 3 | Lansare Proiect | Project Manager / Director Operațiuni / Sistem | PER PROIECT NOU | 15 | 4 spec. | ✓ COMPLET |
| 4 | Aprovizionare Materiale | Project Manager / Resp. Achiziții / Furnizor / Sistem | LA NEVOIE (per proiect) | 11 | 7 spec. | ✓ COMPLET |
| 5 | Operațiuni Zilnice Șantier | Echipă Șantier / Project Manager / Sistem | ZILNIC | 11 | 1 spec. | ✓ COMPLET |
| 6 | Ciclu Lunar — Situație → Factură → Încasare | Project Manager / Client / Sistem | LUNAR | 10 | — | ✓ COMPLET |
| 7 | Management Resurse Cross-Proiecte | Director Operațiuni / Sistem / PM-uri | CONTINUU | 13 | 7 spec. | ✓ COMPLET |
| 8 | Închidere Proiect + Raport Final Costuri | Project Manager / CFO / Director / Sistem | LA FINAL PROIECT | 18 | 3 spec. | ✓ COMPLET |
| TOTAL |  |  |  | 106 | 29 spec. | 8/8 COMPLETE |

## Sheet: 1 — Configurare

### FLUX 1: Configurare Inițială

### O singură dată — Admin + HR + Achiziții într-o sesiune  ⏱ O SINGURĂ DATĂ

| # | ADMINISTRATOR |  | HR |  | RESP. ACHIZIȚII |  | SISTEM |  |
| 1 | Configurez companie: denumire, CUI, adresă | F136  [→ E-024] |  |  |  |  |  |  |
| 2 | Setez roluri: Admin / Director / PM / Echipă | F040  [→ E-024] |  |  |  |  |  |  |
| 3 | Configurez module: CRM, Pipeline, PM, RM | F136  [→ E-024] |  |  |  |  |  |  |
| 4 | Configurez monede: RON + EUR | F139  [→ E-024] |  |  |  |  |  |  |
| 5 | Setez notificări per rol | F141  [→ E-025] |  |  |  |  |  |  |
| 6 |  |  | Adaug angajați: nume, funcție, departament | F107  [→ E-033] |  |  |  |  |
| 7 |  |  | Configurez salarizare + rată orară | F111  [→ E-034] |  |  |  |  |
| 8 |  |  | Setez competențe per angajat | F110  [→ E-033/E-034] |  |  |  |  |
| 9 |  |  | Configurez calendar: concedii, disponibilitate | F109  [→ E-033] |  |  |  |  |
| 10 |  |  | Înregistrez subcontractori (resurse externe) | F120  [→ E-032] |  |  |  |  |
| 11 |  |  |  |  | Configurez categorii materiale, furnizori | F131  [→ E-024] |  |  |
| 12 |  |  |  |  | Setez praguri stoc minim per material | F114  [→ E-035] |  |  |
| 13 | Configurez stadii pipeline + template-uri ofertă | F039  [→ E-024] |  |  |  |  |  |  |
| 14 | Configurez tipuri proiect + checklist kickoff | F106  [→ E-024] |  |  |  |  |  |  |
| 15 |  |  |  |  |  |  | Audit log activ pe toate acțiunile | F041  [→ E-024] |
### ✓ COMPLET — 15 pași, 7 specifice BAHM

### LEGENDĂ:

### ● Acțiune manuală

### ⚡ Automat / Sistem

### ◆ Colectare date

### ◇ Gate / Tranziție

### ⬡ Decizie / Aprobare

### ■ Specific BAHM (P2)


## Sheet: 2 — Vânzare

### FLUX 2: Achiziție Client → Contract Semnat

### Ciclu complet de vânzare (comun P1/P2)  ⏱ PER CLIENT NOU

| # | AGENT VÂNZĂRI |  | SISTEM |  | MANAGER |  |
| 1 | Creez contact + fișă client completă | F001-F005  [→ E-002/E-003 | E-003] |  |  |  |  |
| 2 | Asociez proprietate + date constructive | F010  [→ E-028] |  |  |  |  |
| 3 | Programez vizite, loguez apeluri | F054-F056  [→ E-011 | E-011/E-012] |  |  |  |  |
| 4 | ◇ Handover → Sales Pipeline | F042  [→ E-009/E-010] |  |  |  |  |
| 5 | Deal Scoping: milestone-uri + predimensionare | F043-F048  [→ E-010] |  |  |  |  |
| 6 | Pipeline Board: Kanban → avansare stadii | F050-F051  [→ E-009] |  |  |  |  |
| 7 | Offer Builder → Preview → Export PDF | F019+F023  [→ E-005] |  |  |  |  |
| 8 | ◇ Submit la aprobare | F028  [→ E-006] |  |  |  |  |
| 9 |  |  |  |  | ⬡ Review → Approve / Reject | F028  [→ E-006] |
| 10 | Trimit ofertă → Client acceptă | F026-F027  [→ E-005 | E-006] |  |  |  |  |
| 11 | Contract Builder → Preview → Export | F031+F033  [→ E-007] |  |  |  |  |
| 12 |  |  | Auto-generare grafic facturare | F035  [→ E-007] |  |  |
| 13 |  |  | ⚡ Contract Semnat → Trigger proiect | F031→F063  [→ E-007 | E-014] |  |  |
### ✓ COMPLET — 13 pași

### LEGENDĂ:

### ● Acțiune manuală

### ⚡ Automat / Sistem

### ◆ Colectare date

### ◇ Gate / Tranziție

### ⬡ Decizie / Aprobare

### ■ Specific BAHM (P2)


## Sheet: 3 — Lansare Proiect

### FLUX 3: Lansare Proiect

### De la contract semnat la proiect gata de execuție  ⏱ PER PROIECT NOU

| # | PROJECT MANAGER |  | DIRECTOR OPERAȚIUNI |  | SISTEM |  |
| 1 |  |  |  |  | Auto-creare proiect la semnare | F063  [→ E-014] |
| 2 | Completez checklist kickoff | F063  [→ E-014] |  |  |  |  |
| 3 | Import deviz: Intersoft / eDevize / Excel | F123  [→ E-037] |  |  |  |  |
| 4 |  |  |  |  | Wizard: upload → preview → mapping → WBS | F123  [→ E-037] |
| 5 | Vizualizez deviz arbore ierarhic | F125  [→ E-017] |  |  |  |  |
| 6 | Creez WBS din structura devizului | F069  [→ E-015] |  |  |  |  |
| 7 | Generez Gantt cu dependențe | F070  [→ E-015] |  |  |  |  |
| 8 | Completez deviz estimativ: cantități, prețuri | F071  [→ E-015/E-016] |  |  |  |  |
| 9 | Setez buget per capitol WBS | F080  [→ E-020/E-021] |  |  |  |  |
| 10 | Identific riscuri → Risk Register | F084  [→ E-016] |  |  |  |  |
| 11 |  |  | Verifică capacitate: cine e disponibil? | F130  [→ E-013] |  |  |
| 12 |  |  | Alocă angajați pe proiect/fază: ore per perioadă | F117  [→ E-032] |  |  |
| 13 |  |  | Alocă materiale + buget din RM | F117  [→ E-032] |  |  |
| 14 |  |  |  |  | Sync RM → PM: alocarea vizibilă pe proiect | F083  [→ E-016] |
| 15 | Proiect vizibil în Portfolio: status ACTIV | F101  [→ E-013] |  |  |  |  |
### ✓ COMPLET — 15 pași, 4 specifice BAHM

### LEGENDĂ:

### ● Acțiune manuală

### ⚡ Automat / Sistem

### ◆ Colectare date

### ◇ Gate / Tranziție

### ⬡ Decizie / Aprobare

### ■ Specific BAHM (P2)


## Sheet: 4 — Aprovizionare

### FLUX 4: Aprovizionare Materiale

### Ciclu complet: nevoie → comandă → livrare → stoc → consum  ⏱ LA NEVOIE (per proiect)

| # | PROJECT MANAGER |  | RESP. ACHIZIȚII |  | FURNIZOR |  | SISTEM |  |
| 1 | Identific nevoie material din deviz/WBS | F071+F125  [→ E-015/E-016 | E-017] |  |  |  |  |  |  |
| 2 | Verific stoc: e disponibil? | F114  [→ E-035] |  |  |  |  |  |  |
| 3 |  |  | Creez comandă achiziție → asociez la proiect | F112  [→ E-035] |  |  |  |  |
| 4 |  |  |  |  | Furnizor livrează marfa | — |  |  |
| 5 |  |  | Recepție: NIR + verificare cantitate/calitate | F113  [→ E-035] |  |  |  |  |
| 6 |  |  | Înregistrez factura furnizor | F113  [→ E-035] |  |  |  |  |
| 7 |  |  |  |  |  |  | Actualizare automată stocuri | F114  [→ E-035] |
| 8 |  |  |  |  |  |  | Alertă dacă sub prag minim | F114  [→ E-035] |
| 9 | Consum pe proiect: fișă consum per WBS | F074  [→ E-017/E-019] |  |  |  |  |  |  |
| 10 |  |  |  |  |  |  | Cost material → Project P&L automat | F091  [→ E-020] |
| 11 |  |  | Export documente achiziție ACN | F113  [→ E-035] |  |  |  |  |
### ✓ COMPLET — 11 pași, 7 specifice BAHM

### LEGENDĂ:

### ● Acțiune manuală

### ⚡ Automat / Sistem

### ◆ Colectare date

### ◇ Gate / Tranziție

### ⬡ Decizie / Aprobare

### ■ Specific BAHM (P2)


## Sheet: 5 — Operațiuni Zilnice

### FLUX 5: Operațiuni Zilnice Șantier

### Execuție curentă — cel mai frecvent flux  ⏱ ZILNIC

| # | ECHIPĂ ȘANTIER |  | PROJECT MANAGER |  | SISTEM |  |
| 1 | Loguiesc ore pe task-uri | F072  [→ E-018] |  |  |  |  |
| 2 | Setez status: InProgress / Blocat / Done | F073  [→ E-018] |  |  |  |  |
| 3 | Înregistrez consum materiale per WBS | F074  [→ E-017/E-019] |  |  |  |  |
| 4 | Înregistrez cantități realizate pe deviz | F125  [→ E-017] |  |  |  |  |
| 5 | Completez RZS: activități, personal, meteo | F077  [→ E-017] |  |  |  |  |
| 6 |  |  |  |  | Auto-update Gantt: actual vs baseline | F070  [→ E-015] |
| 7 |  |  | Verific avansare: % fizic vs planificat | F078  [→ E-017] |  |  |
| 8 |  |  | Urmăresc subcontractori: activități, valori, % | F075  [→ E-019] |  |  |
| 9 |  |  | Verific consum resurse vs alocare RM | F118  [→ E-032] |  |  |
| 10 |  |  | Atașez documente/poze în Wiki proiect | F144-F146  [→ E-023] |  |  |
| 11 |  |  |  |  | Notificare automată la blocare task / depășire | F141  [→ E-025] |
### ✓ COMPLET — 11 pași, 1 specifice BAHM

### LEGENDĂ:

### ● Acțiune manuală

### ⚡ Automat / Sistem

### ◆ Colectare date

### ◇ Gate / Tranziție

### ⬡ Decizie / Aprobare

### ■ Specific BAHM (P2)


## Sheet: 6 — Ciclu Lunar

### FLUX 6: Ciclu Lunar — Situație → Factură → Încasare

### Ciclul financiar recurent per proiect  ⏱ LUNAR

| # | PROJECT MANAGER |  | CLIENT |  | SISTEM |  |
| 1 | Generez Situație de Lucrări pe luna curentă | F079  [→ E-017/E-039] |  |  |  |  |
| 2 |  |  |  |  | Preia automat cantități din deviz (F125)  [→ E-017] | F079  [→ E-017/E-039] |
| 3 | Verific: contractat vs executat vs cumulat | F079  [→ E-017/E-039] |  |  |  |  |
| 4 | Export Situație Excel/PDF | F079+F142  [→ E-017/E-039 | E-026] |  |  |  |  |
| 5 |  |  | Client primește și aprobă Situația | — |  |  |
| 6 | ◇ Link direct: Emite factură din Situație | F079→F035  [→ E-007 | E-017/E-039] |  |  |  |  |
| 7 |  |  |  |  | Factura în grafic facturare | F035  [→ E-007] |
| 8 |  |  |  |  | Tracking: Emisă → Trimisă → Plătită/Restantă | F066  [→ E-014] |
| 9 |  |  |  |  | Alertă restanță +7/+14/+30 zile | F066  [→ E-014] |
| 10 |  |  |  |  | Încasare → propagare în Project P&L | F091  [→ E-020] |
### ✓ COMPLET — 10 pași

### LEGENDĂ:

### ● Acțiune manuală

### ⚡ Automat / Sistem

### ◆ Colectare date

### ◇ Gate / Tranziție

### ⬡ Decizie / Aprobare

### ■ Specific BAHM (P2)


## Sheet: 7 — Resurse Multi-Pj

### FLUX 7: Management Resurse Cross-Proiecte

### Director Operațiuni — viziune companie, continuu  ⏱ CONTINUU

| # | DIRECTOR OPERAȚIUNI |  | SISTEM |  | PM-URI |  |
| 1 | Portfolio: toate proiectele, status, health | F101  [→ E-013] |  |  |  |  |
| 2 | Company Capacity: load factor, disponibilitate | F130  [→ E-013] |  |  |  |  |
| 3 |  |  | KPI Dashboard: metrici cross-proiecte | F152  [→ E-022] |  |  |
| 4 | Verific: Proiect A — avansare + resurse | F078+F118  [→ E-017 | E-032] |  |  |  |  |
| 5 | Verific: Proiect B — nevoie resurse suplimentare | F117  [→ E-032] |  |  |  |  |
| 6 |  |  | Detectare conflict: angajat pe ambele proiecte | F117  [→ E-032] |  |  |
| 7 | Rebalansez: mut ore de pe A la B | F117  [→ E-032] |  |  |  |  |
| 8 | Verific impact pe Gantt ambelor proiecte | F070  [→ E-015] |  |  |  |  |
| 9 | Global P&L: situația financiară companie | F093  [→ E-020] |  |  |  |  |
| 10 | TrueCast: Actual vs Forecast cross-module | F140  [→ E-020] |  |  |  |  |
| 11 | Rapoarte utilizare resurse + eficiență | F121+F119  [→ E-032 | E-036] |  |  |  |  |
| 12 |  |  |  |  | PM-ii văd alocările actualizate pe proiectele lor | F083  [→ E-016] |
| 13 | Sales Pipeline: ce proiecte noi vin? | F058  [→ E-011] |  |  |  |  |
### ✓ COMPLET — 13 pași, 7 specifice BAHM

### LEGENDĂ:

### ● Acțiune manuală

### ⚡ Automat / Sistem

### ◆ Colectare date

### ◇ Gate / Tranziție

### ⬡ Decizie / Aprobare

### ■ Specific BAHM (P2)


## Sheet: 8 — Închidere+Raport

### FLUX 8: Închidere Proiect + Raport Final Costuri

### Per proiect finalizat — P&L complet, closeout, arhivare  ⏱ LA FINAL PROIECT

| # | PROJECT MANAGER |  | CFO / DIRECTOR |  | SISTEM |  |
| 1 | Recepție lucrări + punch list remedieri | F086  [→ E-029] |  |  |  |  |
| 2 | PV recepție semnat de client | F086  [→ E-029] |  |  |  |  |
| 3 | Activez garanția post-execuție | F086  [→ E-029] |  |  |  |  |
| 4 | Verific: toate facturile emise și încasate? | F066  [→ E-014] |  |  |  |  |
| 5 |  |  | Deschid Project P&L final | F091  [→ E-020] |  |  |
| 6 |  |  |  |  | Auto: VENITURI = facturi emise + plătite | F035+F066  [→ E-007 | E-014] |
| 7 |  |  |  |  | Auto: COST Personal = ore × rată orară | F072×F111  [→ E-018 | E-034] |
| 8 |  |  |  |  | Auto: COST Materiale consumate | F074  [→ E-017/E-019] |
| 9 |  |  |  |  | Auto: COST Materiale achiziționate | F113  [→ E-035] |
| 10 |  |  |  |  | Auto: COST Subcontractori | F075  [→ E-019] |
| 11 |  |  | P&L: Venituri − Costuri = PROFIT/PIERDERE | F091  [→ E-020] |  |  |
| 12 |  |  | Cash Flow final: intrări vs ieșiri | F092  [→ E-020] |  |  |
| 13 |  |  | Breakdown per capitol WBS: buget vs realizat | F080  [→ E-020/E-021] |  |  |
| 14 |  |  | Eficiență resurse: ore plan vs real per angajat | F119  [→ E-032] |  |  |
| 15 |  |  | Export raport complet Excel/PDF | F142  [→ E-026] |  |  |
| 16 | ◇ Închid formal proiectul (grație 30 zile) | F103  [→ E-021] |  |  |  |  |
| 17 |  |  |  |  | Arhivare completă date proiect | F090  [→ E-029] |
| 18 |  |  |  |  | Status → FINALIZAT pe Portfolio | F101  [→ E-013] |
### ✓ COMPLET — 18 pași, 3 specifice BAHM

### LEGENDĂ:

### ● Acțiune manuală

### ⚡ Automat / Sistem

### ◆ Colectare date

### ◇ Gate / Tranziție

### ⬡ Decizie / Aprobare

### ■ Specific BAHM (P2)

