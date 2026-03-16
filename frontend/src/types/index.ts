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
  is_active: boolean;
  organization_id: string;
}
