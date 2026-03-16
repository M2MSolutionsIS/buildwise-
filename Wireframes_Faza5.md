# Wireframes Faza5

**BuildWise**

Wireframe Specification Document

Faza 5 - Modale & Overlay-uri

22 modale si overlay-uri \| Form modals, diff modals, action modals,
slide-overs

M2M Solutions Consulting SRL - Martie 2026

Cuprins

Faza 5 - Modale & Overlay-uri

22 modale si overlay-uri: form modals (adaugare persoane, produse,
noduri WBS, articole deviz, activitati, comenzi), diff modals (duplicate
guard, versiuni oferta, versiuni wiki), workflow modals (aprobare
contract, rezolvare conflict), detail modals (produs, angajat,
echipament, model ML), action modals (won/lost, schimbare status),
slide-over (quick opportunity), upload modal.

E-003.M1 - Modal: Adauga Persoana Contact

![E-003.M1](media/775a0ec9a0a6f8e21b11ecc51b2d38633ea874e7.jpg "E-003.M1"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN

  **Parent**         E-003 Contact Detail

  **F-codes**        F008

  **Tip**            Form modal

  **Prioritate**     P1
  ------------------ ----------------------------------------------------

**Descriere**

Formular adaugare persoana de contact: nume, rol/functie, telefon,
email, flag principal (da/nu), notite. Validare: email format, telefon
+40. La salvare: se adauga in lista persoane de contact a contactului.

**Note developer**

**API**

POST /api/contacts/:id/persons {name, role, phone, email, is_primary,
notes}.

**UX**

Focus auto pe primul camp. Tab navigare. Enter = save. Escape = close.

E-003.M2 - Modal: Duplicate Guard Compare

![E-003.M2](media/3f57f86a50347b2fc3fbe82ed2ac6bafe5cf3164.jpg "E-003.M2"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN

  **Parent**         E-003 Contact Detail

  **F-codes**        F006

  **Tip**            Diff modal

  **Prioritate**     P1
  ------------------ ----------------------------------------------------

**Descriere**

Comparatie side-by-side a doua contacte suspecte de duplicare. Per camp:
valoarea din contactul A vs B, cu radio button pentru selectia campului
castigator. La merge: contactul B se sterge, toate
interactiunile/ofertele se transfera la A.

**Note developer**

**API**

GET /api/contacts/:id/duplicate-candidates. POST /api/contacts/merge
{keep_id, delete_id, field_choices{}}.

**UX**

Campuri identice: badge verde. Campuri diferite: highlight portocaliu cu
radio selectie. Interactiuni: se combina automat.

E-003.M3 - Modal: Upload Document

![E-003.M3](media/517bf775de51bddc1dc4a196a7ff074f9b14a4f3.jpg "E-003.M3"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN

  **Parent**         E-003 Contact Detail

  **F-codes**        F013

  **Tip**            Upload modal

  **Prioritate**     P2
  ------------------ ----------------------------------------------------

**Descriere**

Zona drag and drop pentru upload fisiere. Categorie obligatorie
(dropdown: Contract, Tehnic, Oferta, Fotografie, Altele). Progress bar
per fisier. Max 25MB. Tipuri acceptate: PDF, DOCX, XLSX, JPG, PNG.

**Note developer**

**API**

POST /api/contacts/:id/documents (multipart form-data). Fields: file,
category.

**UX**

Drag over: border highlight albastru. Drop: start upload instant.
Multiple files simultan. Progress bar animat.

E-004.M1 - Modal: Produs Detail / Edit

![E-004.M1](media/ad15060aa939b72aa2b21366f68a851690d95b87.jpg "E-004.M1"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN

  **Parent**         E-004 Catalog

  **F-codes**        F018

  **Tip**            Form modal

  **Prioritate**     P1
  ------------------ ----------------------------------------------------

**Descriere**

Formular complet editare produs: cod, categorie, denumire, UM, pret
unitar curent, status, descriere. Sectiune istoric preturi (read-only,
cronologic). La salvare pret diferit: se creaza automat versiune noua in
istoric.

**Note developer**

**API**

PATCH /api/products/:id. Pretul: POST /api/products/:id/prices
(auto-versionare).

**UX**

Pret: input cu format EUR. La blur: format automat cu 2 decimale.
Istoric: scroll vertical daca \> 5 entries.

E-005.M1 - Modal: Product Picker

![E-005.M1](media/977f411a0210c2c3a73f50d72c7a653c082d0ec2.jpg "E-005.M1"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN

  **Parent**         E-005 Offer Builder

  **F-codes**        F021

  **Tip**            Search + Select modal

  **Prioritate**     P1
  ------------------ ----------------------------------------------------

**Descriere**

Search produse din catalog cu filtru categorie. Lista cu checkbox per
produs (cod, denumire, UM, pret, categorie). Multi-select. Buton Adauga
(N) la oferta -\> adauga selectia ca line items in Step 2.

**Note developer**

**API**

GET /api/products?search=&category=&status=active&limit=20.

**UX**

Search debounce 300ms. Checkbox toggle instant. Counter selectie in
buton. Click produs (nu checkbox) = toggle selectie.

E-006.M1 - Modal: Compara Versiuni Oferta

![E-006.M1](media/79273d72d97a72df1b614541a2224a29e77dd72f.jpg "E-006.M1"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN

  **Parent**         E-006 Offer Lifecycle

  **F-codes**        F026

  **Tip**            Diff modal

  **Prioritate**     P1
  ------------------ ----------------------------------------------------

**Descriere**

Comparatie side-by-side v1 vs v2 a ofertei. Tabel: articol, valoare v1,
valoare v2, schimbare (badge: pret modificat, articol adaugat/sters).
Footer cu total v1 vs v2 si delta procentual.

**Note developer**

**API**

GET /api/offers/:id/diff?v1=1&v2=2. Returneza: items\[{name, v1_value,
v2_value, change_type}\].

**UX**

Highlight: verde = adaugat, rosu = sters, portocaliu = modificat.
Neschimbat = gri.

E-007.M1 - Modal: Workflow Aprobare Contract

![E-007.M1](media/ba2000b6ef514b2bb5ad82569e516cf06e6663fc.jpg "E-007.M1"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN

  **Parent**         E-007 Contract Builder

  **F-codes**        F034

  **Tip**            Workflow modal

  **Prioritate**     P1
  ------------------ ----------------------------------------------------

**Descriere**

Workflow aprobare cu pasi vizuali (Juridic -\> Director -\> Client).
Fiecare pas: status (aprobat/pending/respins), aprobator, data. Butoane
Aproba/Respinge. Comentariu obligatoriu la respingere.

**Note developer**

**API**

POST /api/contracts/:id/approve {step, decision: approve\|reject,
comment}.

**UX**

Pasul curent evidential albastru. Pasi viitori gri (locked). La
aprobare: auto-advance la pasul urmator + notificare.

E-009.M1 - Slide-over: Quick Opportunity

![E-009.M1](media/d36e9476b9be516d1945755ea712073c59c50074.jpg "E-009.M1"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN

  **Parent**         E-009 Pipeline Kanban

  **F-codes**        F041

  **Tip**            Slide-over panel

  **Prioritate**     P1
  ------------------ ----------------------------------------------------

**Descriere**

Panel slide-over din dreapta la click pe card in Kanban. KPIs: valoare,
probabilitate, zile in stadiu, scoring. Ultima activitate. Quick
actions: planifica apel, creaza oferta, vezi detalii complete. Nu
paraseste board-ul.

**Note developer**

**API**

GET /api/pipeline/opportunities/:id/summary. Subset din detail.

**UX**

Slide-in 300ms din dreapta. Backdrop transparent click = close. Width:
380px. Scroll intern daca continut lung.

E-010.M1 - Modal: Won/Lost Reason

![E-010.M1](media/c0ab83c00360854b5a8fabbe1f3333fa89dfcac3.jpg "E-010.M1"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN

  **Parent**         E-010 Opportunity Detail

  **F-codes**        F046

  **Tip**            Form modal

  **Prioritate**     P2
  ------------------ ----------------------------------------------------

**Descriere**

La mutare oportunitate in Castigat sau Pierdut: modal obligatoriu. Motiv
principal (dropdown), competitor (daca exista), detalii text
(obligatoriu), posibilitate reactivare (radio). Datele se salveaza
pentru analytics.

**Note developer**

**API**

PATCH /api/pipeline/opportunities/:id {status, close_reason, competitor,
details, reactivation_possible}.

**Analytics**

Datele Won/Lost alimenteaza Pipeline Analytics (E-012): win/loss by
reason chart.

E-011.M1 - Modal: Activitate Noua

![E-011.M1](media/581fe4e18846fce5b690890122ea378feb778ca7.jpg "E-011.M1"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN

  **Parent**         E-011 Activity Planner

  **F-codes**        F051

  **Tip**            Form modal

  **Prioritate**     P1
  ------------------ ----------------------------------------------------

**Descriere**

Formular creare activitate: tip (apel/email/vizita/meeting/nota cu
toggle vizual), titlu, data/ora, durata estimata, client/oportunitate
linkat (search), notite. La salvare: apare in calendar si in timeline-ul
oportunitate.

**Note developer**

**API**

POST /api/activities {type, title, date, time, duration,
linked_opportunity_id, notes}.

**UX**

Tip = toggle buttons colorate. Data = datepicker cu default azi. Ora =
time picker. Client = autocomplete search.

E-014.M1 - Modal: Schimbare Status Proiect

![E-014.M1](media/9487d87914f69f89de8f71f78f5c46c5a1177a5b.jpg "E-014.M1"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN

  **Parent**         E-014 Project Detail

  **F-codes**        F062

  **Tip**            Confirm modal

  **Prioritate**     P1
  ------------------ ----------------------------------------------------

**Descriere**

Confirmare la schimbare status proiect. Arata: proiect, status curent
-\> status nou. Warning cu consecintele (ex: la Post-Execution se
blocheaza tab-urile Executie). Comentariu optional.

**Note developer**

**API**

PATCH /api/projects/:id {status, status_comment}. Trigger: notificare
echipa, unlock/lock tab-uri.

**Consecinte**

Fiecare tranzitie status are consecinte predefinite afisate in modal.
Config server-side.

E-015.M1 - Modal: Adauga Nod WBS

![E-015.M1](media/f497eebf83e7d9aeacf95d20f2cd3a31efb6edb6.jpg "E-015.M1"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN

  **Parent**         E-015 WBS Editor

  **F-codes**        F064

  **Tip**            Form modal

  **Prioritate**     P1
  ------------------ ----------------------------------------------------

**Descriere**

Creare nod WBS: tip (faza/activitate/sub), parent (dropdown daca
activitate/sub), denumire, responsabil (dropdown echipa), durata
estimata (numar + unitate), cost estimat. La salvare: nodul apare in
arbore + se recalculeaza totalurile.

**Note developer**

**API**

POST /api/projects/:id/wbs/nodes {type, parent_id, name, responsible,
duration, duration_unit, estimated_cost}.

**Cod WBS**

Auto-generat server-side pe baza pozitiei in arbore (1.0, 1.1,
1.1.1\...).

E-017.M1 - Modal: Adauga Articol Deviz

![E-017.M1](media/12d2d03c4ff82cc5eb81f4e9084672085df4a073.jpg "E-017.M1"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN

  **Parent**         E-017 Deviz Tracker

  **F-codes**        F068

  **Tip**            Form modal

  **Prioritate**     P1
  ------------------ ----------------------------------------------------

**Descriere**

Creare articol deviz: nod WBS (dropdown obligatoriu), denumire, UM,
cantitate estimata, pret unitar. Total estimat calculat automat. Buton
Salveaza & Adauga altul pentru input rapid serial.

**Note developer**

**API**

POST /api/projects/:id/budget/items {wbs_node_id, name, unit, quantity,
unit_price}.

**Calcul**

Client-side: total = quantity x unit_price. Update instant la keystroke.

E-019.M1 - Modal: Inregistrare Consum Material

![E-019.M1](media/133d9367a8dcc753e1727454c6211fc7077ddc7d.jpg "E-019.M1"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN

  **Parent**         E-019 Fise Consum

  **F-codes**        F074

  **Tip**            Form modal

  **Prioritate**     P1
  ------------------ ----------------------------------------------------

**Descriere**

Inregistrare consum: material (dropdown din deviz, cu rest disponibil
afisat), cantitate consumata, data consum, activitate WBS, nota. La
salvare: se actualizeaza stocul si deviz tracker.

**Note developer**

**API**

POST /api/projects/:id/consumption {budget_item_id, quantity, date,
wbs_node_id, note}.

**Validare**

Cantitate \> 0. Warning (nu blocant) daca depaseste restul disponibil.
Legatura bidirectionala cu E-035 Materiale (P2).

E-021.M1 - Modal: Adauga Defect Punch List

![E-021.M1](media/e7ea9f5a9ae2250b49e658068bc4abcb89fdcc52.jpg "E-021.M1"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN

  **Parent**         E-021 Receptie

  **F-codes**        F082

  **Tip**            Form modal

  **Prioritate**     P2
  ------------------ ----------------------------------------------------

**Descriere**

Creare defect: descriere, severitate (Critica/Minora cu toggle vizual),
WBS asociat, responsabil remediere, deadline, fotografii (upload max 5,
10MB/foto), notite. La salvare: apare in Punch List.

**Note developer**

**API**

POST /api/projects/:id/reception/punch-list {description, severity,
wbs_node_id, responsible, deadline, photos\[\], notes}.

**Fotografii**

Upload multipart. Preview thumbnail inline. Max 5 per defect. Click =
lightbox.

E-023.M1 - Modal: Istoric Versiuni Wiki

![E-023.M1](media/fac3d0b7283b88bf06bbd531d18abb42477cb613.jpg "E-023.M1"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN

  **Parent**         E-023 Wiki

  **F-codes**        F143

  **Tip**            List + Diff modal

  **Prioritate**     P2
  ------------------ ----------------------------------------------------

**Descriere**

Lista versiuni articol wiki (cronologic desc). Fiecare: numar versiune,
data, autor, rezumat modificari. Buton Compara cu versiunea curenta -\>
diff vizual. Buton Restaureaza -\> revert la versiunea selectata.

**Note developer**

**API**

GET /api/wiki/articles/:id/versions. POST /api/wiki/articles/:id/revert
{version_id}.

**Diff**

Server-side text diff. Frontend: highlight verde = adaugat, rosu =
sters. Format inline sau side-by-side.

E-024.M1 - Modal: Invita Utilizator

![E-024.M1](media/aefab154654c5607d8542f389949c1ff7f3cbbad.jpg "E-024.M1"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN

  **Parent**         E-024 Settings

  **F-codes**        F131

  **Tip**            Form modal

  **Prioritate**     P2
  ------------------ ----------------------------------------------------

**Descriere**

Invitare utilizator nou: email (validare format), rol (dropdown:
Admin/Sales/PM/Viewer), mesaj personalizat optional. La trimitere: email
cu link de inregistrare. Contul se activeaza la prima autentificare.

**Note developer**

**API**

POST /api/settings/users/invite {email, role, message}.

**UX**

Email: validare format client-side. Duplicate check: daca email exista
deja -\> warning.

E-030.M1 - Modal: Detalii Model ML

![E-030.M1](media/57c959ece0685fd36790cd02cd2703da9a780233.jpg "E-030.M1"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          SPECIFIC P1

  **Parent**         E-030 Data ML

  **F-codes**        F112

  **Tip**            Detail modal

  **Prioritate**     P1
  ------------------ ----------------------------------------------------

**Descriere**

Detalii model ML: KPIs (eroare, datasets, versiune, status), istoric
antrenari (tabel: versiune, data, datasets, eroare, durata), parametri
model (algoritm, features, target, threshold). Buton Re-antreneaza.

**Note developer**

**API**

GET /api/ml/models/:id/details. POST /api/ml/models/:id/retrain.

**Grafic**

Optional: mini line chart eroare per versiune (trend descrescator =
bun).

E-032.M1 - Modal: Rezolvare Conflict Resurse

![E-032.M1](media/8019579c88fd9b863e88df1bb25899ba5252f421.jpg "E-032.M1"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          SPECIFIC P2

  **Parent**         E-032 Resource Dashboard

  **F-codes**        RM-F03

  **Tip**            Action modal

  **Prioritate**     P1
  ------------------ ----------------------------------------------------

**Descriere**

Detalii conflict (resursa, proiecte implicate, perioada overlap) + 3
optiuni solutie (re-alocare cu delay, inchiriere suplimentara, utilizare
partajata). Fiecare optiune cu descriere + impact estimat. Radio
select + Aplica.

**Note developer**

**API**

POST /api/rm/conflicts/:id/resolve {solution_type, details}.

**Impact**

Server-side: simulare impact per solutie (delay estimat, cost
suplimentar). Afisat inline per optiune.

E-033.M1 - Modal: Fisa Angajat

![E-033.M1](media/0c20098648f6450d928c3292a854f4879b0ca675.jpg "E-033.M1"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          SPECIFIC P2

  **Parent**         E-033 HR

  **F-codes**        RM-F04

  **Tip**            Detail modal

  **Prioritate**     P1
  ------------------ ----------------------------------------------------

**Descriere**

Fisa completa angajat: avatar + nume + echipa + data angajare + status.
Date contact: telefon, email. Competente (tags). Alocare curenta
(proiect + %). Istoric proiecte (tabel). Link la calendar personal.

**Note developer**

**API**

GET /api/rm/staff/:id/details. Include: allocations\[\],
project_history\[\], competencies\[\].

E-034.M1 - Modal: Echipament Detail

![E-034.M1](media/2d74e180fe5a7195f28331c5276841eff1bef621.jpg "E-034.M1"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          SPECIFIC P2

  **Parent**         E-034 Echipamente

  **F-codes**        RM-F09

  **Tip**            Detail modal

  **Prioritate**     P1
  ------------------ ----------------------------------------------------

**Descriere**

Detalii echipament: tip, status, capacitate, data achizitie. Program
mentenanta: ultima revizie + urmatoarea + interval. Istoric alocare
(tabel: proiect, perioada).

**Note developer**

**API**

GET /api/rm/equipment/:id/details. Include: maintenance_schedule,
allocation_history\[\].

E-035.M1 - Modal: Comanda Rapida Material

![E-035.M1](media/d36fd9d559ff42813182430e86b1209068060e01.jpg "E-035.M1"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          SPECIFIC P2

  **Parent**         E-035 Materiale

  **F-codes**        RM-F12

  **Tip**            Form modal

  **Prioritate**     P1
  ------------------ ----------------------------------------------------

**Descriere**

Comanda rapida material sub stoc: material pre-selectat (read-only),
cantitate (sugerat: lipsa + buffer), UM, furnizor (dropdown), pret
estimat/UM, ETA livrare. Total estimat calculat. La salvare: comanda
activa in sistem.

**Note developer**

**API**

POST /api/rm/materials/orders {material_id, quantity, supplier_id,
estimated_price, eta}.

**Sugerat**

Cantitate default = (alocat_proiecte - stoc_curent) + 15% buffer.
Editabil.
