/**
 * System module API service — F040, F041, F136, F137, F160
 * Organization settings, roles, feature flags, tenant setup.
 */
import api from "../../../services/api";
import type {
  ApiResponse,
  Organization,
  TenantSetupPayload,
  SystemRole,
  FeatureFlag,
  User,
  PipelineStageConfig,
  RMResourceCategory,
  RMUnitOfMeasure,
  RMAlertThreshold,
} from "../../../types";

const BASE = "/system";

export const systemService = {
  // ─── Organization (F136) ──────────────────────────────────────────────────

  getOrganization: async (): Promise<ApiResponse<Organization>> => {
    const { data } = await api.get(`${BASE}/organization`);
    return data;
  },

  updateOrganization: async (
    payload: Partial<Organization>
  ): Promise<ApiResponse<Organization>> => {
    const { data } = await api.patch(`${BASE}/organization`, payload);
    return data;
  },

  // ─── Tenant Setup Wizard (F160) ───────────────────────────────────────────

  completeTenantSetup: async (
    payload: TenantSetupPayload
  ): Promise<ApiResponse<Organization>> => {
    const { data } = await api.post(`${BASE}/tenant-setup`, payload);
    return data;
  },

  // ─── Roles (F040) ────────────────────────────────────────────────────────

  listRoles: async (): Promise<ApiResponse<SystemRole[]>> => {
    const { data } = await api.get(`${BASE}/roles`);
    return data;
  },

  createRole: async (
    payload: { name: string; code: string; description?: string }
  ): Promise<ApiResponse<SystemRole>> => {
    const { data } = await api.post(`${BASE}/roles`, payload);
    return data;
  },

  updateRole: async (
    roleId: string,
    payload: Record<string, unknown>
  ): Promise<ApiResponse<SystemRole>> => {
    const { data } = await api.put(`${BASE}/roles/${roleId}`, payload);
    return data;
  },

  deleteRole: async (roleId: string): Promise<void> => {
    await api.delete(`${BASE}/roles/${roleId}`);
  },

  assignPermissions: async (
    roleId: string,
    permissionIds: string[]
  ): Promise<ApiResponse<SystemRole>> => {
    const { data } = await api.put(`${BASE}/roles/${roleId}/permissions`, {
      permission_ids: permissionIds,
    });
    return data;
  },

  // ─── Users Management (F040) ──────────────────────────────────────────────

  listUsers: async (): Promise<ApiResponse<User[]>> => {
    const { data } = await api.get(`${BASE}/users`);
    return data;
  },

  inviteUser: async (
    payload: { email: string; first_name: string; last_name: string; role_code: string }
  ): Promise<ApiResponse<User>> => {
    const { data } = await api.post(`${BASE}/users/invite`, payload);
    return data;
  },

  assignUserRoles: async (
    userId: string,
    roleCodes: string[]
  ): Promise<ApiResponse<User>> => {
    const { data } = await api.put(`${BASE}/users/${userId}/roles`, {
      role_codes: roleCodes,
    });
    return data;
  },

  // ─── Feature Flags (F136) ─────────────────────────────────────────────────

  listFeatureFlags: async (): Promise<ApiResponse<FeatureFlag[]>> => {
    const { data } = await api.get(`${BASE}/feature-flags`);
    return data;
  },

  updateFeatureFlag: async (
    flagId: string,
    payload: { is_enabled: boolean; config?: Record<string, unknown> }
  ): Promise<ApiResponse<FeatureFlag>> => {
    const { data } = await api.put(`${BASE}/feature-flags/${flagId}`, payload);
    return data;
  },

  // ─── Audit Logs (F041) ────────────────────────────────────────────────────

  // ─── Pipeline Stages Config (F061) ──────────────────────────────────────────

  listPipelineStages: async (): Promise<ApiResponse<PipelineStageConfig[]>> => {
    const { data } = await api.get(`${BASE}/pipeline-stages`);
    return data;
  },

  createPipelineStage: async (
    payload: Partial<PipelineStageConfig>
  ): Promise<ApiResponse<PipelineStageConfig>> => {
    const { data } = await api.post(`${BASE}/pipeline-stages`, payload);
    return data;
  },

  updatePipelineStage: async (
    stageId: string,
    payload: Partial<PipelineStageConfig>
  ): Promise<ApiResponse<PipelineStageConfig>> => {
    const { data } = await api.put(`${BASE}/pipeline-stages/${stageId}`, payload);
    return data;
  },

  deletePipelineStage: async (stageId: string): Promise<void> => {
    await api.delete(`${BASE}/pipeline-stages/${stageId}`);
  },

  // ─── RM Configurator (F131) ───────────────────────────────────────────────

  listRMCategories: async (): Promise<ApiResponse<RMResourceCategory[]>> => {
    const { data } = await api.get(`${BASE}/rm-config/categories`);
    return data;
  },

  createRMCategory: async (
    payload: Partial<RMResourceCategory>
  ): Promise<ApiResponse<RMResourceCategory>> => {
    const { data } = await api.post(`${BASE}/rm-config/categories`, payload);
    return data;
  },

  updateRMCategory: async (
    catId: string,
    payload: Partial<RMResourceCategory>
  ): Promise<ApiResponse<RMResourceCategory>> => {
    const { data } = await api.put(`${BASE}/rm-config/categories/${catId}`, payload);
    return data;
  },

  deleteRMCategory: async (catId: string): Promise<void> => {
    await api.delete(`${BASE}/rm-config/categories/${catId}`);
  },

  listRMUnits: async (): Promise<ApiResponse<RMUnitOfMeasure[]>> => {
    const { data } = await api.get(`${BASE}/rm-config/units`);
    return data;
  },

  createRMUnit: async (
    payload: Partial<RMUnitOfMeasure>
  ): Promise<ApiResponse<RMUnitOfMeasure>> => {
    const { data } = await api.post(`${BASE}/rm-config/units`, payload);
    return data;
  },

  updateRMUnit: async (
    unitId: string,
    payload: Partial<RMUnitOfMeasure>
  ): Promise<ApiResponse<RMUnitOfMeasure>> => {
    const { data } = await api.put(`${BASE}/rm-config/units/${unitId}`, payload);
    return data;
  },

  deleteRMUnit: async (unitId: string): Promise<void> => {
    await api.delete(`${BASE}/rm-config/units/${unitId}`);
  },

  listRMThresholds: async (): Promise<ApiResponse<RMAlertThreshold[]>> => {
    const { data } = await api.get(`${BASE}/rm-config/thresholds`);
    return data;
  },

  createRMThreshold: async (
    payload: Partial<RMAlertThreshold>
  ): Promise<ApiResponse<RMAlertThreshold>> => {
    const { data } = await api.post(`${BASE}/rm-config/thresholds`, payload);
    return data;
  },

  updateRMThreshold: async (
    thresholdId: string,
    payload: Partial<RMAlertThreshold>
  ): Promise<ApiResponse<RMAlertThreshold>> => {
    const { data } = await api.put(`${BASE}/rm-config/thresholds/${thresholdId}`, payload);
    return data;
  },

  deleteRMThreshold: async (thresholdId: string): Promise<void> => {
    await api.delete(`${BASE}/rm-config/thresholds/${thresholdId}`);
  },

  // ─── Audit Logs (F041) ────────────────────────────────────────────────────

  listAuditLogs: async (params?: {
    page?: number;
    per_page?: number;
    entity_type?: string;
    action?: string;
    user_id?: string;
    from_date?: string;
    to_date?: string;
  }): Promise<ApiResponse<unknown[]>> => {
    const { data } = await api.get(`${BASE}/audit-logs`, { params });
    return data;
  },
};
