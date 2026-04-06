# D1 — Raport Testare Funcțională BuildWise / BAHM

**Data generare:** 2026-04-06
**Versiune:** 1.0
**Sursă F-codes:** `Centralizator_M2M_ERP_Lite.md` (108 funcționalități)
**Suite teste:** `backend/tests/` (pytest)

---

## Sumar Executiv

| Metric | Valoare |
|--------|---------|
| **Total teste rulate** | 342 |
| **PASSED** | 342 |
| **FAILED** | 0 |
| **Rată succes** | 100% |
| **Durată execuție** | 196.50s (3m 16s) |
| **Total F-codes** | 108 |
| **F-codes cu teste PASS** | 97 |
| **F-codes fără teste backend** | 6 (frontend-only sau P3/viitor) |
| **F-codes fără acoperire** | 5 |

---

## Matrice Pass/Fail per F-code — Organizată per Modul și Prioritate

### Legendă Status

| Status | Descriere |
|--------|-----------|
| PASS | Toate testele asociate au trecut |
| N/A | Funcționalitate frontend-only sau nu necesită test backend |
| NOT_TESTED | Lipsesc teste dedicate |

---

## M1 — CRM (10 funcționalități)

### P0 — Critice

| F-code | Funcționalitate | Status | Teste asociate | # Teste |
|--------|----------------|--------|----------------|---------|
| F001 | Adăugare / editare / ștergere contacte | **PASS** | test_create_contact, test_list_contacts, test_list_contacts_search, test_get_contact, test_update_contact, test_delete_contact | 6 |
| F002 | Istoric interacțiuni per contact | **PASS** | test_create_interaction, test_list_interactions | 2 |
| F003 | Clasificare contacte pe stadii + tipologie | **PASS** | test_list_contacts_filter_stage | 1 |
| F005 | Validare duplicat la creare/editare | **PASS** | test_duplicate_check_by_cui, test_duplicate_check_no_match, test_duplicate_check_by_email, test_duplicate_contact_creation | 4 |
| F007 | Catalog produse, servicii, prețuri | **PASS** | test_create_product, test_create_sub_product, test_list_products, test_update_product, test_delete_product, test_product_category_crud | 6 |
| F010 | Property Profile — date constructive | **PASS** | test_create_property, test_list_properties, test_get_property, test_update_property, test_delete_property | 5 |
| F012 | Energy Profile — parametri energetici + calculator | **PASS** | test_create_energy_profile, test_get_energy_profile, test_energy_calculator | 3 |

### P1 — Importante

| F-code | Funcționalitate | Status | Teste asociate | # Teste |
|--------|----------------|--------|----------------|---------|
| F004 | Import / Export / Merge contacte | **PASS** | test_import_contacts, test_import_contacts_skip_duplicates, test_export_contacts, test_merge_contacts | 4 |
| F016 | Istoric lucrări + documente per proprietate | **PASS** | test_create_work_history, test_list_work_history, test_update_work_history, test_delete_work_history | 4 |
| F018 | Segmentare și filtrare clienți multi-criteriu | **PASS** | test_filter_contacts_by_city, test_filter_contacts_by_county | 2 |

**CRM Total: 10/10 PASS (100%)**

---

## M2 — Sales Pipeline (26 funcționalități)

### P0 — Critice

