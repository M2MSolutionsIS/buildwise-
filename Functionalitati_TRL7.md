## Sheet: ModulCRM

### Modul CRM – Customer Relationship Management pentru eficiență energetică

### Functionalitate:  Gestionarea relațiilor cu clienții și centralizarea datelor despre imobile

Valoare adaugata:  Reducerea timpului de onboarding și îmbunătățirea calității datelor colectate despre clădiri

Descriere:  Modul de management al clienților (proprietari, arhitecți, dezvoltatori) cu profilare automată AI a imobilelor și istoricul complet al interacțiunilor.

### Submodule:

### ●   Client Records (CR): Evidența completă a clienților și portofoliului de imobile

### ●   Building Profile (BP): Profilarea automată AI a caracteristicilor energetice ale clădirilor

### ●   Interaction History (IH): Istoricul complet al interacțiunilor și recomandărilor

Exemplu: Un proprietar cu un bloc din anii '80 este profilat automat de AI pe baza datelor introduse, generând un scor energetic și recomandări personalizate.

| Nr. | Funcționalitate | Status | Prioritate | Observații |
| 1 | Înregistrare client (date contact, tip proprietar, portofoliu imobile) | Definit | Mare | Bază CRM |
| 2 | Profilare imobil: tip construcție, an, suprafață, zonă climatică, materiale | Definit | Mare | Input principal AI |
| 3 | Scor energetic automat generat de AI pe baza profilului imobilului | Definit | Mare | Output AI principal |
| 4 | Segmentare clienți pe tipologii (rezidențial, comercial, industrial) | Definit | Mare | Baza targetare |
| 5 | Istoric interacțiuni și recomandări anterioare per client | Definit | Mare | Continuitate relație |
| 6 | Management documente imobil (planuri, facturi energie, audituri anterioare) | Recomandat | Mare | Suport analiză AI |
| 7 | Notificări automate de follow-up pentru clienți inactivi | Recomandat | Medie | Retention |
| 8 | Tagging și categorii personalizate per agent/consultant | Recomandat | Medie | Organizare internă |
| 9 | Import/export date clienți (CSV, Excel, API) | Recomandat | Mare | Interoperabilitate |
| 10 | RBAC: roluri agent, manager, admin cu permisiuni granulare | Obligatoriu (CS) | Mare | Securitate & GDPR |
| 11 | Audit trail complet: cine a accesat/modificat date client | Obligatoriu (CS) | Mare | Conformitate GDPR |
| 12 | Consimțământ GDPR și drepturi client (export/ștergere date) | Obligatoriu (CS) | Mare | Obligatoriu legal |
| 13 | Dashboard KPI per agent: clienți activi, recomandări generate, conversii | Recomandat | Mare | Management performanță |
| 14 | Căutare avansată și filtrare multi-criteriu în baza de clienți | Definit | Mare | Uzabilitate |
| 15 | Integrare API cu modulul Pipeline pentru transferul automat de proiecte | Obligatoriu (CS) | Mare | Coeziune platformă |

## Sheet: ModulPipeline

### Modul Pipeline – Urmărirea activității și oportunităților energetice

Functionalitate:  Vizualizarea și gestionarea întregului pipeline de proiecte de eficiență energetică

Valoare adaugata:  Reducerea timpului de răspuns și creșterea ratei de conversie prin automatizare AI

Descriere:  Modul de urmărire a oportunităților de audit/renovare energetică, de la prospectare până la contractare, cu prioritizare automată AI bazată pe potențialul de economie.

### Submodule:

### ●   Opportunity Tracking (OT): Urmărirea oportunităților pe etape (Kanban/pipeline)

### ●   AI Scoring (AS): Scorarea automată a oportunităților după potențial energetic

### ●   Automation Engine (AE): Automatizări de follow-up și escaladare

Exemplu: Un consultant vede în pipeline că 3 clienți comerciali cu consum ridicat nu au primit ofertă în 30 de zile; AI generează automat un reminder și un draft de ofertă.

