"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { RefreshCw, CheckCircle, XCircle, AlertCircle, GitMerge } from "lucide-react";
import { getSyncStatus, getSyncLogs, triggerSync, getSyncConflicts, resolveConflict } from "@/lib/api/sync";
import Link from "next/link";

function formatDate(iso: string | null) {
  if (!iso) return "—";
  return new Date(iso).toLocaleString("es-ES", { dateStyle: "short", timeStyle: "short" });
}

function StatusBadge({ status }: { status: string }) {
  if (status === "completed") {
    return (
      <span className="flex items-center gap-1 text-xs text-green-400">
        <CheckCircle className="h-3.5 w-3.5" /> Completado
      </span>
    );
  }
  if (status === "failed") {
    return (
      <span className="flex items-center gap-1 text-xs text-red-400">
        <XCircle className="h-3.5 w-3.5" /> Error
      </span>
    );
  }
  return (
    <span className="flex items-center gap-1 text-xs text-amber-400">
      <RefreshCw className="h-3.5 w-3.5 animate-spin" /> En curso
    </span>
  );
}

type Tab = "historial" | "conflictos";

export default function SincronizacionPage() {
  const queryClient = useQueryClient();
  const [tab, setTab] = useState<Tab>("historial");
  const [triggerError, setTriggerError] = useState<string | null>(null);

  const { data: syncStatus, isLoading: statusLoading } = useQuery({
    queryKey: ["sync-status"],
    queryFn: getSyncStatus,
    refetchInterval: (data) => (data?.state?.data?.is_running ? 3000 : 30000),
  });

  const { data: logsData } = useQuery({
    queryKey: ["sync-logs"],
    queryFn: () => getSyncLogs(1, 20),
  });

  const { data: conflicts = [] } = useQuery({
    queryKey: ["sync-conflicts"],
    queryFn: getSyncConflicts,
    enabled: tab === "conflictos",
  });

  const triggerMutation = useMutation({
    mutationFn: () => triggerSync("guesty"),
    onSuccess: () => {
      setTriggerError(null);
      queryClient.invalidateQueries({ queryKey: ["sync-status"] });
      queryClient.invalidateQueries({ queryKey: ["sync-logs"] });
    },
    onError: (err: { response?: { data?: { detail?: string } } }) => {
      setTriggerError(err?.response?.data?.detail ?? "Error al iniciar la sincronización");
    },
  });

  const resolveMutation = useMutation({
    mutationFn: ({ blockId, resolution }: { blockId: string; resolution: "keep_local" | "accept_remote" }) =>
      resolveConflict(blockId, resolution),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["sync-conflicts"] }),
  });

  const isRunning = syncStatus?.is_running ?? false;
  const lastSync = syncStatus?.last_sync;

  return (
    <div>
      <div className="mb-6 flex items-start justify-between">
        <div>
          <h1 className="text-xl font-bold text-white/90">Sincronización</h1>
          <p className="mt-1 text-sm text-white/45">Importa y actualiza propiedades desde Guesty.</p>
        </div>
        <button
          onClick={() => triggerMutation.mutate()}
          disabled={isRunning || triggerMutation.isPending}
          className="flex items-center gap-2 rounded-input bg-accent px-4 py-2 text-sm text-white hover:bg-accent-hover disabled:opacity-50"
        >
          <RefreshCw className={`h-4 w-4 ${isRunning ? "animate-spin" : ""}`} />
          {isRunning ? "Sincronizando..." : "Sincronizar ahora"}
        </button>
      </div>

      {triggerError && (
        <div className="mb-4 flex items-center gap-2 rounded-card border border-red-500/20 bg-red-500/5 p-4 text-sm text-red-400">
          <AlertCircle className="h-4 w-4 shrink-0" />
          {triggerError}
        </div>
      )}

      {/* Status card */}
      <div className="mb-6 glass-card p-6">
        <h2 className="mb-4 font-semibold text-white/90">Estado actual — Guesty</h2>
        {statusLoading ? (
          <div className="h-16 animate-pulse rounded-card bg-surface" />
        ) : lastSync ? (
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            <div>
              <p className="mb-1 text-xs text-white/40">Estado</p>
              <StatusBadge status={isRunning ? "running" : lastSync.status} />
            </div>
            <div>
              <p className="mb-1 text-xs text-white/40">Última ejecución</p>
              <p className="text-sm text-white/75">{formatDate(lastSync.started_at)}</p>
            </div>
            <div>
              <p className="mb-1 text-xs text-white/40">Propiedades procesadas</p>
              <p className="text-sm text-white/75">{lastSync.listings_processed}</p>
            </div>
            <div>
              <p className="mb-1 text-xs text-white/40">Bloques creados / actualizados</p>
              <p className="text-sm text-white/75">
                {lastSync.blocks_created} / {lastSync.blocks_updated}
              </p>
            </div>
          </div>
        ) : (
          <p className="text-sm text-white/30">No se ha realizado ninguna sincronización aún.</p>
        )}
      </div>

      {/* Tabs */}
      <div className="mb-4 flex gap-1 border-b border-surface-border">
        {(["historial", "conflictos"] as Tab[]).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2 text-sm capitalize transition-colors ${
              tab === t
                ? "border-b-2 border-accent text-accent"
                : "text-white/45 hover:text-white/70"
            }`}
          >
            {t === "historial" ? "Historial" : `Conflictos${conflicts.length > 0 ? ` (${conflicts.length})` : ""}`}
          </button>
        ))}
      </div>

      {tab === "historial" && (
        <div className="glass-card p-6">
          {!logsData || logsData.items.length === 0 ? (
            <p className="py-6 text-center text-sm text-white/30">Sin historial.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-surface-border text-left text-xs text-white/40">
                    <th className="pb-2 pr-4">Inicio</th>
                    <th className="pb-2 pr-4">Duración</th>
                    <th className="pb-2 pr-4">Estado</th>
                    <th className="pb-2 pr-4">Procesadas</th>
                    <th className="pb-2 pr-4">Creados</th>
                    <th className="pb-2 pr-4">Actualizados</th>
                    <th className="pb-2">Omitidos</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-surface-border">
                  {logsData.items.map((log) => {
                    const duration = log.completed_at
                      ? `${Math.round((new Date(log.completed_at).getTime() - new Date(log.started_at).getTime()) / 1000)}s`
                      : "—";
                    return (
                      <tr key={log.id} className="text-white/70">
                        <td className="py-2.5 pr-4">{formatDate(log.started_at)}</td>
                        <td className="py-2.5 pr-4 text-white/40">{duration}</td>
                        <td className="py-2.5 pr-4"><StatusBadge status={log.status} /></td>
                        <td className="py-2.5 pr-4">{log.listings_processed}</td>
                        <td className="py-2.5 pr-4 text-green-400/80">{log.blocks_created}</td>
                        <td className="py-2.5 pr-4 text-blue-400/80">{log.blocks_updated}</td>
                        <td className="py-2.5 text-white/40">{log.blocks_skipped}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {tab === "conflictos" && (
        <div className="space-y-3">
          {conflicts.length === 0 ? (
            <div className="glass-card p-8 text-center">
              <GitMerge className="mx-auto mb-3 h-8 w-8 text-white/20" />
              <p className="text-sm text-white/30">
                No hay conflictos. Todos los bloques sincronizados están al día.
              </p>
            </div>
          ) : (
            conflicts.map((conflict) => (
              <div key={conflict.block_id} className="glass-card p-5">
                <div className="mb-3 flex items-start justify-between">
                  <div>
                    <Link
                      href={`/propiedades/${conflict.property_slug}`}
                      className="text-sm font-medium text-accent hover:underline"
                    >
                      {conflict.property_name}
                    </Link>
                    <p className="text-xs text-white/45">{conflict.title}</p>
                  </div>
                  <span className="text-xs text-white/30">
                    Editado {formatDate(conflict.updated_at)}
                  </span>
                </div>

                <pre className="mb-4 max-h-32 overflow-y-auto rounded-sm bg-surface-hover p-3 font-mono text-xs text-white/60 leading-relaxed">
                  {conflict.local_content.slice(0, 500)}
                  {conflict.local_content.length > 500 ? "…" : ""}
                </pre>

                <div className="flex gap-2">
                  <button
                    onClick={() => resolveMutation.mutate({ blockId: conflict.block_id, resolution: "keep_local" })}
                    disabled={resolveMutation.isPending}
                    className="rounded-input border border-surface-border px-3 py-1.5 text-xs text-white/55 hover:border-accent/40 hover:text-accent disabled:opacity-50"
                  >
                    Mantener edición local
                  </button>
                  <button
                    onClick={() => resolveMutation.mutate({ blockId: conflict.block_id, resolution: "accept_remote" })}
                    disabled={resolveMutation.isPending}
                    className="rounded-input border border-amber-500/20 px-3 py-1.5 text-xs text-amber-400/70 hover:border-amber-400/40 hover:text-amber-400 disabled:opacity-50"
                  >
                    Aceptar versión de Guesty
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
