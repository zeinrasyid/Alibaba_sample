import type {
  UserResponse,
  ApiKeyResponse,
  ApiKeyValidationResponse,
  Transaction,
  Budget,
} from "@/types";

const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export class ApiRequestError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiRequestError";
    this.status = status;
  }
}

export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  try {
    const response = await fetch(`${BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });

    if (!response.ok) {
      let detail = "Terjadi kesalahan";
      try {
        const body = await response.json();
        if (body.detail) {
          detail = body.detail;
        }
      } catch {
        // response body not JSON, use default message
      }
      throw new ApiRequestError(response.status, detail);
    }

    return response.json() as Promise<T>;
  } catch (error) {
    if (error instanceof ApiRequestError) throw error;
    throw new ApiRequestError(
      0,
      "Tidak dapat terhubung ke server, periksa koneksi internet Anda"
    );
  }
}

export function createUser(
  username: string,
  email: string,
  inviteCode: string
): Promise<UserResponse> {
  return apiRequest<UserResponse>("/api/v1/users/", {
    method: "POST",
    body: JSON.stringify({ username, email, invite_code: inviteCode }),
  });
}

export function generateApiKey(
  username: string,
  email: string
): Promise<ApiKeyResponse> {
  return apiRequest<ApiKeyResponse>("/api/v1/generate-api-key/", {
    method: "POST",
    body: JSON.stringify({ username, email }),
  });
}

export function validateApiKey(
  apiKey: string
): Promise<ApiKeyValidationResponse> {
  return apiRequest<ApiKeyValidationResponse>("/api/v1/validate-api-key/", {
    method: "POST",
    body: JSON.stringify({ api_key: apiKey }),
  });
}

export function getUser(email: string): Promise<UserResponse> {
  return apiRequest<UserResponse>(`/api/v1/users/${encodeURIComponent(email)}`);
}

export function getTransactions(
  email: string,
  month?: number,
  year?: number
): Promise<Transaction[]> {
  const params = new URLSearchParams({ email });
  if (month !== undefined) params.set("month", String(month));
  if (year !== undefined) params.set("year", String(year));
  return apiRequest<Transaction[]>(`/api/v1/transactions/?${params.toString()}`);
}

export function getBudgets(
  email: string,
  month?: number,
  year?: number
): Promise<Budget[]> {
  const params = new URLSearchParams({ email });
  if (month !== undefined) params.set("month", String(month));
  if (year !== undefined) params.set("year", String(year));
  return apiRequest<Budget[]>(`/api/v1/budgets/?${params.toString()}`);
}
