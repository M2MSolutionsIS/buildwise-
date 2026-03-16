# Wireframes Faza0

**BuildWise**

Wireframe Specification Document

Faza 0 --- Ecrane Validate

9 ecrane \| 3 prototipuri (P1 BuildWise, P2 BAHM, P3 ERP Lite)

6 comune + 3 specifice P1

**M2M Solutions Consulting SRL**

Martie 2026 --- Document intern

Cuprins

Legendă & Convenții

**Scope (domeniu de aplicabilitate)**

  --------------- ---------------------------------------------- ---------
  **COMUN**       Ecran identic în toate cele 3 prototipuri. Se  ■
                  wireframe-ează o singură dată.                 

  **SPECIFIC P1** Ecran exclusiv BuildWise (AI/energie). Nu      ■
                  apare în P2 sau P3.                            

  **SPECIFIC P2** Ecran exclusiv BAHM Operational                ■
                  (RM/construcții). Nu apare în P1 sau P3.       

  **SPECIFIC P3** Ecran exclusiv M2M ERP Lite (generic). Nu      ■
                  apare în P1 sau P2.                            
  --------------- ---------------------------------------------- ---------

**Priorități**

P0 --- Critică: trebuie implementat înainte de lansare MVP. P1 ---
Importantă: necesar pentru produs complet. P2 --- Utilă: nice-to-have,
poate fi amânat.

**Structura per ecran**

Fiecare ecran conține: (1) Screenshot wireframe în culorile reale ale
design system-ului, (2) Tabel specificații (scope, F-codes, tip,
complexitate, status, prioritate, tab-uri), (3) Descriere narativă, (4)
Stări ale ecranului (empty, loading, error, variante per prototip), (5)
Note developer (API, validări, responsive, biblioteci recomandate).

Faza 0 --- Ecrane Validate

9 ecrane: 6 comune (CRM, Pipeline, PM) + 3 specifice P1 (Technical Data,
Post-Exec Energy, Data→ML). Wireframe-uri V1 finalizate --- servesc
drept referință vizuală și funcțională pentru developeri.

E-001 --- Dashboard Principal

