/** Format angka besar ke gaya ringkas Indonesia (rb, jt, M). */
export function formatMetric(n?: number): string {
  if (n == null) return "";
  if (n >= 1_000_000_000) return `${(n / 1_000_000_000).toFixed(1)} M`;
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)} jt`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)} rb`;
  return `${n}`;
}

const BULAN_ID = [
  "Januari", "Februari", "Maret", "April", "Mei", "Juni",
  "Juli", "Agustus", "September", "Oktober", "November", "Desember"
];

/** Kunci tanggal stabil "YYYY-MM-DD" (UTC) untuk pengelompokan. */
export function dateKey(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "";
  return d.toISOString().slice(0, 10);
}

/** Tanggal gaya Indonesia, mis. "9 Juli 2026". Terima ISO atau "YYYY-MM-DD". */
export function formatDateID(value: string): string {
  const d = new Date(value.length === 10 ? `${value}T00:00:00Z` : value);
  if (Number.isNaN(d.getTime())) return value;
  return `${d.getUTCDate()} ${BULAN_ID[d.getUTCMonth()]} ${d.getUTCFullYear()}`;
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
