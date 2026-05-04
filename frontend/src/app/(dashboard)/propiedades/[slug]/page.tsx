"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, Edit2, Save, X, MapPin, Users, Bed, Bath } from "lucide-react";
import Link from "next/link";
import { getProperty, updateProperty } from "@/lib/api/properties";
import { Badge } from "@/components/ui/Badge";
import {
  REGION_LABELS,
  REGION_COLORS,
  TYPE_LABELS,
  STATUS_LABELS,
  STATUS_COLORS,
} from "@/lib/constants/regions";
import { KnowledgeBlockSection } from "@/components/domain/KnowledgeBlockSection";
import { LinkedSystemsSection } from "@/components/domain/LinkedSystemsSection";

export default function PropiedadDetallePage() {
  const { slug } = useParams<{ slug: string }>();
  const queryClient = useQueryClient();
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState<Record<string, unknown>>({});

  const { data: property, isLoading } = useQuery({
    queryKey: ["property", slug],
    queryFn: () => getProperty(slug),
  });

  const mutation = useMutation({
    mutationFn: (data: Record<string, unknown>) => updateProperty(slug, data),
    onSuccess: (updated) => {
      queryClient.setQueryData(["property", slug], updated);
      queryClient.invalidateQueries({ queryKey: ["properties"] });
      setEditing(false);
    },
  });

  function startEdit() {
    if (!property) return;
    setForm({
      name: property.name,
      address: property.address ?? "",
      capacity: property.capacity,
      bedrooms: property.bedrooms,
      bathrooms: property.bathrooms,
      status: property.status,
    });
    setEditing(true);
  }

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="glass-card h-10 w-48 animate-pulse" />
        <div className="glass-card h-56 animate-pulse" />
      </div>
    );
  }

  if (!property) return null;

  return (
    <div>
      <div className="mb-6 flex items-center gap-3">
        <Link
          href="/propiedades"
          className="flex items-center gap-1 text-sm text-white/45 transition-colors hover:text-white/90"
        >
          <ArrowLeft className="h-4 w-4" />
          Propiedades
        </Link>
        <span className="text-white/20">/</span>
        <span className="text-sm text-white/70">{property.name}</span>
      </div>

      {/* Property info card */}
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
              <h1 className="text-xl font-bold text-white/90">{property.name}</h1>
            )}
            <p className="mt-1 text-sm text-white/40">/{property.slug}</p>
          </div>

          <div className="flex gap-2">
            {editing ? (
              <>
                <button
                  onClick={() => mutation.mutate(form)}
                  disabled={mutation.isPending}
                  className="flex items-center gap-1.5 rounded-input bg-accent px-3 py-1.5 text-sm text-white hover:bg-accent-hover disabled:opacity-50"
                >
                  <Save className="h-3.5 w-3.5" />
                  Guardar
                </button>
                <button
                  onClick={() => setEditing(false)}
                  className="flex items-center gap-1.5 rounded-input border border-surface-border px-3 py-1.5 text-sm text-white/55 hover:text-white/90"
                >
                  <X className="h-3.5 w-3.5" />
                  Cancelar
                </button>
              </>
            ) : (
              <button
                onClick={startEdit}
                className="flex items-center gap-1.5 rounded-input border border-surface-border px-3 py-1.5 text-sm text-white/55 hover:border-accent/50 hover:text-accent"
              >
                <Edit2 className="h-3.5 w-3.5" />
                Editar
              </button>
            )}
          </div>
        </div>

        <div className="mb-4 flex flex-wrap gap-2">
          <Badge
            label={REGION_LABELS[property.region] ?? property.region}
            className={REGION_COLORS[property.region]}
          />
          <Badge
            label={TYPE_LABELS[property.type] ?? property.type}
            className="border-white/10 bg-white/5 text-white/55"
          />
          {editing ? (
            <select
              value={String(form.status ?? "")}
              onChange={(e) => setForm((f) => ({ ...f, status: e.target.value }))}
              className="rounded-sm border border-surface-border bg-surface px-2 py-0.5 text-xs text-white/90 outline-none"
            >
              {Object.entries(STATUS_LABELS).map(([v, l]) => (
                <option key={v} value={v}>
                  {l}
                </option>
              ))}
            </select>
          ) : (
            <Badge
              label={STATUS_LABELS[property.status] ?? property.status}
              className={STATUS_COLORS[property.status]}
            />
          )}
        </div>

        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <InfoField
            label="Dirección"
            icon={<MapPin className="h-3.5 w-3.5" />}
            value={editing ? undefined : property.address ?? "—"}
            editValue={editing ? String(form.address ?? "") : undefined}
            onChange={(v) => setForm((f) => ({ ...f, address: v }))}
          />
          <InfoField
            label="Capacidad"
            icon={<Users className="h-3.5 w-3.5" />}
            value={editing ? undefined : property.capacity ? `${property.capacity} huéspedes` : "—"}
            editValue={editing ? String(form.capacity ?? "") : undefined}
            inputType="number"
            onChange={(v) => setForm((f) => ({ ...f, capacity: Number(v) }))}
          />
          <InfoField
            label="Habitaciones"
            icon={<Bed className="h-3.5 w-3.5" />}
            value={editing ? undefined : property.bedrooms ? `${property.bedrooms}` : "—"}
            editValue={editing ? String(form.bedrooms ?? "") : undefined}
            inputType="number"
            onChange={(v) => setForm((f) => ({ ...f, bedrooms: Number(v) }))}
          />
          <InfoField
            label="Baños"
            icon={<Bath className="h-3.5 w-3.5" />}
            value={editing ? undefined : property.bathrooms ? `${property.bathrooms}` : "—"}
            editValue={editing ? String(form.bathrooms ?? "") : undefined}
            inputType="number"
            onChange={(v) => setForm((f) => ({ ...f, bathrooms: Number(v) }))}
          />
        </div>

        {property.tags.length > 0 && (
          <div className="mt-4 flex flex-wrap gap-1.5">
            {property.tags.map((tag) => (
              <span
                key={tag}
                className="rounded-sm bg-accent/10 px-2 py-0.5 text-xs text-accent/70"
              >
                {tag}
              </span>
            ))}
          </div>
        )}

        {property.guesty_listing_id && (
          <p className="mt-4 text-xs text-white/30">
            Guesty ID: {property.guesty_listing_id}
          </p>
        )}
      </div>

      <div className="mt-6 glass-card p-6">
        <KnowledgeBlockSection entityType="property" entityId={property.id} />
      </div>

      <div className="mt-4 glass-card p-6">
        <LinkedSystemsSection propertyId={property.id} />
      </div>
    </div>
  );
}

function InfoField({
  label,
  icon,
  value,
  editValue,
  onChange,
  inputType = "text",
}: {
  label: string;
  icon: React.ReactNode;
  value?: string;
  editValue?: string;
  onChange?: (v: string) => void;
  inputType?: string;
}) {
  return (
    <div>
      <p className="mb-1 flex items-center gap-1 text-xs text-white/40">
        {icon}
        {label}
      </p>
      {editValue !== undefined ? (
        <input
          type={inputType}
          value={editValue}
          onChange={(e) => onChange?.(e.target.value)}
          className="w-full rounded-sm border border-accent/50 bg-surface px-2 py-1 text-sm text-white/90 outline-none"
        />
      ) : (
        <p className="text-sm text-white/75">{value}</p>
      )}
    </div>
  );
}
