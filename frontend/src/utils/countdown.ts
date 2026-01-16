export interface CountdownTime {
  days: number;
  hours: number;
  minutes: number;
  seconds: number;
}

export function calculateCountdown(endTime: string | Date): CountdownTime {
  const now = new Date().getTime();
  const end = new Date(endTime).getTime();
  const timeRemaining = end - now;

  if (timeRemaining <= 0) {
    return { days: 0, hours: 0, minutes: 0, seconds: 0 };
  }

  const days = Math.floor(timeRemaining / (1000 * 60 * 60 * 24));
  const hours = Math.floor(
    (timeRemaining % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60),
  );
  const minutes = Math.floor((timeRemaining % (1000 * 60 * 60)) / (1000 * 60));
  const seconds = Math.floor((timeRemaining % (1000 * 60)) / 1000);

  return { days, hours, minutes, seconds };
}

export function formatTime(num: number): string {
  return String(num).padStart(2, "0");
}
