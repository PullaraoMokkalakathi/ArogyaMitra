import { API_V1_URL, getAuthHeaders, parseErrorMessage } from "./client";

const API_BASE = `${API_V1_URL}/ai`;

export interface Message {
  role: "user" | "assistant" | "system";
  content: string;
}

export const sendChatMessage = async (messages: Message[]): Promise<string> => {
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({ messages })
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: "Failed to get response" }));
    throw new Error(parseErrorMessage(errorData, "Failed to get response"));
  }
  const data = await res.json();
  return data.response;
};
