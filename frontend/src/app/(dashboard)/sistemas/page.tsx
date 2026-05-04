"use client";

import { useState } from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { Plus, Blocks, ExternalLink, Zap } from "lucide-react";
import { listSystems } from "@/lib/api/systems";
import { Badge } from "@/components/ui/Badge";
import {
  CATEGORY_LABELS,
  CATEGORY_COLORS,
  SYSTEM_STATUS_LABELS,
  SYSTEM_STATUS_COLORS,
} from "@/lib/constants/systems";

export default function SistemasPage() {
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [status, setStatus] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["systems", { search, category, status }],
    queryFn: () => listSystems({ search, category, status }),
  });

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white/90">Sistemas</h1>
          <p className="mt-1 text-sm text-white/45">{data?.total ?? 0} sistemas integrados</p>
        </div>
        <Link
          href="/sistemas/nuevo"
          className="flex items-center gap-2 rounded-input bg-accent px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-accent-hover"
        >
          <Plus className="h-4 w-4" />
          Nuevo sistema
        </Link>
      </div>

      <div className="mb-6 flex flex-wrap gap-3">
        <input
          type="text"
          placeholder="Buscar sistemas..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-64 rounded-input border border-surface-border bg-surface px-3 py-2 text-sm text-white/90 outline-none placeholder:text-white/30 focus:border-accent"
        />
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="rounded-input border border-surface-border bg-surface px-3 py-2 text-sm text-white/90 outline-none focus:border-accent"
        >
          <option value="">Todas las categorías</option>
          {Object.entries(CATEGORY_LABELS).map(([v, l]) => (
            <option key={v} value={v}>{l}</option>
          ))}
        </select>
        <select
          value={status}
          onChange={(e) => setStatus(e.target.value)}
          className="rounded-input border border-surface-border bg-surface px-3 py-2 text-sm text-white/90 outline-none focus:border-accent"
        >
          <option value="">Todos los estados</option>
          {Object.entries(SYSTEM_STATUS_LABELS).map(([v, l]) => (
            <option key={v} value={v}>{l}</option>
          ))}
        </select>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="glass-card h-36 animate-pulse" />
          ))}
        </div>
      ) : data?.items.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-card border border-surface-border py-16 text-center">
          <Blocks className="mb-3 h-10 w-10 text-white/20" />
          <p className="text-white/55">No hay sistemas</p>
          <p className="mt-1 text-sm text-white/30">Crea un sistema o usa "Precargar sistemas"</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {data?.items.map((system) => (
            <Link key={system.id} href={`/sistemas/${system.slug}`}>
              <div className="glass-card-hover p-5">
                <div className="mb-3 flex items-start justify-between">
                  <h3 className="font-medium text-white/90">{system.name}</h3>
                  <Badge
                    label={SYSTEM_STATUS_LABELS[system.status] ?? system.status}
                    className={SYSTEM_STATUS_COLORS[system.status]}
                  />
                </div>
                <div className="mb-3 flex flex-wrap gap-2">
                  <Badge
                    label={CATEGORY_LABELS[system.category] ?? system.category}
                    className={CATEGORY_COLORS[system.category]}
                  />
                  {system.has_api && (
                    <Badge
                      label="API"
                      className="border-accent/20 bg-accent/5 text-accent/70"
                    />
                  )}
                  {system.tags.map((tag) => (
                    <Badge
                      key={tag}
                      label={tag}
                      className="border-white/10 bg-white/5 text-white/40"
                    />
                  ))}
                </div>
                {system.has_api && (
                  <div className="flex items-center gap-1 text-xs text-accent/60">
                    <Zap className="h-3 w-3" />
                    Integración disponible
                  </div>
                )}
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
