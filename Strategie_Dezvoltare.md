# Strategie Dezvoltare

BAHN S.R.L.

**BUILDWISE**

Platforma AI pentru Eficienta Energetica a Cladirilor

**STRATEGIE DE DEZVOLTARE A PRODUSULUI**

Roadmap Tehnic \| Strategie de Piata \| Plan Financiar CDI

  ----------------------- -----------------------------------------------
  **Solicitant**          Bahn S.R.L.

  **Produs**              BuildWise --- Platforma AI verticala

  **Program**             PoCIDIF 2021-2027 \| Actiunea 2.1

  **Orizont strategie**   24 luni (6 faze cu milestones)

  **TRL actual → TRL      TRL 5 → TRL 7 (cu perspectiva TRL 9)
  tinta**                 

  **Versiune**            1.0 \| Martie 2026

  **Clasificare**         Confidential
  ----------------------- -----------------------------------------------

CUPRINS

1\. SINTEZA EXECUTIVA

Prezentul document constituie strategia integrata de dezvoltare a
produsului BuildWise, elaborata pe baza cercetarii de piata PoCIDIF v2.0
si a fisei de produs existente. Strategia acopera un orizont de 24 de
luni structurat in 6 faze, de la consolidarea platformei existente (TRL
5) pana la validarea in mediu operational real (TRL 7) si pregatirea
pentru scalare comerciala.

  -----------------------------------------------------------------------
  *Oportunitatea Bahn: o platforma verticala AI care combina predictia
  energetica explicabila, suportul comercial pentru decizia clientului si
  invatarea organizationala din date reale --- un spatiu neocupat in
  piata actuala, intre simulatoarele energetice expert-led si platformele
  CRM/PM generice augmentate cu AI.*

  -----------------------------------------------------------------------

Strategia se construieste pe trei piloni: un roadmap tehnic detaliat cu
activitati CDI, o strategie de piata anchorata in segmentul B2B
mid-market si un plan financiar care justifica necesitatea finantarii
prin PoCIDIF Actiunea 2.1.

  ------------------------------- ---------------------------------------
  **Indicator strategic**         **Valoare tinta**

  Nivel TRL la finalizare proiect TRL 7 --- validat in mediu operational

  Servicii digitale noi           2: predictie energetica externa +
                                  invatare organizationala interna

  Segment de intrare              B2B mid-market: dezvoltatori,
                                  constructori, facility management

  Timp estimat pana la MVP        Lunile 1-9 (Fazele 1-3)

  Timp estimat pana la pilot TRL  Lunile 10-18 (Fazele 4-5)
  7                               

  Numar LOI-uri pilot tinta       Minim 3-5 parteneri relevanti

  Diferentiator cheie             Integrare nativa: building logic + cost
                                  logic + business process logic
  ------------------------------- ---------------------------------------

2\. CONTEXT STRATEGIC SI POZITIONARE

2.1 Problema de piata

Piata relevanta este fragmentata intre trei familii de produse care nu
comunica intre ele: simulatoarele energetice (EnergyPlus, DesignBuilder,
IESVE, PHPP), platformele de energy management operational (Spacewell,
Siemens, Schneider) si platformele CRM/PM augmentate cu AI (HubSpot
Breeze, Salesforce Agentforce, monday.com AI). Niciuna dintre aceste
categorii nu ofera o solutie unitara care sa acopere intregul lant
decizional: de la parametrii cladirii, la scenariu energetic, la
argument comercial, la feedback si invatare organizationala.

In Romania, aceasta fragmentare este amplificata de trei factori
specifici: fondul construit predominant din era socialista (blocuri din
panouri prefabricate, case interbelice, constructii mixte) pentru care
modelele generice europene genereaza recomandari inexacte; adoptia
redusa a AI si cloud (5,2% companii cu AI vs. 20% media UE; 24,9% cloud
vs. 52,7% media UE); si costul prohibitiv al auditurilor energetice
traditionale (500-2.000 EUR/cladire, 2-4 saptamani).

2.2 Oportunitatea Bahn

Cercetarea de piata a identificat un gap structural intre instrumentele
tehnice de simulare si instrumentele de decizie comerciala. BuildWise se
pozitioneaza exact in acest spatiu, propunand o platforma verticala cu
dublu uz:

-   **Serviciu extern (client-facing):** predictia consumului energetic
    si a costurilor de exploatare, cu scenarii comparative explicabile,
    orientat spre educarea pietei si sprijinirea deciziei clientului
    non-expert.