| Nr. | Funcționalitate | Status | Prioritate | Observații |
| 1 | Vizualizare pipeline Kanban cu etape configurabile (Prospect→Analiză→Ofertă→Contractat) | Definit | Mare | Core workflow |
| 2 | Scor AI de prioritizare oportunitate bazat pe potențialul de economie energetică | Definit | Mare | Inovare AI |
| 3 | Estimare automată AI a economiilor potențiale (ROI, perioada amortizare) | Definit | Mare | Valoare diferențiatoare |
| 4 | Creare și urmărire oferte cu scenarii comparative de renovare energetică | Definit | Mare | Output comercial |
| 5 | Automatizare follow-up: notificări, email-uri, taskuri generate automat | Recomandat | Mare | Eficiență operațională |
| 6 | Previziune pipeline (forecast) bazată pe ML – probabilitate de conversie | Recomandat | Mare | AI predictiv |
| 7 | Tracking activitate agent: apeluri, întâlniri, email-uri per oportunitate | Definit | Medie | Monitorizare activitate |
| 8 | Integrare calendar pentru programarea vizitelor de audit la imobile | Recomandat | Medie | Productivitate |
| 9 | Template-uri de ofertă personalizabile per tipologie imobil/client | Recomandat | Mare | Standardizare |
| 10 | Raport săptămânal AI de activitate cu recomandări de acțiuni prioritare | Recomandat | Mare | Serviciu învățare internă |
| 11 | Dashboard pipeline: valoare totală, etape, conversie, viteză medie | Definit | Mare | Management |
| 12 | Alerte automate pentru oportunități stagnante (> prag configurabil zile) | Recomandat | Mare | Prevenire pierderi |
| 13 | Integrare cu modulul PM la contractare – transfer automat de date | Obligatoriu (CS) | Mare | Coeziune platformă |
| 14 | Logging complet activitate cu timestamp – trasabilitate audit | Obligatoriu (CS) | Mare | Conformitate |
| 15 | Export pipeline (CSV/XLSX/PDF) cu filtre per perioadă/agent/status | Recomandat | Medie | Raportare management |

## Sheet: ModulPM

### Modul PM – Project Management pentru implementare soluții energetice

### Functionalitate:  Coordonarea și urmărirea implementării recomandărilor de eficiență energetică

Valoare adaugata:  Reducerea duratei de implementare și asigurarea măsurabilității economiilor obținute

Descriere:  Modul de management al proiectelor de renovare/reabilitare energetică: de la planificare până la măsurarea rezultatelor reale față de baseline-ul stabilit anterior.

### Submodule:

### ●   Project Planning (PP): Planificarea activităților și resurselor

### ●   Progress Tracking (PT): Urmărirea progresului față de plan

### ●   Results Measurement (RM): Măsurarea economiilor reale vs. estimate AI

Exemplu: La 6 luni după implementarea izolației termice, platforma compară automat consumul real cu baseline-ul, confirmă economia de 23% și generează raportul de impact.

| Nr. | Funcționalitate | Status | Prioritate | Observații |
| 1 | Creare proiect din oportunitate contractată cu preluare automată date imobil | Definit | Mare | Continuitate flux |
| 2 | Planificare activități cu termene, responsabili și dependențe (Gantt) | Definit | Mare | Core PM |
| 3 | Baseline consum energetic stabilit pre-implementare (referință măsurare) | Obligatoriu (CS) | Mare | Esențial pentru inovare |
| 4 | Urmărire progres implementare cu % completare per activitate | Definit | Mare | Monitorizare |
| 5 | Documente proiect: contracte, avize, rapoarte tehnice, facturi | Definit | Mare | Gestiune documente |
| 6 | Milestone-uri și alerte la depășire termene sau bugete | Recomandat | Mare | Control execuție |
| 7 | Măsurare automată economii reale post-implementare vs baseline AI | Definit | Mare | Validare inovare TRL7 |
| 8 | Raport de impact energetic: consum înainte/după, economie %, ROI real | Obligatoriu (CS) | Mare | Livrabil principal |
| 9 | Integrare date consum din facturi sau contoare (import manual/API) | Recomandat | Mare | Acuratețe măsurare |
| 10 | Feedback client la finalizare proiect + scor satisfacție (NPS) | Recomandat | Mare | Serviciu învățare internă |
| 11 | Reantrenare model AI pe baza rezultatelor reale măsurate | Definit | Mare | ML pipeline core |
| 12 | Management resurse: echipă, furnizori, subcontractori per proiect | Recomandat | Medie | Operațional |
| 13 | Dashboard portofoliu proiecte: active, finalizate, economii cumulate | Definit | Mare | Management |
| 14 | Export rapoarte proiect în format PDF/Excel pentru clienți | Recomandat | Mare | Comunicare client |
| 15 | Audit trail modificări plan și documente proiect | Obligatoriu (CS) | Mare | Conformitate |

