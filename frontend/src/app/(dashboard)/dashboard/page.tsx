"use client";

import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { Database, Building2, Settings, RefreshCw, MessageSquare, Plus } from "lucide-react";
import { getAdminStats } from "@/lib/api/admin";
import { triggerSync } from "@/lib/api/sync";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";

function StatCard({
  icon,
  label,
  value,
  subtext,
}: {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  subtext?: string;
}) {
  return (
    <div className="glass-card p-5">
      <div className="mb-3 flex items-center gap-2 text-white/40">
        {icon}
        <span className="text-xs uppercase tracking-wide">{label}</span>
      </div>
      <p className="text-3xl font-bold text-white/90">{value}</p>
      {subtext && <p className="mt-1 text-xs text-white/35">{subtext}</p>}
    </div>
  );
}

export default function DashboardPage() {
  const queryClient = useQueryClient();

  const { data: stats, isLoading } = useQuery({
    queryKey: ["admin-stats"],
    queryFn: getAdminStats,
    refetchInterval: 60000,
  });

  const syncMutation = useMutation({
    mutationFn: () => triggerSync("guesty"),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-stats"] });
      queryClient.invalidateQueries({ queryKey: ["sync-status"] });
    },
  });

  const coveragePct = stats
    ? stats.knowledge_blocks_count > 0
      ? Math.round((stats.blocks_with_embeddings / stats.knowledge_blocks_count) * 100)
      : 0
    : null;

  return (
    <div>
      <div className="mb-6 flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white/90">Dashboard</h1>
          <p className="mt-1 text-sm text-white/45">BrAIn — Base de Conocimiento RentalMe.es</p>
        </div>
        <div className="flex gap-2">
          <Link
            href="/propiedades/nueva"
            className="flex items-center gap-1.5 rounded-input border border-surface-border px-3 py-1.5 text-sm text-white/55 hover:border-accent/50 hover:text-accent"
          >
            <Plus className="h-3.5 w-3.5" />
            Nueva propiedad
          </Link>
          <button
            onClick={() => syncMutation.mutate()}
            disabled={syncMutation.isPending}
            className="flex items-center gap-1.5 rounded-input bg-accent px-3 py-1.5 text-sm text-white hover:bg-accent-hover disabled:opacity-50"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${syncMutation.isPending ? "animate-spin" : ""}`} />
            Sincronizar Guesty
          </button>
        </div>
      </div>

      {/* Stats grid */}
      {isLoading ? (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          {[1, 2, 3, 4].map((i) => <div key={i} className="h-28 animate-pulse rounded-card bg-surface" />)}
        </div>
      ) : (
        <div className="mb-8 grid grid-cols-2 gap-4 sm:grid-cols-4">
          <StatCard
            icon={<Building2 className="h-4 w-4" />}
            label="Propiedades"
            value={stats?.properties_count ?? 0}
          />
          <StatCard
            icon={<Settings className="h-4 w-4" />}
            label="Sistemas"
            value={stats?.systems_count ?? 0}
          />
          <StatCard
            icon={<Database className="h-4 w-4" />}
            label="Bloques de conocimiento"
            value={stats?.knowledge_blocks_count ?? 0}
            subtext={coveragePct !== null ? `${coveragePct}% indexados` : undefined}
          />
          <StatCard
            icon={<RefreshCw className="h-4 w-4" />}
            label="Última sincronización"
            value={stats?.last_sync ? (stats.last_sync.status === "completed" ? "OK" : "Error") : "—"}
            subtext={
              stats?.last_sync
                ? `${stats.last_sync.listings_processed} propiedades — ${new Date(stats.last_sync.started_at).toLocaleDateString("es-ES")}`
                : "Sin sincronizaciones"
            }
          />
        </div>
      )}

      {/* Quick actions */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
        <Link href="/propiedades" className="glass-card p-5 transition-all hover:border-accent/30">
          <Building2 className="mb-3 h-6 w-6 text-accent/70" />
          <h3 className="font-medium text-white/85">Propiedades</h3>
          <p className="mt-1 text-sm text-white/40">Gestiona tu cartera de alojamientos</p>
        </Link>
        <Link href="/sistemas" className="glass-card p-5 transition-all hover:border-accent/30">
          <Settings className="mb-3 h-6 w-6 text-accent/70" />
          <h3 className="font-medium text-white/85">Sistemas</h3>
          <p className="mt-1 text-sm text-white/40">PMS, acceso, pricing y más</p>
        </Link>
        <Link href="/chat" className="glass-card p-5 transition-all hover:border-accent/30">
          <MessageSquare className="mb-3 h-6 w-6 text-accent/70" />
          <h3 className="font-medium text-white/85">Chat RAG</h3>
          <p className="mt-1 text-sm text-white/40">Pregunta sobre tu base de conocimiento</p>
        </Link>
        <Link href="/sincronizacion" className="glass-card p-5 transition-all hover:border-accent/30">
          <RefreshCw className="mb-3 h-6 w-6 text-accent/70" />
          <h3 className="font-medium text-white/85">Sincronización</h3>
          <p className="mt-1 text-sm text-white/40">Historial y conflictos de Guesty</p>
        </Link>
        <Link href="/configuracion/integraciones" className="glass-card p-5 transition-all hover:border-accent/30">
          <Database className="mb-3 h-6 w-6 text-accent/70" />
          <h3 className="font-medium text-white/85">Configuración</h3>
          <p className="mt-1 text-sm text-white/40">API keys, credenciales, usuarios</p>
        </Link>
      </div>
    </div>
  );
}