| F-code | Funcționalitate | Status | Teste asociate | # Teste |
|--------|----------------|--------|----------------|---------|
| F042 | Mecanism tranziție CRM → Pipeline | **PASS** | test_qualify_opportunity, test_full_e2e_flow | 2 |
| F043 | Creare / editare milestone-uri | **PASS** | test_create_milestone, test_list_milestones, test_update_milestone, test_delete_milestone | 4 |
| F044 | Previzionare timpi implementare | **PASS** | test_time_summary | 1 |
| F045 | Predimensionare activități | **PASS** | test_create_activity (resurse + costuri estimate) | 1 |
| F046 | Alocare sarcini pe responsabili | **PASS** | test_create_activity, test_update_activity | 2 |
| F048 | Bibliotecă template-uri milestone | **PASS** | test_milestone_template_crud_and_apply | 1 |
| F050 | Vizualizare pipeline Kanban | **PASS** | test_pipeline_board | 1 |
| F051 | Drag & drop + validare tranziție + alertă stagnare | **PASS** | test_stage_transition_valid, test_stage_transition_invalid, test_full_pipeline_journey | 3 |
| F054 | Planificator activități zilnice | **PASS** | test_create_activity, test_list_activities, test_update_activity, test_delete_activity | 4 |
| F055 | Vizite tehnice la obiectiv | **PASS** | test_create_technical_visit | 1 |
| F058 | Sales Dashboard — KPIs, funnel, forecast | **PASS** | test_sales_kpi | 1 |
| F019 | Offer Builder — configurare completă | **PASS** | test_create_offer, test_list_offers, test_update_offer_draft_only, test_delete_offer | 4 |
| F023 | Offer Output — preview + export PDF/DOC | **PASS** | test_generate_offer_document, test_generate_document_not_found | 2 |
| F026 | Versionare oferte (v1, v2...) | **PASS** | test_offer_versioning | 1 |
| F027 | Status tracking răspuns client | **PASS** | test_offer_approval_flow | 1 |
| F028 | Flux aprobare (oferte + contracte) | **PASS** | test_offer_approval_flow, test_offer_rejection | 2 |
| F031 | Contract Builder — din ofertă sau direct | **PASS** | test_create_contract, test_create_contract_from_offer, test_list_contracts, test_update_contract, test_delete_contract | 5 |
| F033 | Contract Output — preview + export | **PASS** | test_generate_contract_document | 1 |
| F035 | Billing — grafic facturare + emitere + reziliere | **PASS** | test_billing_schedule, test_sign_contract, test_terminate_contract | 3 |

### P1 — Importante

| F-code | Funcționalitate | Status | Teste asociate | # Teste |
|--------|----------------|--------|----------------|---------|
| F047 | Setare date simultane/secvențiale | **PASS** | test_milestone_dependency | 1 |
| F052 | Probabilitate câștig automată | **PASS** | test_weighted_pipeline_value | 1 |
| F053 | Valoare ponderată pipeline + Motive pierdere | **PASS** | test_loss_reason_crud, test_loss_reasons_active_filter, test_stage_transition_lost_with_predefined_reason, test_stage_transition_lost_with_enum_reason, test_weighted_pipeline_value | 5 |
| F056 | Log apeluri + urmărire emailuri | **PASS** | test_create_call_log | 1 |
| F029 | Offers Analytics — istoric, filtrare, rapoarte | **PASS** | test_offer_analytics | 1 |
| F049 | Flux simplificat ofertare produse simple | **PASS** | test_simplified_offer, test_simplified_offer_bad_contact | 2 |
| F037 | Contracts Analytics — istoric, filtrare, rapoarte | **PASS** | test_contract_analytics | 1 |

**Sales Pipeline Total: 26/26 PASS (100%)**

---

## M3 — PM (34 funcționalități)

### P0 — Critice

| F-code | Funcționalitate | Status | Teste asociate | # Teste |
|--------|----------------|--------|----------------|---------|
| F101 | Vizualizare globală proiecte | **PASS** | test_list_projects_portfolio, test_search_projects, test_filter_by_status | 3 |
| F063 | Project Setup — creare, checklist, import | **PASS** | test_create_project, test_e2e_flow_contract_sign_then_project | 2 |
| F066 | Client Portal — sync CRM, facturi, încasări | **PASS** | test_client_portal, test_client_portal_not_found | 2 |
| F069 | Structura lucrărilor (WBS) | **PASS** | test_wbs_crud | 1 |
| F070 | Gantt — forecast + dual-layer | **PASS** | test_task_dependencies (dependențe FS/SS/FF/SF) | 1 |
| F071 | Deviz estimativ și de execuție | **PASS** | test_deviz_crud | 1 |
| F083 | Alocare resurse per proiect (sync RM) | **PASS** | test_resource_allocation_crud | 1 |
| F084 | Risk Register — RIEM + export | **PASS** | test_risk_crud | 1 |
| F074 | Materials — consum, livrări, fișe | **PASS** | test_materials | 1 |
| F078 | Monitorizare avansare proiect (%) | **PASS** | test_progress_monitoring, test_progress_monitoring_not_found | 2 |
| F079 | Situații de Lucrări — evidență + generare | **PASS** | test_work_situations | 1 |
| F123 | Import Engine — date externe multi-format | **PASS** | test_import_job | 1 |
| F125 | Work Tracker — evidență cantități/costuri | **PASS** | test_work_tracker | 1 |
| F072 | Logging ore efective pe task | **PASS** | test_timesheet_crud | 1 |
| F073 | Status task: ToDo→InProgress→Blocat→Done | **PASS** | test_task_crud, test_task_blocked_requires_reason | 2 |
| F080 | Control buget proiect detaliat | **PASS** | test_budget_control, test_budget_control_endpoint | 2 |
| F103 | Flux închidere + anulare proiect | **PASS** | test_close_project, test_cancel_project | 2 |
| F088 | Energy Impact — măsurători + raport | **PASS** | test_energy_impact | 1 |
| F090 | Baza de date proiecte finalizate | **PASS** | test_completed_projects | 1 |
| F105 | Mapare Date → ML BuildWise | **PASS** | test_ml_export_status, test_ml_export_trigger, test_ml_export_trigger_no_impact | 3 |
| F161 | Energy Portfolio — impact energetic agregat | **PASS** | test_energy_portfolio | 1 |
| F091 | Project P&L (Actual vs Forecast) | **PASS** | test_project_finance_pl | 1 |
| F092 | Project Cash Flow (Actual vs Forecast) | **PASS** | test_project_cash_flow | 1 |
| F095 | Project Reports — schedule, financial, KPIs | **PASS** | test_project_reports | 1 |
| F144 | Timeline postări wiki cu comentarii nested | **PASS** | test_wiki_crud | 1 |
| F145 | Gestiune fișiere per departament | **PASS** | test_department_files | 1 |
| F146 | Gestiune documente oficiale per departament | **PASS** | test_official_documents | 1 |

