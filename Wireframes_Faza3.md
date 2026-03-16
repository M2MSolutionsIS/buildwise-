# Wireframes Faza3

**BuildWise**

Wireframe Specification Document

Faza 3 --- Ecrane P2 Utile + Specifice

11 ecrane \| 9 comune + 1 specific P1 (AI Assistant) + 1 specific P3
(Reports Builder)

M2M Solutions Consulting SRL · Martie 2026

Cuprins

Faza 3 --- Ecrane P2 Utile + Specifice P1/P3

Ultimele 11 ecrane: 9 comune (Contracts Pipeline, Pipeline Analytics,
Projects Lista, Recepție, BI Dashboard, Wiki, Settings, Notifications,
Global Search) + 1 specific P1 (AI Assistant) + 1 specific P3 (Reports
Builder). Prioritate P2 --- necesare pentru produs complet dar pot fi
simplificate inițial.

E-008 --- Contracts --- Pipeline

![E-008](media/fbf364c61ad5382474bfbc28f7eaf7e12929fb2a.jpg "E-008"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN --- P1 ✓ P2 ✓ P3 ✓

  **F-codes**        F029, F034, F035

  **Tip ecran**      Board + List

  **Complexitate**   Scăzută

  **Prioritate**     P2 --- Utilă

  **Tab-uri**        Pipeline Kanban (În discuții → Curs semnare → Semnat
                     → Blocat → Expirat) \| Toggle Board/Tabel \| Filtre
                     client/perioadă
  ------------------ ----------------------------------------------------

**Descriere**

Reutilizează pattern-ul Kanban din Pipeline Board (E-009). Coloane:
stadii contract. Carduri: client, valoare, dată, status. Link direct la
Contract Builder (E-007) și la proiect PM creat. Toggle între view Board
și Tabel.

**Note developer**

**Implementare**

Reutilizează componenta Kanban din E-009 cu config diferit: {stages:
contract_stages, card_fields: \[client, value, date, linked_project\]}.
Același drag & drop, filtre, calcul footer.

**API**

GET /api/contracts/pipeline. PATCH /api/contracts/:id {status}. Aceleași
mecanisme ca pipeline oportunități.

E-012 --- Pipeline --- Analytics

![E-012](media/94bf1369653c4e58f42f3d67e1ab92feb7e75587.jpg "E-012"){width="6.770833333333333in"
height="5.90625in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN --- P1 ✓ P2 ✓ P3 ✓

  **F-codes**        F056, F057, F058

  **Tip ecran**      Dashboard / Charts

  **Complexitate**   Medie

  **Prioritate**     P2 --- Utilă

  **Tab-uri**        KPIs (pipeline total, win rate, deal size, cycle
                     time) \| Conversion Funnel \| Performance per Agent
                     \| Forecast Revenue \| Export
  ------------------ ----------------------------------------------------

**Descriere**

Dashboard analytics cu grafice: conversion funnel (bară orizontală pe
stadii, cu drop-off %), performance per agent (tabel comparativ: deals,
valoare, win rate, cycle time), forecast revenue (bar chart cu confirmat
vs ponderat pe luni viitoare). Filtru perioadă + agent. Export PDF/CSV.

**Note developer**

**API**

GET /api/pipeline/analytics?period=Q1-2026&agent=all. Returnează:
kpis{}, funnel\[\], agent_performance\[\], forecast\[\].

**Grafice**

Recharts: BarChart (funnel, forecast), Table (agents). Responsive:
chart-urile se redimensionează. Export: server-side PDF cu charts ca
images (Puppeteer).

E-013 --- Projects --- Lista

![E-013](media/4674dc3900221638501defbe9b2edcd9c40af6f2.jpg "E-013"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN --- P1 ✓ P2 ✓ P3 ✓

  **F-codes**        F060, F061, F101

  **Tip ecran**      List + Filters

  **Complexitate**   Scăzută

  **Prioritate**     P2 --- Utilă

  **Tab-uri**        Tabel proiecte \| Cod, Proiect, Client, PM, Status,
                     Avansare (progress bar), Buget, SPI, CPI \| Filtre
                     status/PM \| Quick actions
  ------------------ ----------------------------------------------------

**Descriere**

Pattern identic cu Contacts Lista (E-002). Tabel cu badge-uri status
colorate. Coloana Avansare % cu progress bar inline. Coloane SPI/CPI
colorate pe performanță (verde \>1, roșu \<0.9). Click rând → E-014
Project Detail.

**Note developer**

**API**

GET /api/projects?status=&pm=&search=&sort=&page=. Pattern identic cu
contacts.

**Reutilizare**

Componenta tabel reutilizabilă din E-002 cu config coloane diferit.
Aceeași logică filtre, paginare, export.

E-021 --- Recepție & Punch List

![E-021](media/7b9f42684c6fdfaf5f3e877d899fe7e36a828aeb.jpg "E-021"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN --- P1 ✓ P2 ✓ P3 ✓

  **F-codes**        F081, F082

  **Tip ecran**      Checklist + Detail

  **Complexitate**   Medie

  **Prioritate**     P2 --- Utilă

  **Tab-uri**        Tab Checklist (iteme din WBS cu status
                     OK/Parțial/Defect) \| Tab Punch List (defecte cu
                     severitate, responsabil, deadline, fotografii) \|
                     Finalizare recepție
  ------------------ ----------------------------------------------------

**Descriere**

Checklist cu iteme generate automat din WBS (fiecare activitate = un
item de verificat). Status per item: OK (verde), Parțial (portocaliu),
Defect (roșu → se creează item în Punch List). Punch List: tabel defecte
cu severitate (Critică/Minoră), responsabil, deadline, fotografii
atașate, status (Deschis/Rezolvat). Buton \"Finalizează recepția\" →
schimbă status proiect la Închis (necesită 0 defecte critice deschise).

**Note developer**

**API**

GET /api/projects/:id/reception. POST /reception/checklist-items/:id
{status, notes}. POST /reception/punch-list {defect, severity,
responsible, deadline}. PATCH /punch-list/:id {status}. POST
/reception/finalize.

**Fotografii**

Upload pe punch list item. Max 5 per item, 10MB per foto. Preview
lightbox. Storage: S3/MinIO.

**Finalizare**

Validare: toate itemele checklist OK sau Parțial (nu Defect), zero
defecte critice deschise în punch list. La finalizare: proiect → status
\"Închis\", notificare client, generare raport final.

E-022 --- BI --- Executive Dashboard

![E-022](media/ab2f19ce4a9d1f4d1be99f195d1012a1e3b059a6.jpg "E-022"){width="6.770833333333333in"
height="4.395833333333333in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN --- P1 ✓ P2 ✓ P3 ✓

  **F-codes**        F100, F101, F102, F103

  **Tip ecran**      Dashboard

  **Complexitate**   Medie

  **Prioritate**     P2 --- Utilă

  **Tab-uri**        KPIs globale cross-module \| Revenue realizat vs
                     forecast (bar chart) \| Portofoliu proiecte (status
                     breakdown) \| Alerte
  ------------------ ----------------------------------------------------

**Descriere**

Dashboard C-level cu KPIs agregate din toate modulele. Fiecare card
clickable → drill down la modulul respectiv. Revenue chart: bare pe luni
cu confirmat (verde) vs ponderat din pipeline (albastru dashed).
Portofoliu: breakdown pe statusuri cu count per status. P1 adaugă widget
Impact Energie, P2 adaugă widget RM.

**Note developer**

**API**

GET /api/bi/executive-dashboard. Agregate din: pipeline (valoare totală,
win rate), projects (count per status, revenue), energy (P1: kWh
economisit), rm (P2: utilizare echipe).

**Widget-uri per prototip**

Config: dashboard_widgets = {P1: \[\..., \'energy_impact\'\], P2:
\[\..., \'rm_utilization\'\], P3: \[\...\]}. Componenta dashboard
renderizează doar widget-urile din config.

E-023 --- Wiki --- Documentație

![E-023](media/4c863751fd4c8fff558c89afb4d33bd68dddd91e.jpg "E-023"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN --- P1 ✓ P2 ✓ P3 ✓

  **F-codes**        F140, F141, F142, F143, F144, F145

  **Tip ecran**      Tree + Content

  **Complexitate**   Medie

  **Prioritate**     P2 --- Utilă

  **Tab-uri**        Sidebar arbore categorii + search \| Content area cu
                     editor WYSIWYG \| Versionare (diff vizual) \| Tags
                     \| Timeline modificări
  ------------------ ----------------------------------------------------

**Descriere**

Layout split: sidebar (220px) cu arbore categorii colapsabil + search
full-text, și content area cu articolul selectat. Editor WYSIWYG (la
click \"Editează\") cu markdown support. Versionare automată la fiecare
save --- click \"Istoric versiuni\" → lista cu diff vizual. Tags pentru
categorizare cross-categorii. Timeline din mockup-ul existent.

**Note developer**

**API**

GET /api/wiki/tree (arbore). GET /api/wiki/articles/:id. PATCH (save →
auto-versionare). GET /versions. GET /search?q=.

**Editor**

Recomandare: TipTap (bazat pe ProseMirror) sau Lexical (Meta). Support:
headings, bold, italic, lists, code blocks, images inline, tables.
Markdown shortcutting (## → H2, \*\*bold\*\* → bold).

**Search**

Full-text search server-side (PostgreSQL FTS sau Elasticsearch).
Highlight matches în rezultate. Debounce 300ms.

E-024 --- Settings --- Company & Users

![E-024](media/00711ae049278c49eeaf32dabb05fc9e846803cb.jpg "E-024"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN --- P1 ✓ P2 ✓ P3 ✓

  **F-codes**        F130, F131, F132, F133, F134

  **Tip ecran**      Settings / Forms

  **Complexitate**   Medie

  **Prioritate**     P2 --- Utilă

  **Tab-uri**        Sidebar categorii (Companie, Utilizatori,
                     Permisiuni, Template-uri, Integrări, Notificări,
                     Câmpuri Custom, Pipeline Stadii) \| Content per
                     categorie
  ------------------ ----------------------------------------------------

**Descriere**

Settings clasic cu sidebar categorii. Companie: date firmă editabile.
Utilizatori: tabel CRUD + role assignment (Admin, Sales, PM, Viewer).
Permisiuni: matrice modul × acțiune × rol (read/write/delete).
Template-uri: oferte, contracte, rapoarte --- editor cu placeholders.
Integrări: conectori externi (email, calendar). Câmpuri Custom: definire
câmpuri suplimentare per entitate.

**Note developer**

**API**

GET/PATCH /api/settings/company. CRUD /api/settings/users. GET/PATCH
/api/settings/permissions (matrice). CRUD /api/settings/templates. CRUD
/api/settings/custom-fields.

**Permisiuni**

Matrice: {module}\_{action} per rol. Verificare frontend (UI hiding) +
backend (middleware). Default roles predefinite, custom roles opțional.

E-025 --- Notifications Center

![E-025](media/79edda845bf9257d63c5e4fa0ee695bbe8b8bcc2.jpg "E-025"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN --- P1 ✓ P2 ✓ P3 ✓

  **F-codes**        F135, F136

  **Tip ecran**      List + Settings

  **Complexitate**   Scăzută

  **Prioritate**     P2 --- Utilă

  **Tab-uri**        Feed notificări cronologic \| Filtru modul/tip \|
                     Mark read/unread \| Preferences (ce primește fiecare
                     user) \| Bulk mark all read
  ------------------ ----------------------------------------------------

**Descriere**

Feed cronologic cu notificări colorate pe severitate (roșu=critic,
portocaliu=atenție, verde=info, gri=citit). Click notificare →
navighează la ecranul relevant + mark as read. Tab Preferences: matrice
eveniment × canal (in-app, email) per user.

**Note developer**

**API**

GET /api/notifications?filter=all&page=1. PATCH
/api/notifications/:id/read. PATCH /api/notifications/mark-all-read.
GET/PATCH /api/notifications/preferences.

**Real-time**

WebSocket: /ws/notifications. Event: new_notification → increment badge
count + prepend în feed. Fallback: polling 30s.

E-026 --- Global Search

![E-026](media/2a1bd3ca64d2c0228b4813bb32825237389921dd.jpg "E-026"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN --- P1 ✓ P2 ✓ P3 ✓

  **F-codes**        F137, F138

  **Tip ecran**      Modal / Overlay

  **Complexitate**   Scăzută

  **Prioritate**     P2 --- Utilă

  **Tab-uri**        Modal overlay (Cmd+K) \| Input cu debounce \|
                     Rezultate grupate pe tip (Contacte, Proiecte,
                     Oferte, Contracte) \| Max 5 per categorie \|
                     Keyboard navigation
  ------------------ ----------------------------------------------------

**Descriere**

Modal overlay la Cmd+K. Input cu debounce 300ms, min 2 caractere.
Rezultate grupate pe entitate: Contacte, Proiecte, Oferte, Contracte.
Max 5 rezultate per categorie. Click → navighează. Highlight match în
text. Recent searches salvate local.

**Note developer**

**API**

GET /api/search?q=&limit=5. Returnează: {contacts\[\], projects\[\],
offers\[\], contracts\[\]}. Server-side: search pe titlu/denumire/cod
cross-entity.

**UX**

Focus auto pe input. Esc = close. ↑↓ = navigare rezultate. Enter =
selectare + navigare. Tab = switch categorie. Animație: slide down cu
backdrop blur.

E-031 --- AI Assistant --- Predictive

![E-031](media/dd5a15f6539a149aa6349a817a6ba3495c4ac81e.jpg "E-031"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          SPECIFIC P1 --- doar BuildWise

  **F-codes**        F116, F117, F118

  **Tip ecran**      Chat + Cards

  **Complexitate**   Ridicată

  **Prioritate**     P2 --- Utilă

  **Tab-uri**        Chat interface (input + mesaje) \| Răspunsuri cu
                     carduri vizuale (KPIs, grafice, tabele) \| Sidebar
                     sugestii + context model \| Scenarii what-if
  ------------------ ----------------------------------------------------

**Descriere**

Interfață conversațională cu AI pentru predicții energetice. Input
text + sugestii predefinite (sidebar dreapta). Răspunsuri: text +
carduri vizuale inline (KPI-uri calculate, grafice, tabele comparație).
Contextual: în PM arată predicții pentru proiectul curent, în CRM arată
scoring energetic per proprietate. Sidebar: sugestii rapide + info model
activ (versiune, datasets, eroare).

**Note developer**

**API**

POST /api/ai/chat {message, context: {project_id?, property_id?}}.
Returnează: {text, cards: \[{type: \'kpi\'\|\'chart\'\|\'table\',
data}\]}. Backend: LLM + RAG pe datele din platformă.

**Carduri**

Componente React renderizate inline în chat. KPI card: {label, value,
delta}. Chart card: mini Recharts inline. Table card: tabel simplu.

**Context**

Sidebar afișează model activ, nr datasets, eroare medie. Se actualizează
la fiecare query cu info relevante.

E-041 --- BI --- Reports Builder

![E-041](media/020c8dbb1f44fa9c6aad32678ec7b458ca62fd43.jpg "E-041"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          SPECIFIC P3 --- doar ERP Lite

  **F-codes**        F104, F105, F106

  **Tip ecran**      Builder / Wizard

  **Complexitate**   Ridicată

  **Prioritate**     P2 --- Utilă

  **Tab-uri**        Sidebar surse date (module + câmpuri drag) \| Canvas
                     (grupare, valoare, filtru) \| Preview tabel/grafic
                     \| Salvare template \| Export PDF/Excel
  ------------------ ----------------------------------------------------

**Descriere**

Report builder generic (fără ML). Sidebar: tree cu module (CRM,
Pipeline, PM) și câmpurile fiecăruia --- drag & drop pe canvas. Canvas:
definire grupare (GROUP BY), valoare (SUM/AVG/COUNT), filtre. Preview
real-time: tabel sau grafic. Salvare ca template reutilizabil. Export
PDF/Excel.

**Note developer**

**API**

POST /api/reports/query {source, group_by, aggregate, filters\[\]}.
Returnează: {columns\[\], rows\[\]}. POST /api/reports/templates (save).
GET /templates (list).

**Drag & drop**

Câmpurile din sidebar = draggable. Canvas zones: Group, Value, Filter =
droppable. La drop: update query config → re-fetch preview.

**Export**

PDF: server-side Puppeteer cu tabel/grafic renderizat. Excel: openpyxl
server-side cu formatare.
