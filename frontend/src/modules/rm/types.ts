/**
 * RM Module Types — F107-F122
 * Resource Management: HR, Equipment, Materials, Procurement, Allocations, Budget
 */

// ─── Employee (F107) ─────────────────────────────────────────────────────────

export interface Employee {
  id: string;
  organization_id: string;
  first_name: string;
  last_name: string;
  email?: string;
  phone?: string;
  employee_number?: string;
  position?: string;
  department?: string;
  cost_center?: string;
  contract_type: string;
  hire_date?: string;
  termination_date?: string;
  status: string;
  gross_salary?: number;
  net_salary?: number;
  hourly_rate?: number;
  standard_hours_month: number;
  currency: string;
  skills?: string[];
  qualifications?: string[];
  certifications?: string[];
  is_external: boolean;
  external_company?: string;
  external_contract_ref?: string;
  external_daily_rate?: number;
  user_id?: string;
  created_at?: string;
}

export interface EmployeeCreate {
  first_name: string;
  last_name: string;
  email?: string;
  phone?: string;
  employee_number?: string;
  position?: string;
  department?: string;
  cost_center?: string;
  contract_type?: string;
  hire_date?: string;
  gross_salary?: number;
  net_salary?: number;
  hourly_rate?: number;
  standard_hours_month?: number;
  currency?: string;
  skills?: string[];
  qualifications?: string[];
  certifications?: string[];
  is_external?: boolean;
  external_company?: string;
  external_contract_ref?: string;
  external_daily_rate?: number;
  user_id?: string;
}

export interface EmployeeUpdate extends Partial<EmployeeCreate> {
  status?: string;
  termination_date?: string;
}

// ─── HR Planning (F108) ──────────────────────────────────────────────────────

export interface HRPlanning {
  id: string;
  organization_id: string;
  entry_type: string;
  position: string;
  department?: string;
  target_date: string;
  description?: string;
  employee_id?: string;
  status: string;
  created_at?: string;
}

export interface HRPlanningCreate {
  entry_type: string;
  position: string;
  department?: string;
  target_date: string;
  description?: string;
  employee_id?: string;
}

// ─── Leave (F109) ────────────────────────────────────────────────────────────

export interface Leave {
  id: string;
  organization_id: string;
  employee_id: string;
  leave_type: string;
  start_date: string;
  end_date: string;
  reason?: string;
  status: string;
  approved_by?: string;
  created_at?: string;
}

export interface LeaveCreate {
  employee_id: string;
  leave_type: string;
  start_date: string;
  end_date: string;
  reason?: string;
}

// ─── Equipment ───────────────────────────────────────────────────────────────

export interface Equipment {
  id: string;
  organization_id: string;
  name: string;
  code?: string;
  category?: string;
  description?: string;
  manufacturer?: string;
  model?: string;
  serial_number?: string;
  purchase_date?: string;
  purchase_cost?: number;
  daily_rate?: number;
  currency: string;
  location?: string;
  status: string;
  next_maintenance_date?: string;
  created_at?: string;
}

export interface EquipmentCreate {
  name: string;
  code?: string;
  category?: string;
  description?: string;
  manufacturer?: string;
  model?: string;
  serial_number?: string;
  purchase_date?: string;
  purchase_cost?: number;
  daily_rate?: number;
  currency?: string;
  location?: string;
}

export interface EquipmentUpdate extends Partial<EquipmentCreate> {
  status?: string;
  next_maintenance_date?: string;
}

// ─── Material Stock (F114) ───────────────────────────────────────────────────

export interface MaterialStock {
  id: string;
  organization_id: string;
  name: string;
  code?: string;
  unit_of_measure: string;
  current_quantity: number;
  minimum_quantity: number;
  reserved_quantity: number;
  location?: string;
  warehouse?: string;
  unit_cost?: number;
  currency: string;
  total_value?: number;
  is_below_minimum: boolean;
  product_id?: string;
  created_at?: string;
}

export interface MaterialStockCreate {
  name: string;
  code?: string;
  unit_of_measure?: string;
  current_quantity?: number;
  minimum_quantity?: number;
  location?: string;
  warehouse?: string;
  unit_cost?: number;
  currency?: string;
  product_id?: string;
}

export interface MaterialStockUpdate extends Partial<MaterialStockCreate> {}

