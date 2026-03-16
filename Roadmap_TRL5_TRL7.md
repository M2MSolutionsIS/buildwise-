## Sheet: Dashboard

### 🏗 BuildWise – Platformă AI pentru Predicție Energetică | BAHM S.R.L.

### PoCIDIF 2021–2027 | Acțiunea 2.1 | TRL 5 → TRL 7 | Durata: 24 luni

### DATE CHEIE PROIECT

| Câmp | Valoare / Detalii |  |  |  |
| Solicitant | BAHM S.R.L. |  |  |  |
| Județ / Regiune | Botoșani – Nord-Est (LDR) |  |  |  |
| CAEN eligibil | 6290 – Alte activități servicii IT |  |  |  |
| Valoare totală proiect (EUR) | =Buget!B3 |  |  |  |
| Finanțare nerambursabilă (EUR) | =Buget!B18 |  |  |  |
| Cofinanțare BAHM (EUR) | =Buget!B19 |  |  |  |
| Rată finanțare (%) | =Buget!D18 |  |  |  |
| Durata implementare (luni) | 24 |  |  |  |
| TRL Start | 5 |  |  |  |
| TRL Finish (obiectiv) | 7 |  |  |  |
| Cifra de afaceri 2024 (RON) | 100000000 |  |  |  |
| Număr angajați | 30 |  |  |  |
| Categoria IMM | Întreprindere mică |  |  |  |
### REZUMAT BUGET (EUR)

| Categorie | Valoare (EUR) | % din Total | Eligibil | Obs. |
| A. Cheltuieli CDI (total) | =Buget!B4 | =Buget!C4 | Da | Cercetare-inovare |
| – Salarii echipă CDI | =Buget!B5 | =Buget!C5 | Da |  |
| – Subcontractare CDI | =Buget!B6 | =Buget!C6 | Da |  |
| – Licențe software + cloud | =Buget!B7 | =Buget!C7 | Da |  |
| B. Echipamente & IT | =Buget!B9 | =Buget!C9 | Da |  |
| C. Servicii externe | =Buget!B13 | =Buget!C13 | Da | Expert inovare, audit |
| D. Costuri operaționale | =Buget!B14 | =Buget!C14 | Da | Management, deplasări |
| TOTAL PROIECT | =Buget!B3 | =Buget!C3 |  |  |
### KPI CHEIE – ȚINTE PROIECT

| Indicator | Valoare Țintă | Status | WP Responsabil | Termen |
| Platformă BuildWise funcțională (TRL7) | 1 platformă | =KPI!D3 | WP4, WP5, WP6 | L22 |
| Servicii noi create (S1+S2) | 2 servicii | =KPI!D4 | WP4, WP5 | L18 |
| Procese noi (P1+P2) | 2 procese | =KPI!D5 | WP6 | L20 |
| Modele ML antrenate și validate | Min. 3 modele | =KPI!D6 | WP5 | L18 |
| Clădiri pilot testate | Min. 5 clădiri | =KPI!D7 | WP7 | L22 |
| Acuratețe predicție energetică | Eroare < 15% | =KPI!D8 | WP7 | L22 |
| Utilizatori testați în pilot | Min. 20 utilizatori | =KPI!D9 | WP7 | L22 |
| Reducere consum energetic (post-proiect) | Min. 20% | =KPI!D10 | WP7, WP8 | Post L24 |
| Clienți activi (2 ani post-proiect) | 50+ clienți | =KPI!D11 | WP8 | Post L24 |
| Venituri BuildWise (3 ani post-proiect) | 500.000 EUR | =KPI!D12 | WP8 | Post L24 |

## Sheet: Buget

### BUGET ESTIMAT – BuildWise | BAHM S.R.L. | PoCIDIF 2.1