## Sheet: ServiciuInformare

### Serviciul de Informare și Educare Clienți (AI-powered)

Functionalitate:  Generare automată AI de conținut personalizat despre eficiența energetică a imobilului clientului

Valoare adaugata:  Creșterea gradului de conștientizare și reducerea timpului de decizie al clientului

Descriere:  Serviciu AI care, pe baza profilului imobilului și istoricului interacțiunilor din CRM, generează automat materiale educative personalizate, scenarii de consum și ghiduri de renovare adaptate specificului clădirii.

### Submodule:

### ●   Content Generation (CG): Motor AI de generare conținut personalizat

### ●   Scenario Simulator (SS): Simulator scenarii consum/economii per imobil

### ●   Education Hub (EH): Biblioteca de resurse educative structurate

Exemplu: Un proprietar de apartament dintr-un bloc din 1978 primește automat un ghid personalizat despre reabilitarea termică cu estimări de cost și economii pentru specificul blocului său.

| Nr. | Funcționalitate | Status | Prioritate | Observații |
| 1 | Generare automată raport energetic personalizat per imobil (AI) | Definit | Mare | Core serviciu |
| 2 | Simulator scenarii: 3-5 opțiuni de renovare cu cost, economie, ROI | Definit | Mare | Inovare cheie |
| 3 | Comparație automată imobil vs. medii naționale pe tipologie | Definit | Mare | Contextualizare |
| 4 | Bibliotecă ghiduri educative pe tipologii (bloc panou, casă interbelică, nou) | Definit | Mare | Specific piață RO |
| 5 | Conținut adaptat nivelului de cunoștințe al clientului (tehnic/non-tehnic) | Recomandat | Mare | Accesibilitate |
| 6 | Distribuție multi-canal: email, PDF, in-app, WhatsApp | Recomandat | Mare | Reach |
| 7 | Materiale video explicative generate/selectate automat de AI | Recomandat | Medie | Engagement |
| 8 | Calculator interactiv consum lunar personalizat | Recomandat | Mare | Utilitate directă |
| 9 | Ghid pas-cu-pas pentru obținerea finanțărilor (PNRR, AFM, etc.) | Recomandat | Mare | Valoare adăugată |
| 10 | Notificări proactive la modificări legislative (ex: directive UE energie) | Recomandat | Medie | Relevanță continuă |
| 11 | Rating conținut de către clienți + colectare feedback | Recomandat | Medie | Input ML |
| 12 | Analytics consum conținut: views, timp citire, acțiuni declanșate | Recomandat | Mare | Optimizare serviciu |
| 13 | Conformitate GDPR pentru datele de profil utilizate la personalizare | Obligatoriu (CS) | Mare | Legal |
| 14 | Accesibilitate conținut (contrast, font, responsive mobile/web) | Recomandat | Medie | Incluziune |

## Sheet: ServiciuInvatare

### Serviciul de Învățare Internă (ML din interacțiuni cu clienții)

Functionalitate:  Îmbunătățirea continuă a modelelor AI prin extragerea pattern-urilor din interacțiunile reale cu clienții

Valoare adaugata:  Creșterea acurateței recomandărilor cu fiecare interacțiune – platforma devine mai inteligentă în timp

Descriere:  Mecanism ML care analizează feedback-ul clienților, rezultatele reale ale proiectelor și interacțiunile din CRM pentru a îmbunătăți continuu modelele de predicție energetică și recomandare.

### Submodule:

### ●   Feedback Loop (FL): Colectare și procesare feedback din toate modulele

### ●   Model Retraining (MR): Pipeline automat de reantrenare modele ML

### ●   Knowledge Base (KB): Baza de cunoaștere internă îmbogățită continuu

Exemplu: După 50 de proiecte finalizate, modelul AI constată că estimările pentru blocuri P+4 din zona Moldova erau cu 15% sub realitate și se recalibrează automat.

