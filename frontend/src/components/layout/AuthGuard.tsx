"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/auth";
import { getMe } from "@/lib/api/auth";

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const { user, isLoading, setUser, setLoading } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    if (user) return;

    getMe()
      .then((u) => setUser(u))
      .catch(() => {
        setUser(null);
        router.replace("/login");
      });
  }, [user, setUser, setLoading, router]);

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-accent border-t-transparent" />
      </div>
    );
  }

  if (!user) return null;

  return <>{children}</>;
}
