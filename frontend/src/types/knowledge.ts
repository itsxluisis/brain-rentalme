export type BlockType =
  | "description"
  | "rules"
  | "access_instructions"
  | "faq"
  | "sop"
  | "integration_guide"
  | "pricing_notes"
  | "checkin_notes"
  | "custom";

export interface KnowledgeBlock {
  id: string;
  entity_type: "property" | "system";
  entity_id: string;
  block_type: BlockType;
  title: string;
  content: string;
  source: "manual" | "guesty_sync" | "cloudbeds_sync" | "import";
  language: "es" | "en" | "both";
  is_active: boolean;
  has_embedding: boolean;
  "metadata_": Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface Relation {
  id: string;
  property_id: string;
  system_id: string;
  notes: string | null;
  config: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}