| Nr. | Funcționalitate | Status | Prioritate | Observații |
| 1 | Colectare automată feedback din CRM, Pipeline și PM (implicit și explicit) | Definit | Mare | Input principal ML |
| 2 | Extragere pattern-uri din interacțiunile client-consultant (NLP) | Definit | Mare | Inovare NLP |
| 3 | Comparare estimări AI vs. rezultate reale măsurate în PM | Obligatoriu (CS) | Mare | Validare model |
| 4 | Pipeline automat de reantrenare model la acumulare date suficiente | Definit | Mare | MLOps core |
| 5 | Versionare modele ML cu rollback în caz de degradare performanță | Obligatoriu (CS) | Mare | Stabilitate |
| 6 | Dashboard performanță modele: acuratețe, drift, distribuție erori | Definit | Mare | Monitorizare ML |
| 7 | Alertă automată la degradarea performanței modelului (>prag configurat) | Recomandat | Mare | Calitate model |
| 8 | Baza de cunoaștere: cazuri rezolvate, soluții aplicate, lecții învățate | Recomandat | Mare | Cunoaștere organizațională |
| 9 | Recomandări automate pentru consultanți bazate pe cazuri similare | Recomandat | Mare | Asistare internă |
| 10 | Raport lunar performanță AI: îmbunătățiri, acuratețe, impact business | Recomandat | Mare | Transparență management |
| 11 | Explicabilitate recomandări (XAI): de ce AI a recomandat soluția X | Obligatoriu (CS) | Mare | Transparență & conformitate |
| 12 | Control uman obligatoriu pentru recomandări cu impact major (human-in-loop) | Obligatoriu (CS) | Mare | AI responsabil |
| 13 | Documentație model: date I/O, metrici, limitări, date reantrenare | Obligatoriu (CS) | Mare | Livrabil PoCIDIF |
| 14 | Separare date test/validare pentru evitarea overfitting pe date reale | Recomandat | Mare | Calitate ML |

## Sheet: ProcesMonitorizare

### Procesul de Monitorizare a Activității Platformei

Functionalitate:  Urmărirea în timp real a KPI-urilor operaționali, de business și AI ai platformei BuildWise

### Valoare adaugata:  Identificarea rapidă a problemelor și oportunităților de optimizare

Descriere:  Proces continuu de monitorizare care agregă date din toate modulele (CRM, Pipeline, PM, AI) și furnizează management-ului o viziune completă asupra performanței platformei și impactului real.

### Submodule:

### ●   Operational Monitoring (OM): KPI operaționali în timp real

### ●   Business Monitoring (BM): Metrici de business și impact

### ●   AI Monitoring (AM): Performanța și sănătatea modelelor ML

Exemplu: Managerul vede în dashboard că rata de conversie Pipeline→PM a scăzut cu 12% față de luna trecută și că modelul AI de estimare ROI are un drift crescut – ambele necesită intervenție.

| Nr. | Funcționalitate | Status | Prioritate | Observații |
| 1 | Dashboard operațional: utilizatori activi, sesiuni, timp răspuns platformă | Definit | Mare | Sănătate sistem |
| 2 | KPI business: clienți noi/lună, rata conversie, venit generat, proiecte active | Definit | Mare | Performanță business |
| 3 | KPI impact: economii energetice cumulate, CO2 redus, ROI mediu proiecte | Definit | Mare | Impact real PoCIDIF |
| 4 | Monitorizare performanță modele AI: acuratețe, latență, drift detector | Obligatoriu (CS) | Mare | MLOps |
| 5 | Alerte automate la depășire praguri critice (SLA, erori, degradare ML) | Definit | Mare | Reziliență |
| 6 | Rapoarte periodice automate (zilnic/săptămânal/lunar) trimise pe email | Recomandat | Mare | Raportare management |
| 7 | Monitorizare securitate: tentative acces neautorizat, anomalii sesiuni | Obligatoriu (CS) | Mare | Securitate |
| 8 | Uptime monitoring și incident tracking cu SLA 99% disponibilitate | Obligatoriu (CS) | Mare | Conformitate CS |
| 9 | Heatmap activitate utilizatori pentru optimizare UX | Opțional | Mică | UX îmbunătățire |
| 10 | Export date monitorizare pentru raportare PoCIDIF/finanțator | Obligatoriu (CS) | Mare | Raportare proiect |

