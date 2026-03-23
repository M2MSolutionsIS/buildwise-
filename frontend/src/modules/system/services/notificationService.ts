import api from "../../../services/api";
import type { ApiResponse, AppNotification } from "../../../types";

const BASE = "/system/notifications";

export const notificationService = {
  list: async (params?: {
    notification_status?: string;
    page?: number;
    per_page?: number;
  }): Promise<ApiResponse<AppNotification[]>> => {
    const { data } = await api.get(BASE, { params });
    return data;
  },

  markRead: async (id: string): Promise<ApiResponse<AppNotification>> => {
    const { data } = await api.put(`${BASE}/${id}/read`);
    return data;
  },

  markAllRead: async (): Promise<ApiResponse<{ marked_read: number }>> => {
    const { data } = await api.put(`${BASE}/read-all`);
    return data;
  },

  generateFollowUps: async (): Promise<ApiResponse<AppNotification[]>> => {
    const { data } = await api.post(`${BASE}/follow-up`);
    return data;
  },
};
