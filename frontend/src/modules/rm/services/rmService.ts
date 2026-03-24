/**
 * RM Service — API layer for Resource Management module
 * Endpoints: /api/v1/rm/*
 * F-codes: F107-F122
 */
import api from "../../../services/api";
import type { ApiResponse } from "../../../types";
import type {
  Employee,
  EmployeeCreate,
  EmployeeUpdate,
  HRPlanning,
  HRPlanningCreate,
  Leave,
  LeaveCreate,
  Equipment,
  EquipmentCreate,
  EquipmentUpdate,
  MaterialStock,
  MaterialStockCreate,
  MaterialStockUpdate,
  ProcurementOrder,
  ProcurementOrderCreate,
  ProcurementDocument,
  RMAllocation,
  BudgetEntry,
  BudgetEntryCreate,
  BudgetEntryUpdate,
  ResourceUtilization,
  CapacityKPIs,
  CostAnalysis,
} from "../types";

const RM = "/rm";

export interface EmployeeFilters {
  page?: number;
  per_page?: number;
  search?: string;
  department?: string;
  status?: string;
  is_external?: boolean;
}

export interface EquipmentFilters {
  page?: number;
  per_page?: number;
  status?: string;
  category?: string;
}

export interface MaterialFilters {
  page?: number;
  per_page?: number;
  below_minimum?: boolean;
  warehouse?: string;
}

export interface ProcurementFilters {
  page?: number;
  per_page?: number;
  status?: string;
}

export interface AllocationFilters {
  page?: number;
  per_page?: number;
  project_id?: string;
  employee_id?: string;
  resource_type?: string;
  status?: string;
}

