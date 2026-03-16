## Sheet: INDEX

### BuildWise – BAHM S.R.L. | Funcțiuni Software Existente la TRL 5

### Sistem software intern existent (punct de start al proiectului PoCIDIF 2.1) | 3 Module Operaționale

### 📋  SUMAR MODULE LA TRL 5

| Modul | Descriere scurtă | Nr. funcțiuni | Status | Sheet detaliu | Integrare cu | Notă TRL 5 |
| M1 – CRM | Managementul relațiilor cu clienții: contacte, oferte, pipeline vânzări | =COUNTA('M1 - CRM'!B5:B100) | ✅ Operațional | M1 - CRM | M2 – Pipeline Activity | Date clienți disponibile pentru antrenare ML |
| M2 – Pipeline Activity | Urmărirea activităților comerciale și a oportunităților | =COUNTA('M2 - Pipeline'!B5:B100) | ✅ Operațional | M2 - Pipeline | M1 – CRM, M3 – PM | Date activități disponibile pentru ML |
| M3 – Project Management | Planificarea și urmărirea proiectelor de construcții | =COUNTA('M3 - PM'!B5:B100) | ✅ Operațional | M3 - PM | M1 – CRM, M2 – Pipeline | Date proiecte/consum disponibile pentru ML |
| TOTAL FUNCȚIUNI TRL 5 | Toate modulele combinate | ='M1 - CRM'!J2+'M2 - Pipeline'!J2+'M3 - PM'!J2 | – | – | – | – |
### 📌  LEGENDĂ COLOANE DETALIU

| Nr. | Numărul de ordine al funcțiunii în modul |  |  |  |  |  |
| Funcțiune | Denumirea scurtă a funcțiunii / featurului |  |  |  |  |  |
| Descriere detaliată | Explicația completă a ce face funcțiunea |  |  |  |  |  |
| Tip | Funcțional (F) / Non-Funcțional (NF) / Configurare (C) |  |  |  |  |  |
| Prioritate | Critică / Înaltă / Medie / Scăzută |  |  |  |  |  |
| Date generate pentru ML | Ce date produce această funcțiune, utilizabile în modelele AI/ML |  |  |  |  |  |
| WP BuildWise | Work Package-ul care extinde/valorifică această funcțiune |  |  |  |  |  |

## Sheet: M1 - CRM

### M1 – CRM (Customer Relationship Management) | Funcțiuni TRL 5 – BAHM S.R.L.

| Modul de gestiune a relațiilor cu clienții: contacte, oferte comerciale, parametri tehnici clădiri, date sticlă tratată termic |  |  |  |  |  |  |  |  | =COUNTA(B5:B200) |
| Nr. | Funcțiune | Descriere detaliată | Tip | Prioritate | Date generate pentru ML | WP BuildWise |  |  |  |
### ▶  📁 GESTIUNE CONTACTE

| 1 | Gestiune contacte clienți | Stocare și administrare date complete ale contactelor: persoane fizice și juridice, date de identificare, adrese, roluri (beneficiar, investitor, administrator clădire, asociație proprietari) | F | Critică | Profil client: tip persoană, regiune, tip proprietate → segmentare ML | WP4, WP5 |  |  |  |
| 2 | Tipologie client | Clasificarea automată a clienților după tip: persoană fizică, IMM, persoană juridică mare, instituție publică, asociație proprietari, developer imobiliar | F | Critică | Feature de segmentare pentru modelele ML de predicție adoptare platformă | WP5 |  |  |  |
| 3 | Date proprietăți asociate | Asocierea clienților cu proprietățile lor: adresă clădire, suprafață, an construcție, regim înălțime, tip clădire (rezidențial, comercial, industrial, mixt) | F | Critică | Date tip clădire și locație → parametri de bază pentru motorul de predicție energetică | WP4 |  |  |  |
| 4 | Istoricul interacțiunilor | Log complet al tuturor interacțiunilor cu clientul: apeluri telefonice, e-mailuri, întâlniri, vizite la obiectiv, oferte transmise, contracte semnate | F | Înaltă | Frecvența interacțiunilor → feature pentru predicția probabilității de conversie | WP5 |  |  |  |
| 5 | Segmentare și filtrare clienți | Filtrare multi-criteriu a bazei de clienți: după județ, tip clădire, valoare contract, status relație, dată ultimă interacțiune, produs BAHM achiziționat | F | Înaltă | Segmente de clienți → date de antrenare pentru modele de recomandare produse | WP5 |  |  |  |
### ▶  📋 OFERTE & VÂNZĂRI

