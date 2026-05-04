import { api } from "./client";

export interface AdminStats {
  properties_count: number;
  systems_count: number;
  knowledge_blocks_count: number;
  blocks_with_embeddings: number;
  last_sync: { status: string; started_at: string; listings_processed: number } | null;
}

export interface ActivityLogs {
  sync_logs: {
    type: string;
    provider: string;
    status: string;
    listings_processed: number;
    started_at: string;
    completed_at: string | null;
  }[];
  tool_api_calls: {
    type: string;
    key_name: string;
    endpoint: string;
    response_ms: number | null;
    results_count: number | null;
    created_at: string;
  }[];
}

export async function getAdminStats(): Promise<AdminStats> {
  const { data } = await api.get<AdminStats>("/api/v1/admin/stats");
  return data;
}

export async function getActivityLogs(): Promise<ActivityLogs> {
  const { data } = await api.get<ActivityLogs>("/api/v1/admin/logs");
  return data;
}

export interface ApiKey {
  id: string;
  name: string;
  is_active: boolean;
  last_used_at: string | null;
  created_at: string;
}

export async function listApiKeys(): Promise<ApiKey[]> {
  const { data } = await api.get<ApiKey[]>("/api/v1/api-keys");
  return data;
}

export async function createApiKey(name: string): Promise<{ id: string; name: string; key: string }> {
  const { data } = await api.post<{ id: string; name: string; key: string }>("/api/v1/api-keys", { name });
  return data;
}

export async function revokeApiKey(id: string): Promise<void> {
  await api.delete(`/api/v1/api-keys/${id}`);
}

export interface UserEntry {
  id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  last_login_at: string | null;
  created_at: string;
}

export async function listUsers(): Promise<UserEntry[]> {
  const { data } = await api.get<UserEntry[]>("/api/v1/users");
  return data;
}

export async function createUser(payload: { email: string; full_name: string; password: string; role: string }): Promise<UserEntry> {
  const { data } = await api.post<UserEntry>("/api/v1/users", payload);
  return data;
}

export async function updateUser(id: string, payload: { role?: string; is_active?: boolean; full_name?: string }): Promise<UserEntry> {
  const { data } = await api.patch<UserEntry>(`/api/v1/users/${id}`, payload);
  return data;
}
