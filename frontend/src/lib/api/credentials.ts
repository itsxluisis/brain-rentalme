import { api } from "./client";

export interface CredentialInfo {
  id: string;
  service_name: string;
  updated_at: string | null;
  has_value: boolean;
}

export async function listCredentials(): Promise<CredentialInfo[]> {
  const { data } = await api.get<CredentialInfo[]>("/api/v1/credentials");
  return data;
}

export async function upsertCredential(serviceName: string, value: string): Promise<void> {
  await api.put(`/api/v1/credentials/${serviceName}`, { value });
}

export async function deleteCredential(serviceName: string): Promise<void> {
  await api.delete(`/api/v1/credentials/${serviceName}`);
}

export async function testCredential(serviceName: string): Promise<{ status: "ok" | "error"; message?: string }> {
  const { data } = await api.post(`/api/v1/credentials/${serviceName}/test`);
  return data;
}