| 6 | Creare și editare oferte comerciale | Generarea ofertelor comerciale personalizate pentru clienți: produse BAHM (sticlă tratată termic, izolații, lucrări construcții), cantități, prețuri, termene | F | Critică | Tipuri produse ofertate + suprafețe clădiri → parametri pentru calculul economic BuildWise | WP4 |  |  |  |
| 7 | Calculator suprafețe ferestre/pereți | Modul de calcul rapid al suprafețelor elementelor constructive (ferestre, pereți, acoperiș) pe baza datelor introduse manual sau importate din planuri | F | Critică | Suprafețe constructive reale → date de intrare directe în modelul de predicție energetică | WP4 |  |  |  |
| 8 | Parametri sticlă tratată termic | Stocare și aplicare parametri tehnici ai sticlei tratate termic BAHM: coeficient U = 0,3 W/m²K, transmitanță luminoasă, factor solar, grosime, tip tratament | F | Critică | Coeficient U real (0,3 W/m²K) → parametru fundamental al motorului AI de predicție | WP4, WP3 |  |  |  |
| 9 | Versionare oferte | Gestionarea mai multor versiuni ale aceleiași oferte cu comparare automată: prețuri, cantități, specificații tehnice, data emiterii, status (trimisă, acceptată, respinsă) | F | Medie | Status oferte (acceptat/respins) + parametri → date de antrenare pentru optimizare comercială | WP5 |  |  |  |
| 10 | Status pipeline vânzări | Urmărirea statusului fiecărei oportunități comerciale în etapele definite: Prospect → Contactat → Interesat → Ofertă trimisă → Negociere → Câștigat / Pierdut | F | Critică | Stadiul oportunităților + durate per etapă → ML pentru predicția probabilității de închidere | WP5 |  |  |  |
| 11 | Rapoarte comerciale | Generare rapoarte: valoare oferte emise, rată conversie, venituri pe categorii de produse, clienți activi, comparare periodică (lunar, trimestrial, anual) | F | Înaltă | Date agregate vânzări → validare impact comercial al platformei BuildWise post-implementare | WP8 |  |  |  |
### ▶  🏗 DATE TEHNICE CLĂDIRI

| 12 | Stocare date tehnice clădiri | Baza de date cu parametrii tehnici ai clădirilor clienților: tip structură, materiale pereți exteriori, tip acoperiș, subsol/demisol, orientare cardinală, altitudine | F | Critică | Parametri constructivi reali → dataset principal de antrenare pentru modelele de predicție energetică | WP3, WP4 |  |  |  |
| 13 | Clasificare fond construit | Categorizarea clădirilor după tipologie românească: bloc panou prefabricat, bloc cărămidă, casă interbelică, casă construită post-1990, spațiu industrial, clădire comercială, clădire publică | F | Critică | Tipologie fond construit românesc → antrenare modele ML specializate pe piața RO | WP3 |  |  |  |
| 14 | Date sistem HVAC existent | Stocare informații despre sistemele de încălzire/răcire/ventilație ale clienților: tip (centralizat/individual), combustibil (gaz, electricitate, pompă căldură), vârstă instalație | F | Înaltă | Tip HVAC + consum estimat → parametri cheie în modelul de predicție consum energetic | WP4 |  |  |  |
| 15 | Istoric lucrări BAHM per client | Înregistrarea tuturor lucrărilor executate de BAHM la clădirile clienților: montaj sticlă, izolații, renovări, data execuției, suprafețe tratate, echipă executantă | F | Critică | Date lucrări reale (suprafețe, materiale, date) → date de antrenare și validare modele ML | WP3, WP7 |  |  |  |
| 16 | Fotografii și documente atașate | Stocare documente asociate clienților: planuri clădiri, fotografii, certificare energetică existentă, facturi energie, avize, certificate de performanță | F | Medie | Fotografii clădiri + certificate energetice → validare predicții și calibrare modele | WP3 |  |  |  |
### ▶  ⚙ AUTOMATIZARE & INTEGRARE

