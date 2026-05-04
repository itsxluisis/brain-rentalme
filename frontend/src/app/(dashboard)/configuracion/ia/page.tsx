"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { RefreshCw, CheckCircle, Database } from "lucide-react";
import { api } from "@/lib/api/client";

interface EmbeddingStats {
  total: number;
  embedded: number;
  pending: number;
  coverage_pct: number;
}

async function getEmbeddingStats(): Promise<EmbeddingStats> {
  const { data } = await api.get<EmbeddingStats>("/api/v1/knowledge/stats/embeddings");
  return data;
}

async function triggerReindex(): Promise<{ queued: number }> {
  const { data } = await api.post<{ queued: number }>("/api/v1/knowledge/reindex");
  return data;
}

export default function IAConfigPage() {
  const queryClient = useQueryClient();

  const { data: stats, isLoading } = useQuery({
    queryKey: ["embedding-stats"],
    queryFn: getEmbeddingStats,
    refetchInterval: 10000,
  });

  const reindexMutation = useMutation({
    mutationFn: triggerReindex,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["embedding-stats"] }),
  });

  const coverageColor =
    !stats ? "bg-white/20"
    : stats.coverage_pct >= 90 ? "bg-green-500"
    : stats.coverage_pct >= 60 ? "bg-amber-500"
    : "bg-red-500";

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-xl font-bold text-white/90">Configuración IA</h1>
        <p className="mt-1 text-sm text-white/45">
          Gestiona los modelos de IA y el estado de indexación de conocimiento.
        </p>
      </div>

      {/* AI Models info */}
      <div className="mb-4 glass-card p-6">
        <h2 className="mb-4 font-semibold text-white/90">Modelos configurados</h2>
        <div className="space-y-3">
          <div className="flex items-center justify-between rounded-sm border border-surface-border p-3">
            <div>
              <p className="text-sm text-white/80">Embeddings</p>
              <p className="text-xs text-white/40">OpenAI text-embedding-3-small (1536d)</p>
            </div>
            <span className="rounded-sm bg-blue-500/10 px-2 py-0.5 text-xs text-blue-400">OpenAI</span>
          </div>
          <div className="flex items-center justify-between rounded-sm border border-surface-border p-3">
            <div>
              <p className="text-sm text-white/80">Chat RAG</p>
              <p className="text-xs text-white/40">Anthropic claude-sonnet-4-20250514</p>
            </div>
            <span className="rounded-sm bg-violet-500/10 px-2 py-0.5 text-xs text-violet-400">Anthropic</span>
          </div>
        </div>
        <p className="mt-3 text-xs text-white/30">
          Configura las API keys en{" "}
          <a href="/configuracion/integraciones" className="text-accent hover:underline">Integraciones</a>.
        </p>
      </div>

      {/* Embedding coverage */}
      <div className="glass-card p-6">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="font-semibold text-white/90">Cobertura de embeddings</h2>
          <button
            onClick={() => reindexMutation.mutate()}
            disabled={reindexMutation.isPending || (stats?.pending === 0)}
            className="flex items-center gap-1.5 rounded-input border border-surface-border px-3 py-1.5 text-sm text-white/55 hover:border-accent/50 hover:text-accent disabled:opacity-40"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${reindexMutation.isPending ? "animate-spin" : ""}`} />
            Re-indexar pendientes
          </button>
        </div>

        {isLoading ? (
          <div className="h-20 animate-pulse rounded-card bg-surface" />
        ) : stats ? (
          <>
            <div className="mb-4 grid grid-cols-3 gap-4">
              <div className="rounded-sm border border-surface-border p-3 text-center">
                <p className="text-2xl font-bold text-white/90">{stats.total}</p>
                <p className="text-xs text-white/40">Total bloques</p>
              </div>
              <div className="rounded-sm border border-surface-border p-3 text-center">
                <p className="text-2xl font-bold text-green-400">{stats.embedded}</p>
                <p className="text-xs text-white/40">Indexados</p>
              </div>
              <div className="rounded-sm border border-surface-border p-3 text-center">
                <p className={`text-2xl font-bold ${stats.pending > 0 ? "text-amber-400" : "text-white/40"}`}>
                  {stats.pending}
                </p>
                <p className="text-xs text-white/40">Pendientes</p>
              </div>
            </div>

            {/* Progress bar */}
            <div>
              <div className="mb-1 flex justify-between text-xs text-white/40">
                <span>Cobertura</span>
                <span>{stats.coverage_pct}%</span>
              </div>
              <div className="h-2 w-full overflow-hidden rounded-full bg-white/10">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${coverageColor}`}
                  style={{ width: `${stats.coverage_pct}%` }}
                />
              </div>
            </div>

            {reindexMutation.data && (
              <p className="mt-3 flex items-center gap-1 text-sm text-green-400">
                <CheckCircle className="h-4 w-4" />
                {reindexMutation.data.queued} bloques puestos en cola para indexar.
              </p>
            )}

            {stats.pending === 0 && (
              <p className="mt-3 flex items-center gap-1 text-sm text-green-400">
                <CheckCircle className="h-4 w-4" />
                Todos los bloques están indexados.
              </p>
            )}
          </>
        ) : (
          <p className="text-sm text-white/30">Error cargando estadísticas.</p>
        )}
      </div>
    </div>
  );
}