## Sheet: ProcesPerfectionare

### Procesul de Perfecționare Continuă a Platformei

### Functionalitate:  Ciclul structurat de îmbunătățire a produsului bazat pe date și feedback real

### Valoare adaugata:  Asigurarea relevanței și competitivității platformei pe termen lung

Descriere:  Proces formal de perfecționare care integrează feedback din monitorizare, date de utilizare, feedback clienți și rezultate ML pentru a prioriza și implementa îmbunătățiri continue ale platformei.

### Submodule:

### ●   Feedback Collection (FC): Colectare structurată feedback din toate sursele

### ●   Improvement Backlog (IB): Gestiunea backlog-ului de îmbunătățiri prioritizate

### ●   Release Management (RM): Planificarea și livrarea iterațiilor de produs

Exemplu: Pe baza analizei a 200 de sesiuni, echipa identifică că 40% din consultanți nu folosesc simulatorul de scenarii – se decide un tutorial in-app și o simplificare a UI, livrate în sprint-ul următor.

| Nr. | Funcționalitate | Status | Prioritate | Observații |
| 1 | Colectare NPS și feedback structurat de la clienți la finalizare proiect | Definit | Mare | Vocea clientului |
| 2 | Colectare feedback intern consultanți despre utilitatea funcționalităților | Definit | Mare | Vocea utilizatorului |
| 3 | Analiza automată a pattern-urilor de utilizare pentru identificare fricțiuni UX | Recomandat | Mare | Data-driven |
| 4 | Backlog de îmbunătățiri prioritizat după impact și efort (MoSCoW/RICE) | Definit | Mare | Product management |
| 5 | Sprint-uri de dezvoltare bidirecționale (2 săptămâni) | Definit | Mare | Metodologie Agile |
| 6 | Validare îmbunătățiri cu utilizatori pilot înainte de release general | Recomandat | Mare | Calitate |
| 7 | Documentare release notes și comunicare schimbări către utilizatori | Recomandat | Medie | Transparență |
| 8 | Revizuire trimestrială a roadmap-ului produsului bazată pe date | Recomandat | Mare | Strategie |
| 9 | Benchmarking periodic față de soluții concurente de pe piața europeană | Recomandat | Medie | Competitivitate |
| 10 | Raport semestrial de impact și inovare pentru finanțator (PoCIDIF) | Obligatoriu (CS) | Mare | Raportare obligatorie |

## Sheet: Platforma_AI

### Platforma AI – Capabilități Transversale și Infrastructură

Functionalitate:  Securitate, interoperabilitate, guvernanță date și MLOps pentru toate modulele BuildWise

Valoare adaugata:  Stabilitate, conformitate GDPR și scalabilitate pentru TRL5→TRL7 și expansiune comercială

Descriere:  Capabilități comune care susțin CRM, Pipeline, PM și serviciile AI: identitate, securitate, date, ML infrastructure și administrare.

### Submodule:

### ●   Securitate & Conformitate: Autentificare, autorizare, criptare, audit

### ●   MLOps & XAI: Orchestrare modele, versionare, explicabilitate

### ●   Data Platform: Stocare, procesare, guvernanță date

### ●   API & Integrări: Conectori externi și interni

### ●   Administrare & Configurare: Setări platformă, multi-tenant

