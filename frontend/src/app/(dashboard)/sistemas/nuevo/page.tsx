"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import { createSystem } from "@/lib/api/systems";
import { CATEGORY_LABELS } from "@/lib/constants/systems";
import type { SystemCategory } from "@/types/system";

export default function NuevoSistemaPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [form, setForm] = useState({
    name: "",
    category: "other" as SystemCategory,
    description: "",
    website_url: "",
    has_api: false,
    api_docs_url: "",
  });

  const mutation = useMutation({
    mutationFn: () =>
      createSystem({
        name: form.name,
        category: form.category,
        description: form.description || undefined,
        website_url: form.website_url || undefined,
        has_api: form.has_api,
        api_docs_url: form.api_docs_url || undefined,
      }),
    onSuccess: (system) => {
      queryClient.invalidateQueries({ queryKey: ["systems"] });
      router.push(`/sistemas/${system.slug}`);
    },
  });

  return (
    <div>
      <div className="mb-6 flex items-center gap-3">
        <Link href="/sistemas" className="flex items-center gap-1 text-sm text-white/45 hover:text-white/90">
          <ArrowLeft className="h-4 w-4" />
          Sistemas
        </Link>
        <span className="text-white/20">/</span>
        <span className="text-sm text-white/70">Nuevo sistema</span>
      </div>

      <div className="glass-card mx-auto max-w-xl p-6">
        <h1 className="mb-6 text-lg font-semibold text-white/90">Nuevo sistema</h1>

        <form onSubmit={(e) => { e.preventDefault(); mutation.mutate(); }} className="space-y-4">
          <div>
            <label className="mb-1 block text-sm text-white/60">Nombre *</label>
            <input
              value={form.name}
              onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
              required
              className="w-full rounded-input border border-surface-border bg-surface px-3 py-2 text-sm text-white/90 outline-none focus:border-accent"
            />
          </div>

          <div>
            <label className="mb-1 block text-sm text-white/60">Categoría *</label>
            <select
              value={form.category}
              onChange={(e) => setForm((f) => ({ ...f, category: e.target.value as SystemCategory }))}
              className="w-full rounded-input border border-surface-border bg-surface px-3 py-2 text-sm text-white/90 outline-none focus:border-accent"
            >
              {Object.entries(CATEGORY_LABELS).map(([v, l]) => (
                <option key={v} value={v}>{l}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="mb-1 block text-sm text-white/60">Descripción</label>
            <textarea
              value={form.description}
              onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
              rows={3}
              className="w-full rounded-input border border-surface-border bg-surface px-3 py-2 text-sm text-white/90 outline-none focus:border-accent resize-none"
            />
          </div>

          <div>
            <label className="mb-1 block text-sm text-white/60">Sitio web</label>
            <input
              value={form.website_url}
              onChange={(e) => setForm((f) => ({ ...f, website_url: e.target.value }))}
              className="w-full rounded-input border border-surface-border bg-surface px-3 py-2 text-sm text-white/90 outline-none focus:border-accent"
            />
          </div>

          <div className="flex items-center gap-3">
            <input
              type="checkbox"
              id="has_api"
              checked={form.has_api}
              onChange={(e) => setForm((f) => ({ ...f, has_api: e.target.checked }))}
              className="h-4 w-4 rounded accent-accent"
            />
            <label htmlFor="has_api" className="text-sm text-white/70">Tiene API disponible</label>
          </div>

          {form.has_api && (
            <div>
              <label className="mb-1 block text-sm text-white/60">URL documentación API</label>
              <input
                value={form.api_docs_url}
                onChange={(e) => setForm((f) => ({ ...f, api_docs_url: e.target.value }))}
                className="w-full rounded-input border border-surface-border bg-surface px-3 py-2 text-sm text-white/90 outline-none focus:border-accent"
              />
            </div>
          )}

          {mutation.isError && <p className="text-sm text-red-400">Error al crear el sistema</p>}

          <div className="flex gap-3 pt-2">
            <button
              type="submit"
              disabled={mutation.isPending}
              className="rounded-input bg-accent px-5 py-2 text-sm font-medium text-white hover:bg-accent-hover disabled:opacity-50"
            >
              {mutation.isPending ? "Creando..." : "Crear sistema"}
            </button>
            <Link href="/sistemas" className="rounded-input border border-surface-border px-5 py-2 text-sm text-white/55 hover:text-white/90">
              Cancelar
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
}
