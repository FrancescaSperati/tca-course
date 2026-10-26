import { useEffect, useState } from "react";
import { createHabit, listHabits, setDone } from "./api";
import type { Habit } from "./types";

const HOT_STREAK = 7; // the badge highlights once the streak passes this

const todayLocal = () => new Date().toLocaleDateString("sv"); // YYYY-MM-DD, local time

export default function App() {
  const [habits, setHabits] = useState<Habit[]>([]);
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [emoji, setEmoji] = useState("✅");
  const [name, setName] = useState("");

  const replace = (h: Habit) => setHabits((prev) => prev.map((p) => (p.id === h.id ? h : p)));

  useEffect(() => {
    listHabits()
      .then(setHabits)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoaded(true));
  }, []);

  async function toggle(habit: Habit) {
    const done = !habit.completed_today;
    setError(null);
    // Optimistic: flip the tick now, then take the server's streak (or roll back).
    replace({ ...habit, completed_today: done, last_completed: done ? todayLocal() : habit.last_completed });
    try {
      replace(await setDone(habit.id, done));
    } catch (e) {
      replace(habit);
      setError((e as Error).message);
    }
  }

  async function add(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim() || !emoji.trim()) return;
    setError(null);
    try {
      const created = await createHabit(name, emoji);
      setHabits((prev) => [...prev, created]);
      setName("");
    } catch (err) {
      setError((err as Error).message);
    }
  }

  return (
    <main>
      <h1>Habits</h1>
      {error && <p className="error" role="alert">{error}</p>}

      <ul className="habits">
        {habits.map((h) => (
          <li key={h.id} className={h.completed_today ? "done" : undefined}>
            <label>
              <input
                type="checkbox"
                checked={h.completed_today}
                onChange={() => toggle(h)}
                aria-label={`Mark ${h.name} done today`}
              />
              <span className="emoji">{h.emoji}</span>
              <span className="name">{h.name}</span>
              <span className="last">{h.last_completed ? `last: ${h.last_completed}` : "never done"}</span>
            </label>
            <span className="streaks">
              <span
                className={h.streak > HOT_STREAK ? "streak hot" : "streak"}
                title="Current streak (days)"
              >
                🔥 {h.streak}
              </span>
              <span className="best" title="Longest streak (days)">best {h.longest_streak}</span>
            </span>
          </li>
        ))}
      </ul>
      {loaded && habits.length === 0 && !error && <p className="empty">No habits yet — add one below.</p>}

      <form onSubmit={add}>
        <input
          className="emoji-input"
          value={emoji}
          onChange={(e) => setEmoji(e.target.value)}
          aria-label="Emoji"
          maxLength={16}
        />
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="New habit"
          aria-label="Habit name"
          maxLength={100}
        />
        <button type="submit" disabled={!name.trim() || !emoji.trim()}>Add</button>
      </form>
    </main>
  );
}
