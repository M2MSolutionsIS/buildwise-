import api from "../../../services/api";
import type {
  ApiResponse,
  Opportunity,
  OpportunityListItem,
  OpportunityCreate,
  OpportunityUpdate,
  PipelineBoard,
  SalesKPI,
  WeightedPipeline,
  PipelineAnalytics,
  Activity,
  ActivityListItem,
  Contract,
  ContractListItem,
} from "../../../types";

const BASE = "/pipeline";

export interface OpportunityFilters {
  page?: number;
  per_page?: number;
  stage?: string;
  owner_id?: string;
  contact_id?: string;
  search?: string;
}

export interface ActivityFilters {
  page?: number;
  per_page?: number;
  activity_type?: string;
  status?: string;
  contact_id?: string;
  opportunity_id?: string;
  date_from?: string;
  date_to?: string;
}

export const pipelineService = {
  // ─── Opportunities (F042, F050-F053) ────────────────────────────────────────

  listOpportunities: async (
    filters: OpportunityFilters = {}
  ): Promise<ApiResponse<OpportunityListItem[]>> => {
    const { data } = await api.get(`${BASE}/opportunities`, { params: filters });
    return data;
  },

  getOpportunity: async (id: string): Promise<ApiResponse<Opportunity>> => {
    const { data } = await api.get(`${BASE}/opportunities/${id}`);
    return data;
  },

  createOpportunity: async (
    payload: OpportunityCreate
  ): Promise<ApiResponse<Opportunity>> => {
    const { data } = await api.post(`${BASE}/opportunities`, payload);
    return data;
  },

  updateOpportunity: async (
    id: string,
    payload: OpportunityUpdate
  ): Promise<ApiResponse<Opportunity>> => {
    const { data } = await api.put(`${BASE}/opportunities/${id}`, payload);
    return data;
  },

  deleteOpportunity: async (id: string): Promise<void> => {
    await api.delete(`${BASE}/opportunities/${id}`);
  },

  // F051: Stage transition (drag & drop)
  transitionStage: async (
    id: string,
    newStage: string,
    lossReason?: string,
    lossReasonDetail?: string
  ): Promise<ApiResponse<Opportunity>> => {
    const { data } = await api.post(`${BASE}/opportunities/${id}/transition`, {
      new_stage: newStage,
      loss_reason: lossReason,
      loss_reason_detail: lossReasonDetail,
    });
    return data;
  },

  // F042: Qualify opportunity
  qualifyOpportunity: async (
    id: string,
    checklist?: Record<string, unknown>
  ): Promise<ApiResponse<Opportunity>> => {
    const { data } = await api.post(`${BASE}/opportunities/${id}/qualify`, {
      qualification_checklist: checklist,
    });
    return data;
  },

  // F050: Pipeline Board (Kanban) with agent/value filters
  getBoard: async (
    params?: { owner_id?: string; min_value?: number }
  ): Promise<ApiResponse<PipelineBoard>> => {
    const { data } = await api.get(`${BASE}/board`, { params });
    return data;
  },

  // F053: Weighted pipeline value
  getWeightedPipeline: async (): Promise<ApiResponse<WeightedPipeline>> => {
    const { data } = await api.get(`${BASE}/weighted-value`);
    return data;
  },

  // F058: Sales KPI Dashboard
  getSalesKPI: async (): Promise<ApiResponse<SalesKPI>> => {
    const { data } = await api.get(`${BASE}/kpi/sales`);
    return data;
  },

  // ─── Pipeline Analytics (F058, E-012) ───────────────────────────────────────

  getPipelineAnalytics: async (params?: {
    period_start?: string;
    period_end?: string;
    agent_id?: string;
  }): Promise<ApiResponse<PipelineAnalytics>> => {
    const { data } = await api.get(`${BASE}/analytics/pipeline`, { params });
    return data;
  },

  exportAnalyticsCSV: async (section: string = "all"): Promise<Blob> => {
    const { data } = await api.get(`${BASE}/analytics/pipeline/export-csv`, {
      params: { section },
      responseType: "blob",
    });
    return data;
  },

  // ─── Activities (F054-F056) ─────────────────────────────────────────────────

  listActivities: async (
    filters: ActivityFilters = {}
  ): Promise<ApiResponse<ActivityListItem[]>> => {
    const { data } = await api.get(`${BASE}/activities`, { params: filters });
    return data;
  },

  getActivity: async (id: string): Promise<ApiResponse<Activity>> => {
    const { data } = await api.get(`${BASE}/activities/${id}`);
    return data;
  },

  createActivity: async (
    payload: Record<string, unknown>
  ): Promise<ApiResponse<Activity>> => {
    const { data } = await api.post(`${BASE}/activities`, payload);
    return data;
  },

  updateActivity: async (
    id: string,
    payload: Record<string, unknown>
  ): Promise<ApiResponse<Activity>> => {
    const { data } = await api.put(`${BASE}/activities/${id}`, payload);
    return data;
  },

  deleteActivity: async (id: string): Promise<void> => {
    await api.delete(`${BASE}/activities/${id}`);
  },

  // ─── Contracts (F031, F035, F063) ────────────────────────────────────────────

  listContracts: async (
    params: { page?: number; per_page?: number; status?: string; contact_id?: string } = {}
  ): Promise<ApiResponse<ContractListItem[]>> => {
    const { data } = await api.get(`${BASE}/contracts`, { params });
    return data;
  },

  getContract: async (id: string): Promise<ApiResponse<Contract>> => {
    const { data } = await api.get(`${BASE}/contracts/${id}`);
    return data;
  },

  createContract: async (
    payload: Record<string, unknown>
  ): Promise<ApiResponse<Contract>> => {
    const { data } = await api.post(`${BASE}/contracts`, payload);
    return data;
  },

  createContractFromOffer: async (
    offerId: string,
    payload?: { title?: string; start_date?: string; end_date?: string; additional_terms?: string }
  ): Promise<ApiResponse<Contract>> => {
    const { data } = await api.post(`${BASE}/contracts/from-offer`, {
      offer_id: offerId,
      ...payload,
    });
    return data;
  },

  signContract: async (
    contractId: string,
    signedDate?: string
  ): Promise<ApiResponse<Contract>> => {
    const { data } = await api.post(`${BASE}/contracts/${contractId}/sign`, {
      signed_date: signedDate,
    });
    return data;
  },

  terminateContract: async (
    contractId: string,
    reason: string
  ): Promise<ApiResponse<Contract>> => {
    const { data } = await api.post(`${BASE}/contracts/${contractId}/terminate`, {
      termination_reason: reason,
    });
    return data;
  },
};
