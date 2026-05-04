"use client";

import dynamic from "next/dynamic";
import { useQuery } from "@tanstack/react-query";
import { listProperties } from "@/lib/api/properties";

const PropertiesMap = dynamic(
  () => import("@/components/domain/PropertiesMap").then((m) => ({ default: m.PropertiesMap })),
  { ssr: false, loading: () => <div className="h-full animate-pulse rounded-card bg-surface" /> }
);

export default function MapaPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["properties-map"],
    queryFn: () => listProperties({ limit: 200 }),
  });

  return (
    <div className="flex h-[calc(100vh-8rem)] flex-col">
      <div className="mb-4 flex items-start justify-between">
        <div>
          <h1 className="text-xl font-bold text-white/90">Mapa de propiedades</h1>
          <p className="mt-1 text-sm text-white/45">
            Visualización geográfica de toda la cartera.
          </p>
        </div>
        {data && (
          <span className="text-sm text-white/40">{data.items.length} propiedades</span>
        )}
      </div>

      <div className="flex-1 overflow-hidden rounded-card border border-surface-border">
        {isLoading ? (
          <div className="h-full animate-pulse bg-surface" />
        ) : (
          <PropertiesMap properties={data?.items ?? []} />
        )}
      </div>
    </div>
  );
}