| 17 | Notificări și task-uri automate | Sistem de alerte și task-uri pentru echipa comercială: urmărire oferte nesoluționate, clienți necontactați în X zile, oferte expirate, aniversări contracte | NF | Medie | Frecvența follow-up-urilor → feature pentru modelele de predicție comportament client | WP5 |  |  |  |
| 18 | Import/Export date | Import date clienți din fișiere CSV/Excel, export rapoarte și liste, sincronizare cu aplicații externe (e-mail, calendar, ERP contabil) | F | Medie | Date importate structurate → îmbogățire dataset antrenare ML | WP2 |  |  |  |
| 19 | Roluri și permisiuni utilizatori | Control acces pe roluri: Administrator, Manager Vânzări, Agent Comercial, Tehnician; permisiuni per modul și per câmp de date | NF | Înaltă | Log-uri de acces utilizatori → date pentru auditul platformei BuildWise | WP6 |  |  |  |
| 20 | Audit log acțiuni utilizatori | Înregistrarea automată a tuturor acțiunilor din sistem: cine a modificat, ce a modificat, când – trasabilitate completă pentru audit intern și extern | NF | Înaltă | Log-uri de utilizare → date pentru monitorizarea procesului P1 în BuildWise | WP6 |  |  |  |
| TOTAL FUNCȚIUNI M1 - CRM |  |  |  | =COUNTA(B5:B28) | funcțiuni implementate la TRL 5 |  |  |  |  |

## Sheet: M2 - Pipeline

### M2 – Pipeline Activity (Urmărire Activitate Comercială) | Funcțiuni TRL 5 – BAHM S.R.L.

| Modul de urmărire a oportunităților comerciale, activităților agenților și performanței pipeline-ului de vânzări BAHM |  |  |  |  |  |  |  |  | =COUNTA(B5:B200) |
| Nr. | Funcțiune | Descriere detaliată | Tip | Prioritate | Date generate pentru ML | WP BuildWise |  |  |  |
### ▶  🎯 MANAGEMENTUL OPORTUNITĂȚILOR

| 1 | Înregistrare oportunități comerciale | Crearea și gestionarea oportunităților de vânzare: denumire oportunitate, client asociat, produs/serviciu vizat, valoare estimată, probabilitate estimată de câștig, sursă lead (referință, vizită, eveniment, web) | F | Critică | Oportunități create + surse lead → date pentru modelele de predicție adopție platformă | WP5 |  |  |  |
| 2 | Etape pipeline configurabile | Definirea și configurarea etapelor pipeline-ului comercial specific BAHM: Identificare Nevoie → Evaluare Tehnică → Ofertă → Negociere → Contract → Execuție → Post-vânzare | F | Critică | Durate pe etape + rate de conversie → ML pentru optimizare proces comercial | WP5 |  |  |  |
| 3 | Probabilitate de câștig automată | Calcul automat și ajustare manuală a probabilității de câștig per oportunitate, bazat pe etapa curentă, istoricul clientului și comportamentul trecut al oportunităților similare | F | Critică | Probabilități istorice + outcome real → date de antrenare pentru modele de predicție vânzări | WP5 |  |  |  |
| 4 | Valoare ponderată pipeline | Calculul automat al valorii ponderate a pipeline-ului: Valoare estimată × Probabilitate câștig. Agregare la nivel de agent, echipă, perioadă | F | Înaltă | Valori ponderate per segment → date pentru modelele de forecasting venituri BuildWise | WP5 |  |  |  |
| 5 | Motive pierdere oportunitate | Înregistrarea motivelor de pierdere pentru fiecare oportunitate închisă negativ: preț, concurență, amânare decizie, lipsă buget, schimbare cerințe, neaprobare finanțare | F | Înaltă | Motive pierdere → ML pentru îmbunătățire ofertă și identificare clienți cu risc de abandon | WP5 |  |  |  |
### ▶  📅 URMĂRIRE ACTIVITĂȚI