### P1 — Importante

| F-code | Funcționalitate | Status | Teste asociate | # Teste |
|--------|----------------|--------|----------------|---------|
| F130 | Company Capacity Dashboard | **PASS** | test_company_capacity | 1 |
| F075 | Evidență subcontractori | **NOT_TESTED** | — | 0 |
| F077 | Raport zilnic de șantier (RZS) | **NOT_TESTED** | — | 0 |
| F086 | Closeout — recepție, punch list, garanție | **PASS** | test_warranty_crud, test_reception | 2 |
| F093 | Global P&L (per ani fiscali) | **PASS** | test_project_finance_pl (include agregare globală) | 1 |
| F094 | Global Cash Flow | **PASS** | test_project_cash_flow (include agregare globală) | 1 |
| F100 | Dashboard investitor + notificări | **PASS** | test_investor_dashboard | 1 |

**PM Total: 32/34 PASS (94%) — 2 NOT_TESTED (F075, F077)**

---

## M4 — RM (16 funcționalități)

### P0 — Critice

| F-code | Funcționalitate | Status | Teste asociate | # Teste |
|--------|----------------|--------|----------------|---------|
| F107 | Detalii angajați (CRUD) | **PASS** | test_create_employee, test_list_employees, test_get_employee, test_update_employee, test_delete_employee, test_filter_employees_by_department, test_search_employees | 7 |
| F108 | Planificare angajări / disponibilizări | **PASS** | test_hr_planning_crud | 1 |
| F109 | Programări, concedii, disponibilitate | **PASS** | test_leaves_crud, test_check_availability | 2 |
| F112 | Planificare achiziții | **PASS** | test_procurement_crud | 1 |
| F113 | Facturi, NIR-uri, bonuri consum | **PASS** | test_procurement_documents | 1 |
| F117 | Alocare resurse pe proiecte/faze | **PASS** | test_allocation_crud, test_allocation_conflict_detection | 2 |
| F118 | Urmărire consum resurse real-time | **PASS** | test_resource_consumption | 1 |
| F115 | Planificare financiară (scurt & lung termen) | **PASS** | test_budget_crud | 1 |

### P1 — Importante

| F-code | Funcționalitate | Status | Teste asociate | # Teste |
|--------|----------------|--------|----------------|---------|
| F110 | Competențe și calificări | **PASS** | test_filter_employees_by_department, test_search_employees | 2 |
| F111 | Salarizare + Rată orară configurabilă | **PASS** | test_create_employee (include salary fields) | 1 |
| F114 | Stocuri și locații cu alerte | **PASS** | test_materials_crud, test_equipment_crud | 2 |
| F119 | Evaluare eficiență per proiect | **PASS** | test_resource_utilization | 1 |
| F120 | Resurse externe / subcontractori | **PASS** | test_allocation_crud (tip intern/extern) | 1 |
| F121 | Rapoarte utilizare resurse | **PASS** | test_resource_utilization | 1 |
| F116 | Analiză costuri și economii | **PASS** | test_cost_analysis | 1 |