| Nr. | Funcționalitate | Status | Prioritate | Observații |
| 1 | Management utilizatori, RBAC granular, MFA obligatoriu, SSO opțional | Obligatoriu (CS) | Mare | Securitate |
| 2 | Criptare în tranzit (TLS 1.2+) și în repaus (AES-256), management chei | Obligatoriu (CS) | Mare | Securitate |
| 3 | Audit trail imuabil, loguri acces/modificare, retenție 12 luni, politici GDPR | Obligatoriu (CS) | Mare | Conformitate |
| 4 | API REST securizat (JWT/OAuth2) pentru integrări externe și inter-module | Obligatoriu (CS) | Mare | Interoperabilitate |
| 5 | Integrare API surse date externe: prețuri energie, baze date imobile, meteo | Recomandat | Mare | Calitate date AI |
| 6 | Data platform: stocare time-series consum, data lake, ETL/ELT pipelines | Definit | Mare | Fundație ML |
| 7 | MLOps: orchestrare modele, versionare, deployment, A/B testing | Obligatoriu (CS) | Mare | Calitate ML |
| 8 | Explainable AI (XAI): scoruri, factori de influență, justificări recomandări | Obligatoriu (CS) | Mare | Transparență AI |
| 9 | Monitorizare model drift și trigger automat reantrenare la prag depășit | Definit | Mare | Calitate continuă |
| 10 | Backup periodic + Point-in-Time Recovery, plan DR testat | Obligatoriu (CS) | Mare | Continuitate |
| 11 | Arhitectură cloud-native cu scalare orizontală (Kubernetes/container) | Definit | Mare | Scalabilitate |
| 12 | Multi-tenant: izolare date între clienți enterprise (dacă aplicabil) | Recomandat | Medie | Expansiune B2B |
| 13 | Portabilitate: instalare on-premise și cloud privat (cerință CS) | Obligatoriu (CS) | Mare | Flexibilitate |
| 14 | Conformitate GDPR: minimizare date, drept ștergere, export portabil | Obligatoriu (CS) | Mare | Legal |
| 15 | API documentat (OpenAPI/Swagger) cu exemple și sandbox de testare | Obligatoriu (CS) | Mare | Livrabil |

## Sheet: Conformitate_PoCIDIF

### BuildWise – Conformitate față de criteriile PoCIDIF Acțiunea 2.1 și Grila ETF