-   **Serviciu intern (organizational learning):** transformarea datelor
    istorice din CRM, pipeline si project management in recomandari
    operationale, reguli reutilizabile si suport decizional explicabil.

2.3 Cadrul de reglementare favorabil

Contextul de reglementare european accelereaza cererea pentru solutii de
tipul BuildWise. Directiva EPBD (recast) a intrat in vigoare la
28.05.2024 si trebuie transpusa pana la 29.05.2026. Cladirile noi ale
autoritatilor publice trebuie sa fie zero-emission de la 01.01.2028, iar
toate cladirile noi de la 01.01.2030. Smart Readiness Indicator (SRI) si
cerintele BACS devin obligatorii pentru anumite sisteme HVAC pana in
2029.

3\. ARHITECTURA PRODUSULUI BUILDWISE

Arhitectura BuildWise este structurata pe doua axe functionale
(serviciul extern si serviciul intern) si patru module tehnice,
integrate intr-un motor hibrid reguli explicabile + AI/ML. Aceasta
arhitectura reflecta atat nevoile identificate in cercetarea de piata,
cat si diferentiatorii cheie fata de competitori.

3.1 Module functionale

  ---------------- -------------- ------------------------------- -------------------
  **Modul**        **Serviciu**   **Descriere functionala**       **Diferentiator**

  M1. Analiza AI a Extern         Utilizatorul introduce          Model ML
  cladirii                        parametrii cladirii; platforma  specializat pe
                                  genereaza raport complet in sub fondul construit
                                  5 minute cu estimari energetice romanesc; interfata
                                  si de cost.                     accesibila
                                                                  non-expertilor

  M2. Simulator    Extern         Generare automata de scenarii   Conectare directa
  multi-scenariu                  comparative de renovare cu      la contextul
                                  estimari de cost, economii      clientului si
                                  anuale si ROI. Comparatie       argumentarea
                                  simultana a pana la 5 scenarii. comerciala

  M3. E-learning   Extern +       Cursuri adaptate dinamic pentru Educare explicita a
  AI               Intern         specialisti, actualizate cu     pietei; codificarea
                                  cele mai noi reglementari.      know-how-ului
                                  Componenta de educare a pietei. intern

  M4. Dashboard    Intern         Monitorizare performanta,       Bucla monitorizare
  monitorizare +                  detectie tipare, recomandari    → invatare →
  invatare                        operationale, prioritizare      recalibrare in
                                  oportunitati din date           aceeasi arhitectura
                                  CRM/pipeline/PM.                
  ---------------- -------------- ------------------------------- -------------------

3.2 Motorul hibrid: reguli explicabile + AI/ML

Elementul central de inovare este motorul hibrid care combina reguli de
business explicabile cu modele predictive AI/ML. Aceasta abordare
rezolva o problema critica a pietei: softurile de simulare sunt precise
dar opace, iar platformele AI generice nu inteleg fizica cladirii.
Motorul hibrid BuildWise ofera predictii cu explicatii trasabile,
esentiale atat pentru credibilitatea comerciala, cat si pentru
evaluatorii de inovare.

-   **Stratul de reguli:** codifica normative tehnice, standarde
    nationale/europene, tipologii constructive romanesti si reguli de
    business validate de experti.

-   **Stratul ML:** modele de regresie si retele neuronale antrenate pe
    date specifice fondului construit romanesc, cu pipeline de
    reantrenare automata pe baza feedback-ului.

-   **Stratul NLP:** generare automata de rapoarte in limbaj natural,
    personalizate pe tipul de utilizator (proprietar vs. specialist vs.
    dezvoltator).

-   **Stratul Computer Vision:** analiza fotografiilor cladirii pentru
    identificarea automata a caracteristicilor constructive (faza
    experimentala, TRL 3-4).

3.3 Stack tehnologic

  ---------------- --------------------------- ---------------------------
  **Componenta**   **Tehnologie**              **Rol**

  AI / Machine     Python, TensorFlow /        Modele predictive consum
  Learning         PyTorch, scikit-learn       energetic

  NLP              LLM fine-tuned + template   Generare rapoarte in limbaj
                   engine                      natural

  Computer Vision  CNN pre-trained + transfer  Analiza fotografii cladiri
                   learning                    

  Backend          FastAPI (Python)            API REST, logica de
                                               business, motor hibrid

  Frontend         React.js (web + mobil       Interfata utilizator
                   responsiv)                  

  Cloud            AWS / Azure (scalabil)      Infrastructura, procesare,
                                               storage

  Baza de date     PostgreSQL + Redis          Date structurate + cache

  Integrari        API-uri nationale (preturi  Date actualizate in timp
                   energie, reglementari)      real
  ---------------- --------------------------- ---------------------------

