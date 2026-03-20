// Pipeline Types — Offers, Contracts, Opportunities

export type OfferStatus =
  | "draft"
  | "pending_approval"
  | "approved"
  | "sent"
  | "negotiation"
  | "accepted"
  | "rejected"
  | "expired";

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
  unit_of_measure?: string;
  unit_price: number;
  discount_percent?: number;
  vat_rate?: number;
  sort_order?: number;
}

export interface Offer {
  id: string;
  organization_id: string;
  contact_id: string;
  opportunity_id?: string;
  property_id?: string;
  offer_number: string;
  title: string;
  description?: string;
  status: OfferStatus;
  version: number;
  parent_offer_id?: string;
  is_snapshot: boolean;
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
  next_follow_up?: string;
  follow_up_count: number;
  owner_id?: string;
  template_id?: string;
  is_quick_quote: boolean;
  pdf_path?: string;
  notes?: string;
  created_at: string;
  updated_at?: string;
  line_items: OfferLineItem[];
}

export interface OfferListItem {
  id: string;
  offer_number: string;
  title: string;
  status: OfferStatus;
  version: number;
  contact_id: string;
  subtotal: number;
  total_amount: number;
  currency: string;
  valid_until?: string;
  created_at: string;
}

export interface OfferCreate {
  contact_id: string;
  opportunity_id?: string;
  property_id?: string;
  title: string;
  description?: string;
  currency?: string;
  validity_days?: number;
  terms_and_conditions?: string;
  notes?: string;
  line_items?: OfferLineItemCreate[];
}

export interface OfferUpdate {
  title?: string;
  description?: string;
  contact_id?: string;
  property_id?: string;
  discount_percent?: number;
  currency?: string;
  validity_days?: number;
  terms_and_conditions?: string;
  notes?: string;
  line_items?: OfferLineItemCreate[];
}

export interface OfferVersionCreate {
  changes_description?: string;
}

export interface Product {
  id: string;
  code: string;
  name: string;
  description?: string;
  category?: string;
  unit_of_measure: string;
  unit_price: number;
  is_active: boolean;
}

export interface OfferEstimation {
  energy_savings_percent?: number;
  co2_reduction_kg?: number;
  roi_months?: number;
  cost_breakdown: {
    materials: number;
    labor: number;
    overhead: number;
    total: number;
  };
  surface_calculation?: {
    total_surface_sqm: number;
    glass_surface_sqm: number;
    u_value: number;
    energy_loss_before: number;
    energy_loss_after: number;
  };
}

export interface OfferDiff {
  field: string;
  old_value: string | number | null;
  new_value: string | number | null;
  change_type: "added" | "removed" | "modified";
}

export interface TimelineEvent {
  id: string;
  event_type: string;
  description: string;
  user_name?: string;
  created_at: string;
  metadata?: Record<string, unknown>;
}

// Wizard draft state persisted to localStorage
export interface OfferWizardDraft {
  current_step: number;
  contact_id?: string;
  contact_name?: string;
  property_id?: string;
  property_name?: string;
  opportunity_id?: string;
  title?: string;
  description?: string;
  line_items: OfferLineItemCreate[];
  estimation?: OfferEstimation;
  terms_and_conditions?: string;
  currency: string;
  validity_days: number;
  saved_at?: string;
}
