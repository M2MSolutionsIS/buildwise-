# Wireframes Faza4

**BuildWise**

Wireframe Specification Document

Faza 4 - Sub-ecrane (Tab-uri)

22 sub-ecrane \| Tab-uri individuale din ecranele multi-tab

M2M Solutions Consulting SRL - Martie 2026

Cuprins

Faza 4 - Sub-ecrane (Tab-uri)

22 sub-ecrane individuale: Contact Detail (4 tab-uri), Offer Builder (4
steps), Opportunity Activitati, Project RM (P2), Settings (5 sectiuni),
Notifications Preferences, Technical Data (4 tab-uri P1), Import Engine
(2 steps P2).

E-003.2 - Tab: Istoric Interactiuni

![E-003.2](media/d99e46b11c8be82986467e97dd3f581e3287c563.jpg "E-003.2"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN

  **Parent**         E-003 Contact Detail

  **F-codes**        F009

  **Tip**            Timeline + Filters

  **Prioritate**     P1
  ------------------ ----------------------------------------------------

**Descriere**

Timeline cronologica a tuturor interactiunilor cu contactul (apeluri,
emailuri, vizite, oferte, notite). Filtre pe tip interactiune. Paginare
infinita. Click pe oferta linkata navigheza la E-006.

**Note developer**

**API**

GET
/api/contacts/:id/interactions?page=1&per_page=10&type=all&sort=desc.
Paginare cursor-based.

**UX**

Infinite scroll. Loading indicator la scroll bottom. Filtrele se aplica
instant.

E-003.3 - Tab: Proprietati

![E-003.3](media/ed0d668073272ecafa4d4a91f849693001b8174d.jpg "E-003.3"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN

  **Parent**         E-003 Contact Detail

  **F-codes**        F011, F012

  **Tip**            List / Cards

  **Prioritate**     P1
  ------------------ ----------------------------------------------------

**Descriere**

Lista proprietatilor asociate contactului. Card: denumire, adresa,
regim, suprafata, U-value, proiect, badge energie. Click proprietate -\>
E-028 (P1) sau detail simplu (P2/P3). Badge energie doar P1.

**Note developer**

**API**

GET /api/contacts/:id/properties. Returnaza lista cu sumar energetic.

**Variante prototip**

P1: badge energie + U-value. P2: fara badge, date constructii. P3:
minimal.

E-003.4 - Tab: Documente

![E-003.4](media/1853b9d8e653670929425ddbd8d486939b52e2e8.jpg "E-003.4"){width="6.770833333333333in"
height="5.895833333333333in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN

  **Parent**         E-003 Contact Detail

  **F-codes**        F013

  **Tip**            Grid + Upload

  **Prioritate**     P1
  ------------------ ----------------------------------------------------

**Descriere**

Grid documente cu thumbnail, denumire, dimensiune, data, categorie.
Upload drag and drop. Categorie obligatorie (Contract, Tehnic, Oferta,
Foto, Altele). Preview inline: PDF=iframe, imagine=lightbox. Delete cu
confirmare.

**Note developer**

**Upload**

POST /api/contacts/:id/documents (multipart). Max 25MB. Tipuri: PDF,
DOCX, XLSX, JPG, PNG. Categorie obligatorie.

**Preview**

PDF: iframe/PDF.js. Imagine: lightbox cu zoom. DOCX/XLSX: doar download.

E-003.5 - Tab: Oferte si Contracte

![E-003.5](media/dd448732b0ac09ab306c0c48ad8d9e085e335274.jpg "E-003.5"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN

  **Parent**         E-003 Contact Detail

  **F-codes**        F014

  **Tip**            Tables

  **Prioritate**     P1
  ------------------ ----------------------------------------------------

**Descriere**

Doua tabele: Oferte (ID clickabil-\>E-006, denumire, valoare, status,
versiune, data, agent) si Contracte (ID clickabil-\>E-007, denumire,
valoare, status, perioada, proiect linkat). Sortare desc.

**Note developer**

**API**

GET /api/contacts/:id/offers si /contracts. Liste sortate desc.

E-005.S1 - Step 1: Selectare Client

![E-005.S1](media/2296fd42d459709a7294a0455c719942b4d911aa.jpg "E-005.S1"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN

  **Parent**         E-005 Offer Builder

  **F-codes**        F020

  **Tip**            Form

  **Prioritate**     P1
  ------------------ ----------------------------------------------------

**Descriere**

Search client (denumire, CUI, email) + selectare proprietate optionala
din lista proprietatilor clientului. Pre-populat daca vine din Contact
Detail sau Pipeline.

**Note developer**

**Search**

GET /api/contacts?search=&limit=5. Debounce 300ms. Dropdown rezultate.

**Proprietati**

GET /api/contacts/:id/properties. Lista dupa selectare client.

E-005.S2 - Step 2: Line Items

![E-005.S2](media/54e94b9c627a2bdbfa7da39a372ee56f6e709b32.jpg "E-005.S2"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN

  **Parent**         E-005 Offer Builder

  **F-codes**        F021, F022

  **Tip**            Table + Picker

  **Prioritate**     P1
  ------------------ ----------------------------------------------------

**Descriere**

Tabel editabil cu line items. Buton Adauga din catalog -\> modal Product
Picker. Buton Linie manuala -\> rand gol editabil. Coloane: #, produs,
cod, UM, cantitate (input), pret unitar (input), total (calculat).
Stergere per rand. Subtotal automat.

**Note developer**

**Calcul**

Client-side: total_linie = cantitate x pret. subtotal =
SUM(total_linii). Re-calculare la keystroke.

**Save**

Auto-save la blur. PATCH /api/offers/:id/items.

E-005.S4 - Step 4: Termeni si Conditii

![E-005.S4](media/523521e561dabcf7e4371b4547b84c1764f49a12.jpg "E-005.S4"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN

  **Parent**         E-005 Offer Builder

  **F-codes**        F023

  **Tip**            Editor

  **Prioritate**     P2
  ------------------ ----------------------------------------------------

**Descriere**

Editor text cu template T&C pre-incarcat din Settings. Dropdown
selectare template. Continut editabil inline. Placeholders vizuale se
substituie automat la generare PDF.

**Note developer**

**Templates**

GET /api/settings/templates?type=offer_tc. Select -\> pre-populare.
Editare = override per oferta.

E-005.S5 - Step 5: Preview si Generare

![E-005.S5](media/767cf0abeaf03a84173187e449a9ebbdaafb2cbd.jpg "E-005.S5"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN

  **Parent**         E-005 Offer Builder

  **F-codes**        F024, F025

  **Tip**            Preview

  **Prioritate**     P1
  ------------------ ----------------------------------------------------

**Descriere**

Preview inline oferta finala (format PDF simulat). Watermark DRAFT.
Header companie + client + proprietate. Tabel line items. T&C. Butoane:
Salveaza draft / Genereaza PDF. La generare: server creaza PDF real,
redirect la E-006.

**Note developer**

**Preview**

Client-side render. Nu PDF real. La Genereaza: POST
/api/offers/:id/generate. Server Puppeteer -\> PDF.

**Watermark**

CSS position absolute, rotated, opacity 0.1. Se elimina cand status !=
Draft.

E-010.1 - Tab: Activitati Oportunitate

![E-010.1](media/c10851c3ea8583b81aabc45c23b45bd213f1d244.jpg "E-010.1"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN

  **Parent**         E-010 Opportunity Detail

  **F-codes**        F043, F049

  **Tip**            Timeline

  **Prioritate**     P1
  ------------------ ----------------------------------------------------

**Descriere**

Timeline completa activitati pe oportunitate. Filtre: Toate,
Planificate, Finalizate, Overdue. Overdue evidentiata rosu cu badge.
Buton + Activitate -\> modal. Entry: status dot, data, titlu, descriere,
user.

**Note developer**

**API**

GET /api/pipeline/opportunities/:id/activities?status=all.

**Overdue**

Server-side: data_planificata \< now() && status != completed -\>
overdue. Badge rosu.

E-014.7 - Tab: RM Proiect

![E-014.7](media/8409fc7b1c59d53054b4f08c59969526c7c21948.jpg "E-014.7"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          SPECIFIC P2

  **Parent**         E-014 Project Detail

  **F-codes**        RM-F01 to F03

  **Tip**            Mini dashboard

  **Prioritate**     P1
  ------------------ ----------------------------------------------------

**Descriere**

Doar P2 (BAHM). Mini-versiune E-032, filtrata pe proiectul curent. KPIs:
echipe alocate, echipamente, utilizare, conflicte. Tabel resurse cu
perioada, utilizare %, status. Link la Dashboard RM complet.

**Note developer**

**API**

GET /api/projects/:id/rm-summary. Subset din E-032 filtrat pe
project_id.

**Vizibilitate**

Tab vizibil doar daca prototip === P2. In P1/P3 nu apare.

E-024.1 - Settings: Utilizatori

![E-024.1](media/489eba32f8888d7c4510684b547ebd231719feb7.jpg "E-024.1"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN

  **Parent**         E-024 Settings

  **F-codes**        F131

  **Tip**            Table + CRUD

  **Prioritate**     P2
  ------------------ ----------------------------------------------------

**Descriere**

Tabel utilizatori cu email, rol, status, ultima activitate. CRUD
complet. Buton Invita utilizator -\> modal. Role: Admin, Sales, PM,
Viewer. Actiuni: editare rol, dezactivare, stergere.

**Note developer**

**API**

CRUD /api/settings/users. POST /invite. PATCH /:id {role, status}.

E-024.2 - Settings: Permisiuni

![E-024.2](media/dd556b9a79858f86254ead9f9b1e909f699f1a58.jpg "E-024.2"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN

  **Parent**         E-024 Settings

  **F-codes**        F132

  **Tip**            Matrix

  **Prioritate**     P2
  ------------------ ----------------------------------------------------

**Descriere**

Matrice permisiuni: randuri = modul x actiune, coloane = roluri.
Checkbox per celula. Save automat. Admin locked ON.

**Note developer**

**API**

GET/PATCH /api/settings/permissions {module, action, role, granted}.

**Frontend**

Matrice dinamica. Admin disabled. Debounce 500ms per toggle.

E-024.3 - Settings: Template-uri

![E-024.3](media/fbd05b895c4c54eef323b0fceaf5c6dfb589f21d.jpg "E-024.3"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN

  **Parent**         E-024 Settings

  **F-codes**        F133

  **Tip**            Editor

  **Prioritate**     P2
  ------------------ ----------------------------------------------------

**Descriere**

Grid template-uri documente. Card: titlu, placeholders, ultima editare.
Click -\> editor WYSIWYG cu placeholders. Preview live. Salvare
disponibila in Offer Builder / Contract Builder.

**Note developer**

**Placeholders**

Sistem tokens: {{contact.name}}, {{offer.value}}, etc. Server substituie
la generare PDF.

E-024.4 - Settings: Campuri Custom

![E-024.4](media/4df9e97a03f58bdfe1d5bf0e443c8bb0703f3b41.jpg "E-024.4"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN

  **Parent**         E-024 Settings

  **F-codes**        F134

  **Tip**            CRUD + Config

  **Prioritate**     P2
  ------------------ ----------------------------------------------------

**Descriere**

Definire campuri custom per entitate (Contacte, Oferte, Proiecte).
Tabel: camp, tip (Text, Dropdown, Data, Numeric, Rating), obligatoriu
toggle, optiuni. Campurile apar automat pe ecranele detail.

**Note developer**

**API**

CRUD /api/settings/custom-fields. POST {entity, name, type, required,
options\[\]}.

**Render**

Detail citeste custom fields din API si le rendereaza dinamic. Tip -\>
componenta React.

E-024.5 - Settings: Pipeline Stadii

![E-024.5](media/d1e10e751829a317965a2f9830943fcf907c30fb.jpg "E-024.5"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN

  **Parent**         E-024 Settings

  **F-codes**        F130

  **Tip**            Drag list

  **Prioritate**     P2
  ------------------ ----------------------------------------------------

**Descriere**

Lista stadii pipeline cu drag reorder. Stadiu: culoare, denumire,
threshold stagnare (zile). Castigat/Pierdut fixe (nu se muta/sterg).
Buton adauga stadiu pentru intermediare.

**Note developer**

**API**

GET /api/settings/pipeline-stages. PATCH /reorder. POST (add). DELETE
(doar fara oportunitati).

**Restrictii**

Castigat/Pierdut: fixed, ultimele 2, nu se pot sterge/reordona.

E-025.1 - Notifications: Preferences

![E-025.1](media/885cedd261e732adfc069501cf9337dddcf375ed.jpg "E-025.1"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN

  **Parent**         E-025 Notifications

  **F-codes**        F136

  **Tip**            Matrix

  **Prioritate**     P2
  ------------------ ----------------------------------------------------

**Descriere**

Matrice preferinte: randuri = tipuri eveniment, coloane = canale
(In-App, Email). Toggle per celula. Evenimente critice au In-App locked
ON. Salvare automat.

**Note developer**

**API**

GET/PATCH /api/notifications/preferences. Format: \[{event_type,
channel, enabled}\].

E-028.1 - Tab: Parametri Energetici

![E-028.1](media/bcda30da1c9fa7c71ccdebf86c862df1c927873a.jpg "E-028.1"){width="6.770833333333333in"
height="4.364583333333333in"}

  ------------------ ----------------------------------------------------
  **Scope**          SPECIFIC P1

  **Parent**         E-028 Technical Data

  **F-codes**        F012, F013

  **Tip**            Form

  **Prioritate**     P0
  ------------------ ----------------------------------------------------

**Descriere**

Coeficienti transfer termic per element constructiv (sticla, pereti,
acoperis, planseu). U-value numeric + material. Consum energetic estimat
automat (functie de U-values + suprafata + zona climatica). Clasa
energetica derivata. Diferentiator core BuildWise.

**Note developer**

**Calcul**

Server-side formula C107/2005. Input: U-values, suprafata, zona, HVAC.
Output: kWh/mp/an, clasa A+ la G.

**Validari**

U-value: 0.1-5.0, float, 1-2 decimale. Zona climatica: dropdown I-IV.
Clasa: read-only.

E-028.2 - Tab: HVAC

![E-028.2](media/c12715a6b5005b0bf276474713b00904494d3b4d.jpg "E-028.2"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          SPECIFIC P1

  **Parent**         E-028 Technical Data

  **F-codes**        F014

  **Tip**            Form

  **Prioritate**     P1
  ------------------ ----------------------------------------------------

**Descriere**

Date sistem HVAC: tip incalzire, capacitate kW, tip racire, capacitate,
ventilatie (tip + eficienta recuperator), an instalare, COP. Editabile
inline. Date folosite in calculul consum.

**Note developer**

**Campuri**

Incalzire: centrala gaz, pompa caldura, electric, biomasa, solar.
Racire: VRF, split, chiller, fara. Ventilatie: natural, mecanica,
recuperator + eficienta %.

E-028.3 - Tab: Calculator Suprafete

![E-028.3](media/697bb1c81f31a5594993923ce20ac34c0c938fa8.jpg "E-028.3"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          SPECIFIC P1

  **Parent**         E-028 Technical Data

  **F-codes**        F015

  **Tip**            Calculator dinamic

  **Prioritate**     P1
  ------------------ ----------------------------------------------------

**Descriere**

Formular dinamic: rand per nivel. Coloane: nivel, nr ferestre,
suprafata/fereastra, total vitrata (calculat), tip sticla, U-value.
Buton Adauga nivel. Footer total general. Override manual posibil.

**Note developer**

**Dinamic**

React: array state. Push/pop niveluri. Total nivel = nr_ferestre x
suprafata. Total general = SUM. Override checkbox.

**Persistare**

PATCH /api/properties/:id/technical/surfaces. Array obiecte per nivel.

E-028.4 - Tab: Istoric Masuratori

![E-028.4](media/2101a11042d73f97a2e693283acbc090cff47382.jpg "E-028.4"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          SPECIFIC P1

  **Parent**         E-028 Technical Data

  **F-codes**        F016

  **Tip**            Timeline / Table

  **Prioritate**     P1
  ------------------ ----------------------------------------------------

**Descriere**

Istoric cronologic masuratori energetice pe proprietate. Populat automat
din E-029 (PRE/POST) si audituri. Coloane: data, tip, parametru,
valoare, sursa, proiect. Read-only.

**Note developer**

**API**

GET /api/properties/:id/measurements?sort=desc. Read-only, scrise de
E-029.

**Badge-uri**

PRE = rosu, POST = verde, AUDIT = gri. Colorare pe tip.

E-037.S1 - Import: Step 1 Sursa

![E-037.S1](media/e20fb8a435011dbb3da05695384c6df0c9b1af43.jpg "E-037.S1"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          SPECIFIC P2

  **Parent**         E-037 Import Engine

  **F-codes**        RM-F17

  **Tip**            Selector

  **Prioritate**     P1
  ------------------ ----------------------------------------------------

**Descriere**

Selectare sursa import: Intersoft XML (recomandat), eDevize Export
(CSV/XLSX), CSV Manual. Card per optiune cu icon, denumire, descriere.
Click selecteaza.

**Note developer**

**Config**

Sursele configurabile din Settings. Fiecare: id, name, description,
parser_type, accepted_extensions\[\].

E-037.S2 - Import: Step 2 Upload

![E-037.S2](media/d66c514f84a10b611e51a10ce4d17c30bd49b6f4.jpg "E-037.S2"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          SPECIFIC P2

  **Parent**         E-037 Import Engine

  **F-codes**        RM-F18

  **Tip**            Upload + Table

  **Prioritate**     P1
  ------------------ ----------------------------------------------------

**Descriere**

Zona upload (drag/drop sau click) + preview tabel articole parsate.
Status per articol: Valid (verde), Eroare (rosu). Erori cu detalii
(rand/coloana). Optiuni: re-upload, ignora erori, fix manual.

**Note developer**

**Parsing**

POST multipart. Server parser specific sursei. Returneza session_id +
items\[\] + errors\[\]. Session 24h.

**Erori**

Tipice: camp lipsa, format nerecunoscut, pret negativ. Per eroare: {row,
col, message, severity}.
