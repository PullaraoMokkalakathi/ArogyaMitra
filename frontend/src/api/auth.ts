const API_BASE = "http://127.0.0.1:8000/api/v1/auth";

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterCredentials {
  email: string;
  password: string;
  confirm_password: string;
}

export interface Tokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface LoginResponse {
  success: boolean;
  message: string;
  tokens: Tokens;
  user: Record<string, unknown>;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export async function login(credentials: LoginCredentials): Promise<LoginResponse> {
  const response = await fetch(`${API_BASE}/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(credentials),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Login failed" }));
    throw new Error(error.detail || "Login failed");
  }

  const data: LoginResponse = await response.json();

  if (!data.tokens?.access_token) {
    throw new Error("Invalid login response: no access token received");
  }

  return data;
}

export async function register(data: RegisterCredentials): Promise<AuthResponse> {
  const response = await fetch(`${API_BASE}/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Registration failed" }));
    throw new Error(error.detail || "Registration failed");
  }

  return response.json();
}