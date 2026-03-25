/**
 * BI module API service — F133, F148, F152, F132, F142
 * KPI Engine, Dashboards, Executive Summary, AI Chatbot, Reports.
 */
import api from "../../../services/api";
import type {
  ApiResponse,
  KPIDefinition,
  KPIValue,
  KPIDashboardItem,
  Dashboard,
  ExecutiveSummary,
  ReportDefinition,
} from "../../../types";

const BASE = "/bi";

export const biService = {
  // ─── KPI Definitions (F148) ───────────────────────────────────────────────

  listKPIs: async (params?: {
    page?: number;
    per_page?: number;
    module?: string;
    is_active?: boolean;
  }): Promise<ApiResponse<KPIDefinition[]>> => {
    const { data } = await api.get(`${BASE}/kpis`, { params });
    return data;
  },

  getKPI: async (kpiId: string): Promise<ApiResponse<KPIDefinition>> => {
    const { data } = await api.get(`${BASE}/kpis/${kpiId}`);
    return data;
  },

  createKPI: async (
    payload: Partial<KPIDefinition>
  ): Promise<ApiResponse<KPIDefinition>> => {
    const { data } = await api.post(`${BASE}/kpis`, payload);
    return data;
  },

  updateKPI: async (
    kpiId: string,
    payload: Partial<KPIDefinition>
  ): Promise<ApiResponse<KPIDefinition>> => {
    const { data } = await api.put(`${BASE}/kpis/${kpiId}`, payload);
    return data;
  },

  deleteKPI: async (kpiId: string): Promise<void> => {
    await api.delete(`${BASE}/kpis/${kpiId}`);
  },

  // ─── KPI Values ───────────────────────────────────────────────────────────

  recordKPIValue: async (
    kpiId: string,
    payload: { value: number; period_start?: string; period_end?: string; project_id?: string }
  ): Promise<ApiResponse<KPIValue>> => {
    const { data } = await api.post(`${BASE}/kpis/${kpiId}/values`, payload);
    return data;
  },

  listKPIValues: async (
    kpiId: string,
    limit: number = 50
  ): Promise<ApiResponse<KPIValue[]>> => {
    const { data } = await api.get(`${BASE}/kpis/${kpiId}/values`, { params: { limit } });
    return data;
  },

  // ─── KPI Dashboard (F152) ─────────────────────────────────────────────────

  getKPIDashboard: async (): Promise<ApiResponse<KPIDashboardItem[]>> => {
    const { data } = await api.get(`${BASE}/kpi-dashboard`);
    return data;
  },

  // ─── Dashboards (F133) ────────────────────────────────────────────────────

  listDashboards: async (params?: {
    page?: number;
    per_page?: number;
  }): Promise<ApiResponse<Dashboard[]>> => {
    const { data } = await api.get(`${BASE}/dashboards`, { params });
    return data;
  },

  getDashboard: async (dashId: string): Promise<ApiResponse<Dashboard>> => {
    const { data } = await api.get(`${BASE}/dashboards/${dashId}`);
    return data;
  },

  createDashboard: async (
    payload: Partial<Dashboard> & { widgets?: Record<string, unknown>[] }
  ): Promise<ApiResponse<Dashboard>> => {
    const { data } = await api.post(`${BASE}/dashboards`, payload);
    return data;
  },

  updateDashboard: async (
    dashId: string,
    payload: Partial<Dashboard>
  ): Promise<ApiResponse<Dashboard>> => {
    const { data } = await api.put(`${BASE}/dashboards/${dashId}`, payload);
    return data;
  },

  deleteDashboard: async (dashId: string): Promise<void> => {
    await api.delete(`${BASE}/dashboards/${dashId}`);
  },

  // ─── Executive Summary (F133) ─────────────────────────────────────────────

  getExecutiveSummary: async (): Promise<ApiResponse<ExecutiveSummary>> => {
    const { data } = await api.get(`${BASE}/executive-summary`);
    return data;
  },

  // ─── Reports (E-041, F142) ────────────────────────────────────────────────

  listReports: async (params?: {
    page?: number;
    per_page?: number;
    report_type?: string;
    module?: string;
  }): Promise<ApiResponse<ReportDefinition[]>> => {
    const { data } = await api.get(`${BASE}/reports`, { params });
    return data;
  },

  createReport: async (
    payload: Partial<ReportDefinition>
  ): Promise<ApiResponse<ReportDefinition>> => {
    const { data } = await api.post(`${BASE}/reports`, payload);
    return data;
  },

  updateReport: async (
    reportId: string,
    payload: Partial<ReportDefinition>
  ): Promise<ApiResponse<ReportDefinition>> => {
    const { data } = await api.put(`${BASE}/reports/${reportId}`, payload);
    return data;
  },

  // ─── AI Conversations (F132) ──────────────────────────────────────────────

  listConversations: async (params?: {
    page?: number;
    per_page?: number;
  }): Promise<ApiResponse<unknown[]>> => {
    const { data } = await api.get(`${BASE}/conversations`, { params });
    return data;
  },

  createConversation: async (
    title?: string
  ): Promise<ApiResponse<unknown>> => {
    const { data } = await api.post(`${BASE}/conversations`, { title });
    return data;
  },

  getConversation: async (convId: string): Promise<ApiResponse<unknown>> => {
    const { data } = await api.get(`${BASE}/conversations/${convId}`);
    return data;
  },

  sendMessage: async (
    convId: string,
    content: string
  ): Promise<ApiResponse<unknown>> => {
    const { data } = await api.post(`${BASE}/conversations/${convId}/messages`, { content });
    return data;
  },
};
