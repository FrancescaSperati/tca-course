import type { Habit } from "./types";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`/api${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!res.ok) throw new Error(`${init?.method ?? "GET"} ${path} failed (${res.status})`);
  return res.json() as Promise<T>;
}

export const listHabits = () => request<Habit[]>("/habits");

export const createHabit = (name: string, emoji: string) =>
  request<Habit>("/habits", { method: "POST", body: JSON.stringify({ name, emoji }) });

export const setDone = (id: number, done: boolean) =>
  request<Habit>(`/habits/${id}/complete`, { method: done ? "POST" : "DELETE" });
