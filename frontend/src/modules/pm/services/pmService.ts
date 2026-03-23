/**
 * PM module API service — F063, F069, F070, F072–F075, F077, F083
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
};
