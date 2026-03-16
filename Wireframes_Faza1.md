# Wireframes Faza1

**BuildWise**

Wireframe Specification Document

Faza 1 --- Ecrane P0 Critice

8 ecrane \| 4 comune + 4 specifice P2 (BAHM RM/Construcții)

**M2M Solutions Consulting SRL**

Martie 2026 --- Document intern

Cuprins

Faza 1 --- Ecrane P0 Critice

8 ecrane noi: 4 comune (Contact Detail, WBS Editor, Deviz Tracker, App
Shell) + 4 specifice P2 BAHM (Resource Dashboard, Company Capacity,
Import Engine Devize, Gantt Dual-Layer). Toate prioritate P0 ---
necesare înainte de MVP.

E-003 --- Contact --- Detail

![Wireframe
E-003](media/9f4e4bafae0112b6e0df7fdde39eb840d6d3e56f.jpg "E-003 Contact — Detail"){width="6.770833333333333in"
height="7.416666666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN --- P1 ✓ P2 ✓ P3 ✓

  **F-codes**        F003, F007--F014

  **Tip ecran**      Detail + Tabs

  **Complexitate**   Ridicată

  **Status WF**      Faza 1 --- Nou

  **Prioritate**     P0 --- Critică

  **Tab-uri /        Tab Date generale \| Tab Istoric (24) \| Tab
  Subecrane**        Proprietăți (3) \| Tab Documente (12) \| Tab Oferte
                     & Contracte (5)
  ------------------ ----------------------------------------------------

**Descriere**

Header persistent cu avatar, status badge, acțiuni rapide (+Ofertă,
+Activitate, Edit). Duplicate Guard = banner condiționat. 5 tab-uri
lazy-loaded cu URL routing (?tab=general). Date generale: informații
companie + persoane de contact + sumar activitate + notițe + câmpuri
custom. Toate câmpurile editabile inline (click→input, save la blur).
Tab-urile diferă per prototip: P1 are Technical Data Energy în tab
Proprietăți, P2 are date construcții, P3 are doar date simplificate.

**Stări ale ecranului**

**Contact nou**

Tab Date generale = formular editabil gol. Celelalte tab-uri: mesaj
empty state cu CTA. Contoare tab-uri = 0.

**Duplicate Guard**

Banner apare doar când algoritm detectează duplicat (match
CUI/email/nume cu scor \>0.8). Dismiss = persistat per user. Compară &
Merge = modal diff vizual.

**Read-only (Viewer)**

Fără butoane acțiune în header. Câmpuri needitabile. Tab-uri fără
butoane adăugare. Date vizibile complet.

**Note developer**

**API**

GET /api/contacts/:id (header+general). Tab-urile:
/interactions?page=1&type=all, /properties, /documents?category=all,
/offers, /contracts. Toate independente --- call doar la prima accesare
tab.

**Editare inline**

Click valoare → input. Save automat blur + debounce 500ms. Feedback:
border albastru focus, verde flash success, roșu + tooltip eroare. Undo
Ctrl+Z (store prev value).

**Validări**

CUI: format RO + 2-10 cifre, checksum ANAF. Email: format standard.
Telefon: +40 7XX/2XX. CAEN: dropdown lista oficială (cache local).
Agent: dropdown useri activi. Obligatorii la creare: Denumire, CUI, Tip.

E-015 --- WBS Editor

![Wireframe
E-015](media/c08469bc7c9b00d6c5b7de5b178a554baa16bc62.jpg "E-015 WBS Editor"){width="6.770833333333333in"
height="4.927083333333333in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN --- P1 ✓ P2 ✓ P3 ✓

  **F-codes**        F063, F064, F065

  **Tip ecran**      Tree + Table

  **Complexitate**   Ridicată

  **Status WF**      Faza 1 --- Nou

  **Prioritate**     P0 --- Critică

  **Tab-uri /        Arbore ierarhic (faze → activități → sub-activități)
  Subecrane**        \| Inline edit \| Drag reorder \| Legătură Deviz \|
                     Alocare resurse \| Footer totaluri
  ------------------ ----------------------------------------------------

**Descriere**

Tree view colapsabil cu indent vizual pe 3 niveluri. Fiecare nod: cod
WBS (auto-generat), denumire, responsabil, durată estimată, cost
estimat, avansare %. Expand fază → arată activitățile cu
sub-activitățile. Drag & drop pentru reordonare. Inline edit pe toate
câmpurile. Footer cu totaluri calculate. P2 adaugă coloana alocare
echipamente.

**Stări ale ecranului**

**Proiect nou (WBS gol)**

Tabel gol cu CTA \"Definește prima fază\" + wizard rapid (câmpuri:
denumire, durată, responsabil). Alternativ: buton Import pentru import
din template.

**Drag in progress**

Rând ridicat cu shadow. Linie indicator între rânduri pentru poziția
drop. Restricții: faza nu poate deveni sub-activitate.

**Sincronizare Gantt**

La orice modificare WBS (adăugare/ștergere/reordonare), Gantt-ul se
re-calculează automat. Badge notificare pe tab Gantt.

**Note developer**

**API**

GET /api/projects/:id/wbs (arbore complet). POST
/api/projects/:id/wbs/nodes (creare). PATCH /wbs/nodes/:id (update).
DELETE /wbs/nodes/:id (ștergere + cascadă). PATCH /wbs/reorder {node_id,
parent_id, position}.

**Tree component**

Recomandare: \@tanstack/react-table cu expand/collapse custom sau
react-arborist pentru drag & drop nativ pe arbore. State local cu
optimistic updates.

**Cost calc**

Server-side: cost fază = SUM(cost activități). Cost proiect = SUM(cost
faze). La orice update cost activitate → re-calculare cascadă up.
Avansare fază = weighted average (cost activitate × avansare) / cost
total fază.

E-017 --- Deviz --- Editor & Tracker

![Wireframe
E-017](media/914aba8f57cde36d4e143505d2b0fdc2fbaee02d.jpg "E-017 Deviz — Editor & Tracker"){width="6.770833333333333in"
height="4.927083333333333in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN --- P1 ✓ P2 ✓ P3 ✓

  **F-codes**        F068--F070, F079, F080

  **Tip ecran**      Table (editable)

  **Complexitate**   Ridicată

  **Status WF**      Faza 1 --- Nou

  **Prioritate**     P0 --- Critică

  **Tab-uri /        Articole deviz per nod WBS \| Cantitate estimată vs
  Subecrane**        realizată \| Preț unitar \| Total estimat vs
                     realizat \| Δ% \| SdL (P2) \| Import (P2)
  ------------------ ----------------------------------------------------

**Descriere**

Tabel editabil cu freeze pe primele 2 coloane (WBS + Articol). Rândurile
grupate pe faze WBS (expandable). Colorare automată: verde = sub buget,
roșu = depășire (threshold configurabil, default 5%). Footer = totaluri
calculate. P2 adaugă butoanele Import deviz (→E-037) și Generează SdL
(→E-039). Export Excel/PDF.

**Stări ale ecranului**

**Deviz gol**

Tabel cu header-e vizibile, 0 rânduri. CTA: \"Adaugă primul articol\"
sau \"Import deviz\" (P2). Asociere cu nod WBS obligatorie.

**Editare celulă**

Click celulă → input inline. Tab = next cell. Enter = save + next row.
Escape = cancel. Celulele formule (Total, Δ%) sunt read-only.

**Alerte depășire**

Rânduri cu Δ% \> threshold: background roșu atenuat + icon ⚠. Click
alertă → tooltip cu detalii. Filtru rapid: \"Arată doar depășiri\".

**Note developer**

**API**

GET /api/projects/:id/budget (deviz complet). POST /budget/items. PATCH
/budget/items/:id. DELETE. POST /budget/generate-sdl (P2 --- wizard
SdL). POST /budget/import (P2 --- start import wizard).

**Freeze columns**

CSS: position:sticky + left:0 pe primele 2 coloane. Z-index \> rânduri
normale. Shadow dreapta pe scroll orizontal.

**Formule**

Client-side: total_estimat = cantitate_est × pret_unitar. total_realizat
= cantitate_real × pret_unitar (sau override manual). delta_pct =
(realizat - estimat) / estimat × 100. Footer: SUM per coloană.

E-027 --- App Shell --- Sidebar + Header

![Wireframe
E-027](media/e69aba9f02fab300cabf027e67a044c52abf0f7b.jpg "E-027 App Shell — Sidebar + Header"){width="6.770833333333333in"
height="5.833333333333333in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN --- P1 ✓ P2 ✓ P3 ✓

  **F-codes**        F139, F140

  **Tip ecran**      Layout / Navigation

  **Complexitate**   Medie

  **Status WF**      Faza 1 --- Nou

  **Prioritate**     P0 --- Critică

  **Tab-uri /        Sidebar (200px, colapsabilă) \| Header (40px,
  Subecrane**        sticky) \| Content area \| Responsive breakpoints \|
                     Meniu per prototip \| Keyboard shortcuts
  ------------------ ----------------------------------------------------

**Descriere**

Layout persistent pe toate ecranele. Sidebar: brand + secțiuni module +
items cu icon/label + badge count + user footer. Colapsabilă la 48px
(doar iconițe). Meniul diferă per prototip: P1 fără RM, P2 cu RM, P3
complet. Header: breadcrumb dinamic, search trigger (Cmd+K),
notification bell cu badge count, avatar user. Mobile: sidebar devine
drawer overlay.

**Stări ale ecranului**

**Sidebar colapsată**

Click toggle sau Cmd+B. Sidebar 48px: doar iconițe centrante. Hover pe
icon: tooltip cu label. Brand: doar logo, fără text. User footer: doar
avatar.

**Mobile drawer**

Sub 768px: sidebar ascunsă. Hamburger button în header. Click/swipe:
drawer overlay cu backdrop. Close: click backdrop / swipe left / Esc.

**Notificări active**

Badge roșu pe bell icon cu count. Click → dropdown cu ultimele 5
notificări. Click notificare → navighează la ecranul relevant + mark as
read.

**Note developer**

**Routing**

React Router v6. Layout ca wrapper component. Sidebar = componenta
separată cu props: menuItems (per prototip), collapsed (boolean),
activeItem. Header = componenta cu breadcrumb auto-generat din route.

**State management**

Sidebar collapsed: localStorage per user. Active menu item: derivat din
current route. Notification count: WebSocket sau polling 30s.

**A11y**

Sidebar: role=navigation, aria-label. Items: role=link. Keyboard: Tab
navigare, Enter activare. Skip to content link. Focus trap pe drawer
mobile.

E-032 --- Resource Dashboard --- Overview

![Wireframe
E-032](media/6576dbe40c719b632423c51843dd1bc5fed4fae3.jpg "E-032 Resource Dashboard — Overview"){width="6.770833333333333in"
height="5.53125in"}

  ------------------ ----------------------------------------------------
  **Scope**          SPECIFIC P2 --- doar BAHM

  **F-codes**        RM-F01, RM-F02, RM-F03

  **Tip ecran**      Dashboard

  **Complexitate**   Ridicată

  **Status WF**      Faza 1 --- Nou

  **Prioritate**     P0 --- Critică

  **Tab-uri /        KPI semafoare (echipe, echipamente, conflicte,
  Subecrane**        utilizare) \| Matrice Resurse × Săptămâni (heatmap)
                     \| Conflicte active
  ------------------ ----------------------------------------------------

**Descriere**

Dashboard vizual cu semafoare de disponibilitate. Matrice: rânduri =
resurse (echipe, echipamente, materiale), coloane = săptămâni. Celulele
colorate pe alocaie: verde = OK, albastru = alocat, portocaliu =
overlap, roșu = conflict. Click pe celulă → detail cu detalii alocare.
Secțiunea Conflicte: lista conflictelor cu buton Rezolvă → modal de
re-alocare.

**Stări ale ecranului**

**Zero resurse**

KPIs la 0. Matrice goală cu CTA \"Adaugă echipe din HR\" + link la
E-033. Mesaj explicativ.

**Conflict detectat**

KPI Conflicte devine roșu. Celulele conflict = background roșu pulsant.
Notificare push la PM-ul proiectelor implicate.

**Filtru proiect**

Dropdown filtru per proiect: arată doar resursele alocate proiectului
selectat. Default: toate proiectele.

**Note developer**

**API**

GET /api/rm/dashboard (KPIs). GET
/api/rm/matrix?from=2026-03-01&to=2026-04-30&type=all (matrice). GET
/api/rm/conflicts (lista conflicte). PATCH /api/rm/allocations/:id
(re-alocare).

**Matrice rendering**

Tabel HTML cu celule colorate dinamic. Nu canvas. Hover: tooltip cu
detalii (proiect, responsabil, procent utilizare). Click: modal cu
opțiuni (re-alocare, extindere, anulare).

**Conflict detection**

Server-side cron job la fiecare modificare alocare. Reguli: echipă nu
poate fi pe 2 proiecte simultan în aceeași săptămână (excepție: split
50/50 configurabil). Echipament: exclusiv per proiect.

E-036 --- Company Capacity Dashboard

![Wireframe
E-036](media/ba5a915491c875ec1897b5ad0f87ca07ddeb57fc.jpg "E-036 Company Capacity Dashboard"){width="6.770833333333333in"
height="5.739583333333333in"}

  ------------------ ----------------------------------------------------
  **Scope**          SPECIFIC P2 --- doar BAHM

  **F-codes**        RM-F14, RM-F15, RM-F16

  **Tip ecran**      Dashboard

  **Complexitate**   Ridicată

  **Status WF**      Faza 1 --- Nou

  **Prioritate**     P0 --- Critică

  **Tab-uri /        KPI (proiecte active, capacitate max, încărcare,
  Subecrane**        sloturi libere) \| Heatmap echipe × luni \| Simulare
                     what-if \| Trend utilizare
  ------------------ ----------------------------------------------------

**Descriere**

Dashboard strategic: câte proiecte poate lua firma simultan. Heatmap:
echipe × luni cu intensitate culoare pe procent utilizare
(verde→portocaliu→roșu). Simulare \"Ce-ar fi dacă?\": input proiect nou
(durată, echipe necesare) → sistemul calculează bottleneck-uri și
recomandă timing optim. Trend: grafic bar utilizare medie pe luni.

**Stări ale ecranului**

**Simulare activă**

Formularul simulare devine evidențiat. Heatmap-ul arată overlay cu
impactul proiectului simulat (celule cu pattern diagonal).
Bottleneck-uri evidențiate cu border roșu.

**Fără bottleneck**

Simulare fără conflicte: mesaj verde \"Proiectul poate fi acceptat fără
conflicte\" + buton \"Creează proiect\".

**Note developer**

**API**

GET /api/rm/capacity (KPIs + heatmap). POST /api/rm/capacity/simulate
{project_name, duration_weeks, start_date, teams_needed\[\]}.
Returnează: bottlenecks\[\], recommendation, optimal_start_date.

**Simulare**

Client-side pentru preview rapid (overlay pe heatmap). Server-side
pentru calcul exact bottleneck. Debounce 500ms pe input changes.

E-037 --- Import Engine --- Devize

![Wireframe
E-037](media/230d54ba48a7f33c2f5f4d86bfa0499dff4dc29a.jpg "E-037 Import Engine — Devize"){width="6.770833333333333in"
height="4.927083333333333in"}

  ------------------ ----------------------------------------------------
  **Scope**          SPECIFIC P2 --- doar BAHM

  **F-codes**        RM-F17, RM-F18, RM-F19

  **Tip ecran**      Wizard 4 pași

  **Complexitate**   Ridicată

  **Status WF**      Faza 1 --- Nou

  **Prioritate**     P0 --- Critică

  **Tab-uri /        Step 1: Selectare sursă (Intersoft/eDevize/manual)
  Subecrane**        \| Step 2: Upload + Preview \| Step 3: Mapping WBS
                     \| Step 4: Confirmare import
  ------------------ ----------------------------------------------------

**Descriere**

Wizard 4 pași pentru import devize din surse externe. Step 1: alege
sursa (Intersoft XML, eDevize, CSV manual). Step 2: upload fișier +
preview tabel parsat cu highlight erori. Step 3: mapping fiecare articol
pe nodul WBS corespunzător (auto-match + manual). Step 4: review final
cu totaluri + confirmare. Error handling robust: fișier invalid, format
nerecunoscut, articole duplicate.

**Stări ale ecranului**

**Auto-map**

Butonul \"Auto-map restante\" încearcă match pe denumire articol vs
denumire nod WBS (fuzzy matching). Scor \>0.7 = auto-assign cu badge
\"Auto\". Scor \<0.7 = rămâne nealocat.

**Eroare parsing**

Step 2: dacă fișierul nu se poate parsa → mesaj roșu cu detalii
(rând/coloană eroare). Opțiuni: re-upload sau continuă cu rândurile
valide.

**Articole duplicate**

Dacă articolul importat există deja în deviz (match pe cod): evidențiat
galben cu opțiuni: Suprascrie / Sumează cantități / Exclude.

**Note developer**

**API**

POST /api/projects/:id/budget/import/upload (file multipart). GET
/import/:session_id/preview. PATCH /import/:session_id/mapping
{items\[{import_item_id, wbs_node_id}\]}. POST
/import/:session_id/confirm.

**Parsare**

Server-side: XML parser (Intersoft), custom parser (eDevize), CSV
parser. Fiecare returnează format normalizat: \[{cod, denumire, um,
cantitate, pret_unitar}\]. Timeout: 30s per fișier.

**Session**

Import session persistată server-side. User poate părăsi wizard și
reveni. Session expirare: 24h. La confirmare: inserare batch în tabelul
budget_items.

E-038 --- Gantt Dual-Layer (extensie P2)

![Wireframe
E-038](media/c97ef384a847fff935149fde5dd57112ea72b584.jpg "E-038 Gantt Dual-Layer (extensie P2)"){width="6.770833333333333in"
height="4.927083333333333in"}

  ------------------ ----------------------------------------------------
  **Scope**          SPECIFIC P2 --- doar BAHM

  **F-codes**        RM-F20, RM-F21

  **Tip ecran**      Gantt + RM overlay

  **Complexitate**   Foarte ridicată

  **Status WF**      Faza 1 --- Nou

  **Prioritate**     P0 --- Critică

  **Tab-uri /        Layer 1: Gantt standard (plan vs realizat) ---
  Subecrane**        identic E-016 \| Layer 2: RM overlay (echipe,
                     echipamente, conflicte) \| Toggle layers
  ------------------ ----------------------------------------------------

**Descriere**

Extensie a E-016 Gantt comun. Toggle \"Arată Resurse\" activează al
doilea layer: sub fiecare bară de activitate apare un al doilea rând cu
bare colorate pe tip resursă (echipă = albastru, echipament =
portocaliu). Conflicte de resurse = evidențiate roșu intermitent. Când
toggle e OFF, Gantt-ul e identic cu E-016 (versiunea comună).

**Stări ale ecranului**

**Resurse OFF (default)**

Gantt identic cu E-016. Butonul toggle arată \"Arată Resurse\". Niciun
rând suplimentar.

**Resurse ON**

Fiecare activitate cu resurse alocate primește un al doilea rând (height
redus). Bare colorate pe tip resursă cu label. Conflicte: background
roșu pulsant pe celulele overlap. Toggle: \"Ascunde Resurse\".

**Conflict resursă vizibil**

Dacă echipa A e alocată pe 2 activități în aceeași perioadă: ambele bare
de resurse au border roșu + icon ⚠. Click: popup cu opțiuni rezolvare
(re-alocare, amânare, subcontractare).

**Note developer**

**Implementare**

Extends componenta Gantt (E-016). State: showResources (boolean). Când
ON: pentru fiecare activitate cu alocări, renderizează un rând
suplimentar cu bare proporționale pe timeline. Date: din endpoint
/api/projects/:id/gantt/resources.

**Conflict detection**

Client-side: iterează alocările per interval. Dacă 2 activități share
aceeași resursă în aceeași perioadă → marcaj conflict. Server-side:
validare la orice modificare alocare.

**Performance**

Rândurile resurse: lazy render (doar cele vizibile în viewport). Virtual
scrolling dacă \>50 activități. Canvas pentru rânduri resurse dacă \>100
activități.
