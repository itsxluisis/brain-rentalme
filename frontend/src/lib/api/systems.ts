import { api } from "./client";
import type { PaginatedResponse } from "@/types/property";
import type { SystemDetail, SystemSummary } from "@/types/system";

export async function listSystems(params: {
  page?: number;
  limit?: number;
  category?: string;
  status?: string;
  search?: string;
} = {}): Promise<PaginatedResponse<SystemSummary>> {
  const { data } = await api.get<PaginatedResponse<SystemSummary>>("/api/v1/systems", { params });
  return data;
}

export async function getSystem(slug: string): Promise<SystemDetail> {
  const { data } = await api.get<SystemDetail>(`/api/v1/systems/${slug}`);
  return data;
}

export async function createSystem(payload: Partial<SystemDetail>): Promise<SystemDetail> {
  const { data } = await api.post<SystemDetail>("/api/v1/systems", payload);
  return data;
}

export async function updateSystem(slug: string, payload: Partial<SystemDetail>): Promise<SystemDetail> {
  const { data } = await api.patch<SystemDetail>(`/api/v1/systems/${slug}`, payload);
  return data;
}

export async function deleteSystem(slug: string): Promise<void> {
  await api.delete(`/api/v1/systems/${slug}`);
}

export async function seedSystems(): Promise<{ created: number }> {
  const { data } = await api.post<{ created: number }>("/api/v1/systems/seed");
  return data;
}