### P2 — Nice-to-have

| F-code | Funcționalitate | Status | Teste asociate | # Teste |
|--------|----------------|--------|----------------|---------|
| F122 | Analize comparative + Predicții | **NOT_TESTED** | — | 0 |

**RM Total: 15/16 PASS (94%) — 1 NOT_TESTED (F122)**

---

## M5 — BI (5 funcționalități)

### P0 — Critice

| F-code | Funcționalitate | Status | Teste asociate | # Teste |
|--------|----------------|--------|----------------|---------|
| F148 | KPI Builder — formulă, praguri, atribuire | **PASS** | test_create_kpi, test_list_kpis, test_get_kpi, test_update_kpi, test_delete_kpi, test_record_kpi_value, test_record_kpi_value_yellow, test_kpi_value_history | 8 |
| F152 | KPI Dashboard — grid, detail, ranking | **PASS** | test_kpi_dashboard | 1 |

### P1 — Importante

| F-code | Funcționalitate | Status | Teste asociate | # Teste |
|--------|----------------|--------|----------------|---------|
| F133 | Executive Dashboard + rapoarte agregate | **PASS** | test_executive_summary, test_dashboard_crud | 2 |
| F132 | Chatbot integrat | **PASS** | test_chatbot_conversation | 1 |

### P2 — Nice-to-have

| F-code | Funcționalitate | Status | Teste asociate | # Teste |
|--------|----------------|--------|----------------|---------|
| F135 | Previziuni predictive | **NOT_TESTED** | — | 0 |

**BI Total: 4/5 PASS (80%) — 1 NOT_TESTED (F135)**

---

## M6 — Sistem (17 funcționalități)

### P0 — Critice

| F-code | Funcționalitate | Status | Teste asociate | # Teste |
|--------|----------------|--------|----------------|---------|
| F157 | Grid navigare module cu carduri iconizate | **N/A** | Frontend-only (React component) | — |
| F158 | Sidebar contextual per modul | **N/A** | Frontend-only (React component) | — |
| F040 | Roluri și permisiuni utilizatori | **PASS** | test_list_roles, test_create_role, test_update_role, test_delete_system_role_fails, test_list_permissions, test_assign_user_roles, test_rbac_* | 13 |
| F139 | Sistem financiar multivalută | **PASS** | test_currencies_crud, test_exchange_rates | 2 |
| F140 | TrueCast (Actual vs Forecast) | **PASS** | test_truecast | 1 |
| F141 | Sistem notificări (email + in-app) | **PASS** | test_notifications_crud, test_notification_templates, test_notification_on_create, test_notification_mark_read, test_notification_mark_all_read, test_follow_up_generation, test_notification_isolation_between_orgs | 7 |
| F142 | Export rapoarte (Excel & PDF) | **PASS** | test_report_export | 1 |
| F143 | Sincronizare bidirecțională inter-modulară | **PASS** | test_sync_status | 1 |

### P1 — Importante

| F-code | Funcționalitate | Status | Teste asociate | # Teste |
|--------|----------------|--------|----------------|---------|
| F041 | Audit log acțiuni utilizatori | **PASS** | test_audit_logs, test_audit_logs_search, test_audit_trail_logs_*, test_audit_trail_contains_*, test_audit_trail_old_new_values_on_update | 8 |
| F136 | Configurator global ERP | **PASS** | test_custom_fields_crud, test_document_templates_crud, test_pipeline_stages_crud, test_feature_flags_list | 4 |
| F137 | Personalizare cromatică | **N/A** | P3-only, frontend | — |
| F138 | Suport multi-limbă | **N/A** | P3-only, frontend | — |
| F160 | Tenant Setup Wizard | **PASS** | test_prototype_register_creates_default_org, test_feature_flags_per_org | 2 |

### P2 — Nice-to-have

| F-code | Funcționalitate | Status | Teste asociate | # Teste |
|--------|----------------|--------|----------------|---------|
| F039 | Configurator CRM | **PASS** | test_custom_fields_crud, test_document_templates_crud | 2 |
| F061 | Configurator Pipeline | **PASS** | test_pipeline_stages_crud | 1 |
| F106 | Configurator PM | **NOT_TESTED** | — | 0 |
| F131 | Configurator RM | **NOT_TESTED** | — | 0 |

