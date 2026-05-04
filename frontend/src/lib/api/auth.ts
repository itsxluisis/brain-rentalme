import { api } from "./client";

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: "admin" | "user";
  is_active: boolean;
  last_login_at: string | null;
  created_at: string;
}

export async function getMe(): Promise<User> {
  const { data } = await api.get<User>("/api/v1/auth/me");
  return data;
}

export async function login(email: string, password: string): Promise<User> {
  const { data } = await api.post<User>("/api/v1/auth/login", { email, password });
  return data;
}

export async function setup(email: string, password: string, full_name: string): Promise<User> {
  const { data } = await api.post<User>("/api/v1/auth/setup", { email, password, full_name });
  return data;
}

export async function logout(): Promise<void> {
  await api.post("/api/v1/auth/logout");
}
