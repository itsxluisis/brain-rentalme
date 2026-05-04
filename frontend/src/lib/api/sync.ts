import { api } from "./client";

export interface SyncLogEntry {
  id: string;
  provider: string;
  status: string;
  listings_processed: number;
  blocks_created: number;
  blocks_updated: number;
  blocks_skipped: number;
  errors: string[];
  started_at: string;
  completed_at: string | null;
}

export interface SyncStatus {
  is_running: boolean;
  last_sync: SyncLogEntry | null;
}

export async function getSyncStatus(): Promise<SyncStatus> {
  const { data } = await api.get<SyncStatus>("/api/v1/sync/status");
  return data;
}

export async function triggerSync(provider = "guesty"): Promise<{ message: string }> {
  const { data } = await api.post<{ message: string }>("/api/v1/sync/trigger", { provider });
  return data;
}

export async function getSyncLogs(page = 1, limit = 20): Promise<{ items: SyncLogEntry[]; total: number }> {
  const { data } = await api.get<{ items: SyncLogEntry[]; total: number }>("/api/v1/sync/logs", {
    params: { page, limit },
  });
  return data;
}

export interface ConflictEntry {
  block_id: string;
  title: string;
  local_content: string;
  property_name: string;
  property_slug: string;
  updated_at: string;
}

export async function getSyncConflicts(): Promise<ConflictEntry[]> {
  const { data } = await api.get<ConflictEntry[]>("/api/v1/sync/conflicts");
  return data;
}

export async function resolveConflict(blockId: string, resolution: "keep_local" | "accept_remote"): Promise<void> {
  await api.post(`/api/v1/sync/conflicts/${blockId}/resolve`, { resolution });
}
