"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Pencil, Trash2, Zap, ChevronDown, ChevronUp, RefreshCw } from "lucide-react";
import { listBlocks, createBlock, updateBlock, deleteBlock } from "@/lib/api/knowledge";
import { Badge } from "@/components/ui/Badge";
import { BLOCK_TYPE_LABELS, BLOCK_TYPE_COLORS } from "@/lib/constants/blocks";
import type { BlockType, KnowledgeBlock } from "@/types/knowledge";
import { cn } from "@/lib/utils/cn";

const BLOCK_TYPES: BlockType[] = [
  "description", "rules", "access_instructions", "faq",
  "sop", "integration_guide", "pricing_notes", "checkin_notes", "custom",
];

interface Props {
  entityType: "property" | "system";
  entityId: string;
}

export function KnowledgeBlockSection({ entityType, entityId }: Props) {
  const queryClient = useQueryClient();
  const [adding, setAdding] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [newForm, setNewForm] = useState({ title: "", content: "", block_type: "description" as BlockType });
  const [editForm, setEditForm] = useState<{ title: string; content: string; block_type: BlockType }>({
    title: "", content: "", block_type: "description",
  });

  const queryKey = ["knowledge", entityType, entityId];

  const { data, isLoading } = useQuery({
    queryKey,
    queryFn: () => listBlocks({ entity_type: entityType, entity_id: entityId, limit: 100 }),
  });

  const createMutation = useMutation({
    mutationFn: () => createBlock({ ...newForm, entity_type: entityType, entity_id: entityId }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey });
      setAdding(false);
      setNewForm({ title: "", content: "", block_type: "description" });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: typeof editForm }) => updateBlock(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey });
      setEditingId(null);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => deleteBlock(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey }),
  });

  function startEdit(block: KnowledgeBlock) {
    setEditingId(block.id);
    setEditForm({ title: block.title, content: block.content, block_type: block.block_type });
  }

  const blocks = data?.items ?? [];

  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <h2 className="font-semibold text-white/90">
          Bloques de conocimiento
          {blocks.length > 0 && (
            <span className="ml-2 text-sm text-white/40">({blocks.length})</span>
          )}
        </h2>
        <button
          onClick={() => setAdding(true)}
          className="flex items-center gap-1.5 rounded-input border border-surface-border px-3 py-1.5 text-sm text-white/55 hover:border-accent/50 hover:text-accent"
        >
          <Plus className="h-3.5 w-3.5" />
          Añadir bloque
        </button>
      </div>

      {/* Add form */}
      {adding && (
        <div className="mb-4 rounded-card border border-accent/30 bg-surface p-4">
          <div className="mb-3 grid grid-cols-2 gap-3">
            <input
              placeholder="Título del bloque"
              value={newForm.title}
              onChange={(e) => setNewForm((f) => ({ ...f, title: e.target.value }))}
              className="rounded-input border border-surface-border bg-surface-hover px-3 py-2 text-sm text-white/90 outline-none focus:border-accent"
            />
            <select
              value={newForm.block_type}
              onChange={(e) => setNewForm((f) => ({ ...f, block_type: e.target.value as BlockType }))}
              className="rounded-input border border-surface-border bg-surface-hover px-3 py-2 text-sm text-white/90 outline-none focus:border-accent"
            >
              {BLOCK_TYPES.map((t) => (
                <option key={t} value={t}>{BLOCK_TYPE_LABELS[t]}</option>
              ))}
            </select>
          </div>
          <textarea
            placeholder="Contenido del bloque..."
            value={newForm.content}
            onChange={(e) => setNewForm((f) => ({ ...f, content: e.target.value }))}
            rows={6}
            className="mb-3 w-full rounded-input border border-surface-border bg-surface-hover px-3 py-2 font-mono text-sm text-white/90 outline-none focus:border-accent resize-none"
          />
          <div className="flex gap-2">
            <button
              onClick={() => createMutation.mutate()}
              disabled={!newForm.title || !newForm.content || createMutation.isPending}
              className="rounded-input bg-accent px-4 py-1.5 text-sm text-white hover:bg-accent-hover disabled:opacity-50"
            >
              {createMutation.isPending ? "Guardando..." : "Guardar"}
            </button>
            <button
              onClick={() => setAdding(false)}
              className="rounded-input border border-surface-border px-4 py-1.5 text-sm text-white/55 hover:text-white/90"
            >
              Cancelar
            </button>
          </div>
        </div>
      )}

      {isLoading ? (
        <div className="space-y-2">
          {[1, 2].map((i) => <div key={i} className="h-14 animate-pulse rounded-card bg-surface" />)}
        </div>
      ) : blocks.length === 0 && !adding ? (
        <p className="py-8 text-center text-sm text-white/30">
          No hay bloques de conocimiento. Añade el primero.
        </p>
      ) : (
        <div className="space-y-2">
          {blocks.map((block) => (
            <div key={block.id} className="rounded-card border border-surface-border bg-surface">
              <div
                className="flex cursor-pointer items-center gap-3 px-4 py-3"
                onClick={() => setExpandedId(expandedId === block.id ? null : block.id)}
              >
                <Badge
                  label={BLOCK_TYPE_LABELS[block.block_type as BlockType] ?? block.block_type}
                  className={cn(BLOCK_TYPE_COLORS[block.block_type as BlockType], "shrink-0")}
                />
                <span className="flex-1 text-sm text-white/80">{block.title}</span>
                <div className="flex items-center gap-2">
                  {block.source !== "manual" && (
                    <span className="rounded-sm bg-blue-500/10 px-1.5 py-0.5 text-xs text-blue-400">
                      {block.source === "guesty_sync" ? "Guesty" : "Sync"}
                    </span>
                  )}
                  {!block.has_embedding && (
                    <span className="flex items-center gap-0.5 text-xs text-amber-400/70">
                      <RefreshCw className="h-3 w-3 animate-spin" />
                      Indexando
                    </span>
                  )}
                  <button
                    onClick={(e) => { e.stopPropagation(); startEdit(block); }}
                    className="rounded p-1 text-white/30 hover:text-accent"
                  >
                    <Pencil className="h-3.5 w-3.5" />
                  </button>
                  <button
                    onClick={(e) => { e.stopPropagation(); deleteMutation.mutate(block.id); }}
                    className="rounded p-1 text-white/30 hover:text-red-400"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                  {expandedId === block.id ? (
                    <ChevronUp className="h-4 w-4 text-white/30" />
                  ) : (
                    <ChevronDown className="h-4 w-4 text-white/30" />
                  )}
                </div>
              </div>

              {expandedId === block.id && (
                <div className="border-t border-surface-border px-4 pb-4 pt-3">
                  {editingId === block.id ? (
                    <div>
                      <div className="mb-2 grid grid-cols-2 gap-2">
                        <input
                          value={editForm.title}
                          onChange={(e) => setEditForm((f) => ({ ...f, title: e.target.value }))}
                          className="rounded border border-accent/50 bg-surface-hover px-2 py-1.5 text-sm text-white/90 outline-none"
                        />
                        <select
                          value={editForm.block_type}
                          onChange={(e) => setEditForm((f) => ({ ...f, block_type: e.target.value as BlockType }))}
                          className="rounded border border-surface-border bg-surface-hover px-2 py-1.5 text-sm text-white/90 outline-none"
                        >
                          {BLOCK_TYPES.map((t) => <option key={t} value={t}>{BLOCK_TYPE_LABELS[t]}</option>)}
                        </select>
                      </div>
                      <textarea
                        value={editForm.content}
                        onChange={(e) => setEditForm((f) => ({ ...f, content: e.target.value }))}
                        rows={8}
                        className="mb-2 w-full rounded border border-accent/50 bg-surface-hover px-3 py-2 font-mono text-sm text-white/90 outline-none resize-none"
                      />
                      <div className="flex gap-2">
                        <button
                          onClick={() => updateMutation.mutate({ id: block.id, data: editForm })}
                          disabled={updateMutation.isPending}
                          className="rounded-sm bg-accent px-3 py-1.5 text-sm text-white hover:bg-accent-hover disabled:opacity-50"
                        >
                          {updateMutation.isPending ? "Guardando..." : "Guardar cambios"}
                        </button>
                        <button
                          onClick={() => setEditingId(null)}
                          className="rounded-sm border border-surface-border px-3 py-1.5 text-sm text-white/55 hover:text-white/90"
                        >
                          Cancelar
                        </button>
                      </div>
                    </div>
                  ) : (
                    <pre className="whitespace-pre-wrap font-mono text-sm text-white/70 leading-relaxed">
                      {block.content}
                    </pre>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
