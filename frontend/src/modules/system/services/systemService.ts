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
