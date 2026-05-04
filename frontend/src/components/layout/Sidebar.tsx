"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Building2,
  Blocks,
  MessageSquare,
  RefreshCw,
  Calendar,
  Settings,
  Map,
} from "lucide-react";
import { cn } from "@/lib/utils/cn";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/propiedades", label: "Propiedades", icon: Building2 },
  { href: "/mapa", label: "Mapa", icon: Map },
  { href: "/sistemas", label: "Sistemas", icon: Blocks },
  { href: "/chat", label: "Chat IA", icon: MessageSquare },
  { href: "/sincronizacion", label: "Sincronización", icon: RefreshCw },
  { href: "/reservas", label: "Reservas", icon: Calendar },
  { href: "/configuracion", label: "Configuración", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex h-screen w-64 flex-col border-r border-surface-border bg-surface backdrop-blur-glass">
      <div className="flex h-16 items-center px-6">
        <h1 className="text-xl font-bold text-accent">BrAIn</h1>
        <span className="ml-2 text-xs text-white/30">RentalMe</span>
      </div>

      <nav className="flex-1 space-y-1 px-3 py-4">
        {navItems.map((item) => {
          const isActive =
            pathname === item.href || pathname.startsWith(item.href + "/");
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-input px-3 py-2.5 text-sm transition-colors",
                isActive
                  ? "bg-accent/10 text-accent"
                  : "text-white/55 hover:bg-surface-hover hover:text-white/90"
              )}
            >
              <item.icon className="h-4 w-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