4\. ROADMAP TEHNIC SI PLAN DE DEZVOLTARE

Roadmap-ul acopera 24 de luni structurate in 6 faze distincte, fiecare
cu obiective clare, activitati CDI specifice, deliverables si criterii
de succes. Primele 18 luni (Fazele 1-5) acopera traiectoria TRL 5 → TRL
7 finantabila prin PoCIDIF, iar Faza 6 pregateste scalarea comerciala
spre TRL 8-9.

4.1 Faza 1: Consolidare si cercetare aplicata (Lunile 1-3)

  -----------------------------------------------------------------------
  *TRL 5 → TRL 5+ \| Obiectiv: Stabilizarea bazei existente si definirea
  modelului de date*

  -----------------------------------------------------------------------

  ----------------- ---------------------------------- -------------------
  **Activitate      **Descriere**                      **Deliverable**
  CDI**                                                

  A1.1 Audit tehnic Evaluarea starii curente a         Raport de audit
  platforma         codului, arhitecturii si datelor   tehnic
  existenta         disponibile din CRM/pipeline/PM.   

  A1.2 Cercetare    Definirea structurii de date       Specificatie model
  model de date     pentru tipologiile constructive    de date v1.0
  energetic         romanesti; identificarea surselor  
                    de date de antrenament.            

  A1.3 Definire     Cercetare aplicata pe arhitectura  Document
  motor hibrid      motorului hibrid; prototip         arhitectura motor
  reguli + ML       conceptual al interactiunii        hibrid
                    reguli-predictii.                  

  A1.4 Inventar     Catalogarea datelor din CRM,       Inventar de date +
  date disponibile  pipeline, PM; evaluare calitate,   gap analysis
                    completitudine, reguli de          
                    guvernanta.                        

  A1.5 Obtinere     Identificarea si contactarea a 3-5 Minim 3 LOI semnate
  LOI-uri pilot     parteneri relevanti pentru         
                    pilotare.                          
  ----------------- ---------------------------------- -------------------

4.2 Faza 2: Dezvoltare MVP - Serviciu extern (Lunile 4-6)

  -----------------------------------------------------------------------
  *TRL 5+ → TRL 6 \| Obiectiv: Primul prototip functional al modulelor M1
  si M2*

  -----------------------------------------------------------------------

  ----------------- ---------------------------------- -------------------
  **Activitate      **Descriere**                      **Deliverable**
  CDI**                                                

  A2.1 Dezvoltare   Implementarea fluxului de          Modul M1 functional
  M1 - Analiza AI   introducere parametri → procesare  (beta)
                    ML → generare raport. Antrenare    
                    model initial pe dataset romanesc. 

  A2.2 Dezvoltare   Implementarea generarii automate   Modul M2 functional
  M2 - Simulator    de scenarii comparative cu calcul  (beta)
                    ROI. Motor de comparatie           
                    multi-scenariu.                    

  A2.3 Motor hibrid Prima versiune functionala a       Motor hibrid
  v1.0              motorului reguli + ML cu           integrat in M1/M2
                    explicatii trasabile.              

  A2.4 Interfata    Frontend React.js cu flux complet: Aplicatie web
  web MVP           input → analiza → scenarii →       accesibila
                    raport.                            

  A2.5 Generare     Implementarea generarii automate   Template rapoarte +
  rapoarte NLP      de rapoarte in limbaj natural,     engine NLP
                    personalizate per tip utilizator.  
  ----------------- ---------------------------------- -------------------