| Categorie de Cheltuieli | Valoare (EUR) | % din Total | Eligibil | Notă |
| TOTAL VALOARE PROIECT | =SUM(B4,B9,B13,B14) | =B3/B3 | Eligibil | Valoare totală proiect |
| A. Cheltuieli CDI (total) | =SUM(B5:B8) | =B4/B3 | Eligibil | ≥50% din total – condiție ETF |
| – Salarii echipă CDI | 600000 | =B5/B3 | Eligibil | Cercetători, Data Scientists, Dev AI/ML |
| – Subcontractare servicii CDI | 400000 | =B6/B3 | Eligibil | Cercetare date energetice, validare modele |
| – Licențe software + cloud CDI | 200000 | =B7/B3 | Eligibil | Mediu dev, cloud computing |
| – Alte CDI | 0 | =B8/B3 | Eligibil | Rezervă CDI |
| B. Echipamente & Infrastructură IT | =SUM(B10:B12) | =B9/B3 | Eligibil |  |
| – Servere, cloud, echipamente pilot | 300000 | =B10/B3 | Eligibil | Infrastructură HW/SW |
| – Echipamente măsurare clădiri pilot | 100000 | =B11/B3 | Eligibil | Senzori, data loggers |
| – Alte echipamente IT | 0 | =B12/B3 | Eligibil | Rezervă |
| C. Servicii externe | 200000 | =B13/B3 | Eligibil | Expert inovare, audit, diseminare |
| D. Costuri operaționale | 200000 | =B14/B3 | Eligibil | Management proiect, deplasări |
### STRUCTURA FINANȚĂRII

| Tip | Valoare (EUR) | % din Total | Sursă | Notă |
| Grant PoCIDIF (nerambursabil) | =B3*0.75 | =B18/B3 | UE + Buget național | Rată 75% – IMM LDR Botoșani |
| Cofinanțare BAHM S.R.L. | =B3*0.25 | =B19/B3 | Surse proprii BAHM | 25% contribuție proprie |
| TOTAL FINANȚARE | =B18+B19 | =B20/B3 |  | Trebuie = Total Proiect |
### VERIFICARE ELIGIBILITATE – PONDERE CDI

| Indicator | Valoare calculată | Prag minim ETF | Status | Obs. |
| Pondere cheltuieli CDI din total | =B4/B3 | 0.5 | =IF(B24>=C24,"✅ ÎNDEPLINIT","❌ NEÎNDEPLINIT") | Min. 50% pentru 5 pct ETF |
| Pondere salarii din CDI | =B5/B4 | 0.4 | =IF(B25>=C25,"✅ OK","⚠ Verificați") | Rată optimă personal CDI |
| Pondere subcontractare din CDI | =B6/B4 | 0.33 | =IF(B26<=C26,"✅ OK","⚠ Verificați") | Max recomandat subcontractare |
| Cofinanțare ca % din total | =B19/B3 | 0.25 | =IF(ABS(B27-C27)<0.01,"✅ Corect","❌ Eroare") | Trebuie = 25% |

## Sheet: Work Packages

### PLAN WORK PACKAGES – BuildWise BAHM S.R.L. | Gantt 24 Luni

| WP | Titlu Work Package | Start (L) | End (L) | Tip | L1 | L2 | L3 | L4 | L5 | L6 | L7 | L8 | L9 | L10 | L11 | L12 | L13 | L14 | L15 | L16 | L17 | L18 | L19 | L20 | L21 | L22 | L23 | L24 |
| WP1 | Management de Proiect | 1 | 24 | Management |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| WP2 | Analiză și Specificații | 1 | 4 | CDI |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| WP3 | Cercetare & Date Energetice | 3 | 10 | CDI |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| WP4 | Dezvoltare Serviciu Educare (S1) | 5 | 16 | CDI |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| WP5 | Dezvoltare Serviciu Învățare (S2) | 7 | 18 | CDI |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| WP6 | Implementare Procese (P1+P2) | 10 | 20 | CDI |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| WP7 | Pilot și Validare TRL7 | 16 | 22 | Pilot |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| WP8 | Comercializare și Diseminare | 20 | 24 | Comercial |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
|  | Durata totală (luni) per WP → | Start | Durată |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
### LEGENDĂ TIPURI ACTIVITĂȚI

### Management

### CDI

### Pilot

### Comercial


## Sheet: KPI

### KPI & INDICATORI MONITORIZARE – BuildWise BAHM S.R.L.