| 6 | Planificator activități zilnice | Calendar de activități comerciale per agent: apeluri de prospectare, întâlniri la sediul clientului, vizite la obiectiv, demonstrații tehnice, participare licitații; vizualizare zilnică/săptămânală/lunară | F | Critică | Tipuri activități + frecvențe → date pentru analiza eficienței comerciale și ML de optimizare resurse | WP5, WP6 |  |  |  |
| 7 | Înregistrare vizite tehnice la obiectiv | Documentarea vizitelor tehnice la clădirile clienților: date vizită, persoane prezente, observații tehnice, fotografii, măsurători efectuate (suprafețe, stare tâmplărie, sistem termic) | F | Critică | Date tehnice reale din teren → dataset de antrenare ML cu parametri clădiri reale | WP3, WP4 |  |  |  |
| 8 | Log apeluri telefonice | Înregistrarea apelurilor telefonice: durată, subiect, rezultat (interesat, amânat, refuzat, callback programat), transcriere notițe | F | Medie | Frecvență + outcome apeluri → feature pentru ML de predicție angajament client | WP5 |  |  |  |
| 9 | Urmărire e-mailuri trimise/primite | Integrare cu clientul de e-mail: asocierea e-mailurilor relevante la oportunitățile CRM, urmărire rate deschidere, răspuns, follow-up automat | F | Medie | Rate de răspuns e-mail → indicatori engagement client pentru modele ML | WP5 |  |  |  |
| 10 | Raport activitate zilnică/săptămânală | Generare automată raport activitate per agent: activități planificate vs. realizate, oportunități avansate în pipeline, valoare generată în perioadă | F | Înaltă | Activitate reală vs. planificată → date pentru procesul de monitorizare P1 din BuildWise | WP6 |  |  |  |
### ▶  📊 RAPORTARE & ANALYTICS

| 11 | Dashboard comercial în timp real | Panou de bord cu KPI-uri comerciale actualizate în timp real: oportunități active, valoare totală pipeline, activități restante, obiective lunare vs. realizări | F | Critică | KPI-uri comerciale agregate → date pentru monitorizarea impactului post-implementare BuildWise | WP6, WP8 |  |  |  |
| 12 | Analiză conversie pe etape (funnel) | Vizualizarea ratei de conversie între etapele pipeline-ului: câte oportunități trec din etapa A în etapa B, timp mediu petrecut per etapă, blocaje identificate | F | Înaltă | Rate de conversie reale → date pentru benchmarking și îmbunătățire modele ML comerciale | WP5 |  |  |  |
| 13 | Forecast vânzări lunar/trimestrial | Proiecție automată a vânzărilor bazată pe pipeline curent ponderat, sezonalitate istorică și tendințe; comparare forecast vs. realizat | F | Înaltă | Date historice forecast vs. realizat → antrenare modele de predicție venituri BuildWise | WP5 |  |  |  |
| 14 | Raport performanță per agent comercial | Analiza comparativă a performanței agenților: număr oportunități, valoare câștigată, rată de conversie, timp mediu de închidere, activități efectuate vs. planificate | F | Medie | Performanță agenți → date pentru optimizarea alocării resurselor în procesul P2 BuildWise | WP6 |  |  |  |
| 15 | Analiză produse vândute (mix) | Raport detaliat al produselor/serviciilor BAHM vândute: sticlă tratată termic (suprafețe), lucrări construcții (valori), servicii consultanță – cu distribuție geografică și per segment client | F | Înaltă | Mix produse + tipologie client → date pentru calibrarea motorului de predicție economică BuildWise | WP4, WP8 |  |  |  |
### ▶  ⚙ AUTOMATIZARE PIPELINE

