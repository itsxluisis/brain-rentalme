import { api } from "./client";

export interface AutomationTask {
  id: string;
  name: string;
  action_type: string;
  schedule_type: string;
  schedule_config: Record<string, unknown>;
  is_active: boolean;
  last_run_at: string | null;
  next_run_at: string | null;
  last_status: string | null;
  created_at: string;
}

export async function listAutomations(): Promise<AutomationTask[]> {
  const { data } = await api.get<AutomationTask[]>("/api/v1/automations");
  return data;
}

export async function createAutomation(payload: {
  name: string;
  action_type: string;
  schedule_type: string;
  schedule_config: Record<string, unknown>;
}): Promise<AutomationTask> {
  const { data } = await api.post<AutomationTask>("/api/v1/automations", payload);
  return data;
}

export async function updateAutomation(id: string, payload: Partial<AutomationTask>): Promise<AutomationTask> {
  const { data } = await api.patch<AutomationTask>(`/api/v1/automations/${id}`, payload);
  return data;
}

export async function deleteAutomation(id: string): Promise<void> {
  await api.delete(`/api/v1/automations/${id}`);
}
