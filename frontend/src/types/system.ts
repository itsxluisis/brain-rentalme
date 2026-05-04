export type SystemCategory = "pms" | "ai_response" | "access" | "checkin" | "pricing" | "other";
export type SystemStatus = "active" | "inactive" | "testing";

export interface SystemSummary {
  id: string;
  name: string;
  slug: string;
  category: SystemCategory;
  has_api: boolean;
  status: SystemStatus;
  tags: string[];
  created_at: string;
  updated_at: string;
}

export interface SystemDetail extends SystemSummary {
  description: string | null;
  website_url: string | null;
  api_docs_url: string | null;
  "metadata_": Record<string, unknown>;
}