| 16 | Alerte depășire termen activități | Notificări automate pentru activitățile depășite (follow-up-uri, oferte expirate, vizite programate și neefectuate); escaladare automată la manager | NF | Medie | Frecvența alertelor → date pentru indicatorii de performanță proces P1 | WP6 |  |  |  |
| 17 | Reguli automate de avansare pipeline | Configurarea regulilor de avansare automată a oportunităților între etape pe baza criteriilor definite: ofertă trimisă → etapă Negociere, contract semnat → etapă Execuție | F | Medie | Durate tranziție automată → date pentru ML de optimizare flux comercial | WP5 |  |  |  |
| 18 | Duplicat și clonare oportunitate | Funcție de duplicare rapidă a unei oportunități existente cu toate datele asociate – utilă pentru comenzi repetitive sau clienți cu portofoliu similar | F | Scăzută | Frecvența duplicărilor → indicator pattern clienți fideli pentru ML de segmentare | WP5 |  |  |  |
| TOTAL FUNCȚIUNI M2 - PIPELINE |  |  |  | =COUNTA(B5:B26) | funcțiuni implementate la TRL 5 |  |  |  |  |

## Sheet: M3 - PM

### M3 – Project Management (Managementul Proiectelor de Construcții) | Funcțiuni TRL 5 – BAHM S.R.L.

| Modul de planificare, execuție și monitorizare a proiectelor de construcții civile și industriale BAHM | Sursa principală de date ML |  |  |  |  |  |  |  |  | =COUNTA(B5:B200) |
| Nr. | Funcțiune | Descriere detaliată | Tip | Prioritate | Date generate pentru ML | WP BuildWise |  |  |  |
### ▶  📁 PLANIFICARE PROIECT

| 1 | Creare și configurare proiecte | Inițierea proiectelor de construcții/renovări: denumire proiect, client beneficiar, locație (adresă, coordonate GPS, județ), tip lucrare (construcție nouă, renovare termică, montaj tâmplărie, lucrare industrială), valoare contract, dată contractuală de finalizare | F | Critică | Tip proiect + locație + suprafețe → parametri de identificare pentru corelarea cu predicțiile energetice | WP4, WP7 |  |  |  |
| 2 | Structura lucrărilor (WBS) | Descompunerea proiectului în activități și sub-activități ierarhice: capitole de lucrări, categorii de lucrări, articole de deviz; alocare responsabilitate per activitate | F | Critică | Structura lucrărilor + materiale utilizate → date pentru calibrarea parametrilor constructivi în ML | WP3 |  |  |  |
| 3 | Plan de lucru Gantt | Planificarea temporală a activităților cu dependențe (FS, SS, FF, SF), resurse alocate, durată estimată vs. realizată, identificare cale critică | F | Critică | Durate reale per activitate → date pentru modelele de estimare durate și costuri similare | WP5 |  |  |  |
| 4 | Alocarea resurselor umane | Atribuirea angajaților BAHM la proiecte și activități: procentaj de alocare, perioadă, competențe necesare; vizualizare încărcare resurse per angajat și perioadă | F | Înaltă | Alocare resurse + durate reale → date pentru optimizarea planificării resurselor în procesul P2 | WP6 |  |  |  |
| 5 | Deviz estimativ și de execuție | Elaborarea devizelor de lucrări: cantități, prețuri unitare (materiale + manoperă + utilaje + transport), total pe categorii, comparare estimat vs. realizat la finalizare | F | Critică | Deviz materiale + suprafețe → date pentru calibrarea costurilor în modelul economic BuildWise | WP4 |  |  |  |
### ▶  📦 EXECUȚIE & CONSUM

| 6 | Fișe de consum materiale | Înregistrarea zilnică/săptămânală a consumului real de materiale pe șantier: cod material, cantitate consumată, unitate de măsură, lot/batch, magazie de proveniență, activitate asociată | F | Critică | Consum real materiale → date de referință pentru calibrarea predicțiilor de cost și consum energetic | WP3, WP4 |  |  |  |
| 7 | Pontaj manoperă pe șantier | Înregistrarea orelor lucrate per angajat pe fiecare proiect și activitate: prezență zilnică, ore normale, ore suplimentare, tip activitate (manoperă directă, transport, admin) | F | Critică | Ore lucrate + activități → date pentru calculul costurilor reale de execuție și benchmarking ML | WP3 |  |  |  |
| 8 | Evidența subcontractorilor | Gestionarea contractelor cu subcontractorii: activități subcontractate, valori contractate, stadiu plăți, calitatea lucrărilor evaluate, documente (contracte, PV recepție) | F | Înaltă | Costuri subcontractare → componente ale modelului de cost total al lucrării | WP3 |  |  |  |
| 9 | Urmărire livrări materiale | Tracking livrărilor de materiale la șantier: furnizor, cantitate comandată vs. livrată, date livrare, facturi asociate, recepție calitativă (inclusiv sticlă tratată termic) | F | Înaltă | Date livrări sticlă tratată → confirmare instalare și corelare cu măsurători consum post-instalare | WP3, WP7 |  |  |  |
| 10 | Raport zilnic de șantier (RZS) | Completarea și arhivarea raportului zilnic de șantier: activități executate, personal prezent, utilaje utilizate, evenimente deosebite, condiții meteorologice, fotografii | F | Înaltă | Condiții meteo + activități reale → date de contextualitate pentru modelele de predicție energetică (sezonalitate) | WP3 |  |  |  |
### ▶  📊 MONITORIZARE & CONTROL