| Nr. | Indicator | Valoare Țintă | Status curent | Realizat (%) | WP | Modalitate verificare |
| 1 | Platformă BuildWise funcțională (TRL7) | 1 platformă | În desfășurare | 0 | WP4-6 | Raport de recepție |
| 2 | Servicii noi create (S1 + S2) | 2 servicii | În desfășurare | 0 | WP4, WP5 | Documentație tehnică |
| 3 | Procese noi implementate (P1 + P2) | 2 procese | În desfășurare | 0 | WP6 | Proceduri operaționale |
| 4 | Modele ML antrenate și validate | Min. 3 modele | În desfășurare | 0 | WP5 | Documentație ML |
| 5 | Clădiri pilot testate (TRL7) | Min. 5 clădiri | În desfășurare | 0 | WP7 | Rapoarte pilot |
| 6 | Acuratețe predicție energetică | Eroare < 15% | Nedemarat | 0 | WP7 | Comparație baseline vs. real |
| 7 | Utilizatori testați în pilot | Min. 20 utilizatori | Nedemarat | 0 | WP7 | Raport UAT |
| 8 | Documentație tehnică completă | 5 documente | În desfășurare | 0 | Toate WP | Livrabile proiect |
| 9 | RCR03 – IMM cu inovații de produs | 1 IMM (BAHM) | Confirmat | 0 | WP1 | Cerere de finanțare |
| 10 | Reducere consum energetic (post-proiect) | Min. 20% | Post-proiect | 0 | WP7-8 | Raport impact L24 |
| 11 | Clienți activi (2 ani post-proiect) | 50+ clienți | Post-proiect | 0 | WP8 | CRM BAHM |
| 12 | Venituri BuildWise (3 ani post-proiect) | 500.000 EUR | Post-proiect | 0 | WP8 | Raport financiar |
| 13 | Reducere costuri întreținere zone comune | 15–25% | Post-proiect | 0 | WP7-8 | Comparație facturi |
### SUMAR PROGRES – CALCUL AUTOMAT

| Metrică | Valoare | Formula |  |  |  |  |
| KPI-uri cu status Confirmat | =COUNTIF(D3:D15,"Confirmat") | COUNTIF status=Confirmat |  |  |  |  |
| KPI-uri În desfășurare | =COUNTIF(D3:D15,"În desfășurare") | COUNTIF status=În desfășurare |  |  |  |  |
| KPI-uri Nedemarat | =COUNTIF(D3:D15,"Nedemarat") | COUNTIF status=Nedemarat |  |  |  |  |
| KPI-uri Post-proiect | =COUNTIF(D3:D15,"Post-proiect") | COUNTIF status=Post-proiect |  |  |  |  |
| Total KPI-uri urmărite | =COUNTA(B3:B15) | COUNTA indicator list |  |  |  |  |
| Progres mediu realizat (%) | =AVERAGE(E3:E15) | AVERAGE % realizare |  |  |  |  |
| KPI-uri la 100% realizare | =COUNTIF(E3:E15,1) | COUNTIF 100% |  |  |  |  |

## Sheet: TRL Progresie

### MATRICEA TRL – BuildWise: De la TRL 5 la TRL 7

| TRL | Componentă | TRL 5 – PUNCT START (existent) | TRL 7 – PUNCT FINISH (obiectiv) | WP Responsabil |
| TRL 5 | Software / Platformă | 3 module funcționale (CRM, Pipeline Activity, Project Management) utilizate în producție curentă BAHM | Platformă BuildWise cu AI/ML integrat, validat pe minim 5 clădiri pilot cu date reale măsurate | WP2, WP4, WP5, WP6 |
| TRL 5 | Sticlă tratată termic | Tehnologie demonstrată în laborator/fabrică (0,3 W/m²K); date tehnice complete în curs de obținere 2025 | Date tehnice validate, integrate în motorul AI ca parametri de calcul verificabili și auditabili | WP3 |
| TRL 5 | AI/ML | Concept validat; date istorice disponibile din activitatea BAHM; algoritmi identificați | Modele ML antrenate, validate și reantrenate automat; XAI implementat; demonstrat în pilot real | WP3, WP4, WP5, WP7 |
| TRL 5 | Interfață utilizator | Module ERP/CRM cu interfețe interne pentru uzul echipei BAHM | Interfață publică accesibilă non-tehnic: input simplu → output în lei/lună, % economii | WP4 |
| TRL 5 | Integrare date reale | Date empirice disponibile din proiectele BAHM (nestructurate, neintegrate în ML) | Pipeline automat de colectare → preprocesare → antrenare → validare → predicție în producție | WP3, WP5, WP6 |
| TRL 5 | Validare în câmp | Testare internă în procesele BAHM; fără validare externă documentată TRL7 | Pilot real pe minim 5 clădiri (rezidențial + comercial + industrial); eroare < 15% demonstrată | WP7 |
### SCALA TRL – REFERINȚĂ

