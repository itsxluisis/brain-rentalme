"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Copy, Trash2, CheckCircle, Key } from "lucide-react";
import { listApiKeys, createApiKey, revokeApiKey } from "@/lib/api/admin";

export default function ApiKeysPage() {
  const queryClient = useQueryClient();
  const [newName, setNewName] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [createdKey, setCreatedKey] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const { data: keys = [] } = useQuery({
    queryKey: ["api-keys"],
    queryFn: listApiKeys,
  });

  const createMutation = useMutation({
    mutationFn: () => createApiKey(newName),
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: ["api-keys"] });
      setCreatedKey(result.key);
      setNewName("");
      setShowCreate(false);
    },
  });

  const revokeMutation = useMutation({
    mutationFn: (id: string) => revokeApiKey(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["api-keys"] }),
  });

  function copyKey() {
    if (createdKey) {
      navigator.clipboard.writeText(createdKey);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  }

  function formatDate(iso: string | null) {
    if (!iso) return "—";
    return new Date(iso).toLocaleDateString("es-ES");
  }

  return (
    <div>
      <div className="mb-6 flex items-start justify-between">
        <div>
          <h1 className="text-xl font-bold text-white/90">API Keys para Agentes</h1>
          <p className="mt-1 text-sm text-white/45">
            Genera claves para que agentes IA accedan a la Tool API. Cada clave solo se muestra una vez.
          </p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="flex items-center gap-1.5 rounded-input border border-surface-border px-3 py-1.5 text-sm text-white/55 hover:border-accent/50 hover:text-accent"
        >
          <Plus className="h-3.5 w-3.5" />
          Nueva clave
        </button>
      </div>

      {showCreate && (
        <div className="mb-4 glass-card p-5">
          <div className="mb-3 flex gap-2">
            <input
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              placeholder="Nombre de la clave (ej: Agente UpMarket)"
              className="flex-1 rounded-input border border-surface-border bg-surface-hover px-3 py-2 text-sm text-white/90 outline-none focus:border-accent"
            />
            <button
              onClick={() => createMutation.mutate()}
              disabled={!newName || createMutation.isPending}
              className="rounded-input bg-accent px-4 py-2 text-sm text-white hover:bg-accent-hover disabled:opacity-50"
            >
              {createMutation.isPending ? "Creando..." : "Crear"}
            </button>
            <button
              onClick={() => setShowCreate(false)}
              className="rounded-input border border-surface-border px-4 py-2 text-sm text-white/55"
            >
              Cancelar
            </button>
          </div>
        </div>
      )}

      {createdKey && (
        <div className="mb-4 rounded-card border border-green-500/30 bg-green-500/5 p-4">
          <p className="mb-2 flex items-center gap-2 text-sm font-medium text-green-400">
            <CheckCircle className="h-4 w-4" />
            Clave creada. Cópiala ahora — no se volverá a mostrar.
          </p>
          <div className="flex items-center gap-2">
            <code className="flex-1 rounded-sm bg-black/30 px-3 py-2 font-mono text-sm text-green-300">
              {createdKey}
            </code>
            <button
              onClick={copyKey}
              className="flex items-center gap-1.5 rounded-input border border-green-500/30 px-3 py-2 text-sm text-green-400 hover:bg-green-500/10"
            >
              {copied ? <CheckCircle className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
              {copied ? "Copiado" : "Copiar"}
            </button>
          </div>
          <button onClick={() => setCreatedKey(null)} className="mt-2 text-xs text-white/30 hover:text-white/60">
            Entendido, he copiado la clave
          </button>
        </div>
      )}

      {keys.length === 0 ? (
        <div className="glass-card py-12 text-center">
          <Key className="mx-auto mb-3 h-8 w-8 text-white/20" />
          <p className="text-sm text-white/30">No hay claves de API configuradas.</p>
        </div>
      ) : (
        <div className="glass-card overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-surface-border text-left text-xs text-white/40">
                <th className="px-4 py-3">Nombre</th>
                <th className="px-4 py-3">Estado</th>
                <th className="px-4 py-3">Último uso</th>
                <th className="px-4 py-3">Creada</th>
                <th className="px-4 py-3"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-border">
              {keys.map((key) => (
                <tr key={key.id} className="text-white/70">
                  <td className="px-4 py-3 font-medium">{key.name}</td>
                  <td className="px-4 py-3">
                    <span className={`rounded-sm px-2 py-0.5 text-xs ${key.is_active ? "bg-green-500/10 text-green-400" : "bg-red-500/10 text-red-400"}`}>
                      {key.is_active ? "Activa" : "Revocada"}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-white/40">{formatDate(key.last_used_at)}</td>
                  <td className="px-4 py-3 text-white/40">{formatDate(key.created_at)}</td>
                  <td className="px-4 py-3 text-right">
                    {key.is_active && (
                      <button
                        onClick={() => revokeMutation.mutate(key.id)}
                        className="flex items-center gap-1 text-xs text-red-400/60 hover:text-red-400"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                        Revocar
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
