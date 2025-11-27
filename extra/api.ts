<<<<<<< Updated upstream
// API Base URL - defaults to http://127.0.0.1:5173/ if VITE_API_URL is not set
const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5173/';

=======
>>>>>>> Stashed changes
export interface ApiUser {
  id: number;
  name: string;
}

export interface ApiMessage {
  id: number;
  sender_id: number;
  recipient_id: number;
  ciphertext?: string;
  nonce?: string;
  timestamp: string;
  decrypted?: string;
}

const API_BASE = (import.meta.env.VITE_API_URL as string) || "http://127.0.0.1:8000";

async function safeJson(res: Response) {
  const txt = await res.text();
  try {
    return JSON.parse(txt);
  } catch {
    return txt;
  }
}

async function handleResponse(res: Response) {
  if (!res.ok) {
    const body = await safeJson(res);
    const err = new Error(typeof body === "string" ? body : JSON.stringify(body));
    // @ts-ignore
    err.status = res.status;
    throw err;
  }
  return safeJson(res);
}

export interface HealthStatus {
  status: string;
}

export async function createUser(name: string): Promise<ApiUser> {
  const res = await fetch(`${API_BASE}/users/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
  return handleResponse(res) as Promise<ApiUser>;
}

export async function listUsers(): Promise<ApiUser[]> {
  const res = await fetch(`${API_BASE}/users/`);
  return handleResponse(res) as Promise<ApiUser[]>;
}

export async function sendMessage(
  sender_id: number,
  recipient_id: number,
  message: string
): Promise<ApiMessage> {
  const res = await fetch(`${API_BASE}/messages/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ sender_id, recipient_id, message }),
  });
  return handleResponse(res) as Promise<ApiMessage>;
}

export async function getConversation(userA: number, userB: number): Promise<ApiMessage[]> {
  const res = await fetch(`${API_BASE}/conversations/${userA}/${userB}`);
  return handleResponse(res) as Promise<ApiMessage[]>;
}

export async function getHealth(): Promise<HealthStatus> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) {
    throw new Error(`Failed to get health status: ${res.status} ${res.statusText}`);
  }
  return res.json();
}