| ID | Cerință PoCIDIF / Criteriu ETF | Tip | Acoperire | Referințe (Sheet!Rând) | Observații | Grup |
| E-I-1 | IMM din domeniul TIC cu cod CAEN eligibil (6210/6290/6310 etc.) | Eligibilitate | Da | — | BAHM – IMM TIC; de verificat certificat constatator | Eligibilitate |
| E-I-2 | Profit din exploatare > 0 în ultimul exercițiu financiar | Eligibilitate | Da | — | De confirmat din situații financiare BAHM | Eligibilitate |
| E-I-3 | Fără datorii fiscale nete la bugetul consolidat | Eligibilitate | Da | — | Declarație unică – asumare solicitant | Eligibilitate |
| CS-I-1 | Produs/serviciu/aplicație nou sau semnificativ îmbunătățit (inovare de produs) | Funcțional | Da | ModulCRM!3; ServiciuInformare!1-3; ServiciuInvatare!1-4 | AI aplicat pe fondul construit românesc – diferențiator demonstrabil | Inovare |
| CS-I-2 | Utilizare tehnologie avansată (AI/ML – subdomeniu 2.5 specializare inteligentă) | Funcțional | Da | Platforma_AI!7-9; ServiciuInvatare!3-4; ModulPipeline!6 | ML, NLP, XAI – încadrare clară subdomeniu 2.5 | Inovare |
| CS-I-3 | TRL start ≥ 4-5; TRL final ≥ 7 demonstrat în mediu real | Funcțional | Da | ModulPM!3,7,8; ProcesMonitorizare!3 | TRL5 existent (soft funcțional); TRL7 prin pilot + măsurare baseline vs real | Inovare |
| CS-I-4 | Raport expert extern care validează caracterul inovativ al produsului | Procedural | Necesar | — | De obținut înainte de depunere – OBLIGATORIU pentru punctaj inovare | Inovare |
| CS-I-5 | Diferențiere clară față de soluțiile existente pe piața națională/europeană | Funcțional | Da | ServiciuInformare!3-4; ModulCRM!3 | Model ML pe fond construit RO; specificitate piață locală – argument solid | Inovare |
| ETF-1-A | ETF: Produs rezolvă problemă reală fără soluție eficientă pe piață (4 pct) | ETF Inovare | Da | ServiciuInformare!1-4; ModulCRM!3 | Lipsa soluțiilor specializate pe fondul construit românesc – documentabil | ETF |
| ETF-1-B | ETF: Bazat pe tehnologie emergentă (AI/ML) folosită în mod original (4 pct) | ETF Inovare | Da | Platforma_AI!7-9; ServiciuInvatare!3-4 | ML reantrenat pe date reale RO + NLP pe interacțiuni consultanți | ETF |
| ETF-1-C | ETF: Concept clar de diferențiere față de competitori (4 pct) | ETF Inovare | Da | ServiciuInformare!3-5; ServiciuInvatare!8 | Specializare fond construit RO; learning din interacțiuni = diferențiator | ETF |
| ETF-1-D | ETF: Compatibil cu mai multe platforme/sisteme (4 pct) | ETF Inovare | Da | Platforma_AI!4,11,13 | API REST, cloud-native, on-prem; integrare surse date externe | ETF |
| ETF-1-E | ETF: Demonstrează valoare adăugată clară – economisește timp/bani/resurse (4 pct) | ETF Inovare | Da | ModulPM!8; ProcesMonitorizare!3; ServiciuInformare!2 | Raport impact energetic cu economii măsurate % – dovadă directă | ETF |
| ETF-2-A | ETF: Acorduri prealabile cu clienți/parteneri pilot (5 pct dacă >3 acorduri) | ETF Maturitate | Parțial | — | De semnat LOI/acorduri cu min. 3-5 clienți pilot ÎNAINTE de depunere | Maturitate |
| ETF-2-B | ETF: Grad inovare tehnic cu detalii tehnice și științifice (max 10 pct) | ETF Maturitate | Parțial | Platforma_AI!7-9; ServiciuInvatare!3-6 | Necesită documentație tehnică detaliată ML – arhitectură, algoritmi, metrici | Maturitate |
| ETF-2-C | ETF: Ponderea cheltuielilor CDI ≥ 50% din buget total eligibil (5 pct) | ETF Buget | Necesar | — | Bugetul trebuie structurat cu minim 50% pe activități CDI | Buget |
| ETF-2-D | ETF: Acoperire mai mult de 2 subsectoare de activitate (5 pct) | ETF Piață | Da | ServiciuInformare!3-4 | Rezidențial + Comercial + Specialiști – minim 3 subsectoare demonstrabile | Piață |
| NFR-I-1 | Criptare date stocate și transmise (AES-256 / TLS 1.2+) | Securitate | Da | Platforma_AI!2 | Explicit în arhitectură | Securitate |
| NFR-I-2 | Autentificare bazată pe roluri (RBAC) + MFA obligatoriu | Securitate | Da | Platforma_AI!1; ModulCRM!10 | RBAC + MFA explicit | Securitate |
| NFR-I-3 | Audit trail complet, retenție 12 luni | Securitate | Da | Platforma_AI!3; ModulCRM!11 | Loguri imuabile + GDPR | Securitate |
| NFR-I-4 | Backup periodic + Point-in-Time Recovery | Securitate | Da | Platforma_AI!10 | Backup + DR testat | Securitate |
| NFR-I-5 | Conformitate GDPR (consimțământ, ștergere, export) | Securitate | Da | ModulCRM!12; ServiciuInformare!13; Platforma_AI!14 | GDPR complet acoperit | Securitate |
| NFR-II-1 | Timp răspuns operațiuni uzuale ≤ 3 secunde | Performanță | Da | ProcesMonitorizare!1 | KPI monitorizat în timp real | Performanță |
| NFR-II-2 | Disponibilitate min. 99% | Performanță | Da | ProcesMonitorizare!8; Platforma_AI!11 | SLA monitorizat explicit | Performanță |
| DOC-I-1 | Documentație arhitectură (logică/fizică, diagrame, fluxuri) | Documentație | Necesar | — | Livrabil obligatoriu – de pregătit pe parcursul proiectului | Documentație |
| DOC-I-2 | Documentație ML (date I/O, metrici, limitări, reantrenare) | Documentație | Da | ServiciuInvatare!13 | Cerut explicit în ServiciuInvatare | Documentație |
| DOC-I-3 | Raport pilot demonstrat + economii măsurate (TRL7) | Documentație | Da | ModulPM!7,8; ProcesMonitorizare!3,10 | Livrabil central pentru validare TRL7 | Documentație |
| DOC-I-4 | Plan și rapoarte de testare (funcțional, performanță, securitate) | Documentație | Necesar | — | De elaborat pe parcurs; critic pentru recepție | Documentație |
| DOC-I-5 | Specificații API documentate (OpenAPI/Swagger) | Documentație | Da | Platforma_AI!15 | Explicit în platformă | Documentație |
| DOC-I-6 | Raport semestrial impact și inovare pentru finanțator PoCIDIF | Documentație | Da | ProcesPerfectionare!10 | Asumat în ProcesPerfectionare | Documentație |
| DNSH-1 | Echipamente IT cu eficiență energetică (Directiva 2009/125/CE) | Mediu/DNSH | Necesar | — | Specificat la achiziție echipamente cloud/servere | DNSH |
| DNSH-2 | Sisteme proiectate cu tehnologii de înaltă eficiență energetică | Mediu/DNSH | Da | Platforma_AI!11 | Cloud-native = eficiență energetică intrinsecă | DNSH |