4.3 Faza 3: Dezvoltare MVP - Serviciu intern + integrare (Lunile 7-9)

  -----------------------------------------------------------------------
  *TRL 6 \| Obiectiv: Completarea MVP-ului cu modulele M3, M4 si
  integrarea end-to-end*

  -----------------------------------------------------------------------

  ----------------- ---------------------------------- -------------------
  **Activitate      **Descriere**                      **Deliverable**
  CDI**                                                

  A3.1 Dezvoltare   Platforma de cursuri adaptate      Modul M3 functional
  M3 - E-learning   dinamic; mecanism de actualizare   (beta)
  AI                pe baza reglementarilor noi.       

  A3.2 Dezvoltare   Dashboard de monitorizare cu       Modul M4 functional
  M4 - Dashboard +  detectie tipare, recomandari       (beta)
  learning          operationale din date              
                    CRM/pipeline.                      

  A3.3 Integrare    Conectarea tuturor modulelor in    Platforma integrata
  end-to-end        fluxul unitar: analiza → scenarii  MVP
                    → educatie → monitorizare →        
                    invatare.                          

  A3.4 Integrari    Conectare cu baze de date          API-uri functionale
  API externe       nationale (preturi energie,        
                    materiale, reglementari).          

  A3.5 Testare      Utilizare interna Bahn ca anchor   Raport testare
  interna (Bahn     client pentru validarea fluxurilor interna + feedback
  anchor)           si colectarea feedback-ului.       
  ----------------- ---------------------------------- -------------------

4.4 Faza 4: Pilotare si validare (Lunile 10-14)

  -----------------------------------------------------------------------
  *TRL 6 → TRL 7 \| Obiectiv: Validare in mediu operational real cu
  parteneri pilot*

  -----------------------------------------------------------------------

  ----------------- ---------------------------------- -------------------
  **Activitate      **Descriere**                      **Deliverable**
  CDI**                                                

  A4.1 Onboarding   Configurare platforma pentru 3-5   Parteneri activi pe
  parteneri pilot   parteneri B2B (dezvoltatori,       platforma
                    constructori, administratori).     

  A4.2 Pilotare     Testarea platformei pe cazuri      Minim 20 scenarii
  scenarii reale    reale: ofertare, evaluare          simulate pe cazuri
                    energetica, prioritizare masuri.   reale

  A4.3 Calibrare    Ajustarea modelelor pe baza        Model recalibrat +
  modele ML         feedback-ului din pilot; masurarea metrici de
                    erorilor de predictie.             acuratete

  A4.4 Validare     Testare cu utilizatori             Raport UX +
  explicabilitate   non-experti: intelegerea           satisfaction score
                    rapoartelor, utilitatea            
                    scenariilor, claritatea            
                    explicatiilor.                     

  A4.5 Documentare  Compilarea dovezilor de validare   Dosar TRL 7 complet
  TRL 7             in mediu operational pentru        
                    raportul de inovare.               
  ----------------- ---------------------------------- -------------------

4.5 Faza 5: Optimizare si stabilizare (Lunile 15-18)

  -----------------------------------------------------------------------
  *TRL 7 consolidat \| Obiectiv: Stabilizare produs, optimizare
  performanta, pregatire lansare*

  -----------------------------------------------------------------------

  ----------------- ---------------------------------- -------------------
  **Activitate      **Descriere**                      **Deliverable**
  CDI**                                                

  A5.1 Optimizare   Imbunatatirea acuratetei pe baza   Model ML v2.0
  modele ML         datelor din pilot; reducerea       optimizat
                    timpului de procesare.             

  A5.2 Pipeline     Implementarea mecanismului de      Pipeline CI/CD
  reantrenare       actualizare continua a modelului   pentru ML
  automata          pe baza datelor noi.               

  A5.3 Securitate   Audit de securitate, GDPR,         Raport securitate +
  si conformitate   conformitate cu standarde          certificari
                    nationale/europene.                

  A5.4              Optimizarea cloud pentru suportul  Infrastructura
  Scalabilitate     a 500+ utilizatori simultani.      scalata + load
  infrastructura                                       testing

  A5.5 Documentare  Raportare catre PoCIDIF, raport de Dosar complet
  finala CDI        inovare final, documentatie        PoCIDIF
                    tehnica completa.                  
  ----------------- ---------------------------------- -------------------

4.6 Faza 6: Go-to-market si scalare (Lunile 19-24)

  -----------------------------------------------------------------------
  *TRL 7 → TRL 8+ \| Obiectiv: Lansare comerciala si cresterea bazei de
  utilizatori*

  -----------------------------------------------------------------------

  ----------------- ---------------------------------- --------------------
  **Activitate**    **Descriere**                      **Deliverable**

  A6.1 Lansare      Lansarea publica a platformei      Platforma live +
  comerciala        BuildWise pe segmentul B2B         landing page
                    mid-market.                        

  A6.2 Pachete      Definirea si implementarea         Pricing activ +
  comerciale        pachetelor: Starter, Professional, sistem billing
                    Enterprise.                        

  A6.3 Marketing si Campanii targetate: conferinte     Pipeline vanzari
  vanzari           constructii/energie, content       activ
                    marketing, parteneriate.           

  A6.4 Extindere    Onboarding primii 500 utilizatori; 500+ utilizatori
  baza utilizatori  colectare feedback sistematic.     inregistrati

  A6.5 Evaluare     Analiza fezabilitate pentru        Raport fezabilitate
  extindere UE      adaptarea platformei la alte piete internationalizare
                    europene.                          
  ----------------- ---------------------------------- --------------------

