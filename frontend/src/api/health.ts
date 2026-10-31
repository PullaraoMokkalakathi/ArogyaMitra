import { API_V1_URL, getAuthHeaders, parseErrorMessage } from "./client";

const API_BASE = API_V1_URL;

export interface HealthProfile {
  age: number;
  gender: string;
  height_cm: number;
  weight_kg: number;
  fitness_goal: string;
  activity_level: string;
}

export interface HealthProfileResponse extends HealthProfile {
  id: number;
  user_id: number;
  created_at: string;
  updated_at: string;
}



export async function createHealthProfile(data: HealthProfile): Promise<HealthProfileResponse> {
  const response = await fetch(`${API_BASE}/health/profile`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: "Failed to create health profile" }));
    throw new Error(parseErrorMessage(errorData));
  }

  return response.json();
}

export async function getHealthProfile(): Promise<HealthProfileResponse> {
  const response = await fetch(`${API_BASE}/health/profile`, {
    method: "GET",
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: "Failed to fetch health profile" }));
    throw new Error(parseErrorMessage(errorData));
  }

  return response.json();
}

export async function updateHealthProfile(data: Partial<HealthProfile>): Promise<HealthProfileResponse> {
  const response = await fetch(`${API_BASE}/health/profile`, {
    method: "PUT",
    headers: getAuthHeaders(),
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: "Failed to update health profile" }));
    throw new Error(parseErrorMessage(errorData));
  }

  return response.json();
}

export async function checkHealthProfile(): Promise<{ exists: boolean }> {
  const response = await fetch(`${API_BASE}/health/profile`, {
    method: "GET",
    headers: getAuthHeaders(),
  });

  if (response.status === 404) {
    return { exists: false };
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: "Failed to check health profile" }));
    throw new Error(parseErrorMessage(errorData));
  }

  return { exists: true };
}

export async function fetchHealthProfile(): Promise<HealthProfileResponse> {
  const response = await fetch(`${API_BASE}/health/profile`, {
    method: "GET",
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: "Failed to fetch health profile" }));
    throw new Error(parseErrorMessage(errorData));
  }

  return response.json();
}