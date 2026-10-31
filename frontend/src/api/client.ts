/**
 * Centralized API configuration and client utilities for ArogyaMitra.
 * Reads backend URL from Vite environment variables (VITE_API_BASE_URL)
 * with a fallback to local development server (http://127.0.0.1:8000).
 */
import axios from "axios";

export const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000"
).replace(/\/$/, "");

export const API_V1_URL = `${API_BASE_URL}/api/v1`;

/**
 * Pre-configured Axios instance using the centralized environment base URL.
 * Automatically injects the JWT access token from localStorage when present.
 */
export const apiClient = axios.create({
  baseURL: API_V1_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

/**
 * Returns authorization headers with bearer token if present in localStorage.
 */
export function getAuthHeaders(customHeaders: Record<string, string> = {}): Record<string, string> {
  const token = localStorage.getItem("access_token");
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...customHeaders,
  };
}

/**
 * Helper to safely extract error messages from API response bodies.
 */
export function parseErrorMessage(data: unknown, fallback = "An unexpected error occurred"): string {
  if (!data || typeof data !== "object") {
    return fallback;
  }
  const obj = data as Record<string, unknown>;
  if (Array.isArray(obj.detail)) {
    return obj.detail
      .map((e) => (typeof e === "object" && e?.msg ? `${e.loc?.join(".")} - ${e.msg}` : String(e)))
      .join("; ");
  }
  if (typeof obj.detail === "string") {
    return obj.detail;
  }
  if (typeof obj.message === "string") {
    return obj.message;
  }
  return fallback;
}