| 11 | Monitorizare avansare proiect (%) | Calculul și vizualizarea gradului de avansare per proiect: % fizic realizat vs. planificat (S-curve), avansare financiară, identificare proiecte cu risc de întârziere | F | Critică | Avansare reală vs. planificată → date pentru modelele de predicție durate proiecte BuildWise | WP6 |  |  |  |
| 12 | Evidența situațiilor de lucrări | Gestionarea situațiilor de lucrări lunare: cantități realizate, valori, deduceri garanție, TVA, aprobare client, stadiu facturat vs. plătit | F | Critică | Valori facturate per tip lucrare → componente ale modelului de cost total și ROI pentru client | WP4, WP8 |  |  |  |
| 13 | Control buget proiect | Compararea continuă buget alocat vs. costuri angajate vs. costuri realizate: varianțe pe categorii, prognoză la finalizare (EAC), indicatori EVM (CPI, SPI) | F | Critică | Varianțe bugetare reale → date pentru antrenarea modelelor de estimare costuri BuildWise | WP5 |  |  |  |
| 14 | Registru riscuri proiect | Identificarea, evaluarea și urmărirea riscurilor per proiect: probabilitate × impact, responsabil, măsuri de atenuare, status (activ, atenuat, materializat) | NF | Medie | Riscuri materializate → date pentru îmbunătățirea modelelor de predicție costuri și durate | WP6 |  |  |  |
| 15 | Documente și plan calitate | Gestionarea documentației tehnice a proiectului: planuri de execuție, specificații tehnice, PV-uri de lucrări ascunse, certificate de calitate materiale, rapoarte de testare | NF | Înaltă | Certificate materiale (inclusiv sticlă 0,3 W/m²K) → documentație pentru validarea parametrilor în motorul AI | WP3 |  |  |  |
### ▶  ✅ RECEPȚIE & POST-EXECUȚIE

| 16 | Recepție lucrări și punch list | Procesul de recepție la terminarea lucrărilor: lista de remedieri (punch list), PV de recepție la terminarea lucrărilor, PV de recepție finală, garanție post-recepție | F | Înaltă | Date recepție + observații → date de validare calitate execuție pentru modele ML | WP7 |  |  |  |
| 17 | Monitorizare garanție post-execuție | Urmărirea termenelor de garanție pentru lucrările finalizate: alerte expirare garanție, reclamații în garanție, intervenții efectuate, costuri de remediere | F | Medie | Defecte în garanție + suprafețe → date pentru evaluarea performanței reale a materialelor | WP7 |  |  |  |
| 18 | Măsurători consum energetic post-instalare | Înregistrarea măsurătorilor de consum energetic la clădirile unde BAHM a montat sticlă tratată termic sau alte soluții: consum înainte vs. după, perioadă de măsurare, echipamente de măsură utilizate | F | Critică | Consum real pre/post instalare → date de aur pentru validarea și antrenarea modelelor ML de predicție energetică (WP7 pilot) | WP3, WP7 |  |  |  |
| 19 | Baza de date proiecte finalizate | Arhivă completă a proiectelor finalizate cu toți parametrii: suprafețe tratate, materiale, costuri finale, durate reale, date tehnice, satisfacție client, performanță energetică măsurată | F | Critică | Proiecte finalizate cu date complete → dataset principal pentru antrenarea inițială a modelelor ML BuildWise la TRL 5→7 | WP3, WP5, WP7 |  |  |  |
| 20 | Raport de impact energetic per proiect | Generare raport de impact energetic pentru clientul final: consum estimat înainte, consum real după, economii calculate (kWh/an, lei/an, CO₂ evitat), comparare cu standard național | F | Critică | Economii reale documentate → date de validare și benchmark pentru modelele de predicție BuildWise (target: eroare < 15%) | WP4, WP7, WP8 |  |  |  |
| TOTAL FUNCȚIUNI M3 - PM |  |  |  | =COUNTA(B5:B28) | funcțiuni implementate la TRL 5 |  |  |  |  |

