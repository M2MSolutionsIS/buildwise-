import api from "../../../services/api";
import type { ApiResponse, CrmDocumentListItem, CrmDocument, CrmDocumentCreate } from "../../../types";

const BASE = "/crm/documents";

export const documentService = {
  list: async (
    entityType: string,
    entityId: string,
  ): Promise<ApiResponse<CrmDocumentListItem[]>> => {
    const { data } = await api.get(BASE, {
      params: { entity_type: entityType, entity_id: entityId },
    });
    return data;
  },

  get: async (id: string): Promise<ApiResponse<CrmDocument>> => {
    const { data } = await api.get(`${BASE}/${id}`);
    return data;
  },

  create: async (payload: CrmDocumentCreate): Promise<ApiResponse<CrmDocument>> => {
    const { data } = await api.post(BASE, payload);
    return data;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`${BASE}/${id}`);
  },
};
