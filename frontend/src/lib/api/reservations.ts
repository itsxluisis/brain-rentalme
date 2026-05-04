import { api } from "./client";

export interface Reservation {
  id: string;
  guest_name: string;
  property_name: string;
  property_slug: string | null;
  check_in: string | null;
  check_out: string | null;
  status: string;
  channel: string;
  guests_count: number;
}

export async function listReservations(params: {
  property_slug?: string;
  status?: string;
  from_date?: string;
  to_date?: string;
  page?: number;
  limit?: number;
}): Promise<{ items: Reservation[]; total: number }> {
  const { data } = await api.get<{ items: Reservation[]; total: number }>("/api/v1/reservations", { params });
  return data;
}