5\. MILESTONES SI KPI DE VALIDARE

Fiecare faza are milestones clare cu criterii de acceptanta masurabile.
Acesti KPI sunt esentiali atat pentru managementul intern al
proiectului, cat si pentru raportarea catre PoCIDIF si pentru dosarul de
validare TRL 7.

  ---------- ------------------- --------------------------------- -----------
  **Luna**   **Milestone**       **KPI de validare**               **TRL**

  L3         MS1: Fundament CDI  Audit tehnic finalizat; model de  TRL 5+
             complet             date v1.0 definit; minim 3 LOI    
                                 semnate                           

  L6         MS2: MVP serviciu   M1 + M2 functionali; motor hibrid TRL 6
             extern              v1.0; raport generat in \<5 min   

  L9         MS3: MVP complet    Toate modulele integrate; testare TRL 6
             integrat            interna Bahn finalizata; API-uri  
                                 conectate                         

  L12        MS4: Pilot operativ Minim 3 parteneri activi; 10+     TRL 6-7
                                 scenarii simulate pe cazuri reale 

  L14        MS5: Validare TRL 7 20+ scenarii validate; eroare     TRL 7
                                 predictie \<15%; satisfaction     
                                 score \>7/10                      

  L18        MS6: Produs         Pipeline reantrenare activ; audit TRL 7
             stabilizat          securitate trecut; 100+           
                                 utilizatori beta                  

  L24        MS7: Lansare        500+ utilizatori; 3 pachete       TRL 8
             comerciala          comerciale active; revenue \>0    
  ---------- ------------------- --------------------------------- -----------

6\. STRATEGIA DE PIATA

6.1 Segmentarea pietei si prioritizare

Pe baza cercetarii de piata, strategia de intrare se concentreaza pe
segmentul B2B mid-market, unde Bahn poate demonstra rapid valoare si
pilota cu date reale. Segmentul B2C (persoane fizice) ramane un obiectiv
secundar pentru Faza 6, dupa validarea TRL 7.

  ---------------- ---------------- ------------------ ---------------- ------------
  **Segment**      **Prioritate**   **Nevoie           **Valoare        **Timing**
                                    principala**       BuildWise**      

  Dezvoltatori     **P1 -           Suport ofertare,   Scenarii rapide, Faza 4-5
  imobiliari /     RIDICATA**       argumentare        explicatii       
  constructori                      comerciala, value  clare, integrare 
                                    engineering        in flux vanzare  

  Facility         **P1 -           Vizibilitate       Estimari         Faza 4-5
  management /     RIDICATA**       costuri            explicabile,     
  administratori                    exploatare,        legatura cu      
                                    prioritizare       operarea reala   
                                    masuri                              

  Echipe interne   **P0 - CRITICA** Invatare           Recomandari      Faza 1-3
  Bahn (anchor                      organizationala,   operationale,    
  client)                           codificare         reguli           
                                    know-how           reutilizabile    

  Corporate /      **P2 - MEDIE**   Bugetare, analiza  Integrare,       Faza 6
  industrial                        portofoliu,        trasabilitate,   
                                    sustenabilitate    rapoarte         
                                                       multi-site       

  Persoane fizice  **P3 -           Comparatie         Raport simplu,   Post Faza 6
  / rezidential    SECUNDARA**      optiuni, impact    scenarii         
                                    costuri viitoare   comparative      
  ---------------- ---------------- ------------------ ---------------- ------------

6.2 Pozitionare competitiva

