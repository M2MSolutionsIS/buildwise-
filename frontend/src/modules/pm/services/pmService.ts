/**
 * PM module API service — F063, F069, F070, F073, F083
 */
import api from "../../../services/api";
import type {
  ApiResponse,
  PMProject,
  PMProjectListItem,
  PMTask,
  TaskDependency,
  ResourceAllocation,
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
};
