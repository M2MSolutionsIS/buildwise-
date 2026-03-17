export type Prototype = "P1" | "P2" | "P3";

export interface ApiResponse<T> {
  data: T;
  meta: {
    total: number;
    page: number;
    per_page: number;
  };
}

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  phone?: string;
  avatar_url?: string;
  is_active: boolean;
  is_superuser: boolean;
  organization_id: string;
  language?: string;
  last_login?: string;
  created_at: string;
  roles: string[];
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

// CRM Types
export interface ContactPerson {
  id: string;
  contact_id: string;
  first_name: string;
  last_name: string;
  role: string;
  email?: string;
  phone?: string;
  is_primary: boolean;
  created_at: string;
}

export interface Contact {
  id: string;
  company_name: string;
  cui?: string;
  registration_number?: string;
  stage: string;
  contact_type: string;
  address?: string;
  city?: string;
  county?: string;
  postal_code?: string;
  country?: string;
  phone?: string;
  email?: string;
  website?: string;
  vat_payer?: boolean;
  bank_account?: string;
  bank_name?: string;
  gdpr_consent?: boolean;
  tags?: string[];
  source?: string;
  notes?: string;
  persons: ContactPerson[];
  created_by?: string;
  updated_by?: string;
  created_at: string;
  updated_at: string;
}

export interface ContactListItem {
  id: string;
  company_name: string;
  cui?: string;
  stage: string;
  contact_type: string;
  city?: string;
  county?: string;
  phone?: string;
  email?: string;
  created_at: string;
}

export interface ContactCreate {
  company_name: string;
  cui?: string;
  registration_number?: string;
  stage?: string;
  contact_type?: string;
  address?: string;
  city?: string;
  county?: string;
  postal_code?: string;
  country?: string;
  phone?: string;
  email?: string;
  website?: string;
  vat_payer?: boolean;
  bank_account?: string;
  bank_name?: string;
  gdpr_consent?: boolean;
  tags?: string[];
  source?: string;
  notes?: string;
  persons?: Omit<ContactPerson, "id" | "contact_id" | "created_at">[];
}

export interface Interaction {
  id: string;
  contact_id: string;
  user_id: string;
  interaction_type: string;
  subject: string;
  description?: string;
  interaction_date: string;
  duration_minutes?: number;
  opportunity_id?: string;
  offer_id?: string;
  contract_id?: string;
  metadata_json?: Record<string, unknown>;
  created_at: string;
}

export interface Property {
  id: string;
  contact_id: string;
  name: string;
  property_type: string;
  address?: string;
  city?: string;
  county?: string;
  country?: string;
  total_area_sqm?: number;
  heated_area_sqm?: number;
  floors_count?: number;
  year_built?: number;
  year_renovated?: number;
  structure_material?: string;
  facade_material?: string;
  roof_type?: string;
  energy_certificate?: string;
  energy_class?: string;
  custom_data?: Record<string, unknown>;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface DuplicateMatch {
  contact_id: string;
  company_name: string;
  cui?: string;
  email?: string;
  score: number;
}

export interface DuplicateCheckResponse {
  has_duplicates: boolean;
  matches: DuplicateMatch[];
}
