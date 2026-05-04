"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Key, CheckCircle, XCircle, Eye, EyeOff, Save, Trash2, Zap } from "lucide-react";
import { listCredentials, upsertCredential, deleteCredential, testCredential } from "@/lib/api/credentials";

const KNOWN_SERVICES = [
  {
    key: "GUESTY_API_KEY",
    label: "Guesty API Key",
    description: "API key de la Guesty Pro Open API para sincronizar propiedades y reservas",
    docs: "https://open-api.guesty.com",
  },
  {
    key: "OPENAI_API_KEY",
    label: "OpenAI API Key",
    description: "API key de OpenAI para generar embeddings (text-embedding-3-small)",
    docs: "https://platform.openai.com",
  },
  {
    key: "ANTHROPIC_API_KEY",
    label: "Anthropic API Key",
    description: "API key de Anthropic para el chat RAG (Claude claude-sonnet-4-20250514)",
    docs: "https://console.anthropic.com",
  },
];

export default function IntegracionesPage() {
  const queryClient = useQueryClient();
  const [inputs, setInputs] = useState<Record<string, string>>({});
  const [visible, setVisible] = useState<Record<string, boolean>>({});
  const [testResults, setTestResults] = useState<Record<string, { status: "ok" | "error"; message?: string }>>({});

  const { data: credentials = [] } = useQuery({
    queryKey: ["credentials"],
    queryFn: listCredentials,
  });

  const saveMutation = useMutation({
    mutationFn: ({ service, value }: { service: string; value: string }) =>
      upsertCredential(service, value),
    onSuccess: (_, { service }) => {
      queryClient.invalidateQueries({ queryKey: ["credentials"] });
      setInputs((prev) => ({ ...prev, [service]: "" }));
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (service: string) => deleteCredential(service),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["credentials"] }),
  });

  async function handleTest(service: string) {
    const result = await testCredential(service);
    setTestResults((prev) => ({ ...prev, [service]: result }));
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-xl font-bold text-white/90">Integraciones</h1>
        <p className="mt-1 text-sm text-white/45">
          Configura las credenciales de acceso a servicios externos. Las claves se almacenan cifradas con AES-256-GCM.
        </p>
      </div>

      <div className="space-y-4">
        {KNOWN_SERVICES.map((service) => {
          const stored = credentials.find((c) => c.service_name === service.key);
          const testResult = testResults[service.key];

          return (
            <div key={service.key} className="glass-card p-6">
              <div className="mb-4 flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-accent/10">
                    <Key className="h-4 w-4 text-accent" />
                  </div>
                  <div>
                    <h3 className="font-medium text-white/90">{service.label}</h3>
                    <p className="text-xs text-white/40">{service.description}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {stored ? (
                    <span className="flex items-center gap-1 rounded-sm bg-green-500/10 px-2 py-0.5 text-xs text-green-400">
                      <CheckCircle className="h-3 w-3" />
                      Configurada
                    </span>
                  ) : (
                    <span className="flex items-center gap-1 rounded-sm bg-white/5 px-2 py-0.5 text-xs text-white/40">
                      No configurada
                    </span>
                  )}
                </div>
              </div>

              {stored && (
                <div className="mb-3 flex items-center gap-2 text-xs text-white/30">
                  <span>Última actualización: {stored.updated_at ? new Date(stored.updated_at).toLocaleDateString("es-ES") : "—"}</span>
                </div>
              )}

              <div className="flex gap-2">
                <div className="relative flex-1">
                  <input
                    type={visible[service.key] ? "text" : "password"}
                    placeholder={stored ? "••••••••••••••••••••••••••••••••" : "Pega aquí la API key..."}
                    value={inputs[service.key] ?? ""}
                    onChange={(e) => setInputs((prev) => ({ ...prev, [service.key]: e.target.value }))}
                    className="w-full rounded-input border border-surface-border bg-surface-hover px-3 py-2 pr-10 font-mono text-sm text-white/90 outline-none focus:border-accent"
                  />
                  <button
                    type="button"
                    onClick={() => setVisible((prev) => ({ ...prev, [service.key]: !prev[service.key] }))}
                    className="absolute right-2 top-1/2 -translate-y-1/2 text-white/30 hover:text-white/60"
                  >
                    {visible[service.key] ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
                <button
                  onClick={() => saveMutation.mutate({ service: service.key, value: inputs[service.key] ?? "" })}
                  disabled={!inputs[service.key] || saveMutation.isPending}
                  className="flex items-center gap-1.5 rounded-input bg-accent px-3 py-2 text-sm text-white hover:bg-accent-hover disabled:opacity-50"
                >
                  <Save className="h-3.5 w-3.5" />
                  Guardar
                </button>
                {stored && (
                  <>
                    <button
                      onClick={() => handleTest(service.key)}
                      className="flex items-center gap-1.5 rounded-input border border-surface-border px-3 py-2 text-sm text-white/55 hover:border-accent/50 hover:text-accent"
                    >
                      <Zap className="h-3.5 w-3.5" />
                      Probar
                    </button>
                    <button
                      onClick={() => deleteMutation.mutate(service.key)}
                      className="flex items-center gap-1.5 rounded-input border border-red-500/20 px-3 py-2 text-sm text-red-400/60 hover:border-red-400/40 hover:text-red-400"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </button>
                  </>
                )}
              </div>

              {testResult && (
                <div className={`mt-3 flex items-center gap-2 rounded-sm px-3 py-2 text-sm ${
                  testResult.status === "ok"
                    ? "bg-green-500/10 text-green-400"
                    : "bg-red-500/10 text-red-400"
                }`}>
                  {testResult.status === "ok" ? (
                    <CheckCircle className="h-4 w-4 shrink-0" />
                  ) : (
                    <XCircle className="h-4 w-4 shrink-0" />
                  )}
                  {testResult.message ?? (testResult.status === "ok" ? "Conexión correcta" : "Error de conexión")}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
