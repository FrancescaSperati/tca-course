export interface Habit {
  id: number;
  name: string;
  emoji: string;
  created_at: string;
  completed_today: boolean;
  streak: number;
  longest_streak: number;
  last_completed: string | null;
}
