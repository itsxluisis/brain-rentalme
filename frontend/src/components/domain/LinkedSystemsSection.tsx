"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Unlink, Edit2, Save, X } from "lucide-react";
import { getPropertyRelations, createRelation, updateRelation, deleteRelation } from "@/lib/api/knowledge";
import { listSystems } from "@/lib/api/systems";
import { Badge } from "@/components/ui/Badge";
import { CATEGORY_LABELS, CATEGORY_COLORS } from "@/lib/constants/systems";
import type { SystemSummary } from "@/types/system";

interface Props {
  propertyId: string;
}

export function LinkedSystemsSection({ propertyId }: Props) {
  const queryClient = useQueryClient();
  const [showAdd, setShowAdd] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [addForm, setAddForm] = useState({ system_id: "", notes: "", config: "{}" });
  const [editForm, setEditForm] = useState({ notes: "", config: "{}" });

  const qKey = ["property-relations", propertyId];

  const { data: relations = [] } = useQuery({
    queryKey: qKey,
    queryFn: () => getPropertyRelations(propertyId),
  });

  const { data: allSystems } = useQuery({
    queryKey: ["systems-all"],
    queryFn: () => listSystems({ limit: 100 }),
    enabled: showAdd,
  });

  const linkMutation = useMutation({
    mutationFn: () =>
      createRelation({
        property_id: propertyId,
        system_id: addForm.system_id,
        notes: addForm.notes || undefined,
        config: addForm.config ? JSON.parse(addForm.config) : {},
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: qKey });
      setShowAdd(false);
      setAddForm({ system_id: "", notes: "", config: "{}" });
    },
  });

  const updateMutation = useMutation({
    mutationFn: (id: string) =>
      updateRelation(id, {
        notes: editForm.notes || undefined,
        config: editForm.config ? JSON.parse(editForm.config) : {},
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: qKey });
      setEditingId(null);
    },
  });

  const unlinkMutation = useMutation({
    mutationFn: (id: string) => deleteRelation(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: qKey }),
  });

  const linkedSystemIds = new Set(relations.map((r) => r.system_id));

  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <h2 className="font-semibold text-white/90">
          Sistemas vinculados
          {relations.length > 0 && <span className="ml-2 text-sm text-white/40">({relations.length})</span>}
        </h2>
        <button
          onClick={() => setShowAdd(true)}
          className="flex items-center gap-1.5 rounded-input border border-surface-border px-3 py-1.5 text-sm text-white/55 hover:border-accent/50 hover:text-accent"
        >
          <Plus className="h-3.5 w-3.5" />
          Vincular sistema
        </button>
      </div>

      {showAdd && (
        <div className="mb-4 rounded-card border border-accent/30 bg-surface p-4">
          <div className="mb-3">
            <label className="mb-1 block text-xs text-white/40">Sistema</label>
            <select
              value={addForm.system_id}
              onChange={(e) => setAddForm((f) => ({ ...f, system_id: e.target.value }))}
              className="w-full rounded-input border border-surface-border bg-surface-hover px-3 py-2 text-sm text-white/90 outline-none focus:border-accent"
            >
              <option value="">Seleccionar sistema...</option>
              {allSystems?.items
                .filter((s) => !linkedSystemIds.has(s.id))
                .map((s) => (
                  <option key={s.id} value={s.id}>{s.name}</option>
                ))}
            </select>
          </div>
          <div className="mb-3">
            <label className="mb-1 block text-xs text-white/40">Notas (ej: código de acceso)</label>
            <textarea
              value={addForm.notes}
              onChange={(e) => setAddForm((f) => ({ ...f, notes: e.target.value }))}
              rows={2}
              placeholder="Ej: Código Nuki: 4821"
              className="w-full rounded-input border border-surface-border bg-surface-hover px-3 py-2 text-sm text-white/90 outline-none focus:border-accent resize-none"
            />
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => linkMutation.mutate()}
              disabled={!addForm.system_id || linkMutation.isPending}
              className="rounded-input bg-accent px-4 py-1.5 text-sm text-white hover:bg-accent-hover disabled:opacity-50"
            >
              {linkMutation.isPending ? "Vinculando..." : "Vincular"}
            </button>
            <button
              onClick={() => setShowAdd(false)}
              className="rounded-input border border-surface-border px-4 py-1.5 text-sm text-white/55 hover:text-white/90"
            >
              Cancelar
            </button>
          </div>
        </div>
      )}

      {relations.length === 0 && !showAdd ? (
        <p className="py-8 text-center text-sm text-white/30">No hay sistemas vinculados.</p>
      ) : (
        <div className="space-y-2">
          {relations.map((relation) => {
            const system = allSystems?.items.find((s) => s.id === relation.system_id);
            return (
              <div key={relation.id} className="rounded-card border border-surface-border bg-surface p-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <span className="font-medium text-white/85">
                      {system?.name ?? relation.system_id.slice(0, 8)}
                    </span>
                    {system && (
                      <Badge
                        label={CATEGORY_LABELS[system.category] ?? system.category}
                        className={CATEGORY_COLORS[system.category]}
                      />
                    )}
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => {
                        setEditingId(relation.id);
                        setEditForm({ notes: relation.notes ?? "", config: JSON.stringify(relation.config) });
                      }}
                      className="rounded p-1 text-white/30 hover:text-accent"
                    >
                      <Edit2 className="h-3.5 w-3.5" />
                    </button>
                    <button
                      onClick={() => unlinkMutation.mutate(relation.id)}
                      className="rounded p-1 text-white/30 hover:text-red-400"
                    >
                      <Unlink className="h-3.5 w-3.5" />
                    </button>
                  </div>
                </div>

                {editingId === relation.id ? (
                  <div className="mt-3">
                    <textarea
                      value={editForm.notes}
                      onChange={(e) => setEditForm((f) => ({ ...f, notes: e.target.value }))}
                      rows={2}
                      placeholder="Notas de configuración..."
                      className="mb-2 w-full rounded border border-accent/50 bg-surface-hover px-3 py-2 text-sm text-white/90 outline-none resize-none"
                    />
                    <div className="flex gap-2">
                      <button
                        onClick={() => updateMutation.mutate(relation.id)}
                        className="rounded-sm bg-accent px-3 py-1 text-sm text-white hover:bg-accent-hover"
                      >
                        <Save className="inline h-3.5 w-3.5" /> Guardar
                      </button>
                      <button
                        onClick={() => setEditingId(null)}
                        className="rounded-sm border border-surface-border px-3 py-1 text-sm text-white/55"
                      >
                        <X className="inline h-3.5 w-3.5" /> Cancelar
                      </button>
                    </div>
                  </div>
                ) : relation.notes ? (
                  <p className="mt-2 text-sm text-white/55">{relation.notes}</p>
                ) : null}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