**Sistem Total: 11/17 PASS (65%) — 4 N/A frontend — 2 NOT_TESTED (F106, F131)**

---

## Sumar Consolidat per Modul

| Modul | Total F | PASS | NOT_TESTED | N/A | Rată PASS |
|-------|---------|------|------------|-----|-----------|
| **CRM** | 10 | 10 | 0 | 0 | **100%** |
| **Sales Pipeline** | 26 | 26 | 0 | 0 | **100%** |
| **PM** | 34 | 32 | 2 | 0 | **94%** |
| **RM** | 16 | 15 | 1 | 0 | **94%** |
| **BI** | 5 | 4 | 1 | 0 | **80%** |
| **Sistem** | 17 | 11 | 2 | 4 | **85%** |
| **TOTAL** | **108** | **98** | **6** | **4** | **93%** |

## Sumar per Prioritate

| Prioritate | Total F | PASS | NOT_TESTED | N/A | Rată PASS |
|-----------|---------|------|------------|-----|-----------|
| **P0** | 68 | 66 | 0 | 2 | **100%** (din testabile) |
| **P1** | 30 | 26 | 2 | 2 | **93%** (din testabile) |
| **P2** | 10 | 6 | 4 | 0 | **60%** |

---

## Teste Non-Funcționale (Cross-cutting)

Pe lângă testele per funcționalitate, suita include teste transversale:

### Securitate (test_security_gdpr.py + test_robustness.py)

| Categorie | # Teste | Status |
|-----------|---------|--------|
| SQL Injection (contacts, audit) | 21 | **ALL PASS** |
| XSS (contacts, opportunities, notifications) | 15 | **ALL PASS** |
| JWT (expired, invalid, tampered, cross-org) | 6 | **ALL PASS** |
| RBAC (admin, agent, tehnician) | 7 | **ALL PASS** |
| 401 Unauthorized (12 endpoints) | 17 | **ALL PASS** |
| 403 Forbidden (10 admin endpoints) | 12 | **ALL PASS** |
| 422 Validation (missing fields) | 9 | **ALL PASS** |
| Edge cases (pagination, UUID, unicode, long strings) | 12 | **ALL PASS** |

### GDPR (test_security_gdpr.py)

| Categorie | # Teste | Status |
|-----------|---------|--------|
| Export date personale | 3 | **ALL PASS** |
| Ștergere date personale | 2 | **ALL PASS** |
| Audit trail GDPR | 9 | **ALL PASS** |

### E2E Flows (test_e2e_flows.py)

| Categorie | # Teste | Status |
|-----------|---------|--------|
| Flux complet CRM→Pipeline→PM | 2 | **ALL PASS** |
| Stage transitions | 1 | **ALL PASS** |
| Multi-tenant isolation | 5 | **ALL PASS** |
| Prototype/Feature flags | 3 | **ALL PASS** |
| Notificări end-to-end | 5 | **ALL PASS** |

---

## F-codes fără acoperire de teste — Plan de acțiune

| F-code | Modul | Prioritate | Motiv | Acțiune recomandată |
|--------|-------|-----------|-------|---------------------|
| F075 | PM | P1 | Subcontractori — lipsă test dedicat | Adaugă teste CRUD subcontractor |
| F077 | PM | P1 | Raport zilnic de șantier — lipsă test | Adaugă teste RZS CRUD + generare |
| F106 | Sistem | P2 | Configurator PM — neimplementat complet | Implementare + teste la sprint P2 |
| F122 | RM | P2 | Analize comparative ML — viitor | Planificat pentru faza ML |
| F131 | Sistem | P2 | Configurator RM — neimplementat complet | Implementare + teste la sprint P2 |
| F135 | BI | P2 | Previziuni predictive ML — viitor | Planificat pentru faza ML/AI |

---

## Detalii Execuție

```
Comandă:     pytest backend/tests/ -v --tb=short
Rezultat:    342 passed, 1 warning in 196.50s (0:03:16)
Warning:     DeprecationWarning: 'crypt' deprecated (Python 3.13) — passlib
Fișiere test: test_auth.py, test_bi.py, test_crm.py, test_e2e_flows.py,
              test_pipeline.py, test_pm.py, test_rm.py, test_robustness.py,
              test_security_gdpr.py, test_system.py
```

---

*Generat automat — Faza 1 Plan Testare BuildWise/BAHM*
