"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import { ArrowLeft, Edit2, Save, X, ExternalLink } from "lucide-react";
import Link from "next/link";
import { getSystem, updateSystem } from "@/lib/api/systems";
import { Badge } from "@/components/ui/Badge";
import { CATEGORY_LABELS, CATEGORY_COLORS, SYSTEM_STATUS_LABELS, SYSTEM_STATUS_COLORS } from "@/lib/constants/systems";
import type { SystemCategory, SystemStatus } from "@/types/system";
import { KnowledgeBlockSection } from "@/components/domain/KnowledgeBlockSection";
import { LinkedPropertiesSection } from "@/components/domain/LinkedPropertiesSection";

export default function SistemaDetallePage() {
  const { slug } = useParams<{ slug: string }>();
  const queryClient = useQueryClient();
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState<Record<string, unknown>>({});

  const { data: system, isLoading } = useQuery({
    queryKey: ["system", slug],
    queryFn: () => getSystem(slug),
  });

  const mutation = useMutation({
    mutationFn: (data: Record<string, unknown>) =>
      updateSystem(slug, data as Parameters<typeof updateSystem>[1]),
    onSuccess: (updated) => {
      queryClient.setQueryData(["system", slug], updated);
      queryClient.invalidateQueries({ queryKey: ["systems"] });
      setEditing(false);
    },
  });

  function startEdit() {
    if (!system) return;
    setForm({
      name: system.name,
      description: system.description ?? "",
      website_url: system.website_url ?? "",
      api_docs_url: system.api_docs_url ?? "",
      has_api: system.has_api,
      status: system.status,
    });
    setEditing(true);
  }

  if (isLoading) return <div className="glass-card h-56 animate-pulse" />;
  if (!system) return null;

  return (
    <div>
      <div className="mb-6 flex items-center gap-3">
        <Link href="/sistemas" className="flex items-center gap-1 text-sm text-white/45 hover:text-white/90">
          <ArrowLeft className="h-4 w-4" />
          Sistemas
        </Link>
        <span className="text-white/20">/</span>
        <span className="text-sm text-white/70">{system.name}</span>
      </div>

      <div className="glass-card p-6">
        <div className="mb-4 flex items-start justify-between">
          <div>
            {editing ? (
              <input
                value={String(form.name ?? "")}
                onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
                className="rounded-input border border-accent bg-surface px-3 py-1.5 text-xl font-bold text-white/90 outline-none"
              />
            ) : (
              <h1 className="text-xl font-bold text-white/90">{system.name}</h1>
            )}
            <p className="mt-1 text-sm text-white/40">/{system.slug}</p>
          </div>

          <div className="flex gap-2">
            {editing ? (
              <>
                <button
                  onClick={() => mutation.mutate(form)}
                  disabled={mutation.isPending}
                  className="flex items-center gap-1.5 rounded-input bg-accent px-3 py-1.5 text-sm text-white hover:bg-accent-hover disabled:opacity-50"
                >
                  <Save className="h-3.5 w-3.5" /> Guardar
                </button>
                <button
                  onClick={() => setEditing(false)}
                  className="flex items-center gap-1.5 rounded-input border border-surface-border px-3 py-1.5 text-sm text-white/55 hover:text-white/90"
                >
                  <X className="h-3.5 w-3.5" /> Cancelar
                </button>
              </>
            ) : (
              <button
                onClick={startEdit}
                className="flex items-center gap-1.5 rounded-input border border-surface-border px-3 py-1.5 text-sm text-white/55 hover:border-accent/50 hover:text-accent"
              >
                <Edit2 className="h-3.5 w-3.5" /> Editar
              </button>
            )}
          </div>
        </div>

        <div className="mb-4 flex flex-wrap gap-2">
          <Badge label={CATEGORY_LABELS[system.category] ?? system.category} className={CATEGORY_COLORS[system.category]} />
          {editing ? (
            <select
              value={String(form.status ?? "")}
              onChange={(e) => setForm((f) => ({ ...f, status: e.target.value }))}
              className="rounded-sm border border-surface-border bg-surface px-2 py-0.5 text-xs text-white/90 outline-none"
            >
              {Object.entries(SYSTEM_STATUS_LABELS).map(([v, l]) => <option key={v} value={v}>{l}</option>)}
            </select>
          ) : (
            <Badge label={SYSTEM_STATUS_LABELS[system.status] ?? system.status} className={SYSTEM_STATUS_COLORS[system.status]} />
          )}
          {system.has_api && <Badge label="API" className="border-accent/20 bg-accent/5 text-accent/70" />}
        </div>

        {/* Description */}
        <div className="mb-4">
          <p className="mb-1 text-xs text-white/40">Descripción</p>
          {editing ? (
            <textarea
              value={String(form.description ?? "")}
              onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
              rows={3}
              className="w-full rounded-input border border-accent/50 bg-surface px-3 py-2 text-sm text-white/90 outline-none resize-none"
            />
          ) : (
            <p className="text-sm text-white/70">{system.description || <span className="text-white/30">Sin descripción</span>}</p>
          )}
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="mb-1 text-xs text-white/40">Sitio web</p>
            {editing ? (
              <input
                value={String(form.website_url ?? "")}
                onChange={(e) => setForm((f) => ({ ...f, website_url: e.target.value }))}
                className="w-full rounded-sm border border-surface-border bg-surface px-2 py-1 text-sm text-white/90 outline-none"
              />
            ) : system.website_url ? (
              <a href={system.website_url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1 text-sm text-accent hover:underline">
                {system.website_url} <ExternalLink className="h-3 w-3" />
              </a>
            ) : (
              <p className="text-sm text-white/30">—</p>
            )}
          </div>
          <div>
            <p className="mb-1 text-xs text-white/40">Documentación API</p>
            {editing ? (
              <input
                value={String(form.api_docs_url ?? "")}
                onChange={(e) => setForm((f) => ({ ...f, api_docs_url: e.target.value }))}
                className="w-full rounded-sm border border-surface-border bg-surface px-2 py-1 text-sm text-white/90 outline-none"
              />
            ) : system.api_docs_url ? (
              <a href={system.api_docs_url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1 text-sm text-accent hover:underline">
                Ver documentación <ExternalLink className="h-3 w-3" />
              </a>
            ) : (
              <p className="text-sm text-white/30">—</p>
            )}
          </div>
        </div>
      </div>

      <div className="mt-6 glass-card p-6">
        <KnowledgeBlockSection entityType="system" entityId={system.id} />
      </div>

      <div className="mt-4 glass-card p-6">
        <LinkedPropertiesSection systemId={system.id} />
      </div>
    </div>
  );
}
