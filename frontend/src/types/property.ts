export type PropertyType = "apartment" | "hostel_room" | "hostel_common" | "villa" | "other";
export type PropertyRegion =
  | "asturias"
  | "madrid"
  | "malaga"
  | "costa_brava"
  | "ibiza"
  | "la_manga"
  | "other";
export type PropertyStatus = "active" | "inactive" | "maintenance";

export interface PropertySummary {
  id: string;
  name: string;
  slug: string;
  type: PropertyType;
  region: PropertyRegion;
  status: PropertyStatus;
  capacity: number | null;
  bedrooms: number | null;
  bathrooms: number | null;
  latitude: number | null;
  longitude: number | null;
  tags: string[];
  created_at: string;
  updated_at: string;
}

export interface PropertyDetail extends PropertySummary {
  address: string | null;
  guesty_listing_id: string | null;
  cloudbeds_property_id: string | null;
  "metadata_": Record<string, unknown>;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
}