BuildWise nu concureaza frontal cu simulatoarele energetice existente
(care sunt expert-led) si nici cu platformele CRM/PM generice (care nu
inteleg fizica cladirii). Pozitionarea strategica este in spatiul
neocupat dintre aceste categorii:

  --------------------------- -------------------------------------------
  **Element diferentiator**   **Relevanta strategica**

  D1. Integrare nativa date   Majoritatea produselor aleg fie building
  tehnice + comerciale        simulation, fie CRM/work management.
                              BuildWise le conecteaza in aceeasi
                              platforma.

  D2. Motor hibrid reguli +   Creste credibilitatea si explicabilitatea
  AI/ML                       rezultatelor --- esential pentru piata
                              romaneasca cu adoptie redusa AI.

  D3. Educare explicita a     Produsul nu doar calculeaza, ci traduce
  pietei                      impactul tehnic in cost, scenarii si mesaj
                              comercial inteligibil.

  D4. Dublu uz extern +       Aceeasi investitie CDI genereaza valoare
  intern                      pentru clienti si pentru eficienta
                              operationala interna.

  D5. Invatare                Know-how-ul din CRM, pipeline si PM devine
  organizationala pe date     activ digital reutilizabil.
  reale                       

  D6. Arhitectura pentru      Modelele si regulile pot fi rafinate pe
  recalibrare continua        baza utilizarii si feedback-ului --- nu
                              raman statice.

  D7. Verticalizare pe        Expertiza reala de domeniu, nu AI generic
  constructii si energie      aplicat superficial.
  --------------------------- -------------------------------------------

6.3 Model de business si pricing

Modelul de business este SaaS cu subscriptie lunara/anuala, structurat
pe pachete care cresc in complexitate. Pretul este ancorat in valoarea
economisita comparativ cu auditurile traditionale (500-2.000 EUR/cladire
vs. sub 50 EUR/raport pe BuildWise).

  ---------------- -------------- ------------------------------- -----------------
  **Pachet**       **Pret         **Continut**                    **Segment tinta**
                   orientativ**                                   

  Starter          49 EUR/luna    M1 (Analiza AI) + 10            Administratori,
                                  rapoarte/luna + scenarii de     mici dezvoltatori
                                  baza                            

  Professional     199 EUR/luna   M1 + M2 + M3 + rapoarte         Dezvoltatori,
                                  nelimitate + scenarii           constructori,
                                  avansate + ROI calculator       consultanti

  Enterprise       Custom         Toate modulele + M4 (invatare   Corporate,
                                  organizationala) + integrari    portofolii mari,
                                  CRM + suport dedicat            ESCO

  Pay-per-report   29-49          Raport individual fara          Utilizatori
                   EUR/raport     subscriptie                     ocazionali,
                                                                  persoane fizice
  ---------------- -------------- ------------------------------- -----------------

6.4 Strategie go-to-market

  --------------- ---------------------------------- ------------ -------------------
  **Canal**       **Actiuni**                        **Timing**   **KPI**

  Pilot B2B       Onboarding parteneri LOI; cazuri   Lunile 10-18 3-5 parteneri
  direct          de succes documentate                           activi

  Conferinte si   Prezentari la conferinte           Lunile 15-24 5+ prezentari
  evenimente      constructii/energie/digitalizare                
                  (BIFE-SIM, Expo Energia, etc.)                  

  Content         Blog tehnic, studii de caz,        Lunile 12-24 100+ leads generate
  marketing       webinarii, ghiduri de eficienta                 
                  energetica                                      

  Parteneriate    Asociatii de auditori energetici,  Lunile 18-24 3+ parteneriate
  strategice      camere de comert, firme de                      active
                  consultanta                                     

  Platforme       Prezenta pe marketplaces de        Lunile 20-24 Vizibilitate online
  digitale        constructii si SaaS directories                 crescuta
  --------------- ---------------------------------- ------------ -------------------

7\. PLAN FINANCIAR SI BUGET CDI

7.1 Structura bugetara estimativa

Bugetul este structurat pe categorii eligibile PoCIDIF Actiunea 2.1 si
acopera cele 18 luni de activitati CDI (Fazele 1-5). Faza 6
(go-to-market) este finantata din resurse proprii si din veniturile
generate de primele subscriptii.

  ------------------- ------------- ------------- ------------ -----------
  **Categorie         **Faza 1-3    **Faza 4-5    **Total      **% din
  bugetara**          (L1-9)**      (L10-18)**    CDI**        total**

  Personal CDI        120.000 EUR   100.000 EUR   220.000 EUR  44%
  (echipa tehnica)                                             

  Servicii de         30.000 EUR    20.000 EUR    50.000 EUR   10%
  cercetare si                                                 
  expertiza                                                    

  Infrastructura      15.000 EUR    15.000 EUR    30.000 EUR   6%
  cloud si licente                                             

  Echipamente si      20.000 EUR    5.000 EUR     25.000 EUR   5%
  hardware                                                     

  Achizitie date si   15.000 EUR    10.000 EUR    25.000 EUR   5%
  baze de date                                                 

  Validare, testare   10.000 EUR    30.000 EUR    40.000 EUR   8%
  si certificare                                               

  Management proiect  20.000 EUR    20.000 EUR    40.000 EUR   8%
  si raportare                                                 

  Cheltuieli          20.000 EUR    20.000 EUR    40.000 EUR   8%
  indirecte                                                    
  (overhead)                                                   

  Contingenta (10%)   15.000 EUR    15.000 EUR    30.000 EUR   6%

  **TOTAL CDI**       **265.000     **235.000     **500.000    **100%**
                      EUR**         EUR**         EUR**        
  ------------------- ------------- ------------- ------------ -----------

