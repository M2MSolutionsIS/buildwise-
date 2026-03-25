export type Prototype = "P1" | "P2" | "P3";

export interface ApiResponse<T> {
  data: T;
  meta: {
    total: number;
    page: number;
    per_page: number;
  };
}

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  phone?: string;
  avatar_url?: string;
  is_active: boolean;
  is_superuser: boolean;
  organization_id: string;
  language?: string;
  last_login?: string;
  created_at: string;
  roles: string[];
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

// ─── Organization / Multi-Tenant Types (F160, F136, F137, F040) ──────────────

export interface Organization {
  id: string;
  name: string;
  slug: string;
  logo_url?: string;
  primary_color?: string;
  secondary_color?: string;
  custom_branding?: Record<string, unknown>;
  default_language: string;
  supported_languages: string[];
  default_currency: string;
  reference_currency?: string;
  modules_enabled: string[];
  setup_completed: boolean;
  active_prototype: Prototype;
  is_p1: boolean;
  is_p2: boolean;
  is_p3: boolean;
  created_at: string;
  updated_at?: string;
}

export interface TenantSetupPayload {
  company: {
    name: string;
    slug?: string;
    logo_url?: string;
    address?: string;
    cui?: string;
    phone?: string;
    email?: string;
  };
  branding: {
    primary_color: string;
    secondary_color: string;
    default_language: string;
    default_currency: string;
  };
  modules: string[];
  users: {
    email: string;
    first_name: string;
    last_name: string;
    role: string;
  }[];
}

export interface FeatureFlag {
  id: string;
  f_code: string;
  organization_id: string;
  is_enabled: boolean;
  is_p1: boolean;
  is_p2: boolean;
  is_p3: boolean;
  config?: Record<string, unknown>;
}

export interface SystemRole {
  id: string;
  organization_id: string;
  name: string;
  code: string;
  description?: string;
  is_system: boolean;
  permissions?: string[];
  created_at: string;
}

// ─── BI Types — KPI Engine (F148, F152) ──────────────────────────────────────

export interface KPIThreshold {
  min: number;
  max: number;
  color: "red" | "yellow" | "green";
  label: string;
}

export interface KPIDefinition {
  id: string;
  organization_id: string;
  name: string;
  code: string;
  description?: string;
  module: string;
  formula?: Record<string, unknown>;
  formula_text?: string;
  unit?: string;
  thresholds?: KPIThreshold[];
  display_type: "gauge" | "card" | "chart";
  drill_down_config?: Record<string, unknown>;
  assigned_roles?: string[];
  assigned_users?: string[];
  is_active: boolean;
  sort_order: number;
  created_at: string;
  updated_at?: string;
}

export interface KPIValue {
  id: string;
  kpi_definition_id: string;
  value: number;
  threshold_color: "red" | "yellow" | "green";
  computed_at: string;
  period_start?: string;
  period_end?: string;
  project_id?: string;
  user_id?: string;
}

export interface KPIDashboardItem {
  kpi_id: string;
  name: string;
  code: string;
  unit?: string;
  display_type: string;
  current_value: number | null;
  threshold_color: string | null;
  trend: number[];
  module: string;
}

// ─── BI Types — Dashboards (F133) ────────────────────────────────────────────

export type WidgetType = "kpi_card" | "chart" | "table" | "gauge" | "funnel" | "map" | "custom";

export interface DashboardWidget {
  id: string;
  dashboard_id: string;
  widget_type: WidgetType;
  title: string;
  config?: Record<string, unknown>;
  data_source?: Record<string, unknown>;
  position_x: number;
  position_y: number;
  width: number;
  height: number;
  sort_order: number;
  kpi_definition_id?: string;
}

export interface Dashboard {
  id: string;
  organization_id: string;
  name: string;
  description?: string;
  dashboard_type: string;
  is_default: boolean;
  is_template: boolean;
  layout_config?: Record<string, unknown>;
  visible_roles?: string[];
  widgets?: DashboardWidget[];
  created_at: string;
  updated_at?: string;
}

export interface ExecutiveSummary {
  crm: { total_contacts: number; active_contacts: number; leads: number; clients: number };
  pipeline: { total_opportunities: number; open_opportunities: number; total_pipeline_value: number; weighted_value: number; win_rate: number; currency: string };
  pm: { total_projects: number; active_projects: number; completed_projects: number; avg_progress: number };
  rm: { total_employees: number; active_employees: number; total_equipment: number; active_allocations: number };
  kpis: { total_kpis: number; green: number; yellow: number; red: number };
}

// ─── BI Types — Reports Builder (E-041) ──────────────────────────────────────

export interface ReportColumn {
  field: string;
  label: string;
  type: "text" | "number" | "date" | "currency";
  aggregate?: "sum" | "avg" | "count" | "min" | "max";
  width?: number;
}

export interface ReportFilter {
  field: string;
  operator: "equals" | "contains" | "greater_than" | "less_than" | "between" | "in";
  value: unknown;
}

