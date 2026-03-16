# Wireframes Faza2

**BuildWise**

Wireframe Specification Document

Faza 2 --- Ecrane P1 Importante

13 ecrane \| 7 comune + 6 specifice P2 (BAHM RM/Construcții)

M2M Solutions Consulting SRL · Martie 2026

Cuprins

Faza 2 --- Ecrane P1 Importante

13 ecrane: 7 comune (Catalog, Offer Lifecycle, Contract Builder,
Opportunity Detail, Activity Planner, Timesheet, Fișe Consum, Project
Reporting) + 6 specifice P2 BAHM (HR Echipe, Echipamente, Materiale, SdL
Generator, Financial Planning RM). Toate prioritate P1.

E-004 --- Products & Services --- Catalog

![E-004](media/5adf29b64a057920bbf4b216f9b85fc75b5059ab.jpg "E-004"){width="6.770833333333333in"
height="4.927083333333333in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN --- P1 ✓ P2 ✓ P3 ✓

  **F-codes**        F017, F018, F019

  **Tip ecran**      List + CRUD

  **Complexitate**   Scăzută

  **Prioritate**     P1 --- Importantă

  **Tab-uri**        Sidebar categorii arborescente \| Tabel
                     produse/servicii \| Cod, Denumire, UM, Preț,
                     Categorie, Status
  ------------------ ----------------------------------------------------

**Descriere**

CRUD simplu cu categorii ca tree (sidebar stânga). Prețuri cu versionare
(istoric modificări la save). Produsele se folosesc în Offer Builder
(E-005) ca line items --- picker cu search. Status: Activ/Draft/Arhivat.

**Stări ale ecranului**

**Catalog gol**

Sidebar categorii goală + CTA \"Creează prima categorie\". Tabel gol cu
mesaj.

**Produs Detail (modal)**

Click pe produs → modal cu toate câmpurile editabile. Istoric prețuri ca
timeline. Preview: cum apare în ofertă.

**Note developer**

**API**

CRUD standard: GET/POST/PATCH/DELETE /api/products. GET
/api/products/categories (tree). Prețuri: POST /api/products/:id/prices
(versionare automată la schimbare preț).

**Search in Offer Builder**

GET /api/products?search=sticla&category=&status=active. Debounce 300ms.
Max 20 rezultate. Format: \[{id, cod, denumire, um, pret_curent}\].

E-006 --- Offer --- Detail / Lifecycle

![E-006](media/9d1d0cfb047d0f913863ca145fec397ae33a615b.jpg "E-006"){width="6.770833333333333in"
height="4.927083333333333in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN --- P1 ✓ P2 ✓ P3 ✓

  **F-codes**        F024--F028

  **Tip ecran**      Detail + Timeline

  **Complexitate**   Medie

  **Prioritate**     P1 --- Importantă

  **Tab-uri**        Header (ID, client, valoare, status) \| Status
                     pipeline vizual \| Detalii ofertă (line items) \|
                     Versiuni (diff) \| Timeline activități
  ------------------ ----------------------------------------------------

**Descriere**

Fișa completă a unei oferte. Header cu status pipeline vizual
(Draft→Trimisă→Negociere→Acceptată/Refuzată). Tabel line items. Sidebar:
versiuni cu diff vizual (v1 vs v2) + timeline activități (emailuri,
apeluri, modificări). Buton \"Convertește în Contract\" → E-007
pre-populat.

**Stări ale ecranului**

**Draft**

Status primul. Editabilă complet. Watermark DRAFT pe preview PDF. Nu
apare timeline de trimis.

**Trimisă**

Read-only pe line items (necesită \"Creează versiune nouă\" pentru
editare). Timeline arată data trimiterii.

**Negociere**

Badge portocaliu. Follow-up suggestions automate pe baza timpului scurs.
Alert la \>5 zile fără activitate.

**Acceptată → Contract**

Badge verde. Buton \"Convertește în Contract\" devine proeminent. La
conversie: creează draft contract pre-populat cu toate datele.

**Note developer**

**API**

GET /api/offers/:id (complet). POST /api/offers/:id/send. POST
/api/offers/:id/version (creează v+1). PATCH /api/offers/:id/status
{status}. POST /api/offers/:id/convert-to-contract.

**Diff vizual**

Server-side: diff pe line items (adăugate, șterse, modificate).
Returnează \[{field, old_value, new_value}\]. Frontend: highlight
verde=adăugat, roșu=șters, galben=modificat.

E-007 --- Contract Builder

![E-007](media/b26e4429a55d26a546fbbd92b175858dbbafeeb5.jpg "E-007"){width="6.770833333333333in"
height="5.927083333333333in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN --- P1 ✓ P2 ✓ P3 ✓

  **F-codes**        F030--F036

  **Tip ecran**      Wizard / Form

  **Complexitate**   Medie

  **Prioritate**     P1 --- Importantă

  **Tab-uri**        Date contract \| Billing Schedule (milestone, sumă,
                     scadență) \| Clauze T&C (editabile) \| Aprobare &
                     Semnare \| Generare PDF
  ------------------ ----------------------------------------------------

**Descriere**

Poate porni de la ofertă (pre-populat: client, valoare, line items) sau
de la zero. Billing Schedule = tabel editabil cu milestones, procente,
sume, scadențe. Clauze T&C = editor text cu template-uri predefinite
(din Settings). Workflow aprobare: Juridic → Director → Client. La
semnare finalizată → auto-creare proiect PM (E-014).

**Stări ale ecranului**

**Pre-populat din ofertă**

Banner portocaliu \"Pre-populat din OFR-XXX\". Câmpuri date completate.
Billing Schedule = sugestie automată (30/40/30). Clauze din template
default.

**Aprobare în curs**

Câmpurile locked. Workflow vizual cu status per aprobator
(Pending/Aprobat/Respins). Notificări la fiecare pas.

**Semnat**

Tot read-only. Badge verde \"Contract semnat\". Link la proiect PM creat
automat. PDF final disponibil download.

**Note developer**

**API**

POST /api/contracts (creare, opțional from_offer_id). PATCH
/api/contracts/:id. POST /api/contracts/:id/approve {step, decision}.
POST /api/contracts/:id/sign. POST /api/contracts/:id/generate-pdf.

**Auto-creare PM**

La sign: POST /api/projects (auto). Copiază: client, valoare, billing
schedule. Creează WBS gol cu milestone-urile din billing. Notifică PM
asignat.

E-010 --- Opportunity --- Detail

![E-010](media/dcebf121ec3367c91e6cbffc94028f8370f40391.jpg "E-010"){width="6.770833333333333in"
height="4.927083333333333in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN --- P1 ✓ P2 ✓ P3 ✓

  **F-codes**        F041--F050

  **Tip ecran**      Detail + Activity log

  **Complexitate**   Medie

  **Prioritate**     P1 --- Importantă

  **Tab-uri**        Header (valoare, probabilitate, stadiu, agent) \|
                     Scoring \| Activități recente \| Contacte asociate
                     \| Notițe \| Documente
  ------------------ ----------------------------------------------------

**Descriere**

Fișa oportunității din Pipeline. Header cu valoare, probabilitate, zile
în stadiu, agent. Scoring automat (bazat pe activitate: frecvență
interacțiuni, timp în stadiu, valoare) + override manual. Activity log =
timeline cronologică. Contacte asociate = persoanele implicate în deal.
Buton \"Creează ofertă\" → E-005 pre-populat.

**Stări ale ecranului**

**Stagnare detectată**

Badge roșu \"Stagnare --- X zile fără activitate\". Scoring scade
automat. Sugestie: \"Planifică follow-up\". Alert la PM/Sales manager.

**Won/Lost**

La mutare în Câștigat/Pierdut: modal obligatoriu cu motiv (dropdown +
text liber). Datele se arhivează pentru analytics.

**Note developer**

**Scoring**

Server-side: scor = weighted sum(frecventa_interactiuni\*30 +
valoare_normalizata\*25 + timp_stadiu_inv\*20 +
completitudine_date\*15 + manual_override\*10). Recalculat la fiecare
interacțiune.

**API**

GET /api/pipeline/opportunities/:id. PATCH status. POST /activities. GET
/activities?sort=desc.

E-011 --- Activity Planner

![E-011](media/f662a14b6620a0a71132420f0fdacbbe302d0ece.jpg "E-011"){width="6.770833333333333in"
height="4.927083333333333in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN --- P1 ✓ P2 ✓ P3 ✓

  **F-codes**        F051--F055

  **Tip ecran**      Calendar + List

  **Complexitate**   Medie

  **Prioritate**     P1 --- Importantă

  **Tab-uri**        Calendar (zi/săptămână/lună) \| View listă \|
                     Milestone templates \| Drag to reschedule \| Filtru
                     agent
  ------------------ ----------------------------------------------------

**Descriere**

Calendar vizual cu activități colorate pe tip (apel=albastru,
vizită=verde, meeting=violet, deadline=roșu). Toggle între view calendar
și listă. Milestone templates = secvențe predefinite de activități
(\"Onboarding client\" = 5 pași). Drag pe calendar = reschedule automat.
Filtru pe agent.

**Stări ale ecranului**

**Calendar gol**

Zilele vizibile fără activități. CTA central \"Planifică prima
activitate\" sau \"Aplică template\".

**Drag reschedule**

Drag activitate pe altă zi/oră → update automat data. Dacă conflictează
(overlap altă activitate): warning galben.

**Note developer**

**API**

GET /api/activities?from=&to=&agent=&type=. POST/PATCH/DELETE. GET
/api/activity-templates.

**Calendar lib**

Recomandare: \@fullcalendar/react sau react-big-calendar. Events: drag,
resize, click. Integrare cu Google Calendar opțională (sync
bidirecțional).

E-018 --- Timesheet --- Input & Review

![E-018](media/4f0eb433fd3fcdf09edeb5feece48d87ee2edd20.jpg "E-018"){width="6.770833333333333in"
height="4.927083333333333in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN --- P1 ✓ P2 ✓ P3 ✓

  **F-codes**        F071, F072, F073

  **Tip ecran**      Form + Table

  **Complexitate**   Medie

  **Prioritate**     P1 --- Importantă

  **Tab-uri**        Grid: rânduri=activități WBS, coloane=zile \| Input
                     ore (0.5 increments) \| Aprobare PM \| Cost implicit
                     calculat \| Navigare săptămânală
  ------------------ ----------------------------------------------------

**Descriere**

Grid de input: rânduri = activități WBS ale proiectului, coloane =
zilele săptămânii. Input = ore (0.5 increments, click sau tastare). Tab
= next cell, Enter = save + next row. PM are view aprobare cu status
pending/approved/locked. Ore × cost/oră = cost implicit automat. Footer
cu totaluri.

**Stări ale ecranului**

**Input mode (echipă)**

Grid editabil. Celulele empty = click pentru input. Max 24h/zi
(validare). Submit → status \"Pending aprobare\".

**Review mode (PM)**

Grid read-only cu highlight pe celulele pending. Bulk approve/reject.
Comentarii per celulă (click dreapta).

**Locked (aprobat)**

Tot grid-ul gri, needitabil. Badge \"Aprobat la DD.MM de PM\". Datele se
reflectă în deviz (cost manoperă).

**Note developer**

**API**

GET /api/projects/:id/timesheets?week=2026-W11. POST (submit). PATCH
/approve, /reject. Ore stocate per celulă: {wbs_node_id, date, hours,
status}.

**Cost calc**

Client-side: ore × tarif_orar (din profil angajat sau medie proiect).
Server-side la aprobare: se scrie în budget_actuals.

E-019 --- Fișe Consum Materiale

![E-019](media/88075f9c69778c75652cbdfcdaf38123238c75ca.jpg "E-019"){width="6.770833333333333in"
height="4.927083333333333in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN --- P1 ✓ P2 ✓ P3 ✓

  **F-codes**        F074, F075

  **Tip ecran**      Form + Table

  **Complexitate**   Medie

  **Prioritate**     P1 --- Importantă

  **Tab-uri**        Tabel: materiale din deviz × cantitate planificată
                     vs consumată \| Rest stoc \| Alertă depășire \>10%
                     \| Filtru WBS/perioadă
  ------------------ ----------------------------------------------------

**Descriere**

Similar Timesheet dar pentru materiale. Rânduri = materiale din deviz
(linkate la nod WBS). Coloane: planificat, consumat, rest, diferență %.
Alert automat la depășire \>10% (threshold configurabil). Legătură
bidirecțională cu E-017 Deviz Tracker și E-035 Materiale (P2).

**Stări ale ecranului**

**Depășire detectată**

Rând roșu cu icon ⚠. Banner sub tabel cu cauza probabilă și recomandare.
Notificare la PM.

**Legătură stoc (P2)**

Dacă consumul depășește stocul disponibil: link direct la E-035 cu
sugestie comandă suplimentară.

**Note developer**

**API**

GET /api/projects/:id/consumption?wbs_node=&period=. POST (înregistrare
consum). Calculat: rest = planificat - consumat_cumulat. Delta =
(consumat - planificat) / planificat × 100.

E-020 --- Project Reporting --- 3-in-1

![E-020](media/bd5ef04c0730845651744a7db4ad5b3aa94dd1c3.jpg "E-020"){width="6.770833333333333in"
height="6.572916666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN --- P1 ✓ P2 ✓ P3 ✓

  **F-codes**        F088--F095

  **Tip ecran**      Report / Dashboard

  **Complexitate**   Ridicată

  **Prioritate**     P1 --- Importantă

  **Tab-uri**        KPIs Earned Value (SPI, CPI, EV, EAC) \| P&L Proiect
                     \| Cash Flow \| TrueCast (proiecție finalizare) \|
                     Export PDF
  ------------------ ----------------------------------------------------

**Descriere**

Trei secțiuni într-un ecran scrollabil. (1) Earned Value cu KPIs +
grafic S-curve. (2) P&L = tabel venituri vs costuri per categorie
(buget/realizat/forecast). (3) Cash Flow = tabel lunar cu încasări,
plăți, net, cumulat. TrueCast = proiecție la finalizare bazată pe
tendința curentă (EAC, VAC, data estimată, profit estimat). Export PDF
cu toate secțiunile.

**Stări ale ecranului**

**Proiect nou**

KPIs la 0. P&L doar coloana Buget completată. CF gol. TrueCast =
\"Insuficiente date\".

**Alert CPI \< 0.9**

KPI CPI evidențiat roșu. Banner: \"Proiectul depășește bugetul cu X%.
Recomandare: review costuri materiale.\"

**Note developer**

**API**

GET /api/projects/:id/reports/earned-value. GET /reports/pnl. GET
/reports/cashflow. GET /reports/truecast. POST /reports/export-pdf.

**Earned Value**

Server-side: PV=planned value (din gantt baseline), EV=earned value
(avansare × buget), AC=actual cost (din deviz realizat). SPI=EV/PV,
CPI=EV/AC. EAC=AC+(BAC-EV)/CPI.

E-033 --- HR --- Echipe & Personal

![E-033](media/e7b52b239be66d8223726e43ee4beea676a43a0c.jpg "E-033"){width="6.770833333333333in"
height="4.927083333333333in"}

  ------------------ ----------------------------------------------------
  **Scope**          SPECIFIC P2 --- doar BAHM

  **F-codes**        RM-F04--F07

  **Tip ecran**      List + Detail

  **Complexitate**   Medie

  **Prioritate**     P1 --- Importantă

  **Tab-uri**        Tabel personal \| Echipă \| Competențe \| Alocare
                     curentă \| Disponibilitate \| Status
                     (activ/concediu)
  ------------------ ----------------------------------------------------

**Descriere**

Registru complet personal cu competențe, alocare curentă pe proiecte (%
per proiect), disponibilitate, calendar concedii/absențe. Click pe
persoană → detail cu fișă completă, istoric alocare, calendar personal.

**Stări ale ecranului**

**Conflict alocare**

Dacă suma alocărilor \> 100%: evidențiat roșu. Nu blocant (se permite
supraallocarea) dar warning persistent.

**Concediu planificat**

Rânduri cu badge portocaliu \"Concediu DD-DD\". În matrice RM: celulele
respective gri.

**Note developer**

**API**

CRUD /api/rm/staff. GET /api/rm/staff/:id/allocations. GET
/api/rm/staff/:id/calendar. Competențe: tag-uri din listă predefinită.

E-034 --- Echipamente & Utilaje

![E-034](media/52fb18038f0587ed2175870a0a29a75d89a690df.jpg "E-034"){width="6.770833333333333in"
height="4.927083333333333in"}

  ------------------ ----------------------------------------------------
  **Scope**          SPECIFIC P2 --- doar BAHM

  **F-codes**        RM-F08--F10

  **Tip ecran**      List + Detail

  **Complexitate**   Medie

  **Prioritate**     P1 --- Importantă

  **Tab-uri**        Tabel echipamente \| Cod \| Tip \| Status
                     (disponibil/alocat/mentenanță) \| Alocare proiect \|
                     Program mentenanță
  ------------------ ----------------------------------------------------

**Descriere**

Registru echipamente/utilaje cu status real-time. Similar HR dar pentru
echipamente. Calendar mentenanță preventivă cu alerte. Status badges
colorate. Click → detail cu istoric alocare și program mentenanță.

**Stări ale ecranului**

**Mentenanță programată**

Badge portocaliu cu ETA revenire. În matrice RM: celulele respective
marcate cu 🔧.

**Echipament nou**

Modal cu câmpuri: denumire, cod, tip (dropdown), data achiziție,
valoare, program mentenanță (recurent).

**Note developer**

**API**

CRUD /api/rm/equipment. GET /allocations. POST /maintenance-schedule.
Calendar: calcul automat next maintenance din interval recurent.

E-035 --- Materiale & Stocuri

![E-035](media/4e7b87f3a8a501e3785686bfaa26b009932b9abe.jpg "E-035"){width="6.770833333333333in"
height="4.927083333333333in"}

  ------------------ ----------------------------------------------------
  **Scope**          SPECIFIC P2 --- doar BAHM

  **F-codes**        RM-F11--F13

  **Tip ecran**      List + Detail

  **Complexitate**   Medie

  **Prioritate**     P1 --- Importantă

  **Tab-uri**        Stocuri curente \| Stoc minim \| Alocat per proiect
                     \| Disponibil \| Comenzi active \| Alertă stoc
  ------------------ ----------------------------------------------------

**Descriere**

Gestiune stocuri cu alertă automată sub prag minim. Coloane: stoc
curent, minim, alocat (defalcat per proiect), disponibil (stoc -
alocat), comenzi active cu ETA. Legătură bidirecțională cu Fișe Consum
(E-019) și Deviz (E-017).

**Stări ale ecranului**

**Sub stoc minim**

Badge roșu. Rând evidențiat. Buton \"Comandă rapidă\" → pre-populat cu
cantitate lipsă.

**Comandă în curs**

Badge portocaliu cu ETA. La recepție: actualizare automată stoc.
Notificare la PM proiectelor care așteaptă.

**Note developer**

**API**

CRUD /api/rm/materials. GET /stock-levels. POST /orders. Disponibil =
stoc - SUM(alocat_proiecte). Alert: cron job verifică stoc \< minim la
fiecare modificare consum.

E-039 --- Situație de Lucrări --- Generator

![E-039](media/255297c78902f0d9df7b7fb50b8ad0853b0afad5.jpg "E-039"){width="6.770833333333333in"
height="4.927083333333333in"}

  ------------------ ----------------------------------------------------
  **Scope**          SPECIFIC P2 --- doar BAHM

  **F-codes**        RM-F22--F24

  **Tip ecran**      Wizard + Table

  **Complexitate**   Medie

  **Prioritate**     P1 --- Importantă

  **Tab-uri**        Selectare articole din deviz \| Cantități realizate
                     în perioadă \| Cumulat SdL anterioare \| Preview \|
                     Generare PDF \| Link facturare
  ------------------ ----------------------------------------------------

**Descriere**

Wizard accesat din E-017 Deviz. Selectează articolele din deviz,
inputează cantitățile realizate în perioadă, calculează automat:
valoric, cumulat cu SdL-urile anterioare, procent din contract. Preview
PDF. Generare PDF cu format standard. Link la billing schedule din
contract.

**Stări ale ecranului**

**Prima SdL**

Cumulat anterior = 0 pe toate articolele. Banner: \"Prima situație de
lucrări a proiectului\".

**SdL finală**

Dacă cumulatul = 100% pe toate articolele: banner verde \"SdL finală ---
recepție\". Buton \"Declanșează recepție\" → E-021.

**Note developer**

**API**

GET /api/projects/:id/sdl (lista SdL-uri). POST /sdl (creare). GET
/sdl/:id/items. POST /sdl/:id/generate-pdf. Cantitate perioadă = input
manual. Cumulat = SUM(toate SdL-urile anterioare) + perioadă curentă.

**PDF**

Template format standard construcții (header proiect, tabel articole,
semnături, ștampilă). Server-side: Puppeteer/Handlebars.

E-040 --- Financial Planning --- RM

![E-040](media/aa479a2b915fdc9935cd2841914d490614aa8a10.jpg "E-040"){width="6.770833333333333in"
height="4.927083333333333in"}

  ------------------ ----------------------------------------------------
  **Scope**          SPECIFIC P2 --- doar BAHM

  **F-codes**        RM-F25, RM-F26

  **Tip ecran**      Dashboard / Table

  **Complexitate**   Medie

  **Prioritate**     P1 --- Importantă

  **Tab-uri**        KPIs (cost RM total, bugetat, depășire, forecast) \|
                     Tabel per proiect × categorii RM (personal,
                     echipamente, materiale) \| Trend
  ------------------ ----------------------------------------------------

**Descriere**

Dashboard financiar focusat pe costurile de resurse. Tabel: proiecte ×
categorii RM (personal, echipamente, materiale) × bugetat vs realizat.
KPIs agregate: cost total RM, bugetat, depășire %, forecast. Alertă la
depășire per proiect.

**Stări ale ecranului**

**Depășire globală**

KPI depășire roșu. Tabel cu proiectele sortate descrescător pe depășire.
Recomandare automată: \"Renegociați prețuri furnizor materiale\".

**Note developer**

**API**

GET /api/rm/financial?period=. Agregate din: timesheets (personal),
equipment_allocations × tarife (echipamente), consumption × prețuri
(materiale). Forecast: trend linear pe ultimele 3 luni.