Nota: Sumele sunt estimative si vor fi detaliate in bugetul final al
cererii de finantare. Structura respecta categoriile de cheltuieli
eligibile PoCIDIF si limita de intensitate a ajutorului de stat
aplicabila IMM-urilor din domeniul TIC.

7.2 Proiectii financiare (3 ani post-lansare)

  ----------------------- --------------- --------------- ---------------
  **Indicator**           **An 1          **An 2          **An 3
                          (L19-L30)**     (L31-L42)**     (L43-L54)**

  Utilizatori activi      500+            2.000+          5.000+

  MRR estimat (Monthly    5.000 EUR       25.000 EUR      75.000 EUR
  Recurring Revenue)                                      

  ARR estimat (Annual     60.000 EUR      300.000 EUR     900.000 EUR
  Recurring Revenue)                                      

  Rata de conversie       5-8%            8-12%           12-15%
  (trial → paid)                                          

  Rata de retentie (churn \<30%           \<20%           \<15%
  anual)                                                  

  Break-even estimat      ---             Sfarsit An 2    ---

  Numar clienti           2-3             8-10            20+
  enterprise                                              

  Numar rapoarte generate 200             1.500           5.000
  / luna                                                  
  ----------------------- --------------- --------------- ---------------

7.3 Justificarea necesitatii finantarii CDI

Finantarea prin PoCIDIF este necesara deoarece proiectul implica
activitati de cercetare aplicata cu risc tehnic si comercial ridicat,
care nu pot fi finantate exclusiv din resursele proprii ale unui IMM. In
mod specific, sunt necesare:

-   **Cercetare pe modelul de date:** structurarea datelor specifice
    fondului construit romanesc si antrenarea modelelor ML pe tipologii
    locale care nu exista in bazele de date internationale.

-   **Dezvoltare motor hibrid:** cercetarea si implementarea unui motor
    care combina reguli explicabile cu predictii ML --- o abordare
    netriviala care necesita iteratii multiple si validare stiintifica.

-   **Calibrare si explainability:** asigurarea ca predictiile sunt
    corecte si explicabile pentru utilizatori non-experti --- un domeniu
    activ de cercetare in AI.

-   **Testare si validare TRL 7:** pilotarea pe cazuri reale cu
    parteneri B2B implica costuri de integrare, suport si documentare
    care depasesc operarea curenta.

8\. ANALIZA RISCURILOR SI MASURI DE MITIGARE

  ------------------- ------------------- ------------ ----------------------------------
  **Risc**            **Probabilitate**   **Impact**   **Masura de mitigare**

  R1. Calitatea       Medie               Ridicat      Parteneriate cu auditori
  insuficienta a                                       certificati; achizitie dataset-uri
  datelor de                                           suplimentare; augmentare sintetica
  antrenament                                          date

  R2. Eroare de       Medie               Ridicat      Calibrare iterativa cu feedback
  predictie peste                                      din pilot; motor hibrid cu reguli
  prag acceptabil                                      ca safety net; transparenta
                                                       privind limitarile

  R3. Adoptie lenta   Medie-Ridicata      Mediu        Intrare prin B2B (nu B2C);
  in piata romaneasca                                  freemium/pay-per-report pentru
                                                       bariera redusa; content educativ

  R4. Intarzieri in   Medie               Mediu        Dezvoltare agila cu sprinturi de 2
  dezvoltare                                           saptamani; MVP prioritizat; buffer
                                                       10% in buget si timeline

  R5. Schimbari in    Scazuta             Mediu        Arhitectura modulara a motorului
  reglementari                                         de reguli; actualizari rapide prin
                                                       configurare, nu prin cod

  R6. Concurenta din  Scazuta-Medie       Mediu        Diferentiere prin verticalizare si
  partea jucatorilor                                   cunoasterea pietei locale;
  mari                                                 speed-to-market pe nisa

  R7. Dependenta de   Scazuta             Ridicat      Multi-cloud ready; backup-uri
  infrastructura                                       automate; SLA cu furnizorii de
  cloud                                                cloud

  R8. Pierderea       Scazuta             Ridicat      Documentatie tehnica completa;
  membrilor cheie din                                  knowledge sharing continuu;
  echipa                                               politica de retentie
  ------------------- ------------------- ------------ ----------------------------------

