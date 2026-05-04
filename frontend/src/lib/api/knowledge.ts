import { api } from "./client";
import type { KnowledgeBlock, Relation } from "@/types/knowledge";
import type { PaginatedResponse } from "@/types/property";

export async function listBlocks(params: {
  entity_type?: string;
  entity_id?: string;
  block_type?: string;
  page?: number;
  limit?: number;
}): Promise<PaginatedResponse<KnowledgeBlock>> {
  const { data } = await api.get<PaginatedResponse<KnowledgeBlock>>("/api/v1/knowledge", { params });
  return data;
}

export async function createBlock(payload: {
  entity_type: string;
  entity_id: string;
  block_type: string;
  title: string;
  content: string;
  language?: string;
}): Promise<KnowledgeBlock> {
  const { data } = await api.post<KnowledgeBlock>("/api/v1/knowledge", payload);
  return data;
}

export async function updateBlock(
  id: string,
  payload: Partial<KnowledgeBlock>
): Promise<KnowledgeBlock> {
  const { data } = await api.patch<KnowledgeBlock>(`/api/v1/knowledge/${id}`, payload);
  return data;
}

export async function deleteBlock(id: string): Promise<void> {
  await api.delete(`/api/v1/knowledge/${id}`);
}

// Relations
export async function createRelation(payload: {
  property_id: string;
  system_id: string;
  notes?: string;
  config?: Record<string, unknown>;
}): Promise<Relation> {
  const { data } = await api.post<Relation>("/api/v1/relations", payload);
  return data;
}

export async function updateRelation(
  id: string,
  payload: { notes?: string; config?: Record<string, unknown> }
): Promise<Relation> {
  const { data } = await api.patch<Relation>(`/api/v1/relations/${id}`, payload);
  return data;
}

export async function deleteRelation(id: string): Promise<void> {
  await api.delete(`/api/v1/relations/${id}`);
}

export async function getPropertyRelations(propertyId: string): Promise<Relation[]> {
  const { data } = await api.get<Relation[]>(`/api/v1/properties/${propertyId}/relations`);
  return data;
}

export async function getSystemRelations(systemId: string): Promise<Relation[]> {
  const { data } = await api.get<Relation[]>(`/api/v1/systems/${systemId}/relations`);
  return data;
}
