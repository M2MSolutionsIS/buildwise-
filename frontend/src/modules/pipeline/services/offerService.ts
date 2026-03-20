import api from "../../../services/api";
import type { ApiResponse } from "../../../types";
import type {
  Offer,
  OfferListItem,
  OfferCreate,
  OfferUpdate,
  OfferVersionCreate,
  OfferEstimation,
  OfferDiff,
  TimelineEvent,
  Product,
} from "../../../types/pipeline";

const BASE = "/pipeline";

export interface OfferFilters {
  page?: number;
  per_page?: number;
  search?: string;
  status?: string;
  contact_id?: string;
}

export const offerService = {
  list: async (filters: OfferFilters = {}): Promise<ApiResponse<OfferListItem[]>> => {
    const { data } = await api.get(`${BASE}/offers`, { params: filters });
    return data;
  },

  get: async (id: string): Promise<ApiResponse<Offer>> => {
    const { data } = await api.get(`${BASE}/offers/${id}`);
    return data;
  },

  create: async (payload: OfferCreate): Promise<ApiResponse<Offer>> => {
    const { data } = await api.post(`${BASE}/offers`, payload);
    return data;
  },

  update: async (id: string, payload: OfferUpdate): Promise<ApiResponse<Offer>> => {
    const { data } = await api.put(`${BASE}/offers/${id}`, payload);
    return data;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`${BASE}/offers/${id}`);
  },

  submit: async (id: string): Promise<ApiResponse<Offer>> => {
    const { data } = await api.post(`${BASE}/offers/${id}/submit`);
    return data;
  },

  approve: async (id: string, approved: boolean, comment?: string): Promise<ApiResponse<Offer>> => {
    const { data } = await api.post(`${BASE}/offers/${id}/approve`, { approved, comment });
    return data;
  },

  createVersion: async (id: string, payload?: OfferVersionCreate): Promise<ApiResponse<Offer>> => {
    const { data } = await api.post(`${BASE}/offers/${id}/version`, payload || {});
    return data;
  },

  send: async (id: string): Promise<ApiResponse<Offer>> => {
    const { data } = await api.post(`${BASE}/offers/${id}/send`);
    return data;
  },

  updateStatus: async (id: string, status: string): Promise<ApiResponse<Offer>> => {
    const { data } = await api.patch(`${BASE}/offers/${id}/status`, { status });
    return data;
  },

  convertToContract: async (id: string): Promise<ApiResponse<{ contract_id: string }>> => {
    const { data } = await api.post(`${BASE}/offers/${id}/convert-to-contract`);
    return data;
  },

  estimate: async (
    id: string,
    payload: { property_id?: string; line_items: unknown[] }
  ): Promise<ApiResponse<OfferEstimation>> => {
    const { data } = await api.post(`${BASE}/offers/${id}/estimate`, payload);
    return data;
  },

  generateDocument: async (id: string): Promise<ApiResponse<{ pdf_url: string }>> => {
    const { data } = await api.post(`${BASE}/offers/${id}/generate-document`, {
      format: "pdf",
    });
    return data;
  },

  getTimeline: async (id: string): Promise<ApiResponse<TimelineEvent[]>> => {
    const { data } = await api.get(`${BASE}/offers/${id}/timeline`);
    return data;
  },

  getVersionDiff: async (
    id: string,
    version1: number,
    version2: number
  ): Promise<ApiResponse<OfferDiff[]>> => {
    const { data } = await api.get(`${BASE}/offers/${id}/diff`, {
      params: { v1: version1, v2: version2 },
    });
    return data;
  },

  // Products catalog
  searchProducts: async (
    search?: string,
    category?: string
  ): Promise<ApiResponse<Product[]>> => {
    const { data } = await api.get("/crm/products", {
      params: { search, category, status: "active", per_page: 20 },
    });
    return data;
  },

  // Contacts search (for wizard step 1)
  searchContacts: async (search: string) => {
    const { data } = await api.get("/crm/contacts", {
      params: { search, per_page: 5 },
    });
    return data;
  },

  // Contact properties
  getContactProperties: async (contactId: string) => {
    const { data } = await api.get(`/crm/contacts/${contactId}/properties`);
    return data;
  },
};
