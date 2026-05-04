"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Calendar, Users, ArrowRight } from "lucide-react";
import { listReservations } from "@/lib/api/reservations";
import Link from "next/link";

const STATUS_COLORS: Record<string, string> = {
  confirmed: "bg-green-500/10 text-green-400",
  inquiry: "bg-amber-500/10 text-amber-400",
  cancelled: "bg-red-500/10 text-red-400",
  awaiting_payment: "bg-blue-500/10 text-blue-400",
};

const STATUS_LABELS: Record<string, string> = {
  confirmed: "Confirmada",
  inquiry: "Consulta",
  cancelled: "Cancelada",
  awaiting_payment: "Pendiente pago",
};

function formatDate(iso: string | null) {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("es-ES", { day: "2-digit", month: "short", year: "2-digit" });
}

export default function ReservasPage() {
  const [status, setStatus] = useState("");
  const [page, setPage] = useState(1);

  const { data, isLoading, isError } = useQuery({
    queryKey: ["reservations", status, page],
    queryFn: () => listReservations({ status: status || undefined, page, limit: 20 }),
    staleTime: 300_000, // 5 min
  });

  return (
    <div>
      <div className="mb-6 flex items-start justify-between">
        <div>
          <h1 className="text-xl font-bold text-white/90">Reservas</h1>
          <p className="mt-1 text-sm text-white/45">Vista en tiempo real desde Guesty (caché 5 min).</p>
        </div>
        <select
          value={status}
          onChange={(e) => { setStatus(e.target.value); setPage(1); }}
          className="rounded-input border border-surface-border bg-surface px-3 py-1.5 text-sm text-white/70 outline-none focus:border-accent"
        >
          <option value="">Todos los estados</option>
          <option value="confirmed">Confirmadas</option>
          <option value="inquiry">Consultas</option>
          <option value="cancelled">Canceladas</option>
          <option value="awaiting_payment">Pendiente pago</option>
        </select>
      </div>

      {isLoading && (
        <div className="space-y-2">
          {[1, 2, 3, 4, 5].map((i) => <div key={i} className="h-16 animate-pulse rounded-card bg-surface" />)}
        </div>
      )}

      {isError && (
        <div className="glass-card p-8 text-center">
          <p className="text-sm text-red-400">
            Error al cargar reservas. Verifica que la API key de Guesty esté configurada.
          </p>
        </div>
      )}

      {data && (
        <>
          <div className="space-y-2">
            {data.items.length === 0 ? (
              <div className="glass-card py-12 text-center">
                <Calendar className="mx-auto mb-3 h-8 w-8 text-white/20" />
                <p className="text-sm text-white/30">No hay reservas con los filtros seleccionados.</p>
              </div>
            ) : (
              data.items.map((res) => (
                <div key={res.id} className="glass-card p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div>
                        <p className="font-medium text-white/85">{res.guest_name}</p>
                        <p className="text-xs text-white/40">{res.channel}</p>
                      </div>
                      <div className="hidden sm:block">
                        <div className="flex items-center gap-2 text-sm text-white/55">
                          <Calendar className="h-3.5 w-3.5" />
                          {formatDate(res.check_in)}
                          <ArrowRight className="h-3 w-3" />
                          {formatDate(res.check_out)}
                        </div>
                        <div className="flex items-center gap-1 text-xs text-white/35">
                          <Users className="h-3 w-3" />
                          {res.guests_count} huéspedes
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <span
                        className={`rounded-sm px-2 py-0.5 text-xs ${
                          STATUS_COLORS[res.status] ?? "bg-white/5 text-white/40"
                        }`}
                      >
                        {STATUS_LABELS[res.status] ?? res.status}
                      </span>
                      {res.property_slug && (
                        <Link
                          href={`/propiedades/${res.property_slug}`}
                          className="text-xs text-accent/70 hover:text-accent"
                        >
                          {res.property_name}
                        </Link>
                      )}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>

          {data.total > 20 && (
            <div className="mt-4 flex items-center justify-center gap-3">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="rounded-input border border-surface-border px-3 py-1.5 text-sm text-white/55 hover:text-white/90 disabled:opacity-40"
              >
                Anterior
              </button>
              <span className="text-sm text-white/40">Página {page}</span>
              <button
                onClick={() => setPage((p) => p + 1)}
                disabled={page * 20 >= data.total}
                className="rounded-input border border-surface-border px-3 py-1.5 text-sm text-white/55 hover:text-white/90 disabled:opacity-40"
              >
                Siguiente
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
