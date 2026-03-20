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

// Pipeline Types — Offers (F019, F023, F026, F027, F028, F029, F049)

export type OfferStatus =
  | "DRAFT"
  | "PENDING_APPROVAL"
  | "APPROVED"
  | "SENT"
  | "NEGOTIATION"
  | "ACCEPTED"
  | "REJECTED"
  | "EXPIRED";

export interface OfferLineItem {
  id: string;
  offer_id: string;
  product_id?: string;
  description: string;
  quantity: number;
  unit_of_measure: string;
  unit_price: number;
  discount_percent: number;
  vat_rate: number;
  total_price: number;
  sort_order: number;
}

export interface OfferLineItemCreate {
  product_id?: string;
  description: string;
  quantity: number;
  unit_of_measure: string;
  unit_price: number;
  discount_percent?: number;
  vat_rate?: number;
  sort_order?: number;
}

export interface Offer {
  id: string;
  offer_number: string;
  title: string;
  description?: string;
  contact_id: string;
  opportunity_id?: string;
  property_id?: string;
  owner_id?: string;
  template_id?: string;
  status: OfferStatus;
  version: number;
  parent_offer_id?: string;
  is_snapshot: boolean;
  is_quick_quote: boolean;
  subtotal: number;
  discount_percent: number;
  discount_amount: number;
  vat_amount: number;
  total_amount: number;
  currency: string;
  terms_and_conditions?: string;
  validity_days: number;
  valid_until?: string;
  sent_at?: string;
  accepted_at?: string;
  rejected_at?: string;
  rejection_reason?: string;
  next_follow_up?: string;
  follow_up_count: number;
  pdf_path?: string;
  line_items: OfferLineItem[];
  created_by?: string;
  updated_by?: string;
  created_at: string;
  updated_at: string;
}

export interface OfferListItem {
  id: string;
  offer_number: string;
  title: string;
  contact_id: string;
  status: OfferStatus;
  version: number;
  subtotal: number;
  total_amount: number;
  currency: string;
  validity_days: number;
  valid_until?: string;
  is_quick_quote: boolean;
  created_at: string;
}

export interface OfferCreate {
  contact_id: string;
  opportunity_id?: string;
  property_id?: string;
  title: string;
  description?: string;
  currency?: string;
  terms_and_conditions?: string;
  validity_days?: number;
  template_id?: string;
  is_quick_quote?: boolean;
  line_items?: OfferLineItemCreate[];
}

export interface OfferUpdate {
  title?: string;
  description?: string;
  terms_and_conditions?: string;
  validity_days?: number;
  discount_percent?: number;
}

export interface OfferVersionDiff {
  field: string;
  item?: string;
  type: "added" | "deleted" | "modified";
  old_value?: unknown;
  new_value?: unknown;
}

export interface OfferAnalytics {
  total_offers: number;
  by_status: Record<string, number>;
  conversion_rate: number;
  average_value: number;
  total_value: number;
}

// ─── Pipeline Types — Opportunities (F042, F050-F053) ───────────────────────

export type OpportunityStage =
  | "new"
  | "qualified"
  | "scoping"
  | "offering"
  | "sent"
  | "negotiation"
  | "won"
  | "lost";

export interface Opportunity {
  id: string;
  contact_id: string;
  title: string;
  description?: string;
  stage: OpportunityStage;
  stage_entered_at?: string;
  estimated_value?: number;
  currency: string;
  win_probability?: number;
  weighted_value?: number;
  expected_close_date?: string;
  actual_close_date?: string;
  owner_id?: string;
  loss_reason?: string;
  loss_reason_detail?: string;
  won_reason?: string;
  qualification_checklist?: Record<string, unknown>;
  is_qualified: boolean;
  rm_validated: boolean;
  source?: string;
  tags?: string[];
  notes?: string;
  created_at: string;
  updated_at?: string;
}

export interface OpportunityListItem {
  id: string;
  title: string;
  stage: OpportunityStage;
  estimated_value?: number;
  currency: string;
  win_probability?: number;
  weighted_value?: number;
  contact_id: string;
  owner_id?: string;
  expected_close_date?: string;
  created_at: string;
}

export interface OpportunityCreate {
  contact_id: string;
  title: string;
  description?: string;
  stage?: string;
  estimated_value?: number;
  currency?: string;
  expected_close_date?: string;
  owner_id?: string;
  source?: string;
  tags?: string[];
  notes?: string;
}

export interface OpportunityUpdate {
  title?: string;
  description?: string;
  estimated_value?: number;
  currency?: string;
  expected_close_date?: string;
  owner_id?: string;
  source?: string;
  tags?: string[];
  notes?: string;
}

export interface PipelineBoardStage {
  stage: string;
  count: number;
  total_value: number;
  weighted_value: number;
  opportunities: OpportunityListItem[];
}

export interface PipelineBoard {
  stages: PipelineBoardStage[];
  total_pipeline_value: number;
  total_weighted_value: number;
  currency: string;
}

// ─── Activity Types (F054-F056) ─────────────────────────────────────────────

export interface Activity {
  id: string;
  activity_type: string;
  title: string;
  description?: string;
  status: string;
  scheduled_date: string;
  scheduled_end_date?: string;
  duration_minutes?: number;
  completed_at?: string;
  contact_id?: string;
  opportunity_id?: string;
  owner_id?: string;
  visit_data?: Record<string, unknown>;
  measurements?: Record<string, unknown>;
  call_duration_seconds?: number;
  call_outcome?: string;
  email_subject?: string;
  email_tracked: boolean;
  is_recurring: boolean;
  notes?: string;
  created_at: string;
  updated_at?: string;
}

export interface ActivityListItem {
  id: string;
  activity_type: string;
  title: string;
  status: string;
  scheduled_date: string;
  contact_id?: string;
  opportunity_id?: string;
  owner_id?: string;
  created_at: string;
}

// ─── Sales KPI / Dashboard (F058) ───────────────────────────────────────────

export interface SalesKPI {
  total_contacts: number;
  active_contacts: number;
  total_opportunities: number;
  open_opportunities: number;
  won_opportunities: number;
  lost_opportunities: number;
  pipeline_value: number;
  weighted_pipeline_value: number;
  total_offers: number;
  offers_sent: number;
  offers_accepted: number;
  offers_rejected: number;
  conversion_rate: number;
  total_contracts: number;
  active_contracts: number;
  total_revenue: number;
  total_invoiced: number;
  total_paid: number;
  avg_deal_value: number;
  currency: string;
  funnel: { stage: string; count: number; value: number }[];
}

export interface WeightedPipelineStage {
  stage: string;
  count: number;
  total_value: number;
  weighted_value: number;
  win_probability: number;
}

export interface WeightedPipeline {
  stages: WeightedPipelineStage[];
  total_pipeline_value: number;
  total_weighted_value: number;
  currency: string;
}

// Product types (F017)
export interface Product {
  id: string;
  code: string;
  name: string;
  description?: string;
  product_type: string;
  category?: string;
  unit_of_measure: string;
  unit_price: number;
  currency: string;
  vat_rate: number;
  is_active: boolean;
  created_at: string;
}
