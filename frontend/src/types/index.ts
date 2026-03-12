// User & Auth
export interface UserSession {
  email: string;
  username: string;
}

export interface UserResponse {
  id: number;
  username: string;
  email: string;
  created_at: string;
}

// API Key
export interface ApiKeyResponse {
  api_key: string;
  user_id: number;
  created_at: string;
  expires_at: string | null;
}

export interface ApiKeyValidationResponse {
  valid: boolean;
  user_id?: number;
  username?: string;
  email?: string;
}

// Financial Data
export type Category =
  | "food"
  | "transport"
  | "shopping"
  | "entertainment"
  | "health"
  | "bills"
  | "education"
  | "other";

export interface Transaction {
  id: number;
  email: string;
  amount: number;
  description: string;
  category: Category;
  type: "expense" | "income";
  payment_method: string | null;
  date: string;
  created_at: string;
}

export interface Budget {
  id: number;
  email: string;
  category: Category;
  amount: number;
  month: number;
  year: number;
  created_at: string;
}

// API Error
export interface ApiError {
  detail: string;
}
