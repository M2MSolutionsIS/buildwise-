import api from "./api";
import type { ApiResponse, TokenResponse, User } from "../types";

const AUTH_BASE = "/api/auth";

export const authService = {
  login: async (email: string, password: string): Promise<TokenResponse> => {
    const { data } = await api.post(`${AUTH_BASE}/login`, { email, password });
    return data;
  },

  register: async (payload: {
    email: string;
    password: string;
    first_name: string;
    last_name: string;
    phone?: string;
    organization_name?: string;
  }): Promise<ApiResponse<User>> => {
    const { data } = await api.post(`${AUTH_BASE}/register`, payload);
    return data;
  },

  refresh: async (refresh_token: string): Promise<TokenResponse> => {
    const { data } = await api.post(`${AUTH_BASE}/refresh`, { refresh_token });
    return data;
  },

  logout: async (): Promise<void> => {
    await api.post(`${AUTH_BASE}/logout`);
  },

  getMe: async (): Promise<ApiResponse<User>> => {
    const { data } = await api.get("/me");
    return data;
  },
};
