"use client";

import { useQuery } from "@tanstack/react-query";
import { getSystemRelations } from "@/lib/api/knowledge";
import { listProperties } from "@/lib/api/properties";
import { Badge } from "@/components/ui/Badge";
import { REGION_LABELS, REGION_COLORS, STATUS_LABELS, STATUS_COLORS } from "@/lib/constants/regions";
import Link from "next/link";

interface Props {
  systemId: string;
}

export function LinkedPropertiesSection({ systemId }: Props) {
  const { data: relations = [] } = useQuery({
    queryKey: ["system-relations", systemId],
    queryFn: () => getSystemRelations(systemId),
  });

  const { data: allProperties } = useQuery({
    queryKey: ["properties-all"],
    queryFn: () => listProperties({ limit: 200 }),
    enabled: relations.length > 0,
  });

  return (
    <div>
      <div className="mb-4">
        <h2 className="font-semibold text-white/90">
          Propiedades vinculadas
          {relations.length > 0 && (
            <span className="ml-2 text-sm text-white/40">({relations.length})</span>
          )}
        </h2>
      </div>

      {relations.length === 0 ? (
        <p className="py-8 text-center text-sm text-white/30">
          No hay propiedades vinculadas a este sistema.
        </p>
      ) : (
        <div className="space-y-2">
          {relations.map((relation) => {
            const property = allProperties?.items.find((p) => p.id === relation.property_id);
            return (
              <div key={relation.id} className="rounded-card border border-surface-border bg-surface p-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    {property ? (
                      <Link
                        href={`/propiedades/${property.slug}`}
                        className="font-medium text-white/85 hover:text-accent"
                      >
                        {property.name}
                      </Link>
                    ) : (
                      <span className="font-medium text-white/85">
                        {relation.property_id.slice(0, 8)}
                      </span>
                    )}
                    {property && (
                      <>
                        <Badge
                          label={REGION_LABELS[property.region] ?? property.region}
                          className={REGION_COLORS[property.region]}
                        />
                        <Badge
                          label={STATUS_LABELS[property.status] ?? property.status}
                          className={STATUS_COLORS[property.status]}
                        />
                      </>
                    )}
                  </div>
                </div>
                {relation.notes && (
                  <p className="mt-2 text-sm text-white/55">{relation.notes}</p>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
