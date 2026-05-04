"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const TABS = [
  { href: "/configuracion/integraciones", label: "Integraciones" },
  { href: "/configuracion/ia", label: "IA" },
  { href: "/configuracion/api-keys", label: "API Keys" },
  { href: "/configuracion/automatizaciones", label: "Automatizaciones" },
  { href: "/configuracion/usuarios", label: "Usuarios" },
  { href: "/configuracion/logs", label: "Logs" },
];

export default function ConfiguracionLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div>
      <div className="mb-6">
        <nav className="flex gap-1 border-b border-surface-border">
          {TABS.map((tab) => (
            <Link
              key={tab.href}
              href={tab.href}
              className={`px-4 py-2.5 text-sm transition-colors ${
                pathname.startsWith(tab.href)
                  ? "border-b-2 border-accent text-accent"
                  : "text-white/45 hover:text-white/70"
              }`}
            >
              {tab.label}
            </Link>
          ))}
        </nav>
      </div>
      {children}
    </div>
  );
}
