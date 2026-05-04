import { api } from "./client";

export interface ChatSession {
  id: string;
  title: string | null;
  scope: string;
  scope_entity_id: string | null;
  updated_at: string | null;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources: SearchResult[] | null;
  created_at: string;
}

export interface SearchResult {
  block_id: string;
  entity_type: string;
  entity_id: string;
  entity_name: string | null;
  block_type: string;
  title: string;
  content_preview: string;
  score: number;
}

export async function listSessions(): Promise<ChatSession[]> {
  const { data } = await api.get<ChatSession[]>("/api/v1/chat/sessions");
  return data;
}

export async function createSession(scope = "all", scope_entity_id?: string): Promise<ChatSession> {
  const { data } = await api.post<ChatSession>("/api/v1/chat/sessions", { scope, scope_entity_id });
  return data;
}

export async function renameSession(id: string, title: string): Promise<ChatSession> {
  const { data } = await api.patch<ChatSession>(`/api/v1/chat/sessions/${id}`, { title });
  return data;
}

export async function deleteSession(id: string): Promise<void> {
  await api.delete(`/api/v1/chat/sessions/${id}`);
}

export async function getMessages(sessionId: string): Promise<ChatMessage[]> {
  const { data } = await api.get<ChatMessage[]>(`/api/v1/chat/sessions/${sessionId}/messages`);
  return data;
}