![Wireframe
E-001](media/835c085e4e8cb63572c4befdbe81cd2c3db239fb.jpg "E-001 Dashboard Principal"){width="6.770833333333333in"
height="7.354166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN --- P1 ✓ P2 ✓ P3 ✓

  **F-codes**        F001, F050, F078, F095, F101, F120

  **Tip ecran**      Dashboard

  **Complexitate**   Ridicată

  **Status WF**      WF V1 ✓

  **Prioritate**     P0 --- Critică

  **Tab-uri /        KPI Summary \| Pipeline Overview \| Proiecte Active
  Subecrane**        \| Impact Energetic (P1) \| TrueCast \| Alerte
  ------------------ ----------------------------------------------------

**Descriere**

Ecran de aterizare. Toate cardurile sunt clickable --- fiecare
navighează la ecranul detaliat al modulului respectiv. KPI-urile se
încarcă asincron. Widget Impact Energetic vizibil doar în P1
(BuildWise). Widget RM vizibil doar în P2 (BAHM). TrueCast = P&L + CF
sumarizat din toate proiectele active.

**Stări ale ecranului**

**Empty State (cont nou)**

KPI-uri = 0 sau dash. Carduri Pipeline și Proiecte arată mesaj \"Nicio
oportunitate încă\" cu CTA. TrueCast ascuns.

**Loading**

Skeleton loader pe carduri. KPI-urile au shimmer animation. Se încarcă
paralel (Promise.all pe endpoint-uri).

**Variante prototip**

P1: widget energie (consum mediu kWh/m², economie totală). P2: widget RM
(semafoare echipe, echipamente, conflicte). P3: fără widget-uri
specifice --- doar pipeline + proiecte + TrueCast.

**Note developer**

**API**

GET /api/dashboard/kpis, GET /api/dashboard/pipeline?top=5, GET
/api/dashboard/projects?status=active, GET /api/dashboard/truecast, GET
/api/dashboard/alerts?limit=5. Toate endpoint-urile sunt independente
--- load paralel.

**Refresh**

Auto-refresh la 5 min (configurable). Manual refresh cu Ctrl+R sau
buton. Cache: KPIs 30s, Pipeline 60s, Proiecte 60s, Alerte real-time
(WebSocket).

**Responsive**

Desktop: grid 2 coloane. Tablet: 1 coloană. Mobile: KPIs în scroll
horizontal, carduri stacked.

E-002 --- Contacts --- Lista

![Wireframe
E-002](media/89e58c5b21ef715873815dd3730e83dd35a3d086.jpg "E-002 Contacts — Lista"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN --- P1 ✓ P2 ✓ P3 ✓

  **F-codes**        F002, F003, F004, F005, F006

  **Tip ecran**      List + Filters

  **Complexitate**   Medie

  **Status WF**      WF V1 ✓

  **Prioritate**     P0 --- Critică

  **Tab-uri /        Tabel paginat \| Filtre (status, tip, locație,
  Subecrane**        agent) \| Search \| Bulk actions \| Export \|
                     Duplicate Guard badge
  ------------------ ----------------------------------------------------

**Descriere**

Lista tuturor contactelor cu filtre persistente (salvate în URL params
--- bookmarkable). Tabel cu lazy loading (20 per pagină, infinite scroll
opțional). Duplicate Guard: badge portocaliu pe rândurile detectate ca
potențial duplicate. Bulk actions: export CSV, assign agent, add tag,
delete.

**Stări ale ecranului**

**Empty State**

Tabel gol cu mesaj \"Niciun contact încă\" + buton CTA \"+ Adaugă primul
contact\".

**Filtrat fără rezultate**

Mesaj \"Niciun contact nu corespunde filtrelor\" + buton \"Resetează
filtrele\".

**Bulk Selection**

Checkbox header = select all (pe pagina curentă). Apare toolbar floating
cu acțiuni bulk: Export (X selectate), Assign, Tag, Delete.

**Note developer**

**API**

GET
/api/contacts?page=1&per_page=20&status=all&type=all&location=all&agent=all&search=&sort=last_interaction&order=desc.
Paginare cursor-based (nu offset) pentru performanță.

**Filtre**

Fiecare filtru = URL param. La schimbare filtru: update URL + re-fetch.
Filtrele se persistă în localStorage per user (ultimele filtre
folosite).

**Validări Search**

Debounce 300ms. Min 2 caractere. Search pe: denumire, CUI, email,
telefon, tags. Highlight match în rezultate.

**Export**

CSV cu toate coloanele vizibile. Max 10,000 rânduri. Progress bar pentru
export-uri mari. Format: UTF-8 BOM pentru Excel ro.

E-005 --- Offer Builder --- Wizard

![Wireframe
E-005](media/2602c02e50223e66390254da4fb2a91329c2ee88.jpg "E-005 Offer Builder — Wizard"){width="6.770833333333333in"
height="5.552083333333333in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN --- P1 ✓ P2 ✓ P3 ✓

  **F-codes**        F020, F021, F022, F023, F024, F025

  **Tip ecran**      Wizard multi-step

  **Complexitate**   Ridicată

  **Status WF**      WF V1 ✓

  **Prioritate**     P0 --- Critică

  **Tab-uri /        Step 1: Client + Proprietate \| Step 2: Line Items
  Subecrane**        (catalog) \| Step 3: Estimări & Predimensionare \|
                     Step 4: T&C \| Step 5: Preview & Generare PDF
  ------------------ ----------------------------------------------------

**Descriere**

Wizard cu 5 pași, progress bar, back/next. La Step 3 se calculează
automat estimări bazate pe Technical Data (P1: impact energetic; P2:
estimări construcții; P3: doar cost). Auto-save la fiecare step (draft).
Generare PDF din template configurabil. Poate porni pre-populat de la
Contact Detail sau Pipeline.

**Stări ale ecranului**

**Pre-populat**

Când se vine din Contact Detail: Step 1 pre-completat cu clientul. Când
se vine din Pipeline: pre-completat cu client + oportunitate.

**Draft salvat**

Banner galben \"Draft salvat la HH:MM\" sub progress bar. Resume: reia
de la ultimul step completat.

**Variante Step 3**

P1: estimări energetice (reducere consum %, CO2, ROI). P2: estimări
construcții (manoperă, materiale, durată). P3: doar calcul cost
(cantitate × preț unitar).

**Note developer**

**API**

POST /api/offers (creare draft). PATCH /api/offers/:id/step/:n (save
step). POST /api/offers/:id/generate (generare PDF). State management:
Zustand store cu persistență localStorage.

**Calcul estimări**

Server-side: POST /api/offers/:id/estimate cu payload {property_id,
line_items\[\]}. Returnează: energy_impact, cost_breakdown, roi.
Frontend: afișare read-only, user poate override manual.

**Generare PDF**

Server-side cu template engine (Handlebars/Puppeteer). Template-uri
configurabile din Settings (E-024). Watermark \"DRAFT\" până la status
\"Trimisă\".

E-009 --- Pipeline Board --- Kanban

![Wireframe
E-009](media/c7bbe2d49f5308b51198934dff0e68eb94ebcb4c.jpg "E-009 Pipeline Board — Kanban"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN --- P1 ✓ P2 ✓ P3 ✓

  **F-codes**        F040--F048, F050

  **Tip ecran**      Board (Kanban)

  **Complexitate**   Ridicată

  **Status WF**      WF V1 ✓

  **Prioritate**     P0 --- Critică

  **Tab-uri /        Coloane pe stadii (configurabile) \| Drag & drop \|
  Subecrane**        Carduri cu probabilitate câștig + valoare ponderată
                     \| Filtru agent/perioadă \| Alertă stagnare
  ------------------ ----------------------------------------------------

**Descriere**

Kanban cu coloane configurabile (admin poate adăuga/reordona stadii din
Settings). Drag & drop între coloane actualizează status + timestamp
automat. Fiecare card: client, valoare, probabilitate (%), zile în
stadiu, agent. Footer coloană = total valoare ponderată (valoare ×
probabilitate). Badge alertă pe cardurile stagnante (\>X zile fără
activitate).

**Stări ale ecranului**

**Empty Board**

Coloanele vizibile dar goale. CTA central \"+ Prima oportunitate\".
Mesaj educativ: \"Drag cardurile între stadii pentru a actualiza
pipeline-ul\".

**Drag in progress**

Card ridicat: shadow + opacity 0.8. Coloana target: highlight border
albastru. Coloana sursă: spațiu placeholder. Drop invalid: card revine
cu animație.

**Overflow**

Carduri \>5 per coloană: scroll intern per coloană. Contorul din header
se actualizează. Footer cu total ponderat rămâne fixed.

**Note developer**

**API**

GET /api/pipeline/board?agent=all&period=Q1-2026. PATCH
/api/pipeline/opportunities/:id {stage_id, moved_at}. Optimistic update:
UI se actualizează instant, rollback pe eroare.

**Drag & Drop**

Bibliotecă recomandată: \@hello-pangea/dnd (fork react-beautiful-dnd).
Events: onDragStart, onDragEnd. Payload: {opportunity_id, source_stage,
target_stage}.

**Alertă stagnare**

Calculat server-side. Threshold configurabil per stadiu (default:
Prospectare=14 zile, Ofertă=7 zile, Negociere=5 zile). Badge roșu cu
tooltip \"X zile fără activitate\".

E-014 --- Project --- Detail Hub

![Wireframe
E-014](media/cb5fade15ddcbd3f4019af9d09eb8b630a9101d7.jpg "E-014 Project — Detail Hub"){width="6.770833333333333in"
height="5.729166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN --- P1 ✓ P2 ✓ P3 ✓

  **F-codes**        F062--F095

  **Tip ecran**      Detail + Tabs

  **Complexitate**   Foarte ridicată

  **Status WF**      WF V1 ✓ (parțial)

  **Prioritate**     P0 --- Critică

  **Tab-uri /        Tab Overview (KPIs + Gantt mini) \| Tab WBS \| Tab
  Subecrane**        Gantt \| Tab Deviz \| Tab Execuție (Timesheet + Fișe
                     consum) \| Tab Post-Exec Energy (P1) \| Tab RM (P2)
                     \| Tab Raportare
  ------------------ ----------------------------------------------------

**Descriere**

Cel mai complex ecran din aplicație. Header persistent: nume proiect,
client, PM, status, avansare %. Tab-urile sunt lazy-loaded (componenta
se montează doar la prima accesare). Tab Overview = dashboard mini cu
KPIs Earned Value + Gantt thumbnail clickable. Tab-uri diferite per
prototip: P1 adaugă Post-Exec Energy, P2 adaugă RM + Gantt Dual-Layer.

**Stări ale ecranului**

**Proiect nou (Setup)**

Tab Overview gol. Tab WBS cu wizard \"Definește structura proiectului\".
Tab Gantt dezactivat (necesită WBS). Tab Deviz dezactivat. Alte tab-uri
ascunse.

**Execuție activă**

Toate tab-urile active. KPIs se calculează real-time. Badge pe tab
Execuție cu nr de timesheet-uri pending aprobare.

**Post-Execution**

Tab-uri Execuție = read-only (locked). Tab Post-Exec Energy devine activ
(P1). Tab Raportare: disponibil raport final.

**Închis**

Tot read-only. Banner \"Proiect închis la DD.MM.YYYY\". Export raport
final disponibil.

**Note developer**

**API**

GET /api/projects/:id (header + overview). Tab-urile au endpoint-uri
separate --- se apelează doar la prima accesare tab:
/api/projects/:id/wbs, /gantt, /budget, /execution, /energy, /reports.

**Tab routing**

URL:
/projects/:id?tab=overview\|wbs\|gantt\|budget\|execution\|energy\|reports.
Lazy loading cu React.lazy() + Suspense. Cache în memorie (nu re-fetch
la switch tab).

**Permisiuni**

PM: full edit pe toate tab-urile. Sales: read-only pe PM tabs, edit pe
CRM-linked data. Viewer: read-only total. Admin: full + delete proiect.

**Real-time**

WebSocket pe /ws/projects/:id. Events: progress_updated, budget_alert,
timesheet_submitted, energy_measurement_added. UI se actualizează fără
refresh.

E-016 --- Gantt Chart

![Wireframe
E-016](media/a327da10445439c30441c5c38b7a1b6f21d65374.jpg "E-016 Gantt Chart"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN --- P1 ✓ P2 ✓ P3 ✓

  **F-codes**        F066, F067, F078

  **Tip ecran**      Gantt (interactive)

  **Complexitate**   Foarte ridicată

  **Status WF**      WF V1 ✓ (simplificat)

  **Prioritate**     P0 --- Critică

  **Tab-uri /        Bare temporale target vs realizat \| Dependențe (FS,
  Subecrane**        FF, SS, SF) \| Milestone markers \| Zoom
                     (zi/săpt/lună) \| Critical path \| Drag to adjust \|
                     Baseline vs actual
  ------------------ ----------------------------------------------------

**Descriere**

Gantt cu două bare per activitate: gri = plan (baseline), colorată =
realizat. Dependențe = săgeți între bare. Milestone = romb. Zoom smooth
cu 3 niveluri (zi/săptămână/lună). Critical path = evidențiat roșu. Drag
to adjust: PM poate muta/redimensiona barele pentru re-planificare. P2
extinde la Dual-Layer cu overlay resurse.

**Stări ale ecranului**

**Fără activități**

Gantt gol cu mesaj \"Definește structura WBS pentru a vedea Gantt-ul\" +
link la tab WBS.

**Baseline locked**

După prima aprobare PM: baseline devine fixed (gri). Orice modificare se
reflectă doar în bara colorată.

**Print mode**

La print: fundal alb, bare cu pattern (nu doar culoare) pentru B&W.
Header cu nume proiect + dată + PM. Footer cu legendă.

**Note developer**

**Bibliotecă**

Recomandare: DHTMLX Gantt (comercial) sau frappe-gantt (open source).
Custom implementation cu D3.js dacă licența nu permite DHTMLX.
Canvas-based pentru performanță cu \>100 activități.

**Drag**

Drag start/end de bară = modifică dată start/end. Drag mijloc = mutare
fără resize. Shift+drag = modifycă doar selected, nu cascadează.
Auto-update dependențe la drag.

**Critical Path**

Calculat server-side cu algoritmul CPM (Critical Path Method).
Re-calculat la fiecare modificare. Endpoint: GET
/api/projects/:id/gantt/critical-path. Evidențiat cu border roșu +
label.

**Export**

Export PNG (screenshot), PDF (multi-page dacă \> 1 pagină), MS Project
XML (.mpp compatible).

E-028 --- Technical Data --- Property Energy

![Wireframe
E-028](media/14441555dc5f4791ebd08d837bafc072b144e5ab.jpg "E-028 Technical Data — Property Energy"){width="6.770833333333333in"
height="6.145833333333333in"}

  ------------------ ----------------------------------------------------
  **Scope**          SPECIFIC P1 --- doar BuildWise

  **F-codes**        F011, F012, F013, F014, F015, F016

  **Tip ecran**      Detail + Sub-tabs

  **Complexitate**   Ridicată

  **Status WF**      WF V1 ✓

  **Prioritate**     P0 --- Critică

  **Tab-uri /        Tab Identificare clădire \| Tab Parametri Energetici
  Subecrane**        (U-value, izolație) \| Tab HVAC \| Tab Calculator
                     Suprafețe \| Tab Istoric Măsurători
  ------------------ ----------------------------------------------------

**Descriere**

Diferențiator #1 BuildWise. Ecran de date tehnice per
proprietate/clădire, cu focus pe parametri energetici. Câmpuri numerice
cu unități de măsură fixe (W/m²K, kWh/m²/an). Calculator suprafețe =
formular dinamic (nr camere × suprafață per cameră). Istoric măsurători
= timeline cu valori PRE/POST montaj. Acest ecran NU există în P2 și P3
--- în acele prototipuri, proprietățile au doar date simplificate
(adresă, tip, suprafață).

**Stări ale ecranului**

**Proprietate nouă**

Doar tab Identificare activ cu formular gol. Celelalte tab-uri se
activează progresiv pe măsură ce se completează datele.

**Post-montaj**

Tab Istoric Măsurători se populează automat din datele introduse în
E-029 Post-Exec Energy. Badge verde \"Validat\" pe parametri confirmați
de măsurători reale.

**Note developer**

**API**

GET /api/properties/:id/technical. PATCH /api/properties/:id/technical.
Nested: /energy-params, /hvac, /surfaces, /measurements.

**Validări**

U-value: 0.1--5.0 W/m²K (float, 1 decimal). Suprafețe: \>0, max 100,000
m². HVAC: dropdown cu tipuri predefinite. Anul construcției: 1900--2030.

**Calculator**

Client-side: nr_nivele × suprafață_medie_nivel. Formulare dinamice ---
adaugă/elimină niveluri. Total automat. Override manual posibil cu
checkbox \"Suprafață manuală\".

E-029 --- Post-Execution --- Energy Measurements

![Wireframe
E-029](media/91b11c444e522262b3961af04c76663c56931162.jpg "E-029 Post-Execution — Energy Measurements"){width="6.770833333333333in"
height="6.625in"}

  ------------------ ----------------------------------------------------
  **Scope**          SPECIFIC P1 --- doar BuildWise

  **F-codes**        F082, F083, F084, F085, F086, F087

  **Tip ecran**      Form + Dashboard

  **Complexitate**   Ridicată

  **Status WF**      WF V1 ✓

  **Prioritate**     P0 --- Critică

  **Tab-uri /        KPI Summary (PRE/POST/Economie/ROI) \| Grafic
  Subecrane**        comparativ \| Impact Mediu & Financiar \| Tabel
                     Măsurători Detaliate \| Buton Dataset ML
  ------------------ ----------------------------------------------------

**Descriere**

Diferențiator #2 BuildWise. Formular structurat: kWh/an PRE montaj,
kWh/an POST montaj, tip sursă energie, suprafață. Calcul automat:
economie %, tone CO₂ evitate, ROI (ani). Grafic bar PRE vs POST cu scala
vizuală. Buton \"Adaugă la Dataset ML\" trimite datele validate către
modulul Data→ML (E-030) pentru antrenarea modelelor predictive.

**Stări ale ecranului**

**Fără măsurători PRE**

Formular de input cu câmpuri PRE goale. KPIs arată \"---\". Grafic
ascuns. Mesaj: \"Introduceți consumul PRE montaj din facturi sau smart
meter\".

**Doar PRE (montaj în curs)**

KPIs PRE populate. POST = \"Așteptare date\". Grafic arată doar bara
PRE. Economie = proiecție bazată pe model S1.

**PRE + POST complet**

Toate KPIs calculate. Grafic complet. Buton ML activ. Badge \"Validat\"
dacă eroare predicție \< 15%. Badge \"Atenție\" dacă \> 15%.

**Adăugat la Dataset**

Badge verde \"În dataset ML\" pe card. Buton ML devine \"Actualizează
dataset\". Timestamp ultimei sincronizări afișat.

**Note developer**

**API**

GET /api/projects/:id/energy-measurements. POST (creare). PATCH
(update). POST /api/ml/datasets/add {project_id, measurements}.

**Calcule**

Server-side: economie_pct = (pre - post) / pre × 100. co2 = (pre - post)
× suprafata × factor_emisie (0.233 kgCO2/kWh RO). roi_ani =
investitie_totala / (economie_kWh × pret_kWh). Pret kWh = din config
(actualizabil).

**Validări**

kWh: \>0, max 500 kWh/m²/an. POST \<= PRE (altfel warning, nu blocant).
Sursa măsurătoare: obligatorie (dropdown: Smart meter, Facturi, Senzori
IoT, Estimare).

E-030 --- Data → ML --- Mapping & Status

![Wireframe
E-030](media/27aca729a0ac1e9912dbfcf7db3d021daeec6abd.jpg "E-030 Data → ML — Mapping & Status"){width="6.770833333333333in"
height="4.96875in"}

  ------------------ ----------------------------------------------------
  **Scope**          SPECIFIC P1 --- doar BuildWise

  **F-codes**        F110, F111, F112, F113, F114, F115

  **Tip ecran**      Dashboard / Table

  **Complexitate**   Ridicată

  **Status WF**      WF V1 ✓

  **Prioritate**     P0 --- Critică

  **Tab-uri /        KPI Summary (datasets, modele active, eroare medie)
  Subecrane**        \| Tabel Status Modele (S1/S2/P1/P2) \| Matrice
                     Mapare Surse→Modele
  ------------------ ----------------------------------------------------

**Descriere**

Diferențiator #3 BuildWise. Dashboard centralizat pentru monitorizarea
pipeline-ului ML. Tabel cu cele 4 modele (S1 Predicție Energetică, S2
Învățare, P1 Monitorizare, P2 Perfecționare) --- fiecare cu status,
surse date, nr datasets, eroare, ultima antrenare. Matrice de mapare: ce
date din ce modul alimentează ce model. Grafic evoluție eroare predicție
în timp.

**Stări ale ecranului**

**Zero datasets**

KPIs la 0. Tabel modele cu status \"Nu a pornit\". Matrice vizibilă dar
gri. CTA: \"Adaugă primul proiect cu date energetice\".

**Antrenare în curs**

Modelul care se antrenează: progress bar animat + ETA. Celelalte modele:
status normal. Badge \"Antrenare\...\" lângă model.

**Eroare peste threshold**

Modelul cu eroare \>15%: evidențiat roșu. Recomandare automată: \"Model
S1 necesită re-antrenare --- eroare 18.2% (threshold 15%)\". Buton
\"Re-antrenează\".

**Note developer**

**API**

GET /api/ml/status (summary). GET /api/ml/models (lista cu detalii). GET
/api/ml/mapping (matrice surse→modele). POST /api/ml/models/:id/retrain
(declanșează antrenare).

**Real-time**

WebSocket pe /ws/ml/training. Events: training_started,
training_progress, training_completed, training_failed. UI update fără
refresh.

**Grafic eroare**

Chart.js line chart. X = data antrenare, Y = eroare %. Linie threshold
la 15%. Hover: tooltip cu detalii antrenare. Zoom pe perioada selectată.
