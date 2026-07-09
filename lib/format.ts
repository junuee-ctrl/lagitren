/** Format angka besar ke gaya ringkas Indonesia (rb, jt, M). */
export function formatMetric(n?: number): string {
  if (n == null) return "";
  if (n >= 1_000_000_000) return `${(n / 1_000_000_000).toFixed(1)} M`;
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)} jt`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)} rb`;
  return `${n}`;
}

/** Waktu relatif sederhana dalam Bahasa Indonesia. */
export function timeAgo(iso: string, nowMs?: number): string {
  const then = new Date(iso).getTime();
  if (Number.isNaN(then)) return "";
  const now = nowMs ?? Date.now();
  const diff = Math.max(0, now - then);
  const min = Math.floor(diff / 60000);
  if (min < 1) return "baru saja";
  if (min < 60) return `${min} menit yang lalu`;
  const hr = Math.floor(min / 60);
  if (hr < 24) return `${hr} jam yang lalu`;
  const day = Math.floor(hr / 24);
  return `${day} hari yang lalu`;
}
