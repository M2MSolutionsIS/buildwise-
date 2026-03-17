import api from "./api";
import type {
  ApiResponse,
  Contact,
  ContactListItem,
  ContactCreate,
  ContactPerson,
  Interaction,
  Property,
  DuplicateCheckResponse,
} from "../types";

const BASE = "/crm";

export interface ContactFilters {
  page?: number;
  per_page?: number;
  search?: string;
  stage?: string;
  contact_type?: string;
  city?: string;
  county?: string;
  source?: string;
}

export const contactService = {
  list: async (filters: ContactFilters = {}): Promise<ApiResponse<ContactListItem[]>> => {
    const { data } = await api.get(`${BASE}/contacts`, { params: filters });
    return data;
  },

  get: async (id: string): Promise<ApiResponse<Contact>> => {
    const { data } = await api.get(`${BASE}/contacts/${id}`);
    return data;
  },

  create: async (payload: ContactCreate): Promise<ApiResponse<Contact>> => {
    const { data } = await api.post(`${BASE}/contacts`, payload);
    return data;
  },

  update: async (id: string, payload: Partial<ContactCreate>): Promise<ApiResponse<Contact>> => {
    const { data } = await api.put(`${BASE}/contacts/${id}`, payload);
    return data;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`${BASE}/contacts/${id}`);
  },

  checkDuplicates: async (payload: ContactCreate): Promise<ApiResponse<DuplicateCheckResponse>> => {
    const { data } = await api.post(`${BASE}/contacts/check-duplicates`, payload);
    return data;
  },

  // Contact Persons
  addPerson: async (
    contactId: string,
    payload: Omit<ContactPerson, "id" | "contact_id" | "created_at">
  ): Promise<ContactPerson> => {
    const { data } = await api.post(`${BASE}/contacts/${contactId}/persons`, payload);
    return data;
  },

  updatePerson: async (
    contactId: string,
    personId: string,
    payload: Partial<ContactPerson>
  ): Promise<ContactPerson> => {
    const { data } = await api.put(`${BASE}/contacts/${contactId}/persons/${personId}`, payload);
    return data;
  },

  deletePerson: async (contactId: string, personId: string): Promise<void> => {
    await api.delete(`${BASE}/contacts/${contactId}/persons/${personId}`);
  },

  // Interactions
  listInteractions: async (
    contactId: string,
    params: { page?: number; per_page?: number; interaction_type?: string } = {}
  ): Promise<ApiResponse<Interaction[]>> => {
    const { data } = await api.get(`${BASE}/contacts/${contactId}/interactions`, { params });
    return data;
  },

  addInteraction: async (
    contactId: string,
    payload: Omit<Interaction, "id" | "contact_id" | "user_id" | "created_at">
  ): Promise<Interaction> => {
    const { data } = await api.post(`${BASE}/contacts/${contactId}/interactions`, payload);
    return data;
  },

  // Properties
  listProperties: async (contactId: string): Promise<ApiResponse<Property[]>> => {
    const { data } = await api.get(`${BASE}/contacts/${contactId}/properties`);
    return data;
  },

  addProperty: async (
    contactId: string,
    payload: Omit<Property, "id" | "contact_id" | "created_at" | "updated_at">
  ): Promise<Property> => {
    const { data } = await api.post(`${BASE}/contacts/${contactId}/properties`, payload);
    return data;
  },

  // Import / Export / Merge
  importContacts: async (rows: Record<string, string>[], skip_duplicates: boolean) => {
    const { data } = await api.post(`${BASE}/contacts/import`, { rows, skip_duplicates });
    return data;
  },

  exportContacts: async (filters: ContactFilters) => {
    const { data } = await api.post(`${BASE}/contacts/export`, filters);
    return data;
  },

  mergeContacts: async (source_id: string, target_id: string, fields_from_source: string[]) => {
    const { data } = await api.post(`${BASE}/contacts/merge`, {
      source_id,
      target_id,
      fields_from_source,
    });
    return data;
  },
};