9\. ALINIERE CU PoCIDIF ACTIUNEA 2.1

BuildWise se incadreaza in mod direct in criteriile de eligibilitate ale
apelului PoCIDIF Actiunea 2.1. Tabelul urmator sintetizeaza
corespondenta punct cu punct:

  ----------------------- -----------------------------------------------
  **Criteriu PoCIDIF**    **Indeplinire BuildWise**

  Solicitant eligibil     Bahn S.R.L. --- IMM din domeniul TIC, cu
                          activitate in sectorul IT

  Subdomeniu de           2.5 Sisteme de inteligenta artificiala ---
  specializare            platforma utilizeaza ML, NLP si Computer Vision
  inteligenta             

  Inovare de produs       Serviciu nou, semnificativ diferit de oferta
                          existenta pe piata; combinatie functionala
                          unica validata prin cercetare de piata si
                          raport de inovare

  Tehnologii avansate     AI/ML, NLP, Computer Vision, Cloud Computing,
                          integrari API in timp real

  Rezultat masurabil CDI  Doua servicii digitale noi: (1) predictie
                          energetica externa si (2) invatare
                          organizationala interna

  Nivel TRL               De la TRL 5 (platforma existenta) la TRL 7
                          (validat in mediu operational real)

  Necesitate CDI          Cercetare aplicata pe model date, motor hibrid,
  demonstrata             calibrare, explainability, testare si validare
                          in mediu real

  Impact masurabil        Reducere timp analiza de la 2-4 saptamani la
                          \<5 min; reducere cost de la 500-2.000 EUR la
                          \<50 EUR/raport; 15-30% economii energetice
                          estimate
  ----------------------- -----------------------------------------------

10\. CONCLUZII SI PASI URMATORI

Strategia de dezvoltare BuildWise demonstreaza ca Bahn S.R.L. are o
oportunitate credibila si bine fundamentata de a dezvolta o platforma
verticala AI in spatiul neocupat dintre simulatoarele energetice
expert-led si platformele CRM/PM generice. Cercetarea de piata confirma
existenta gap-ului, iar planul de dezvoltare structureaza traiectoria de
la TRL 5 la TRL 7 intr-un mod realist, masurabil si aliniat cu cerintele
PoCIDIF Actiunea 2.1.

  -----------------------------------------------------------------------
  *Mesaj central: BuildWise nu este un upgrade incremental de CRM sau un
  nou simulator energetic generalist. Este o platforma verticala AI care
  ocupa spatiul ramas liber dintre aceste categorii, combinand parametrii
  cladirii, reguli explicabile, predictii AI si date
  comerciale/operationale pentru a genera valoare externa si interna in
  acelasi produs.*

  -----------------------------------------------------------------------

10.1 Actiuni prioritare imediate

  --------- ----------------------------------- ------------------- ------------
  **Nr.**   **Actiune**                         **Responsabil**     **Termen**

  A1        Finalizarea raportului de inovare   PM + Consultant     2 saptamani
            (incorporand cercetarea de piata si                     
            strategia)                                              

  A2        Obtinerea LOI-urilor de la minim 3  Business            4 saptamani
            parteneri pilot                     Development         

  A3        Inventarierea completa a datelor    Echipa IT           3 saptamani
            disponibile (CRM, pipeline, PM)                         

  A4        Definirea KPI-urilor de validare    PM + Echipa tehnica 2 saptamani
            TRL 7                                                   

  A5        Construirea demonstratorului de     Echipa AI           4 saptamani
            explicabilitate                                         

  A6        Pregatirea bugetului detaliat       PM + Financiar      3 saptamani
            pentru cererea de finantare PoCIDIF                     

  A7        Actualizarea fisei de produs        PM                  1 saptamana
            conform strategiei aprobate                             
  --------- ----------------------------------- ------------------- ------------

Bahn S.R.L. \| BuildWise --- Strategie de Dezvoltare Produs v1.0 \|
Martie 2026 \| Confidential
