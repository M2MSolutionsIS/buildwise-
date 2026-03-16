# BuildWise — Documentație Tehnică

Această documentație conține specificațiile complete pentru platforma BuildWise, convertite din fișierele originale (.xlsx/.docx) în format Markdown pentru a fi citite de Claude Code.

> ⭐ **SURSA DE ADEVĂR pentru implementare este `Centralizator_M2M_ERP_Lite.md`**. Toate celelalte fișiere sunt suport și context. Dacă există contradicții, Centralizatorul câștigă.

## Specificații Implementare (FOLOSEȘTE ACESTEA)

| Fișier | Conținut | Sursa originală |
|--------|---------|-----------------|
| `Centralizator_M2M_ERP_Lite.md` | ⭐ **108 funcționalități** cu F-codes, mapping P1/P2/P3, priorități, user stories | M2M_ERP_Lite_Centralizator_V7.xlsx |
| `Roadmap_TRL5_TRL7.md` | Roadmap tehnic TRL5→TRL7 pe 6 faze / 24 luni | BuildWise_Roadmap_TRL5_TRL7.xlsx |

## Wireframes și Ecrane

| Fișier | Conținut | Sursa originală |
|--------|---------|-----------------|
| `Wireframe_Masterplan.md` | 98 ecrane: ID, modul, tip, complexitate, prioritate, F-codes, navigare (54 flow-uri) | BuildWise_Wireframe_Masterplan_V4.xlsx |
| `Wireframes_Faza0.md` | 9 ecrane principale (Dashboard, Contacts, Pipeline Kanban, Project Hub, etc.) | BuildWise_Wireframes_Faza0.docx |
| `Wireframes_Faza1.md` | 8 ecrane P0 critice (Contact Detail completare, WBS, Deviz, Resource Dashboard) | BuildWise_Wireframes_Faza1.docx |
| `Wireframes_Faza2.md` | 13 ecrane P1 importante (Catalog, Offer, Contract, Activity, Timesheet, etc.) | BuildWise_Wireframes_Faza2.docx |
| `Wireframes_Faza3.md` | 11 ecrane P2 (Contracts Pipeline, Analytics, Wiki, Settings, AI Assistant) | BuildWise_Wireframes_Faza3.docx |
| `Wireframes_Faza4.md` | 21 sub-ecrane (tab-uri individuale) | BuildWise_Wireframes_Faza4.docx |
| `Wireframes_Faza5.md` | 21 modale & overlay-uri | BuildWise_Wireframes_Faza5.docx |
| `Wireframes_Faza6.md` | 5 componente globale (Toast, Empty State, Skeleton, PDF Preview) | BuildWise_Wireframes_Faza6.docx |

## Flow Diagrams

| Fișier | Conținut | Sursa originală |
|--------|---------|-----------------|
| `FlowDiagrams_BuildWise.md` | Fluxuri operaționale P1 (BuildWise — energie + AI) | BuildWise_FlowDiagrams_V2.xlsx |
| `FlowDiagrams_BAHM.md` | Fluxuri operaționale P2 (BAHM — construcții) | BAHM_Op_FlowDiagrams_V2.xlsx |
| `FlowDiagrams_M2M_Lite.md` | Fluxuri operaționale P3 (M2M Lite — SaaS generic) | M2M_Lite_FlowDiagrams_V2.xlsx |

## Strategie și Context

| Fișier | Conținut | Sursa originală |
|--------|---------|-----------------|
| `Strategie_Dezvoltare.md` | Strategie completă: arhitectură, roadmap 24 luni, plan financiar CDI | BuildWise_Strategie_Dezvoltare_Produs.docx |
| `Cercetare_Piata.md` | Cercetarea de piață PoCIDIF v3: competitori, gap-uri, oportunități | BuildWise_Cercetare_Piata_PoCIDIF_v3.docx |
| `Fisa_Proiect.md` | Fișa de proiect PoCIDIF Acțiunea 2.1 | BuildWise_Fisa_Proiect_BuildWise_PoCIDIF.docx |
| `Product_Owner_Guide.md` | Ghidul Product Owner M2M ERP Lite | M2M_ERP_Lite_Product_Owner_Guide.docx |

## Context Strategic (NU pentru implementare directă)

| Fișier | Conținut | De ce e separat |
|--------|---------|-----------------|
| `context/Specificatii_TRL5.md` | 58 funcțiuni existente BAHM + mapare date→ML | Informații utile pentru TRL7, dar Centralizatorul e sursa de cod |
| `context/Functionalitati_TRL7.md` | Target TRL7: module AI, Serviciu Informare, Învățare, Monitorizare | Descrie viitorul, nu ce construim acum. NU implementa din el |