export interface ReportDefinition {
  id: string;
  organization_id: string;
  name: string;
  description?: string;
  report_type: "schedule" | "financial" | "kpi" | "custom";
  module: string;
  query_config?: Record<string, unknown>;
  columns_config?: ReportColumn[];
  filters_config?: ReportFilter[];
  grouping_config?: Record<string, unknown>;
  chart_config?: Record<string, unknown>;
  is_scheduled: boolean;
  schedule_cron?: string;
  recipients?: string[];
  is_template: boolean;
  created_at: string;
  updated_at?: string;
}

// ─── AI / ML Types (F132, F135) ──────────────────────────────────────────────

export interface AIMessage {
  id: string;
  conversation_id: string;
  role: "user" | "assistant";
  content: string;
  cards?: AIResponseCard[];
  created_at: string;
}

export interface AIConversation {
  id: string;
  organization_id: string;
  user_id: string;
  title?: string;
  context?: Record<string, unknown>;
  messages?: AIMessage[];
  created_at: string;
  updated_at?: string;
}

export interface AIResponseCard {
  type: "kpi" | "chart" | "table" | "text" | "suggestion";
  title?: string;
  data: Record<string, unknown>;
}

export interface MLModelConfig {
  id: string;
  organization_id: string;
  name: string;
  model_type: string;
  data_sources?: Record<string, unknown>;
  status: "configured" | "training" | "ready" | "error";
  last_trained_at?: string;
  error_metric?: number;
  parameters?: Record<string, unknown>;
  created_at: string;
}

export interface MLForecastResult {
  period: string;
  predicted_value: number;
  confidence_lower: number;
  confidence_upper: number;
  actual_value?: number;
}

// CRM Types
export interface ContactPerson {
  id: string;
  contact_id: string;
  first_name: string;
  last_name: string;
  role: string;
  email?: string;
  phone?: string;
  is_primary: boolean;
  created_at: string;
}

export interface Contact {
  id: string;
  company_name: string;
  cui?: string;
  registration_number?: string;
  stage: string;
  contact_type: string;
  address?: string;
  city?: string;
  county?: string;
  postal_code?: string;
  country?: string;
  phone?: string;
  email?: string;
  website?: string;
  vat_payer?: boolean;
  bank_account?: string;
  bank_name?: string;
  gdpr_consent?: boolean;
  tags?: string[];
  source?: string;
  notes?: string;
  persons: ContactPerson[];
  created_by?: string;
  updated_by?: string;
  created_at: string;
  updated_at: string;
}

export interface ContactListItem {
  id: string;
  company_name: string;
  cui?: string;
  stage: string;
  contact_type: string;
  city?: string;
  county?: string;
  phone?: string;
  email?: string;
  created_at: string;
}

export interface ContactCreate {
  company_name: string;
  cui?: string;
  registration_number?: string;
  stage?: string;
  contact_type?: string;
  address?: string;
  city?: string;
  county?: string;
  postal_code?: string;
  country?: string;
  phone?: string;
  email?: string;
  website?: string;
  vat_payer?: boolean;
  bank_account?: string;
  bank_name?: string;
  gdpr_consent?: boolean;
  tags?: string[];
  source?: string;
  notes?: string;
  persons?: Omit<ContactPerson, "id" | "contact_id" | "created_at">[];
}

export interface Interaction {
  id: string;
  contact_id: string;
  user_id: string;
  interaction_type: string;
  subject: string;
  description?: string;
  interaction_date: string;
  duration_minutes?: number;
  opportunity_id?: string;
  offer_id?: string;
  contract_id?: string;
  metadata_json?: Record<string, unknown>;
  created_at: string;
}

