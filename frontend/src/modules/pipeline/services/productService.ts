import api from "../../../services/api";
import type { ApiResponse, Product } from "../../../types";

const BASE = "/crm/products";

export interface ProductFilters {
  page?: number;
  per_page?: number;
  search?: string;
  category?: string;
  product_type?: string;
  is_active?: boolean;
}

export interface ProductCreate {
  code: string;
  name: string;
  description?: string;
  product_type: string;
  category?: string;
  unit_of_measure: string;
  unit_price: number;
  currency?: string;
  vat_rate?: number;
  is_active?: boolean;
}

export interface ProductCategory {
  id: string;
  name: string;
  parent_id?: string;
  children?: ProductCategory[];
}

export const productService = {
  // F017 — List products with filtering
  list: async (filters: ProductFilters = {}): Promise<ApiResponse<Product[]>> => {
    const { data } = await api.get(BASE, { params: filters });
    return data;
  },

  // F017 — Get single product
  get: async (id: string): Promise<ApiResponse<Product>> => {
    const { data } = await api.get(`${BASE}/${id}`);
    return data;
  },

  // F017 — Create product
  create: async (payload: ProductCreate): Promise<ApiResponse<Product>> => {
    const { data } = await api.post(BASE, payload);
    return data;
  },

  // F017 — Update product
  update: async (id: string, payload: Partial<ProductCreate>): Promise<ApiResponse<Product>> => {
    const { data } = await api.put(`${BASE}/${id}`, payload);
    return data;
  },

  // F017 — Delete product
  delete: async (id: string): Promise<void> => {
    await api.delete(`${BASE}/${id}`);
  },

  // Product categories
  listCategories: async (): Promise<ApiResponse<ProductCategory[]>> => {
    const { data } = await api.get("/crm/product-categories");
    return data;
  },
};
