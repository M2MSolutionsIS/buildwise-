# Wireframes Faza6

**BuildWise**

Wireframe Specification Document

Faza 6 - Componente Globale

5 componente globale reutilizabile \| Design patterns pentru delete,
toast, empty state, skeleton, PDF preview

M2M Solutions Consulting SRL - Martie 2026

Cuprins

Faza 6 - Componente Globale

5 componente globale: Confirmare Stergere (3 variante), Toast
Notifications (4 variante), Empty State (4 variante contextuale),
Skeleton Loader (6 variante), PDF Preview Modal.

C-001 - Confirmare Stergere - Pattern Global

![C-001](media/27131a948f15670e0ce56551c86eae2d461c2511.jpg "C-001"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN

  **Parent**         Global (reutilizat pe orice entitate)

  **F-codes**        ---

  **Tip**            Confirm modal

  **Prioritate**     P1
  ------------------ ----------------------------------------------------

**Descriere**

Modal confirmare stergere reutilizat pe toate entitatile. 3 variante:
(1) Stergere simpla - doar confirmare text, (2) Stergere cu dependente -
arata cascade (cate entitati dependente se sterg), (3) Stergere cu
confirmare text - pentru entitati critice (proiect, contract) necesita
tastarea DELETE.

**Note developer**

**Componenta**

ConfirmDeleteModal({entity_type, entity_name, dependencies\[\],
require_text_confirm}). Props determina varianta afisata automat.

**API**

DELETE /api/{entity_type}/{id}. La success: toast.success + redirect la
lista. La eroare: toast.error cu detalii.

C-002 - Toast Notifications - 4 Variante

![C-002](media/e302e9d15dc7decc60431dfb1939d5a3b2198ff6.jpg "C-002"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN

  **Parent**         Global (afisate din orice ecran)

  **F-codes**        ---

  **Tip**            Toast component

  **Prioritate**     P1
  ------------------ ----------------------------------------------------

**Descriere**

4 variante: Success (verde, auto-dismiss 5s), Error (rosu, persistent
pana la close manual), Warning (portocaliu, auto-dismiss 8s), Info
(albastru, auto-dismiss 5s). Pozitie: top-right fixed. Max 3 vizibile
simultan, stack vertical. Hover pauzeza auto-dismiss.

**Note developer**

**Biblioteca**

Recomandare: react-hot-toast sau sonner. API: toast.success(msg),
toast.error(msg), toast.warning(msg), toast.info(msg).

**Config**

Z-index: 300 (peste modale). Width: 320-400px. Animatie: slide-in
dreapta 300ms. Close: click X sau auto-dismiss.

C-003 - Empty State Pattern - Variante

![C-003](media/82c42457573e488dfe492ba2b19737897d47d7bd.jpg "C-003"){width="6.770833333333333in"
height="6.5in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN

  **Parent**         Global (in orice lista/tabel/dashboard gol)

  **F-codes**        ---

  **Tip**            Empty state component

  **Prioritate**     P2
  ------------------ ----------------------------------------------------

**Descriere**

4 variante contextuale: (1) Tabel/lista goala - icon + mesaj + CTA
adaugare, (2) Filtru fara rezultate - mesaj + buton reset filtre, (3)
Dependenta neindeplinita - mesaj + link la ecranul prerequisit, (4) Date
insuficiente - mesaj + CTA adaugare date. Structura: icon (36px, opacity
0.3) + titlu (14px bold) + descriere (11px, max 2 randuri) + CTA button.

**Note developer**

**Componenta**

EmptyState({variant, icon, title, description, cta_text, cta_action}).
Centrat vertical si orizontal in container parinte.

**Variante**

variant: empty_list \| no_results \| dependency \| insufficient_data.
Fiecare cu icon si mesaj default, overrideable prin props.

C-004 - Skeleton Loader Pattern - Variante

![C-004](media/1b314cf3f5e32fbb9654348e6649356d7def514d.jpg "C-004"){width="6.770833333333333in"
height="6.114583333333333in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN

  **Parent**         Global (in orice componenta la loading)

  **F-codes**        ---

  **Tip**            Skeleton component

  **Prioritate**     P2
  ------------------ ----------------------------------------------------

**Descriere**

6 variante: KPI Card, Table Row, Card, Contact Header, Form Fields,
Kanban Card. CSS shimmer animation (gradient moving left-to-right, 1.5s
infinite). Dimensiuni proportionale cu continutul real. Se afiseaza
instant la mount, se inlocuieste cu date la API response.

**Note developer**

**Implementare**

CSS: \@keyframes shimmer gradient animation. Componente: SkeletonKPI,
SkeletonTableRow, SkeletonCard, SkeletonHeader, SkeletonForm,
SkeletonKanban. Fiecare cu width/height matching componenta reala.

**UX**

Se afiseaza imediat (nu dupa delay). Se inlocuieste fara flicker (fade
transition 200ms). Culoare: rgba(59,130,246,0.04-0.08) pe fundal dark.

C-005 - PDF Preview Modal

![C-005](media/388f7d2e673a3b18fbc9e6fd08702cd42b796bea.jpg "C-005"){width="6.770833333333333in"
height="4.229166666666667in"}

  ------------------ ----------------------------------------------------
  **Scope**          COMUN

  **Parent**         Global (Offer Builder, Contract Builder, SdL,
                     Rapoarte)

  **F-codes**        ---

  **Tip**            Preview modal

  **Prioritate**     P1
  ------------------ ----------------------------------------------------

**Descriere**

Modal preview PDF inline cu zoom controls (+, -, procent). Content area
cu background gri si pagina alba centrata. Butoane: Print (browser print
dialog), Download PDF (descarca fisierul), Close. Reutilizat pentru:
oferte, contracte, situatii de lucrari, rapoarte.

**Note developer**

**Implementare**

PDF renderizat cu PDF.js (iframe fallback). Zoom: CSS transform scale().
Download: window.open(pdf_url) sau blob download. Print: window.print()
pe iframe.

**API**

GET /api/{entity_type}/{id}/pdf. Returneaza blob PDF. Cache client-side
(nu re-fetch la re-open).
