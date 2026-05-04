"use client";

import { useState } from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { Plus, Building2, Bed, Bath, Users } from "lucide-react";
import { listProperties } from "@/lib/api/properties";
import { Badge } from "@/components/ui/Badge";
import {
  REGION_LABELS,
  REGION_COLORS,
  TYPE_LABELS,
  STATUS_LABELS,
  STATUS_COLORS,
} from "@/lib/constants/regions";

export default function PropiedadesPage() {
  const [search, setSearch] = useState("");
  const [region, setRegion] = useState("");
  const [type, setType] = useState("");
  const [status, setStatus] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["properties", { search, region, type, status }],
    queryFn: () => listProperties({ search, region, type, status }),
  });

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white/90">Propiedades</h1>
          <p className="mt-1 text-sm text-white/45">
            {data?.total ?? 0} propiedades en total
          </p>
        </div>
        <Link
          href="/propiedades/nueva"
          className="flex items-center gap-2 rounded-input bg-accent px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-accent-hover"
        >
          <Plus className="h-4 w-4" />
          Nueva propiedad
        </Link>
      </div>

      {/* Filters */}
      <div className="mb-6 flex flex-wrap gap-3">
        <input
          type="text"
          placeholder="Buscar propiedades..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-64 rounded-input border border-surface-border bg-surface px-3 py-2 text-sm text-white/90 outline-none placeholder:text-white/30 focus:border-accent"
        />
        <select
          value={region}
          onChange={(e) => setRegion(e.target.value)}
          className="rounded-input border border-surface-border bg-surface px-3 py-2 text-sm text-white/90 outline-none focus:border-accent"
        >
          <option value="">Todas las regiones</option>
          {Object.entries(REGION_LABELS).map(([v, l]) => (
            <option key={v} value={v}>
              {l}
            </option>
          ))}
        </select>
        <select
          value={type}
          onChange={(e) => setType(e.target.value)}
          className="rounded-input border border-surface-border bg-surface px-3 py-2 text-sm text-white/90 outline-none focus:border-accent"
        >
          <option value="">Todos los tipos</option>
          {Object.entries(TYPE_LABELS).map(([v, l]) => (
            <option key={v} value={v}>
              {l}
            </option>
          ))}
        </select>
        <select
          value={status}
          onChange={(e) => setStatus(e.target.value)}
          className="rounded-input border border-surface-border bg-surface px-3 py-2 text-sm text-white/90 outline-none focus:border-accent"
        >
          <option value="">Todos los estados</option>
          {Object.entries(STATUS_LABELS).map(([v, l]) => (
            <option key={v} value={v}>
              {l}
            </option>
          ))}
        </select>
      </div>

      {/* Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="glass-card h-44 animate-pulse" />
          ))}
        </div>
      ) : data?.items.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-card border border-surface-border py-16 text-center">
          <Building2 className="mb-3 h-10 w-10 text-white/20" />
          <p className="text-white/55">No hay propiedades</p>
          <p className="mt-1 text-sm text-white/30">
            Sincroniza desde Guesty o crea una manualmente
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {data?.items.map((property) => (
            <Link key={property.id} href={`/propiedades/${property.slug}`}>
              <div className="glass-card-hover p-5">
                <div className="mb-3 flex items-start justify-between gap-2">
                  <h3 className="font-medium text-white/90 leading-tight">{property.name}</h3>
                  <Badge
                    label={STATUS_LABELS[property.status] ?? property.status}
                    className={STATUS_COLORS[property.status]}
                  />
                </div>

                <div className="mb-3 flex flex-wrap gap-2">
                  <Badge
                    label={REGION_LABELS[property.region] ?? property.region}
                    className={REGION_COLORS[property.region]}
                  />
                  <Badge
                    label={TYPE_LABELS[property.type] ?? property.type}
                    className="border-white/10 bg-white/5 text-white/55"
                  />
                </div>

                <div className="flex gap-4 text-xs text-white/40">
                  {property.capacity && (
                    <span className="flex items-center gap-1">
                      <Users className="h-3 w-3" />
                      {property.capacity}
                    </span>
                  )}
                  {property.bedrooms && (
                    <span className="flex items-center gap-1">
                      <Bed className="h-3 w-3" />
                      {property.bedrooms}
                    </span>
                  )}
                  {property.bathrooms && (
                    <span className="flex items-center gap-1">
                      <Bath className="h-3 w-3" />
                      {property.bathrooms}
                    </span>
                  )}
                </div>

                {property.tags.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-1">
                    {property.tags.slice(0, 3).map((tag) => (
                      <span
                        key={tag}
                        className="rounded-sm bg-accent/10 px-1.5 py-0.5 text-xs text-accent/70"
                      >
                        {tag}
                      </span>
                    ))}
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