## Sheet: Gaps_Actiuni

### BuildWise – Gap-uri față de PoCIDIF și acțiuni necesare înainte de depunere

| ID | Gap identificat | Risc | Acțiune recomandată | Termen | Responsabil |
| G-01 | Raport expert extern privind inovarea – LIPSEȘTE | CRITIC – fără acesta proiectul se respinge automat | Identificare și contractare expert extern acreditat; pregătire dosar tehnic de inovare | Înainte de depunere | Management BAHM |
| G-02 | Acorduri/LOI cu clienți pilot – INSUFICIENTE | Mare – fără >3 acorduri se pierd 5 puncte ETF | Semnare min. 4-5 LOI cu proprietari sau firme care testează platforma | Înainte de depunere | Business Dev BAHM |
| G-03 | Documentație tehnică ML detaliată – PARȚIALĂ | Mare – evaluatorul ETF verifică detalii tehnice și științifice | Elaborare document arhitectură ML: algoritmi, date antrenare, metrici acuratețe, validare | Luna 1-2 proiect | Tech Lead BAHM |
| G-04 | Ponderea CDI în buget – DE VERIFICAT | Mare – sub 50% pierde 5 puncte ETF | Structurare buget cu minim 50% pe activități CDI (salarii cercetători, subcontractare CDI) | La elaborare buget | CFO / PM BAHM |
| G-05 | Baseline consum energetic pentru pilot – INEXISTENT | Mare – necesar pentru demonstrarea TRL7 și validarea economiilor | Identificare min. 3-5 clădiri pilot cu date istorice de consum disponibile | Luna 1-3 proiect | Tech + Business Dev |
| G-06 | Benchmarking față de soluții concurente – LIPSEȘTE | Medie – evaluatorul va verifica diferențierea față de piață | Analiză competitivă documentată: soluții europene vs BuildWise, tabel comparativ | Înainte de depunere | Product BAHM |
| G-07 | Plan de comercializare post-proiect – LIPSEȘTE | Medie – necesar pentru criteriul de durabilitate | Elaborare plan go-to-market: prețuri, canale, target clienți ani 1-3 post-finanțare | La elaborare cerere | Management BAHM |
| G-08 | Documentație arhitectură sistem – LIPSEȘTE | Medie – livrabil obligatoriu PoCIDIF | Diagrame logice/fizice, fluxuri date, stack tehnologic documentat | Luna 2-3 proiect | Tech Lead BAHM |

## Sheet: Legendă

### BuildWise – Legendă coduri culori și status-uri

### STATUS FUNCȚIONALITATE

| Obligatoriu (CS) | Cerință minimă obligatorie conform caietului de sarcini / PoCIDIF |  |
| Definit | Funcționalitate planificată și specificată în detaliu |  |
| Recomandat | Funcționalitate recomandată pentru calitate și competitivitate |  |
| Opțional | Funcționalitate de luat în considerare în versiuni viitoare |  |
### ACOPERIRE CONFORMITATE

| Da | Cerință acoperită în workbook |  |
| Parțial | Cerință parțial acoperită – necesită completare |  |
| Necesar | Cerință neacoperită – acțiune obligatorie înainte de depunere |  |
### RISC GAP-URI

| CRITIC | Proiectul se respinge automat dacă nu este rezolvat |  |
| Mare | Pierdere semnificativă de puncte ETF |  |
| Medie | Impact moderat asupra scorului sau durabilității |  |
