"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, UserCheck, UserX, Shield } from "lucide-react";
import { listUsers, createUser, updateUser } from "@/lib/api/admin";

export default function UsuariosPage() {
  const queryClient = useQueryClient();
  const [showInvite, setShowInvite] = useState(false);
  const [form, setForm] = useState({ email: "", full_name: "", password: "", role: "user" });

  const { data: users = [] } = useQuery({
    queryKey: ["users"],
    queryFn: listUsers,
  });

  const inviteMutation = useMutation({
    mutationFn: () => createUser(form),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
      setShowInvite(false);
      setForm({ email: "", full_name: "", password: "", role: "user" });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Parameters<typeof updateUser>[1] }) =>
      updateUser(id, payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["users"] }),
  });

  function formatDate(iso: string | null) {
    if (!iso) return "—";
    return new Date(iso).toLocaleDateString("es-ES");
  }

  return (
    <div>
      <div className="mb-6 flex items-start justify-between">
        <div>
          <h1 className="text-xl font-bold text-white/90">Usuarios</h1>
          <p className="mt-1 text-sm text-white/45">Gestiona los accesos al sistema.</p>
        </div>
        <button
          onClick={() => setShowInvite(true)}
          className="flex items-center gap-1.5 rounded-input border border-surface-border px-3 py-1.5 text-sm text-white/55 hover:border-accent/50 hover:text-accent"
        >
          <Plus className="h-3.5 w-3.5" />
          Invitar usuario
        </button>
      </div>

      {showInvite && (
        <div className="mb-4 glass-card p-5">
          <div className="mb-3 grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-xs text-white/40">Email</label>
              <input
                type="email"
                value={form.email}
                onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
                className="w-full rounded-input border border-surface-border bg-surface-hover px-3 py-2 text-sm text-white/90 outline-none focus:border-accent"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs text-white/40">Nombre completo</label>
              <input
                value={form.full_name}
                onChange={(e) => setForm((f) => ({ ...f, full_name: e.target.value }))}
                className="w-full rounded-input border border-surface-border bg-surface-hover px-3 py-2 text-sm text-white/90 outline-none focus:border-accent"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs text-white/40">Contraseña inicial</label>
              <input
                type="password"
                value={form.password}
                onChange={(e) => setForm((f) => ({ ...f, password: e.target.value }))}
                className="w-full rounded-input border border-surface-border bg-surface-hover px-3 py-2 text-sm text-white/90 outline-none focus:border-accent"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs text-white/40">Rol</label>
              <select
                value={form.role}
                onChange={(e) => setForm((f) => ({ ...f, role: e.target.value }))}
                className="w-full rounded-input border border-surface-border bg-surface-hover px-3 py-2 text-sm text-white/90 outline-none focus:border-accent"
              >
                <option value="user">Usuario</option>
                <option value="admin">Administrador</option>
              </select>
            </div>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => inviteMutation.mutate()}
              disabled={!form.email || !form.full_name || !form.password || inviteMutation.isPending}
              className="rounded-input bg-accent px-4 py-1.5 text-sm text-white hover:bg-accent-hover disabled:opacity-50"
            >
              {inviteMutation.isPending ? "Creando..." : "Crear usuario"}
            </button>
            <button
              onClick={() => setShowInvite(false)}
              className="rounded-input border border-surface-border px-4 py-1.5 text-sm text-white/55"
            >
              Cancelar
            </button>
          </div>
        </div>
      )}

      <div className="glass-card overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-surface-border text-left text-xs text-white/40">
              <th className="px-4 py-3">Usuario</th>
              <th className="px-4 py-3">Rol</th>
              <th className="px-4 py-3">Estado</th>
              <th className="px-4 py-3">Último acceso</th>
              <th className="px-4 py-3">Acciones</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-surface-border">
            {users.map((user) => (
              <tr key={user.id} className="text-white/70">
                <td className="px-4 py-3">
                  <p className="font-medium">{user.full_name}</p>
                  <p className="text-xs text-white/40">{user.email}</p>
                </td>
                <td className="px-4 py-3">
                  <select
                    value={user.role}
                    onChange={(e) => updateMutation.mutate({ id: user.id, payload: { role: e.target.value } })}
                    className="rounded-sm border border-surface-border bg-transparent px-2 py-0.5 text-xs text-white/70 outline-none"
                  >
                    <option value="user">Usuario</option>
                    <option value="admin">Administrador</option>
                  </select>
                </td>
                <td className="px-4 py-3">
                  <span className={`flex items-center gap-1 text-xs ${user.is_active ? "text-green-400" : "text-red-400"}`}>
                    {user.is_active ? <UserCheck className="h-3.5 w-3.5" /> : <UserX className="h-3.5 w-3.5" />}
                    {user.is_active ? "Activo" : "Desactivado"}
                  </span>
                </td>
                <td className="px-4 py-3 text-white/40">{formatDate(user.last_login_at)}</td>
                <td className="px-4 py-3">
                  <button
                    onClick={() => updateMutation.mutate({ id: user.id, payload: { is_active: !user.is_active } })}
                    className={`text-xs ${user.is_active ? "text-red-400/60 hover:text-red-400" : "text-green-400/60 hover:text-green-400"}`}
                  >
                    {user.is_active ? "Desactivar" : "Activar"}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
