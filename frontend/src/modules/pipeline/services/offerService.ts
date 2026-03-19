import api from "../../../services/api";
import type {
  ApiResponse,
  Offer,
  OfferListItem,
  OfferCreate,
  OfferUpdate,
  OfferLineItemCreate,
  OfferAnalytics,
} from "../../../types";

const BASE = "/pipeline/offers";

export interface OfferFilters {
  page?: number;
  per_page?: number;
  status?: string;
  contact_id?: string;
  search?: string;
}

export const offerService = {
  // F019 — List offers with filtering
  list: async (filters: OfferFilters = {}): Promise<ApiResponse<OfferListItem[]>> => {
    const { data } = await api.get(BASE, { params: filters });
    return data;
  },

  // F019 — Get single offer with line items
  get: async (id: string): Promise<ApiResponse<Offer>> => {
    const { data } = await api.get(`${BASE}/${id}`);
    return data;
  },

  // F019 — Create offer with line items
  create: async (payload: OfferCreate): Promise<ApiResponse<Offer>> => {
    const { data } = await api.post(BASE, payload);
    return data;
  },

  // F019 — Update draft offer
  update: async (id: string, payload: OfferUpdate): Promise<ApiResponse<Offer>> => {
    const { data } = await api.put(`${BASE}/${id}`, payload);
    return data;
  },

  // F019 — Delete draft offer
  delete: async (id: string): Promise<void> => {
    await api.delete(`${BASE}/${id}`);
  },

  // F019 — Add line item
  addLineItem: async (offerId: string, item: OfferLineItemCreate): Promise<ApiResponse<Offer>> => {
    const { data } = await api.post(`${BASE}/${offerId}/items`, item);
    return data;
  },

  // F019 — Update line item
  updateLineItem: async (
    offerId: string,
    itemId: string,
    item: Partial<OfferLineItemCreate>
  ): Promise<ApiResponse<Offer>> => {
    const { data } = await api.put(`${BASE}/${offerId}/items/${itemId}`, item);
    return data;
  },

  // F019 — Delete line item
  deleteLineItem: async (offerId: string, itemId: string): Promise<void> => {
    await api.delete(`${BASE}/${offerId}/items/${itemId}`);
  },

  // F028 — Submit for approval
  submit: async (id: string): Promise<ApiResponse<Offer>> => {
    const { data } = await api.post(`${BASE}/${id}/submit`);
    return data;
  },

  // F028 — Approve/reject
  approve: async (
    id: string,
    decision: { approved: boolean; comment?: string }
  ): Promise<ApiResponse<Offer>> => {
    const { data } = await api.post(`${BASE}/${id}/approve`, decision);
    return data;
  },

  // F027 — Send to client (status → SENT)
  send: async (id: string): Promise<ApiResponse<Offer>> => {
    const { data } = await api.post(`${BASE}/${id}/send`);
    return data;
  },

  // F027 — Update status
  updateStatus: async (
    id: string,
    status: string,
    reason?: string
  ): Promise<ApiResponse<Offer>> => {
    const { data } = await api.patch(`${BASE}/${id}/status`, { status, rejection_reason: reason });
    return data;
  },

  // F026 — Create new version
  createVersion: async (
    id: string,
    lineItems?: OfferLineItemCreate[]
  ): Promise<ApiResponse<Offer>> => {
    const { data } = await api.post(`${BASE}/${id}/version`, {
      line_items: lineItems,
    });
    return data;
  },

  // F026 — List versions
  listVersions: async (id: string): Promise<ApiResponse<Offer[]>> => {
    const { data } = await api.get(`${BASE}/${id}/versions`);
    return data;
  },

  // F023 — Generate PDF/DOC
  generateDocument: async (
    id: string,
    format: "pdf" | "docx" = "pdf"
  ): Promise<ApiResponse<{ document_url: string }>> => {
    const { data } = await api.post(`${BASE}/${id}/generate-document`, { format });
    return data;
  },

  // F049 — Quick quote (simplified)
  createQuick: async (payload: {
    contact_id: string;
    title: string;
    total_value: number;
    currency?: string;
    valid_until?: string;
    notes?: string;
  }): Promise<ApiResponse<Offer>> => {
    const { data } = await api.post(`${BASE}/quick`, payload);
    return data;
  },

  // F029 — Analytics
  getAnalytics: async (params?: {
    contact_id?: string;
    date_from?: string;
    date_to?: string;
  }): Promise<ApiResponse<OfferAnalytics>> => {
    const { data } = await api.get(`${BASE}/analytics`, { params });
    return data;
  },
};
