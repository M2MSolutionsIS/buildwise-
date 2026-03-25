/**
 * PM module API service — F063, F069, F070, F072–F088, F090
 */
import api from "../../../services/api";
import type {
  ApiResponse,
  PMProject,
  PMProjectListItem,
  PMTask,
  TaskDependency,
  ResourceAllocation,
  TimesheetEntry,
  MaterialConsumption,
  PMSubcontractor,
  DailyReport,
  WorkSituation,
  PMRisk,
  ProjectFinanceEntry,
  ProjectCashFlowEntry,
  ProgressMonitoring,
  BudgetControl,
  PunchItem,
  PMWarranty,
  EnergyImpact,
  ProjectReport,
  EnergyPortfolio,
  DevizItem,
  GanttResourceRow,
  ResourceConflict,
  SdLGeneratorPreview,
} from "../../../types";

const BASE = "/pm";

export interface ProjectFilters {
  page?: number;
  per_page?: number;
  status?: string;
  project_type?: string;
  search?: string;
}

export interface TaskFilters {
  page?: number;
  per_page?: number;
  status?: string;
  assigned_to?: string;
}

export const pmService = {
  // ─── Projects (F063, F101) ────────────────────────────────────────────────

  listProjects: async (
    filters: ProjectFilters = {}
  ): Promise<ApiResponse<PMProjectListItem[]>> => {
    const { data } = await api.get(`${BASE}/projects`, { params: filters });
    return data;
  },

  getProject: async (id: string): Promise<ApiResponse<PMProject>> => {
    const { data } = await api.get(`${BASE}/projects/${id}`);
    return data;
  },

  // ─── Tasks / Gantt (F070, F073) ───────────────────────────────────────────

  listTasks: async (
    projectId: string,
    filters: TaskFilters = {}
  ): Promise<ApiResponse<PMTask[]>> => {
    const { data } = await api.get(`${BASE}/projects/${projectId}/tasks`, {
      params: { ...filters, per_page: 500 },
    });
    return data;
  },

  getTask: async (taskId: string): Promise<ApiResponse<PMTask & { dependencies: TaskDependency[] }>> => {
    const { data } = await api.get(`${BASE}/tasks/${taskId}`);
    return data;
  },

  createTask: async (
    projectId: string,
    payload: Record<string, unknown>
  ): Promise<ApiResponse<PMTask>> => {
    const { data } = await api.post(`${BASE}/projects/${projectId}/tasks`, payload);
    return data;
  },

  updateTask: async (
    taskId: string,
    payload: Record<string, unknown>
  ): Promise<ApiResponse<PMTask>> => {
    const { data } = await api.put(`${BASE}/tasks/${taskId}`, payload);
    return data;
  },

  deleteTask: async (taskId: string): Promise<void> => {
    await api.delete(`${BASE}/tasks/${taskId}`);
  },

  // F070: Task dependencies
  addDependency: async (
    taskId: string,
    dependsOnId: string,
    type: string = "finish_to_start",
    lagDays: number = 0
  ): Promise<ApiResponse<TaskDependency>> => {
    const { data } = await api.post(`${BASE}/tasks/${taskId}/dependencies`, {
      depends_on_id: dependsOnId,
      dependency_type: type,
      lag_days: lagDays,
    });
    return data;
  },

  removeDependency: async (taskId: string, depId: string): Promise<void> => {
    await api.delete(`${BASE}/tasks/${taskId}/dependencies/${depId}`);
  },

  // ─── Resource Allocations (F083) ──────────────────────────────────────────

  listAllocations: async (
    projectId: string
  ): Promise<ApiResponse<ResourceAllocation[]>> => {
    const { data } = await api.get(`${BASE}/projects/${projectId}/resource-allocations`);
    return data;
  },

  createAllocation: async (
    projectId: string,
    payload: Record<string, unknown>
  ): Promise<ApiResponse<ResourceAllocation>> => {
    const { data } = await api.post(
      `${BASE}/projects/${projectId}/resource-allocations`,
      payload
    );
    return data;
  },

  updateAllocation: async (
    allocId: string,
    payload: Record<string, unknown>
  ): Promise<ApiResponse<ResourceAllocation>> => {
    const { data } = await api.put(`${BASE}/resource-allocations/${allocId}`, payload);
    return data;
  },

  // ─── Timesheets / Pontaj (F072, F073) ─────────────────────────────────────

  listTimesheets: async (
    projectId: string,
    params: { week?: string; user_id?: string; status?: string } = {}
  ): Promise<ApiResponse<TimesheetEntry[]>> => {
    const { data } = await api.get(`${BASE}/projects/${projectId}/timesheets`, { params });
    return data;
  },

  createTimesheet: async (
    projectId: string,
    payload: Record<string, unknown>
  ): Promise<ApiResponse<TimesheetEntry>> => {
    const { data } = await api.post(`${BASE}/projects/${projectId}/timesheets`, payload);
    return data;
  },

  updateTimesheet: async (
    entryId: string,
    payload: Record<string, unknown>
  ): Promise<ApiResponse<TimesheetEntry>> => {
    const { data } = await api.put(`${BASE}/timesheets/${entryId}`, payload);
    return data;
  },

  approveTimesheet: async (entryId: string): Promise<ApiResponse<TimesheetEntry>> => {
    const { data } = await api.patch(`${BASE}/timesheets/${entryId}/approve`);
    return data;
  },

  rejectTimesheet: async (entryId: string): Promise<ApiResponse<TimesheetEntry>> => {
    const { data } = await api.patch(`${BASE}/timesheets/${entryId}/reject`);
    return data;
  },

  submitTimesheet: async (entryId: string): Promise<ApiResponse<TimesheetEntry>> => {
    const { data } = await api.patch(`${BASE}/timesheets/${entryId}/submit`);
    return data;
  },

  // ─── Material Consumption / Fișe Consum (F074) ────────────────────────────

  listConsumptions: async (
    projectId: string,
    params: { wbs_node_id?: string; period?: string } = {}
  ): Promise<ApiResponse<MaterialConsumption[]>> => {
    const { data } = await api.get(`${BASE}/projects/${projectId}/consumptions`, { params });
    return data;
  },

  createConsumption: async (
    projectId: string,
    payload: Record<string, unknown>
  ): Promise<ApiResponse<MaterialConsumption>> => {
    const { data } = await api.post(`${BASE}/projects/${projectId}/consumptions`, payload);
    return data;
  },

  updateConsumption: async (
    consumptionId: string,
    payload: Record<string, unknown>
  ): Promise<ApiResponse<MaterialConsumption>> => {
    const { data } = await api.put(`${BASE}/consumptions/${consumptionId}`, payload);
    return data;
  },

  deleteConsumption: async (consumptionId: string): Promise<void> => {
    await api.delete(`${BASE}/consumptions/${consumptionId}`);
  },

  // ─── Subcontractors (F075) ────────────────────────────────────────────────

  listSubcontractors: async (
    projectId: string
  ): Promise<ApiResponse<PMSubcontractor[]>> => {
    const { data } = await api.get(`${BASE}/projects/${projectId}/subcontractors`);
    return data;
  },

  createSubcontractor: async (
    projectId: string,
    payload: Record<string, unknown>
  ): Promise<ApiResponse<PMSubcontractor>> => {
    const { data } = await api.post(`${BASE}/projects/${projectId}/subcontractors`, payload);
    return data;
  },

  updateSubcontractor: async (
    subId: string,
    payload: Record<string, unknown>
  ): Promise<ApiResponse<PMSubcontractor>> => {
    const { data } = await api.put(`${BASE}/subcontractors/${subId}`, payload);
    return data;
  },

  deleteSubcontractor: async (subId: string): Promise<void> => {
    await api.delete(`${BASE}/subcontractors/${subId}`);
  },

  // ─── Daily Reports / Raport Zilnic Șantier (F077) ─────────────────────────

  listDailyReports: async (
    projectId: string,
    params: { from?: string; to?: string } = {}
  ): Promise<ApiResponse<DailyReport[]>> => {
    const { data } = await api.get(`${BASE}/projects/${projectId}/daily-reports`, { params });
    return data;
  },

  getDailyReport: async (reportId: string): Promise<ApiResponse<DailyReport>> => {
    const { data } = await api.get(`${BASE}/daily-reports/${reportId}`);
    return data;
  },

  createDailyReport: async (
    projectId: string,
    payload: Record<string, unknown>
  ): Promise<ApiResponse<DailyReport>> => {
    const { data } = await api.post(`${BASE}/projects/${projectId}/daily-reports`, payload);
    return data;
  },

  updateDailyReport: async (
    reportId: string,
    payload: Record<string, unknown>
  ): Promise<ApiResponse<DailyReport>> => {
    const { data } = await api.put(`${BASE}/daily-reports/${reportId}`, payload);
    return data;
  },

  deleteDailyReport: async (reportId: string): Promise<void> => {
    await api.delete(`${BASE}/daily-reports/${reportId}`);
  },

  // ─── Progress Monitoring / S-Curve (F078) ─────────────────────────────────

  getProgressMonitoring: async (
    projectId: string
  ): Promise<ApiResponse<ProgressMonitoring>> => {
    const { data } = await api.get(`${BASE}/projects/${projectId}/progress-monitoring`);
    return data;
  },

  // ─── Budget Control / EVM (F080) ──────────────────────────────────────────

  getBudgetControl: async (
    projectId: string
  ): Promise<ApiResponse<BudgetControl>> => {
    const { data } = await api.get(`${BASE}/projects/${projectId}/budget-control`);
    return data;
  },

  // ─── Work Situations / Situații de Lucrări (F079) ─────────────────────────

  listWorkSituations: async (
    projectId: string
  ): Promise<ApiResponse<WorkSituation[]>> => {
    const { data } = await api.get(`${BASE}/projects/${projectId}/work-situations`);
    return data;
  },

  createWorkSituation: async (
    projectId: string,
    payload: Record<string, unknown>
  ): Promise<ApiResponse<WorkSituation>> => {
    const { data } = await api.post(`${BASE}/projects/${projectId}/work-situations`, payload);
    return data;
  },

  updateWorkSituation: async (
    sdlId: string,
    payload: Record<string, unknown>
  ): Promise<ApiResponse<WorkSituation>> => {
    const { data } = await api.put(`${BASE}/work-situations/${sdlId}`, payload);
    return data;
  },

  approveWorkSituation: async (sdlId: string): Promise<ApiResponse<WorkSituation>> => {
    const { data } = await api.post(`${BASE}/work-situations/${sdlId}/approve`);
    return data;
  },

  // ─── Risk Register (F084) ─────────────────────────────────────────────────

  listRisks: async (projectId: string): Promise<ApiResponse<PMRisk[]>> => {
    const { data } = await api.get(`${BASE}/projects/${projectId}/risks`);
    return data;
  },

  createRisk: async (
    projectId: string,
    payload: Record<string, unknown>
  ): Promise<ApiResponse<PMRisk>> => {
    const { data } = await api.post(`${BASE}/projects/${projectId}/risks`, payload);
    return data;
  },

  updateRisk: async (
    riskId: string,
    payload: Record<string, unknown>
  ): Promise<ApiResponse<PMRisk>> => {
    const { data } = await api.put(`${BASE}/risks/${riskId}`, payload);
    return data;
  },

  deleteRisk: async (riskId: string): Promise<void> => {
    await api.delete(`${BASE}/risks/${riskId}`);
  },

  // ─── Project Finance P&L (F091) ──────────────────────────────────────────

  listFinanceEntries: async (
    projectId: string
  ): Promise<ApiResponse<ProjectFinanceEntry[]>> => {
    const { data } = await api.get(`${BASE}/projects/${projectId}/finance`);
    return data;
  },

  createFinanceEntry: async (
    projectId: string,
    payload: Record<string, unknown>
  ): Promise<ApiResponse<ProjectFinanceEntry>> => {
    const { data } = await api.post(`${BASE}/projects/${projectId}/finance`, payload);
    return data;
  },

  // ─── Project Cash Flow (F092) ─────────────────────────────────────────────

  listCashFlow: async (
    projectId: string
  ): Promise<ApiResponse<ProjectCashFlowEntry[]>> => {
    const { data } = await api.get(`${BASE}/projects/${projectId}/cash-flow`);
    return data;
  },

  createCashFlow: async (
    projectId: string,
    payload: Record<string, unknown>
  ): Promise<ApiResponse<ProjectCashFlowEntry>> => {
    const { data } = await api.post(`${BASE}/projects/${projectId}/cash-flow`, payload);
    return data;
  },

  // ─── Punch Items / Reception (F081, F082, F086) ───────────────────────────

  listPunchItems: async (
    projectId: string
  ): Promise<ApiResponse<PunchItem[]>> => {
    const { data } = await api.get(`${BASE}/projects/${projectId}/punch-items`);
    return data;
  },

  createPunchItem: async (
    projectId: string,
    payload: Record<string, unknown>
  ): Promise<ApiResponse<PunchItem>> => {
    const { data } = await api.post(`${BASE}/projects/${projectId}/punch-items`, payload);
    return data;
  },

  updatePunchItem: async (
    itemId: string,
    payload: Record<string, unknown>
  ): Promise<ApiResponse<PunchItem>> => {
    const { data } = await api.put(`${BASE}/punch-items/${itemId}`, payload);
    return data;
  },

  createReception: async (
    projectId: string,
    payload: Record<string, unknown>
  ): Promise<ApiResponse<unknown>> => {
    const { data } = await api.post(`${BASE}/projects/${projectId}/receptions`, payload);
    return data;
  },

  // ─── Warranties (F086) ────────────────────────────────────────────────────

  listWarranties: async (
    projectId: string
  ): Promise<ApiResponse<PMWarranty[]>> => {
    const { data } = await api.get(`${BASE}/projects/${projectId}/warranties`);
    return data;
  },

  createWarranty: async (
    projectId: string,
    payload: Record<string, unknown>
  ): Promise<ApiResponse<PMWarranty>> => {
    const { data } = await api.post(`${BASE}/projects/${projectId}/warranties`, payload);
    return data;
  },

  updateWarranty: async (
    warrantyId: string,
    payload: Record<string, unknown>
  ): Promise<ApiResponse<PMWarranty>> => {
    const { data } = await api.put(`${BASE}/warranties/${warrantyId}`, payload);
    return data;
  },

  // ─── Energy Impact (F088, F090) ───────────────────────────────────────────

  getEnergyImpact: async (
    projectId: string
  ): Promise<ApiResponse<EnergyImpact | null>> => {
    const { data } = await api.get(`${BASE}/projects/${projectId}/energy-impact`);
    return data;
  },

  upsertEnergyImpact: async (
    projectId: string,
    payload: Record<string, unknown>
  ): Promise<ApiResponse<EnergyImpact>> => {
    const { data } = await api.put(`${BASE}/projects/${projectId}/energy-impact`, payload);
    return data;
  },

  // ─── Project Report 3-in-1 (F095) ─────────────────────────────────────────

  getProjectReport: async (
    projectId: string
  ): Promise<ApiResponse<ProjectReport>> => {
    const { data } = await api.get(`${BASE}/projects/${projectId}/reports`);
    return data;
  },

  // ─── Completed Projects Archive (F090) ─────────────────────────────────────

  listCompletedProjects: async (
    params: { page?: number; per_page?: number; search?: string } = {}
  ): Promise<ApiResponse<PMProjectListItem[]>> => {
    const { data } = await api.get(`${BASE}/completed-projects`, { params });
    return data;
  },

  // ─── Energy Portfolio (F161) ───────────────────────────────────────────────

  getEnergyPortfolio: async (): Promise<ApiResponse<EnergyPortfolio>> => {
    const { data } = await api.get(`${BASE}/energy-portfolio`);
    return data;
  },

  // ─── Export (F142) ─────────────────────────────────────────────────────────

  exportProjectReport: async (
    projectId: string,
    format: "pdf" | "excel" = "pdf"
  ): Promise<Blob> => {
    const { data } = await api.get(`${BASE}/projects/${projectId}/reports/export`, {
      params: { format },
      responseType: "blob",
    });
    return data;
  },

  exportCompletedProjects: async (
    format: "pdf" | "excel" = "excel"
  ): Promise<Blob> => {
    const { data } = await api.get(`${BASE}/completed-projects/export`, {
      params: { format },
      responseType: "blob",
    });
    return data;
  },

  // ─── Deviz Items (F071, F074, F125) ─────────────────────────────────────────

  listDevizItems: async (
    projectId: string
  ): Promise<ApiResponse<DevizItem[]>> => {
    const { data } = await api.get(`${BASE}/projects/${projectId}/deviz-items`);
    return data;
  },

  // ─── Gantt Resources — E-038 Dual-Layer (F083, F117, F118) ──────────────────

  listGanttResources: async (
    projectId: string
  ): Promise<ApiResponse<GanttResourceRow[]>> => {
    const { data } = await api.get(`${BASE}/projects/${projectId}/gantt/resources`);
    return data;
  },

  listResourceConflicts: async (
    projectId: string
  ): Promise<ApiResponse<ResourceConflict[]>> => {
    const { data } = await api.get(`${BASE}/projects/${projectId}/gantt/conflicts`);
    return data;
  },

  resolveConflict: async (
    projectId: string,
    conflictPayload: { resource_id: string; resolution: string; details?: Record<string, unknown> }
  ): Promise<ApiResponse<unknown>> => {
    const { data } = await api.post(
      `${BASE}/projects/${projectId}/gantt/resolve-conflict`,
      conflictPayload
    );
    return data;
  },

  // ─── SdL Generator — E-039 (F079) ──────────────────────────────────────────

  generateSdLPreview: async (
    projectId: string,
    payload: { period_month: number; period_year: number; items: { deviz_item_id: string; current_period_qty: number }[] }
  ): Promise<ApiResponse<SdLGeneratorPreview>> => {
    const { data } = await api.post(
      `${BASE}/projects/${projectId}/sdl/generate-preview`,
      payload
    );
    return data;
  },

  createSdLFromPreview: async (
    projectId: string,
    payload: Record<string, unknown>
  ): Promise<ApiResponse<WorkSituation>> => {
    const { data } = await api.post(
      `${BASE}/projects/${projectId}/sdl/create`,
      payload
    );
    return data;
  },

  generateSdLPdf: async (sdlId: string): Promise<Blob> => {
    const { data } = await api.get(`${BASE}/work-situations/${sdlId}/generate-pdf`, {
      responseType: "blob",
    });
    return data;
  },
};