| TRL | Descriere | Fază |  |  |
| TRL 1-2 | Principii de bază / Concept tehnologic | Cercetare fundamentală |  |  |
| TRL 3-4 | Dovadă conceptuală / Validare în laborator | Cercetare aplicată |  |  |
| TRL 5 | Validare în mediu relevant ★ BAHM START | Demonstrare |  |  |
| TRL 6 | Demonstrare în mediu relevant | Demonstrare avansată |  |  |
| TRL 7 | Demonstrare în mediu operațional ★ BAHM FINISH | Prototip |  |  |
| TRL 8 | Sistem finalizat și calificat | Pre-producție |  |  |
| TRL 9 | Sistem în producție (misiune demonstrată) | Producție |  |  |

## Sheet: Riscuri

### MATRICE RISCURI – BuildWise BAHM S.R.L.

| Nr. | Risc identificat | Probabilitate | Impact | Scor Risc | Măsuri de atenuare |
| R1 | Date insuficiente pentru antrenarea ML (fond construit românesc) | Medie | Mare | 6 | WP3 dedicat; parteneriate asociații proprietari; date INCERC și baze publice |
| R2 | Finalizare întârziată date tehnice sticlă tratată termic | Medie | Medie | 4 | WP3 L3–L10 cu buffer 6 luni; testare cu valori provizorii validate ulterior |
| R3 | Raport expert extern nu confirmă caracterul inovativ | Mică | Critic | 4 | Expert identificat; dosar tehnic inovare pregătit; benchmarking documentat |
| R4 | Dificultăți recrutare experți AI/ML | Medie | Mare | 6 | Recrutare înainte de semnare contract; opțiune subcontractare CDI |
| R5 | Acuratețe insuficientă modele ML (eroare > 15%) | Mică | Medie | 2 | Abordare iterativă; reantrenare pe date pilot; marjă acceptabilă definită contractual |
| R6 | Adoptare scăzută clienți BAHM în faza pilot | Mică | Medie | 2 | LOI-uri pre-semnate min. 5 clienți; valoare demonstrată rapid (lei/lună) |
### LEGENDĂ MATRICE RISCURI (Probabilitate × Impact)

| 1-2 | RISC SCĂZUT |  |  |  |  |
| 3-4 | RISC MEDIU |  |  |  |  |
| 6 | RISC RIDICAT |  |  |  |  |
| 9-12 | RISC CRITIC |  |  |  |  |

## Sheet: Echipa

### ECHIPA DE IMPLEMENTARE – BuildWise BAHM S.R.L.

| Rol în Proiect | Calificare | Alocare (%) | Responsabilități principale | WP Implicat |
| Manager de Proiect | Ing. construcții / MBA | 1 | Coordonare generală, raportare finanțator, management riscuri, relație evaluator extern | WP1 |
| Expert Tehnic Principal – Construcții & Energie | Ing. construcții, expert eficiență energetică | 0.8 | Definire parametri constructivi, validare modele energetice, coordonare pilot, interpretare date sticlă | WP2, WP3, WP7 |
| Expert AI/ML (Expert 2 PoCIDIF) | Ing. informatică / Data Scientist | 1 | Proiectare și implementare modele ML, pipeline reantrenare, XAI, MLOps, arhitectură AI | WP3, WP4, WP5, WP6 |
| Dezvoltator Software Senior | Ing. informatică | 1 | Dezvoltare backend/frontend, integrare CRM/Pipeline/PM, API REST, securitate | WP4, WP5, WP6 |
| Specialist Date & Cercetare Energetică | Fizician / Ing. instalații | 0.8 | Colectare și procesare date consum energetic, construire dataset ML, validare pilot | WP3, WP7 |
| Expert Diseminare & Comercializare | Economist / Marketing | 0.5 | Strategie go-to-market, materiale comerciale, participare evenimente, raportare impact | WP8 |
| TOTAL FTE ECHIPĂ (Echivalent Normă Întreagă) |  | =SUM(C3:C8) | FTE = Suma % alocări |  |