// ─── Procurement (F112, F113) ────────────────────────────────────────────────

export interface ProcurementLineItem {
  id: string;
  order_id: string;
  description: string;
  quantity: number;
  unit_of_measure: string;
  unit_price: number;
  total_price: number;
  received_quantity: number;
  material_stock_id?: string;
  product_id?: string;
}

export interface ProcurementLineItemCreate {
  description: string;
  quantity: number;
  unit_of_measure?: string;
  unit_price: number;
  material_stock_id?: string;
  product_id?: string;
}

export interface ProcurementOrder {
  id: string;
  organization_id: string;
  order_number: string;
  status: string;
  supplier_contact_id?: string;
  project_id?: string;
  wbs_node_id?: string;
  currency: string;
  total_amount: number;
  expected_delivery?: string;
  actual_delivery?: string;
  order_date?: string;
  line_items: ProcurementLineItem[];
  created_at?: string;
}

export interface ProcurementOrderCreate {
  supplier_contact_id?: string;
  project_id?: string;
  wbs_node_id?: string;
  currency?: string;
  expected_delivery?: string;
  line_items?: ProcurementLineItemCreate[];
}

export interface ProcurementDocument {
  id: string;
  organization_id: string;
  order_id?: string;
  document_type: string;
  document_number: string;
  document_date: string;
  amount: number;
  currency: string;
  file_path?: string;
  created_at?: string;
}

// ─── Resource Allocation (F117-F120) ─────────────────────────────────────────

export interface RMAllocation {
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
  created_at?: string;
}

// ─── Budget (F115, F116) ─────────────────────────────────────────────────────

export interface BudgetEntry {
  id: string;
  organization_id: string;
  cost_center: string;
  category: string;
  description?: string;
  period_month: number;
  period_year: number;
  budgeted_amount: number;
  actual_amount: number;
  variance: number;
  currency: string;
  project_id?: string;
  created_at?: string;
}

// ─── Utilization (F121) ──────────────────────────────────────────────────────

export interface ResourceUtilization {
  employee_id: string;
  employee_name: string;
  total_allocated_hours: number;
  total_actual_hours: number;
  utilization_percent: number;
  project_count: number;
}

// ─── Company Capacity (E-036, F121, F122) ───────────────────────────────────

export interface CapacityKPIs {
  total_employees: number;
  allocated_employees: number;
  available_employees: number;
  total_equipment: number;
  allocated_equipment: number;
  available_equipment: number;
  total_allocated_hours: number;
  total_planned_cost: number;
  utilization_rate: number;
  active_projects_count: number;
  allocations_with_conflicts: number;
}

export interface CapacityHeatmapCell {
  team: string;
  period: string;
  utilization_percent: number;
  allocated_hours: number;
  total_hours: number;
  projects: string[];
}

export interface SimulationInput {
  project_name: string;
  duration_weeks: number;
  start_date: string;
  teams_needed: { team: string; allocation_percent: number }[];
}

export interface SimulationResult {
  can_accept: boolean;
  bottlenecks: { team: string; period: string; overload_percent: number }[];
  recommendation: string;
  optimal_start_date?: string;
}

// ─── Cost Analysis (E-040, F115, F116) ──────────────────────────────────────

export interface CostAnalysis {
  cost_center: string;
  total_budgeted: number;
  total_actual: number;
  total_variance: number;
  entries: BudgetEntry[];
}

export interface BudgetEntryCreate {
  cost_center: string;
  category: string;
  description?: string;
  period_month: number;
  period_year: number;
  budgeted_amount?: number;
  actual_amount?: number;
  currency?: string;
  project_id?: string;
}

export interface BudgetEntryUpdate extends Partial<BudgetEntryCreate> {}

export interface FinancialKPIs {
  total_cost: number;
  total_budgeted: number;
  overage_pct: number;
  forecast: number;
  currency: string;
}

export interface ProjectFinancialRow {
  project_id: string;
  project_name: string;
  personal: { budgeted: number; actual: number; variance: number; pct: number };
  equipment: { budgeted: number; actual: number; variance: number; pct: number };
  materials: { budgeted: number; actual: number; variance: number; pct: number };
  total: { budgeted: number; actual: number; variance: number; pct: number };
}
