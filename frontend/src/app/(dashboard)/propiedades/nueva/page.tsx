"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import { createProperty } from "@/lib/api/properties";
import { REGION_LABELS, TYPE_LABELS } from "@/lib/constants/regions";

export default function NuevaPropiedadPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [form, setForm] = useState({
    name: "",
    type: "apartment",
    region: "malaga",
    address: "",
    capacity: "",
    bedrooms: "",
    bathrooms: "",
    status: "active",
  });

  const mutation = useMutation({
    mutationFn: () =>
      createProperty({
        name: form.name,
        type: form.type as import("@/types/property").PropertyType,
        region: form.region as import("@/types/property").PropertyRegion,
        address: form.address || undefined,
        status: form.status as import("@/types/property").PropertyStatus,
        capacity: form.capacity ? Number(form.capacity) : undefined,
        bedrooms: form.bedrooms ? Number(form.bedrooms) : undefined,
        bathrooms: form.bathrooms ? Number(form.bathrooms) : undefined,
      }),
    onSuccess: (property) => {
      queryClient.invalidateQueries({ queryKey: ["properties"] });
      router.push(`/propiedades/${property.slug}`);
    },
  });

  const field = (key: keyof typeof form) => ({
    value: form[key],
    onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
      setForm((f) => ({ ...f, [key]: e.target.value })),
  });

  return (
    <div>
      <div className="mb-6 flex items-center gap-3">
        <Link
          href="/propiedades"
          className="flex items-center gap-1 text-sm text-white/45 hover:text-white/90"
        >
          <ArrowLeft className="h-4 w-4" />
          Propiedades
        </Link>
        <span className="text-white/20">/</span>
        <span className="text-sm text-white/70">Nueva propiedad</span>
      </div>

      <div className="glass-card mx-auto max-w-xl p-6">
        <h1 className="mb-6 text-lg font-semibold text-white/90">Nueva propiedad</h1>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            mutation.mutate();
          }}
          className="space-y-4"
        >
          <div>
            <label className="mb-1 block text-sm text-white/60">Nombre *</label>
            <input
              {...field("name")}
              required
              className="w-full rounded-input border border-surface-border bg-surface px-3 py-2 text-sm text-white/90 outline-none focus:border-accent"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="mb-1 block text-sm text-white/60">Tipo *</label>
              <select
                {...field("type")}
                className="w-full rounded-input border border-surface-border bg-surface px-3 py-2 text-sm text-white/90 outline-none focus:border-accent"
              >
                {Object.entries(TYPE_LABELS).map(([v, l]) => (
                  <option key={v} value={v}>
                    {l}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-sm text-white/60">Región *</label>
              <select
                {...field("region")}
                className="w-full rounded-input border border-surface-border bg-surface px-3 py-2 text-sm text-white/90 outline-none focus:border-accent"
              >
                {Object.entries(REGION_LABELS).map(([v, l]) => (
                  <option key={v} value={v}>
                    {l}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="mb-1 block text-sm text-white/60">Dirección</label>
            <input
              {...field("address")}
              className="w-full rounded-input border border-surface-border bg-surface px-3 py-2 text-sm text-white/90 outline-none focus:border-accent"
            />
          </div>

          <div className="grid grid-cols-3 gap-4">
            {(
              [
                ["capacity", "Capacidad"],
                ["bedrooms", "Habitaciones"],
                ["bathrooms", "Baños"],
              ] as const
            ).map(([k, label]) => (
              <div key={k}>
                <label className="mb-1 block text-sm text-white/60">{label}</label>
                <input
                  type="number"
                  min={0}
                  {...field(k)}
                  className="w-full rounded-input border border-surface-border bg-surface px-3 py-2 text-sm text-white/90 outline-none focus:border-accent"
                />
              </div>
            ))}
          </div>

          {mutation.isError && (
            <p className="text-sm text-red-400">Error al crear la propiedad</p>
          )}

          <div className="flex gap-3 pt-2">
            <button
              type="submit"
              disabled={mutation.isPending}
              className="rounded-input bg-accent px-5 py-2 text-sm font-medium text-white hover:bg-accent-hover disabled:opacity-50"
            >
              {mutation.isPending ? "Creando..." : "Crear propiedad"}
            </button>
            <Link
              href="/propiedades"
              className="rounded-input border border-surface-border px-5 py-2 text-sm text-white/55 hover:text-white/90"
            >
              Cancelar
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
}