export const rmService = {
  // ─── Employees (F107) ────────────────────────────────────────────────────
  listEmployees: async (filters?: EmployeeFilters) => {
    const { data } = await api.get<ApiResponse<Employee[]>>(`${RM}/employees`, { params: filters });
    return data;
  },
  createEmployee: async (payload: EmployeeCreate) => {
    const { data } = await api.post<ApiResponse<Employee>>(`${RM}/employees`, payload);
    return data;
  },
  getEmployee: async (id: string) => {
    const { data } = await api.get<ApiResponse<Employee>>(`${RM}/employees/${id}`);
    return data;
  },
  updateEmployee: async (id: string, payload: EmployeeUpdate) => {
    const { data } = await api.put<ApiResponse<Employee>>(`${RM}/employees/${id}`, payload);
    return data;
  },
  deleteEmployee: async (id: string) => {
    const { data } = await api.delete(`${RM}/employees/${id}`);
    return data;
  },

  // ─── HR Planning (F108) ──────────────────────────────────────────────────
  listHRPlanning: async (filters?: { page?: number; per_page?: number; status?: string; entry_type?: string; department?: string }) => {
    const { data } = await api.get<ApiResponse<HRPlanning[]>>(`${RM}/hr-planning`, { params: filters });
    return data;
  },
  createHRPlanning: async (payload: HRPlanningCreate) => {
    const { data } = await api.post<ApiResponse<HRPlanning>>(`${RM}/hr-planning`, payload);
    return data;
  },

  // ─── Leaves (F109) ───────────────────────────────────────────────────────
  listLeaves: async (filters?: { page?: number; per_page?: number; employee_id?: string; status?: string }) => {
    const { data } = await api.get<ApiResponse<Leave[]>>(`${RM}/leaves`, { params: filters });
    return data;
  },
  createLeave: async (payload: LeaveCreate) => {
    const { data } = await api.post<ApiResponse<Leave>>(`${RM}/leaves`, payload);
    return data;
  },
  checkAvailability: async (employeeId: string, startDate: string, endDate: string) => {
    const { data } = await api.get(`${RM}/employees/${employeeId}/availability`, {
      params: { start_date: startDate, end_date: endDate },
    });
    return data;
  },

  // ─── Equipment ───────────────────────────────────────────────────────────
  listEquipment: async (filters?: EquipmentFilters) => {
    const { data } = await api.get<ApiResponse<Equipment[]>>(`${RM}/equipment`, { params: filters });
    return data;
  },
  createEquipment: async (payload: EquipmentCreate) => {
    const { data } = await api.post<ApiResponse<Equipment>>(`${RM}/equipment`, payload);
    return data;
  },
  getEquipment: async (id: string) => {
    const { data } = await api.get<ApiResponse<Equipment>>(`${RM}/equipment/${id}`);
    return data;
  },
  updateEquipment: async (id: string, payload: EquipmentUpdate) => {
    const { data } = await api.put<ApiResponse<Equipment>>(`${RM}/equipment/${id}`, payload);
    return data;
  },
  deleteEquipment: async (id: string) => {
    const { data } = await api.delete(`${RM}/equipment/${id}`);
    return data;
  },

  // ─── Materials & Stock (F114) ────────────────────────────────────────────
  listMaterials: async (filters?: MaterialFilters) => {
    const { data } = await api.get<ApiResponse<MaterialStock[]>>(`${RM}/materials`, { params: filters });
    return data;
  },
  createMaterial: async (payload: MaterialStockCreate) => {
    const { data } = await api.post<ApiResponse<MaterialStock>>(`${RM}/materials`, payload);
    return data;
  },
  updateMaterial: async (id: string, payload: MaterialStockUpdate) => {
    const { data } = await api.put<ApiResponse<MaterialStock>>(`${RM}/materials/${id}`, payload);
    return data;
  },

  // ─── Procurement (F112, F113) ────────────────────────────────────────────
  listProcurement: async (filters?: ProcurementFilters) => {
    const { data } = await api.get<ApiResponse<ProcurementOrder[]>>(`${RM}/procurement`, { params: filters });
    return data;
  },
  createProcurement: async (payload: ProcurementOrderCreate) => {
    const { data } = await api.post<ApiResponse<ProcurementOrder>>(`${RM}/procurement`, payload);
    return data;
  },
  getProcurement: async (id: string) => {
    const { data } = await api.get<ApiResponse<ProcurementOrder>>(`${RM}/procurement/${id}`);
    return data;
  },
  listProcurementDocs: async (orderId: string) => {
    const { data } = await api.get<ApiResponse<ProcurementDocument[]>>(`${RM}/procurement/${orderId}/documents`);
    return data;
  },

  // ─── Allocations (F117-F120) ─────────────────────────────────────────────
  listAllocations: async (filters?: AllocationFilters) => {
    const { data } = await api.get<ApiResponse<RMAllocation[]>>(`${RM}/allocations`, { params: filters });
    return data;
  },

  // ─── Budget (F115, F116) ─────────────────────────────────────────────────
  listBudgets: async (filters?: { page?: number; per_page?: number; cost_center?: string; period_year?: number }) => {
    const { data } = await api.get<ApiResponse<BudgetEntry[]>>(`${RM}/budgets`, { params: filters });
    return data;
  },

  // ─── Utilization (F121) ──────────────────────────────────────────────────
  getUtilization: async () => {
    const { data } = await api.get<ApiResponse<ResourceUtilization[]>>(`${RM}/utilization`);
    return data;
  },

  // ─── Company Capacity (E-036, F121, F122) ──────────────────────────────
  getCapacity: async () => {
    const { data } = await api.get<ApiResponse<CapacityKPIs>>("/pm/company-capacity");
    return data;
  },

  // ─── Budget CRUD (F115, F116) ──────────────────────────────────────────
  createBudget: async (payload: BudgetEntryCreate) => {
    const { data } = await api.post<ApiResponse<BudgetEntry>>(`${RM}/budgets`, payload);
    return data;
  },
  updateBudget: async (id: string, payload: BudgetEntryUpdate) => {
    const { data } = await api.put<ApiResponse<BudgetEntry>>(`${RM}/budgets/${id}`, payload);
    return data;
  },

  // ─── Cost Analysis (F116) ─────────────────────────────────────────────
  getCostAnalysis: async (filters?: { cost_center?: string; period_year?: number }) => {
    const { data } = await api.get<ApiResponse<CostAnalysis[]>>(`${RM}/cost-analysis`, { params: filters });
    return data;
  },
};