export interface Property {
  id: string;
  contact_id: string;
  name: string;
  property_type: string;
  address?: string;
  city?: string;
  county?: string;
  country?: string;
  total_area_sqm?: number;
  heated_area_sqm?: number;
  floors_count?: number;
  year_built?: number;
  year_renovated?: number;
  structure_material?: string;
  facade_material?: string;
  roof_type?: string;
  energy_certificate?: string;
  energy_class?: string;
  custom_data?: Record<string, unknown>;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface DuplicateMatch {
  contact_id: string;
  company_name: string;
  cui?: string;
  email?: string;
  score: number;
}

export interface DuplicateCheckResponse {
  has_duplicates: boolean;
  matches: DuplicateMatch[];
}

// ─── Pipeline Stage Config (F061) ───────────────────────────────────────────

export interface PipelineStageConfig {
  id: string;
  organization_id: string;
  name: string;
  code: string;
  sort_order: number;
  color?: string;
  win_probability?: number;
  stagnation_days?: number;
  required_fields?: string[];
  auto_advance_rules?: {
    field: string;
    operator: "equals" | "greater_than" | "not_empty" | "contains";
    value: string;
    target_stage_code: string;
  }[];
  is_active: boolean;
  is_closed_won: boolean;
  is_closed_lost: boolean;
  created_at: string;
  updated_at?: string;
}

// ─── RM Configurator Types (F131) ───────────────────────────────────────────

export interface RMResourceCategory {
  id: string;
  organization_id: string;
  name: string;
  code: string;
  resource_type: "employee" | "equipment" | "material";
  description?: string;
  default_unit?: string;
  is_active: boolean;
  sort_order: number;
  created_at: string;
}

export interface RMUnitOfMeasure {
  id: string;
  organization_id: string;
  name: string;
  code: string;
  category: "time" | "quantity" | "weight" | "volume" | "area" | "length";
  is_active: boolean;
  sort_order: number;
}

export interface RMAlertThreshold {
  id: string;
  organization_id: string;
  metric: string;
  threshold_type: "min" | "max" | "range";
  warning_value: number;
  critical_value: number;
  is_active: boolean;
  applies_to: "employee" | "equipment" | "material" | "all";
  notification_enabled: boolean;
}

export interface RMConfig {
  categories: RMResourceCategory[];
  units: RMUnitOfMeasure[];
  thresholds: RMAlertThreshold[];
}

// Pipeline Types — Offers (F019, F023, F026, F027, F028, F029, F049)

export type OfferStatus =
  | "DRAFT"
  | "PENDING_APPROVAL"
  | "APPROVED"
  | "SENT"
  | "NEGOTIATION"
  | "ACCEPTED"
  | "REJECTED"
  | "EXPIRED";

export interface OfferLineItem {
  id: string;
  offer_id: string;
  product_id?: string;
  description: string;
  quantity: number;
  unit_of_measure: string;
  unit_price: number;
  discount_percent: number;
  vat_rate: number;
  total_price: number;
  sort_order: number;
}

export interface OfferLineItemCreate {
  product_id?: string;
  description: string;
  quantity: number;
  unit_of_measure: string;
  unit_price: number;
  discount_percent?: number;
  vat_rate?: number;
  sort_order?: number;
}

export interface Offer {
  id: string;
  offer_number: string;
  title: string;
  description?: string;
  contact_id: string;
  opportunity_id?: string;
  property_id?: string;
  owner_id?: string;
  template_id?: string;
  status: OfferStatus;
  version: number;
  parent_offer_id?: string;
  is_snapshot: boolean;
  is_quick_quote: boolean;
  subtotal: number;
  discount_percent: number;
  discount_amount: number;
  vat_amount: number;
  total_amount: number;
  currency: string;
  terms_and_conditions?: string;
  validity_days: number;
  valid_until?: string;
  sent_at?: string;
  accepted_at?: string;
  rejected_at?: string;
  rejection_reason?: string;
  next_follow_up?: string;
  follow_up_count: number;
  pdf_path?: string;
  line_items: OfferLineItem[];
  created_by?: string;
  updated_by?: string;
  created_at: string;
  updated_at: string;
}

export interface OfferListItem {
  id: string;
  offer_number: string;
  title: string;
  contact_id: string;
  status: OfferStatus;
  version: number;
  subtotal: number;
  total_amount: number;
  currency: string;
  validity_days: number;
  valid_until?: string;
  is_quick_quote: boolean;
  created_at: string;
}

export interface OfferCreate {
  contact_id: string;
  opportunity_id?: string;
  property_id?: string;
  title: string;
  description?: string;
  currency?: string;
  terms_and_conditions?: string;
  validity_days?: number;
  template_id?: string;
  is_quick_quote?: boolean;
  line_items?: OfferLineItemCreate[];
}

export interface OfferUpdate {
  title?: string;
  description?: string;
  terms_and_conditions?: string;
  validity_days?: number;
  discount_percent?: number;
}

export interface OfferVersionDiff {
  field: string;
  item?: string;
  type: "added" | "deleted" | "modified";
  old_value?: unknown;
  new_value?: unknown;
}

export interface OfferAnalytics {
  total_offers: number;
  by_status: Record<string, number>;
  conversion_rate: number;
  average_value: number;
  total_value: number;
}

// ─── Pipeline Types — Opportunities (F042, F050-F053) ───────────────────────

export type OpportunityStage =
  | "new"
  | "qualified"
  | "scoping"
  | "offering"
  | "sent"
  | "negotiation"
  | "won"
  | "lost";

export interface Opportunity {
  id: string;
  contact_id: string;
  title: string;
  description?: string;
  stage: OpportunityStage;
  stage_entered_at?: string;
  estimated_value?: number;
  currency: string;
  win_probability?: number;
  weighted_value?: number;
  expected_close_date?: string;
  actual_close_date?: string;
  owner_id?: string;
  loss_reason?: string;
  loss_reason_detail?: string;
  won_reason?: string;
  qualification_checklist?: Record<string, unknown>;
  is_qualified: boolean;
  rm_validated: boolean;
  source?: string;
  tags?: string[];
  notes?: string;
  created_at: string;
  updated_at?: string;
}

export interface OpportunityListItem {
  id: string;
  title: string;
  stage: OpportunityStage;
  estimated_value?: number;
  currency: string;
  win_probability?: number;
  weighted_value?: number;
  contact_id: string;
  owner_id?: string;
  expected_close_date?: string;
  created_at: string;
}

export interface OpportunityCreate {
  contact_id: string;
  title: string;
  description?: string;
  stage?: string;
  estimated_value?: number;
  currency?: string;
  expected_close_date?: string;
  owner_id?: string;
  source?: string;
  tags?: string[];
  notes?: string;
}

export interface OpportunityUpdate {
  title?: string;
  description?: string;
  estimated_value?: number;
  currency?: string;
  expected_close_date?: string;
  owner_id?: string;
  source?: string;
  tags?: string[];
  notes?: string;
}

export interface PipelineBoardStage {
  stage: string;
  count: number;
  total_value: number;
  weighted_value: number;
  opportunities: OpportunityListItem[];
}

export interface PipelineBoard {
  stages: PipelineBoardStage[];
  total_pipeline_value: number;
  total_weighted_value: number;
  currency: string;
}

// ─── Activity Types (F054-F056) ─────────────────────────────────────────────

export interface Activity {
  id: string;
  activity_type: string;
  title: string;
  description?: string;
  status: string;
  scheduled_date: string;
  scheduled_end_date?: string;
  duration_minutes?: number;
  completed_at?: string;
  contact_id?: string;
  opportunity_id?: string;
  owner_id?: string;
  visit_data?: Record<string, unknown>;
  measurements?: Record<string, unknown>;
  call_duration_seconds?: number;
  call_outcome?: string;
  email_subject?: string;
  email_tracked: boolean;
  is_recurring: boolean;
  notes?: string;
  created_at: string;
  updated_at?: string;
}

export interface ActivityListItem {
  id: string;
  activity_type: string;
  title: string;
  status: string;
  scheduled_date: string;
  contact_id?: string;
  opportunity_id?: string;
  owner_id?: string;
  created_at: string;
}

// ─── Sales KPI / Dashboard (F058) ───────────────────────────────────────────

export interface SalesKPI {
  total_contacts: number;
  active_contacts: number;
  total_opportunities: number;
  open_opportunities: number;
  won_opportunities: number;
  lost_opportunities: number;
  pipeline_value: number;
  weighted_pipeline_value: number;
  total_offers: number;
  offers_sent: number;
  offers_accepted: number;
  offers_rejected: number;
  conversion_rate: number;
  total_contracts: number;
  active_contracts: number;
  total_revenue: number;
  total_invoiced: number;
  total_paid: number;
  avg_deal_value: number;
  currency: string;
  funnel: { stage: string; count: number; value: number }[];
}

export interface WeightedPipelineStage {
  stage: string;
  count: number;
  total_value: number;
  weighted_value: number;
  win_probability: number;
}

export interface WeightedPipeline {
  stages: WeightedPipelineStage[];
  total_pipeline_value: number;
  total_weighted_value: number;
  currency: string;
}

// ─── Pipeline Analytics (F058, E-012) ────────────────────────────────────────

export interface FunnelStage {
  stage: string;
  count: number;
  value: number;
  conversion_rate: number;
  drop_off_rate: number;
}

export interface AgentPerformance {
  agent_id: string | null;
  agent_name: string;
  total_deals: number;
  won_deals: number;
  lost_deals: number;
  open_deals: number;
  total_value: number;
  won_value: number;
  win_rate: number;
  avg_deal_value: number;
  avg_cycle_days: number;
  activities_count: number;
}

export interface ForecastMonth {
  month: string;
  confirmed_value: number;
  weighted_value: number;
  deal_count: number;
}

export interface ProductMixItem {
  category: string;
  deal_count: number;
  total_value: number;
  percentage: number;
}

export interface PipelineAnalytics {
  kpis: {
    total_opportunities: number;
    open_opportunities: number;
    won_opportunities: number;
    lost_opportunities: number;
    pipeline_value: number;
    won_value: number;
    weighted_value: number;
    win_rate: number;
    avg_deal_value: number;
    avg_cycle_days: number;
  };
  funnel: FunnelStage[];
  agent_performance: AgentPerformance[];
  forecast: ForecastMonth[];
  product_mix: ProductMixItem[];
  currency: string;
}

// ─── PM Types — Projects, Tasks, Gantt (F063, F069-F073, F083) ──────────────

export type ProjectStatus =
  | "draft" | "kickoff" | "planning" | "in_progress"
  | "on_hold" | "post_execution" | "closing" | "completed" | "cancelled";

export interface PMProject {
  id: string;
  project_number: string;
  name: string;
  description?: string;
  project_type: string;
  status: ProjectStatus;
  health_indicator?: string;
  percent_complete: number;
  planned_start_date?: string;
  planned_end_date?: string;
  actual_start_date?: string;
  actual_end_date?: string;
  budget_allocated?: number;
  budget_actual?: number;
  currency: string;
  project_manager_id?: string;
  contract_id?: string;
  contact_id?: string;
  cpi?: number;
  spi?: number;
  created_at: string;
}

export interface PMProjectListItem {
  id: string;
  project_number: string;
  name: string;
  project_type: string;
  status: ProjectStatus;
  health_indicator?: string;
  percent_complete: number;
  planned_start_date?: string;
  planned_end_date?: string;
  budget_allocated?: number;
  budget_actual?: number;
  currency: string;
  project_manager_id?: string;
  created_at: string;
}

export type TaskStatus = "todo" | "in_progress" | "blocked" | "done";

export interface PMTask {
  id: string;
  project_id: string;
  wbs_node_id?: string;
  parent_task_id?: string;
  title: string;
  description?: string;
  status: TaskStatus;
  blocked_reason?: string;
  escalated: boolean;
  planned_start?: string;
  planned_end?: string;
  planned_duration_days?: number;
  actual_start?: string;
  actual_end?: string;
  percent_complete: number;
  estimated_hours?: number;
  actual_hours?: number;
  estimated_cost?: number;
  actual_cost?: number;
  assigned_to?: string;
  is_critical_path: boolean;
  is_milestone: boolean;
  sort_order: number;
  notes?: string;
  created_at: string;
  updated_at?: string;
}

export interface TaskDependency {
  id: string;
  task_id: string;
  depends_on_id: string;
  dependency_type: "finish_to_start" | "start_to_start" | "finish_to_finish" | "start_to_finish";
  lag_days: number;
}

export interface ResourceAllocation {
  id: string;
  organization_id: string;
  resource_type: string;
  employee_id?: string;
  equipment_id?: string;
  project_id: string;
  wbs_node_id?: string;
  task_id?: string;
  start_date: string;
  end_date: string;
  allocated_hours?: number;
  actual_hours?: number;
  planned_cost?: number;
  actual_cost?: number;
  currency: string;
  status: string;
  has_conflict: boolean;
  conflict_details?: Record<string, unknown>;
  allocation_percent: number;
  created_at: string;
}

// ─── PM Types — Execution: Timesheet, Materials, Subcontractors, Daily Reports ──

export type TimesheetStatus = "draft" | "submitted" | "approved" | "rejected";

export interface TimesheetEntry {
  id: string;
  project_id: string;
  task_id?: string;
  user_id: string;
  work_date: string;
  hours: number;
  hourly_rate?: number;
  cost?: number;
  description?: string;
  status: TimesheetStatus;
  approved_by?: string;
  approved_at?: string;
  created_at: string;
  updated_at?: string;
}

export interface TimesheetCreate {
  task_id?: string;
  user_id?: string;
  work_date: string;
  hours: number;
  hourly_rate?: number;
  description?: string;
}

export interface MaterialConsumption {
  id: string;
  project_id: string;
  wbs_node_id?: string;
  deviz_item_id?: string;
  product_id?: string;
  material_name: string;
  unit_of_measure: string;
  planned_quantity: number;
  consumed_quantity: number;
  unit_price?: number;
  total_cost?: number;
  consumption_date: string;
  registered_by?: string;
  created_at: string;
  updated_at?: string;
}

export interface MaterialConsumptionCreate {
  wbs_node_id?: string;
  deviz_item_id?: string;
  product_id?: string;
  material_name: string;
  unit_of_measure: string;
  planned_quantity: number;
  consumed_quantity: number;
  unit_price?: number;
  consumption_date: string;
}

export interface PMSubcontractor {
  id: string;
  project_id: string;
  contact_id?: string;
  company_name: string;
  contract_number?: string;
  contract_value?: number;
  currency: string;
  scope_description?: string;
  start_date?: string;
  end_date?: string;
  percent_complete: number;
  invoiced_amount: number;
  paid_amount: number;
  notes?: string;
  created_at: string;
  updated_at?: string;
}

export interface PMSubcontractorCreate {
  contact_id?: string;
  company_name: string;
  contract_number?: string;
  contract_value?: number;
  currency?: string;
  scope_description?: string;
  start_date?: string;
  end_date?: string;
  notes?: string;
}

export interface DailyReport {
  id: string;
  project_id: string;
  report_date: string;
  weather?: string;
  temperature_min?: number;
  temperature_max?: number;
  activities_summary?: string;
  personnel_present?: PersonnelEntry[];
  equipment_used?: EquipmentEntry[];
  materials_received?: MaterialDelivery[];
  observations?: string;
  issues?: string;
  photos?: string[];
  reported_by?: string;
  created_at: string;
  updated_at?: string;
}

export interface PersonnelEntry {
  name: string;
  role: string;
  hours: number;
}

export interface EquipmentEntry {
  name: string;
  hours: number;
  notes?: string;
}

export interface MaterialDelivery {
  material_name: string;
  quantity: number;
  unit_of_measure: string;
  supplier?: string;
  delivery_note?: string;
  date?: string;
}

export interface DailyReportCreate {
  report_date: string;
  weather?: string;
  temperature_min?: number;
  temperature_max?: number;
  activities_summary?: string;
  personnel_present?: PersonnelEntry[];
  equipment_used?: EquipmentEntry[];
  materials_received?: MaterialDelivery[];
  observations?: string;
  issues?: string;
}

// ─── PM Types — Monitoring: EVM, Work Situations, Risks (F078-F084) ─────────

export interface WorkSituation {
  id: string;
  project_id: string;
  period_month: number;
  period_year: number;
  sdl_number: string;
  contracted_total: number;
  executed_current: number;
  executed_cumulated: number;
  remaining: number;
  currency: string;
  is_approved: boolean;
  approved_by?: string;
  approved_at?: string;
  is_invoiced: boolean;
  line_items?: WorkSituationLineItem[];
  pdf_path?: string;
  created_at: string;
  updated_at?: string;
}

export interface WorkSituationLineItem {
  description: string;
  unit_of_measure: string;
  contracted_qty: number;
  contracted_price: number;
  executed_current_qty: number;
  executed_cumulated_qty: number;
  remaining_qty: number;
  total_value: number;
}

export interface WorkSituationCreate {
  period_month: number;
  period_year: number;
  sdl_number: string;
  contracted_total: number;
  executed_current: number;
  executed_cumulated: number;
  remaining: number;
  currency?: string;
  line_items?: WorkSituationLineItem[];
}

export type RiskProbability = "very_low" | "low" | "medium" | "high" | "very_high";
export type RiskImpact = "negligible" | "minor" | "moderate" | "major" | "critical";
export type RiskStatus = "identified" | "assessed" | "mitigating" | "resolved" | "accepted";

export interface PMRisk {
  id: string;
  project_id: string;
  title: string;
  description?: string;
  category?: string;
  probability: RiskProbability;
  impact: RiskImpact;
  risk_score?: number;
  status: RiskStatus;
  mitigation_plan?: string;
  contingency_plan?: string;
  owner_id?: string;
  identified_date?: string;
  review_date?: string;
  notes?: string;
  created_at: string;
  updated_at?: string;
}

export interface PMRiskCreate {
  title: string;
  description?: string;
  category?: string;
  probability: RiskProbability;
  impact: RiskImpact;
  status?: RiskStatus;
  mitigation_plan?: string;
  contingency_plan?: string;
  owner_id?: string;
  identified_date?: string;
  review_date?: string;
  notes?: string;
}

export interface ProjectFinanceEntry {
  id: string;
  project_id: string;
  entry_type: string;
  category: string;
  subcategory?: string;
  period_month: number;
  period_year: number;
  forecast_amount: number;
  actual_amount: number;
  variance: number;
  currency: string;
  source_entity_type?: string;
  source_entity_id?: string;
  created_at: string;
}

export interface ProjectCashFlowEntry {
  id: string;
  project_id: string;
  entry_type: string;
  description?: string;
  amount: number;
  currency: string;
  transaction_date: string;
  invoice_id?: string;
  source_entity_type?: string;
  source_entity_id?: string;
  created_at: string;
}

export interface ProgressMonitoring {
  project_id: string;
  project_name: string;
  percent_complete: number;
  planned_progress: number;
  schedule_variance: number;
  status: string;
  health_indicator: string;
  cpi: number;
  spi: number;
  tasks_summary: {
    total: number;
    done: number;
    in_progress: number;
    blocked: number;
    todo: number;
  };
  delay_alerts: { task_title: string; days_delayed: number }[];
  milestones: { title: string; planned_date: string; actual_date?: string; status: string }[];
  s_curve_data: SCurveDataPoint[];
}

export interface SCurveDataPoint {
  date: string;
  planned_percent: number;
  actual_percent: number;
  earned_value?: number;
}

export interface BudgetControl {
  project_id: string;
  budget_allocated: number;
  budget_committed: number;
  budget_actual: number;
  currency: string;
  cpi: number;
  spi: number;
  eac: number;
  etc: number;
  vac: number;
  ev: number;
  pv: number;
  ac: number;
  sv: number;
  cv: number;
  by_category: BudgetCategory[];
  alerts: string[];
}

export interface BudgetCategory {
  category: string;
  allocated: number;
  committed: number;
  actual: number;
  variance: number;
  variance_pct: number;
}

// ─── PM Types — Reception, Warranty, Energy Impact (F081, F082, F086, F088) ──

export type PunchItemSeverity = "low" | "medium" | "high" | "critical";
export type PunchItemStatus = "open" | "in_progress" | "resolved" | "verified";

export interface PunchItem {
  id: string;
  project_id: string;
  title: string;
  description?: string;
  severity: PunchItemSeverity;
  status: PunchItemStatus;
  responsible_id?: string;
  due_date?: string;
  resolved_at?: string;
  photos?: string[];
  location?: string;
  created_at: string;
  updated_at?: string;
}

export interface PunchItemCreate {
  title: string;
  description?: string;
  severity?: PunchItemSeverity;
  responsible_id?: string;
  due_date?: string;
  location?: string;
}

export interface PMWarranty {
  id: string;
  project_id: string;
  description: string;
  start_date: string;
  end_date: string;
  responsible_id?: string;
  alert_before_days: number;
  is_active: boolean;
  interventions?: WarrantyIntervention[];
  created_at: string;
  updated_at?: string;
}

export interface WarrantyIntervention {
  date: string;
  description: string;
  performed_by?: string;
  cost?: number;
}

export interface PMWarrantyCreate {
  description: string;
  start_date: string;
  end_date: string;
  responsible_id?: string;
  alert_before_days?: number;
}

export interface EnergyImpact {
  id: string;
  project_id: string;
  property_id?: string;
  pre_kwh_annual?: number;
  pre_gas_mc_annual?: number;
  pre_co2_kg_annual?: number;
  pre_u_value_avg?: number;
  post_kwh_annual?: number;
  post_gas_mc_annual?: number;
  post_co2_kg_annual?: number;
  post_u_value_avg?: number;
  estimated_kwh_savings?: number;
  estimated_co2_reduction?: number;
  actual_kwh_savings?: number;
  actual_co2_reduction?: number;
  total_area_sqm?: number;
  treated_area_sqm?: number;
  materials_summary?: Record<string, unknown>;
  total_project_cost?: number;
  duration_days?: number;
  is_verified: boolean;
  verified_by?: string;
  verified_at?: string;
  created_at: string;
  updated_at?: string;
}

export interface EnergyImpactCreate {
  property_id?: string;
  pre_kwh_annual?: number;
  pre_gas_mc_annual?: number;
  pre_co2_kg_annual?: number;
  pre_u_value_avg?: number;
  post_kwh_annual?: number;
  post_gas_mc_annual?: number;
  post_co2_kg_annual?: number;
  post_u_value_avg?: number;
  estimated_kwh_savings?: number;
  estimated_co2_reduction?: number;
  actual_kwh_savings?: number;
  actual_co2_reduction?: number;
  total_area_sqm?: number;
  treated_area_sqm?: number;
  total_project_cost?: number;
  duration_days?: number;
}

// ─── PM Types — Project Reports, Archive, Energy Portfolio (F090, F091, F095, F142, F161) ──

export interface ProjectReport {
  project_id: string;
  project_name: string;
  status: string;
  percent_complete: number;
  planned_start?: string;
  planned_end?: string;
  actual_start?: string;
  actual_end?: string;
  budget_allocated?: number;
  budget_actual?: number;
  budget_variance?: number;
  cpi?: number;
  spi?: number;
  total_tasks: number;
  completed_tasks: number;
  open_risks: number;
  open_punch_items: number;
}

export interface EnergyPortfolio {
  total_kwh_saved: number;
  total_co2_reduced: number;
  total_projects: number;
  total_area_treated_sqm: number;
  avg_u_value_pre?: number;
  avg_u_value_post?: number;
}

// ─── PM Types — Import Engine (E-037, F123) ──────────────────────────────────

export type ImportSourceType = "intersoft" | "edevize" | "csv" | "excel";
export type ImportJobStatus = "pending" | "mapping" | "importing" | "completed" | "error";

export interface ImportJob {
  id: string;
  project_id: string;
  source_type: ImportSourceType;
  file_name: string;
  status: ImportJobStatus;
  mapping_config?: Record<string, unknown>;
  preview_data?: ImportPreviewItem[];
  error_log?: ImportError[];
  records_imported: number;
  records_total: number;
  completed_at?: string;
  created_at: string;
  updated_at?: string;
}

export interface ImportPreviewItem {
  row_index: number;
  code?: string;
  description: string;
  unit_of_measure: string;
  quantity: number;
  unit_price: number;
  total: number;
  is_valid: boolean;
  errors?: ImportError[];
  wbs_node_id?: string;
  wbs_node_name?: string;
  match_score?: number;
  duplicate_action?: "overwrite" | "sum" | "exclude";
  is_duplicate?: boolean;
}

export interface ImportError {
  row?: number;
  col?: string;
  message: string;
  severity: "error" | "warning";
}

export interface ImportUploadResponse {
  session_id: string;
  items: ImportPreviewItem[];
  errors: ImportError[];
  total_rows: number;
  valid_rows: number;
}

export interface ImportMappingPayload {
  items: { import_row_index: number; wbs_node_id: string | null }[];
  duplicate_action: "overwrite" | "sum" | "exclude";
}

export interface RMProjectSummary {
  teams_allocated: number;
  equipment_count: number;
  utilization_percent: number;
  conflicts_count: number;
  allocations: ResourceAllocation[];
}

// ─── PM Types — Deviz Items (F071, F074, F125) ──────────────────────────────

export interface DevizItem {
  id: string;
  project_id: string;
  wbs_node_id?: string;
  parent_id?: string;
  code?: string;
  description: string;
  unit_of_measure: string;
  estimated_quantity: number;
  estimated_unit_price_material: number;
  estimated_unit_price_labor: number;
  estimated_total: number;
  actual_quantity: number;
  actual_unit_price_material: number;
  actual_unit_price_labor: number;
  actual_total: number;
  currency: string;
  sort_order: number;
  over_budget_alert: boolean;
  import_source?: string;
  import_reference?: string;
  created_at: string;
  updated_at?: string;
}

// ─── PM Types — SdL Generator (E-039, F079) ─────────────────────────────────

export interface SdLGeneratorItem {
  deviz_item_id: string;
  code?: string;
  description: string;
  unit_of_measure: string;
  contracted_qty: number;
  contracted_unit_price: number;
  contracted_total: number;
  previous_cumulated_qty: number;
  current_period_qty: number;
  new_cumulated_qty: number;
  remaining_qty: number;
  current_period_value: number;
  cumulated_value: number;
  percent_complete: number;
}

export interface SdLGeneratorPreview {
  project_id: string;
  sdl_number: string;
  period_month: number;
  period_year: number;
  items: SdLGeneratorItem[];
  total_contracted: number;
  total_current_period: number;
  total_cumulated: number;
  total_remaining: number;
  is_first_sdl: boolean;
  is_final_sdl: boolean;
}

// ─── PM Types — Gantt Resource Overlay (E-038, F083, F117, F118) ─────────────

export interface GanttResourceRow {
  allocation_id: string;
  task_id: string;
  resource_type: "employee" | "equipment";
  resource_name: string;
  resource_id: string;
  start_date: string;
  end_date: string;
  allocated_hours: number;
  allocation_percent: number;
  has_conflict: boolean;
  conflict_details?: {
    conflicting_task_id: string;
    conflicting_task_title: string;
    overlap_start: string;
    overlap_end: string;
  };
}

export interface ResourceConflict {
  resource_id: string;
  resource_name: string;
  resource_type: "employee" | "equipment";
  task_a_id: string;
  task_a_title: string;
  task_b_id: string;
  task_b_title: string;
  overlap_start: string;
  overlap_end: string;
  resolution_options: ("reallocate" | "postpone" | "subcontract")[];
}

// ─── Pipeline Types — Contracts (F031, F035, F063) ───────────────────────────

export type ContractStatus =
  | "draft"
  | "pending_approval"
  | "approved"
  | "sent"
  | "negotiation"
  | "signed"
  | "active"
  | "completed"
  | "terminated";

export interface Contract {
  id: string;
  contact_id: string;
  offer_id?: string;
  opportunity_id?: string;
  contract_number: string;
  title: string;
  description?: string;
  status: ContractStatus;
  total_value: number;
  currency: string;
  start_date?: string;
  end_date?: string;
  signed_date?: string;
  terms_and_conditions?: string;
  owner_id?: string;
  project_id?: string;
  pdf_path?: string;
  notes?: string;
  created_at: string;
  updated_at?: string;
}

export interface ContractListItem {
  id: string;
  contract_number: string;
  title: string;
  status: ContractStatus;
  total_value: number;
  currency: string;
  contact_id: string;
  start_date?: string;
  end_date?: string;
  created_at: string;
}

export interface ContractCreate {
  contact_id: string;
  offer_id?: string;
  opportunity_id?: string;
  title: string;
  description?: string;
  total_value: number;
  currency?: string;
  start_date?: string;
  end_date?: string;
  terms_and_conditions?: string;
}

// ─── Document Types (F005, F016) ─────────────────────────────────────────────

export interface CrmDocument {
  id: string;
  entity_type: string;
  entity_id: string;
  contact_id?: string;
  property_id?: string;
  file_name: string;
  file_path: string;
  file_size?: number;
  mime_type?: string;
  category: string;
  description?: string;
  version: number;
  created_by?: string;
  created_at: string;
}

export interface CrmDocumentListItem {
  id: string;
  file_name: string;
  file_size?: number;
  mime_type?: string;
  category: string;
  description?: string;
  version: number;
  created_by?: string;
  created_at: string;
}

export interface CrmDocumentCreate {
  entity_type: string;
  entity_id: string;
  file_name: string;
  file_path: string;
  file_size?: number;
  mime_type?: string;
  category?: string;
  description?: string;
}

// ─── Notification Types (F141) ───────────────────────────────────────────────

export interface AppNotification {
  id: string;
  user_id: string;
  title: string;
  message: string;
  status: "unread" | "read" | "archived";
  link?: string;
  entity_type?: string;
  entity_id?: string;
  read_at?: string;
  created_at: string;
}

export interface NotificationCreate {
  title: string;
  message: string;
  link?: string;
  entity_type?: string;
  entity_id?: string;
}

// Product types (F017)
export interface Product {
  id: string;
  code: string;
  name: string;
  description?: string;
  product_type: string;
  category?: string;
  unit_of_measure: string;
  unit_price: number;
  currency: string;
  vat_rate: number;
  is_active: boolean;
  created_at: string;
}