## Sheet: Mapare Date → ML

### MAPARE DATE TRL 5 → MODELE ML BuildWise (TRL 7)

Ce date generate de modulele existente (TRL 5) alimentează modelele AI/ML ale platformei BuildWise (TRL 7)

### 📊  MATRICE DATE DISPONIBILE LA TRL 5 → UTILIZARE ÎN MODELE ML BuildWise

| Modul Sursă (TRL 5) | Tip Date Disponibile | Descriere Date | Model ML BuildWise alimentat | WP Utilizare |  |  |
| M1 – CRM | Date constructive clădiri | Tip clădire, suprafețe, an construcție, tip pereți, orientare, locație geografică (județ) | Model de predicție consum energetic (S1) – feature engineering | WP4 |  |  |
| M1 – CRM | Parametri sticlă tratată termic | Coeficient U = 0,3 W/m²K, suprafețe montate per client/clădire | Motor AI calcul transfer termic real – parametru validat | WP4, WP3 |  |  |
| M1 – CRM | Tip sistem HVAC | Combustibil, capacitate, vârstă instalație per clădire | Model predicție consum încălzire/răcire – feature HVAC | WP4 |  |  |
| M1 – CRM | Tipologie client | Persoană fizică/juridică, sector, regiune, suprafață proprietate | Model de segmentare clienți și personalizare output BuildWise | WP5 |  |  |
| M2 – Pipeline | Oportunități comerciale istorice | Valoare, tip produs, stadiu, outcome (câștigat/pierdut), durată ciclu | Model de predicție adoptare platformă și conversie clienți | WP5 |  |  |
| M2 – Pipeline | Date vizite tehnice la obiectiv | Observații tehnice reale, fotografii, măsurători din teren per clădire | Îmbogățire dataset de antrenare cu date de teren validate | WP3 |  |  |
| M2 – Pipeline | Activitate comercială temporală | Frecvență interacțiuni per client, sezonalitate cerere, regiuni active | Model de forecasting cerere și planificare capacitate BAHM | WP5 |  |  |
| M3 – PM | Consum real materiale per proiect | Cantități materiale (sticlă, izolații, etc.) per suprafață/tip clădire | Calibrare costuri materiale în modelul economic BuildWise | WP3, WP4 |  |  |
| M3 – PM | Măsurători consum energetic pre/post | kWh/an înainte și după montaj sticlă tratată; perioadă măsurare; tip clădire | Dataset de aur pentru antrenare și validare ML predicție energetică | WP3, WP7 |  |  |
| M3 – PM | Baza de date proiecte finalizate | Suprafețe tratate, materiale, costuri, durate, performanță energetică măsurată | Dataset principal antrenare inițială modele ML – 3+ modele | WP3, WP5 |  |  |
| M3 – PM | Parametri constructivi reali (WBS) | Materiale pereți, tip acoperiș, structură, subsol – date structurale validate | Feature engineering pentru modelele de predicție energetică pe tipologii RO | WP3, WP4 |  |  |
| M3 – PM | Rapoarte impact energetic | Economii documentate per clădire (kWh, lei, CO₂) – date validate | Date de validare și benchmark – target: eroare predicție < 15% (WP7) | WP7 |  |  |
| M1+M2+M3 | Date integrate multi-modul | Corelarea client (CRM) + oportunitate (Pipeline) + proiect (PM) + consum real → profil complet | Model integrat S2 – Serviciu de Învățare Internă, reantrenare continuă | WP5, WP6 |  |  |
