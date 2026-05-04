import { api } from "./client";
import type { PaginatedResponse, PropertyDetail, PropertySummary } from "@/types/property";

export interface ListPropertiesParams {
  page?: number;
  limit?: number;
  region?: string;
  type?: string;
  status?: string;
  search?: string;
}

export async function listProperties(
  params: ListPropertiesParams = {}
): Promise<PaginatedResponse<PropertySummary>> {
  const { data } = await api.get<PaginatedResponse<PropertySummary>>("/api/v1/properties", {
    params,
  });
  return data;
}

export async function getProperty(slug: string): Promise<PropertyDetail> {
  const { data } = await api.get<PropertyDetail>(`/api/v1/properties/${slug}`);
  return data;
}

export async function createProperty(payload: Partial<PropertyDetail>): Promise<PropertyDetail> {
  const { data } = await api.post<PropertyDetail>("/api/v1/properties", payload);
  return data;
}

export async function updateProperty(
  slug: string,
  payload: Partial<PropertyDetail>
): Promise<PropertyDetail> {
  const { data } = await api.patch<PropertyDetail>(`/api/v1/properties/${slug}`, payload);
  return data;
}

export async function deleteProperty(slug: string): Promise<void> {
  await api.delete(`/api/v1/properties/${slug}`);
}
