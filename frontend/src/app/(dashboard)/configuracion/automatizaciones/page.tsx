"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Play, Pause, Trash2, Clock } from "lucide-react";
import { listAutomations, createAutomation, updateAutomation, deleteAutomation } from "@/lib/api/automations";

const ACTION_TYPES = [{ value: "guesty_sync", label: "Sincronizar desde Guesty" }];

const SCHEDULE_PRESETS = [
  { label: "Cada 6 horas", type: "interval", config: { hours: 6 } },
  { label: "Cada 12 horas", type: "interval", config: { hours: 12 } },
  { label: "Diariamente a las 2:00", type: "cron", config: { hour: 2, minute: 0 } },
  { label: "Diariamente a las 8:00", type: "cron", config: { hour: 8, minute: 0 } },
];

function formatDate(iso: string | null) {
  if (!iso) return "—";
  return new Date(iso).toLocaleString("es-ES", { dateStyle: "short", timeStyle: "short" });
}

function scheduleLabel(task: { schedule_type: string; schedule_config: Record<string, unknown> }) {
  if (task.schedule_type === "interval") {
    return `Cada ${task.schedule_config.hours}h`;
  }
  if (task.schedule_type === "cron") {
    const h = String(task.schedule_config.hour ?? 0).padStart(2, "0");
    const m = String(task.schedule_config.minute ?? 0).padStart(2, "0");
    return `Diariamente ${h}:${m}`;
  }
  return task.schedule_type;
}

export default function AutomatizacionesPage() {
  const queryClient = useQueryClient();
  const [adding, setAdding] = useState(false);
  const [form, setForm] = useState({
    name: "",
    action_type: "guesty_sync",
    schedule_preset: 2,
  });

  const { data: tasks = [] } = useQuery({
    queryKey: ["automations"],
    queryFn: listAutomations,
  });

  const createMutation = useMutation({
    mutationFn: () => {
      const preset = SCHEDULE_PRESETS[form.schedule_preset];
      return createAutomation({
        name: form.name,
        action_type: form.action_type,
        schedule_type: preset.type,
        schedule_config: preset.config,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["automations"] });
      setAdding(false);
      setForm({ name: "", action_type: "guesty_sync", schedule_preset: 2 });
    },
  });

  const toggleMutation = useMutation({
    mutationFn: ({ id, active }: { id: string; active: boolean }) =>
      updateAutomation(id, { is_active: active }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["automations"] }),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => deleteAutomation(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["automations"] }),
  });

  return (
    <div>
      <div className="mb-6 flex items-start justify-between">
        <div>
          <h1 className="text-xl font-bold text-white/90">Automatizaciones</h1>
          <p className="mt-1 text-sm text-white/45">Configura tareas programadas para sincronización automática.</p>
        </div>
        <button
          onClick={() => setAdding(true)}
          className="flex items-center gap-1.5 rounded-input border border-surface-border px-3 py-1.5 text-sm text-white/55 hover:border-accent/50 hover:text-accent"
        >
          <Plus className="h-3.5 w-3.5" />
          Nueva tarea
        </button>
      </div>

      {adding && (
        <div className="mb-4 glass-card p-5">
          <div className="mb-3 grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-xs text-white/40">Nombre</label>
              <input
                value={form.name}
                onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
                placeholder="Ej: Sync Guesty diario"
                className="w-full rounded-input border border-surface-border bg-surface-hover px-3 py-2 text-sm text-white/90 outline-none focus:border-accent"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs text-white/40">Acción</label>
              <select
                value={form.action_type}
                onChange={(e) => setForm((f) => ({ ...f, action_type: e.target.value }))}
                className="w-full rounded-input border border-surface-border bg-surface-hover px-3 py-2 text-sm text-white/90 outline-none focus:border-accent"
              >
                {ACTION_TYPES.map((a) => (
                  <option key={a.value} value={a.value}>{a.label}</option>
                ))}
              </select>
            </div>
          </div>
          <div className="mb-4">
            <label className="mb-2 block text-xs text-white/40">Frecuencia</label>
            <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
              {SCHEDULE_PRESETS.map((preset, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => setForm((f) => ({ ...f, schedule_preset: i }))}
                  className={`rounded-input border px-3 py-2 text-xs transition-colors ${
                    form.schedule_preset === i
                      ? "border-accent bg-accent/10 text-accent"
                      : "border-surface-border text-white/55 hover:border-accent/40"
                  }`}
                >
                  {preset.label}
                </button>
              ))}
            </div>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => createMutation.mutate()}
              disabled={!form.name || createMutation.isPending}
              className="rounded-input bg-accent px-4 py-1.5 text-sm text-white hover:bg-accent-hover disabled:opacity-50"
            >
              {createMutation.isPending ? "Creando..." : "Crear tarea"}
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

      {tasks.length === 0 && !adding ? (
        <div className="glass-card py-12 text-center">
          <Clock className="mx-auto mb-3 h-8 w-8 text-white/20" />
          <p className="text-sm text-white/30">No hay automatizaciones configuradas.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {tasks.map((task) => (
            <div key={task.id} className="glass-card p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`h-2 w-2 rounded-full ${task.is_active ? "bg-green-400" : "bg-white/20"}`} />
                  <div>
                    <p className="font-medium text-white/85">{task.name}</p>
                    <p className="text-xs text-white/40">
                      {ACTION_TYPES.find((a) => a.value === task.action_type)?.label ?? task.action_type}
                      {" · "}
                      {scheduleLabel(task)}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3 text-xs text-white/30">
                  <span>Última: {formatDate(task.last_run_at)}</span>
                  <div className="flex gap-1">
                    <button
                      onClick={() => toggleMutation.mutate({ id: task.id, active: !task.is_active })}
                      className="rounded p-1.5 hover:bg-white/5"
                      title={task.is_active ? "Pausar" : "Activar"}
                    >
                      {task.is_active ? (
                        <Pause className="h-3.5 w-3.5 text-amber-400/70" />
                      ) : (
                        <Play className="h-3.5 w-3.5 text-green-400/70" />
                      )}
                    </button>
                    <button
                      onClick={() => deleteMutation.mutate(task.id)}
                      className="rounded p-1.5 hover:bg-white/5"
                    >
                      <Trash2 className="h-3.5 w-3.5 text-red-400/50 hover:text-red-400" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
