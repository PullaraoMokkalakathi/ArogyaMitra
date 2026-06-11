export interface Message {
  role: "user" | "assistant" | "system";
  content: string;
}

export const sendChatMessage = async (messages: Message[]): Promise<string> => {
  const token = localStorage.getItem("access_token");
  const res = await fetch("http://127.0.0.1:8000/api/v1/ai/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify({ messages })
  });
  if (!res.ok) throw new Error("Failed to get response");
  const data = await res.json();
  return data.response;
};
