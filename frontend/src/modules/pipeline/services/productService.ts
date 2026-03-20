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
};
