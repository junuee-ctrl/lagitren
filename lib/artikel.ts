import type { ArticleCategory } from "./types";

/** Label tampil kategori artikel. */
export const KATEGORI_LABEL: Record<ArticleCategory, string> = {
  panduan: "Panduan",
  analisis: "Analisis",
  rekap: "Rekap Mingguan",
  kurasi: "Kurasi",
  bulanan: "Rekap Bulanan"
};

/** Warna chip kategori (inline style, konsisten dgn pola PLATFORMS.color). */
export const KATEGORI_COLOR: Record<ArticleCategory, string> = {
  panduan: "#00C9B1",
  analisis: "#E6007A",
  rekap: "#8B3DD6",
  kurasi: "#F59E0B",
  bulanan: "#3B82F6"
};

/** "2026-08-18 10:00:00" → "18 Agustus 2026". */
export function formatTanggal(value: string): string {
  const d = new Date(value.includes("T") ? value : value.replace(" ", "T") + "Z");
  if (Number.isNaN(d.getTime())) return value;
  return d.toLocaleDateString("id-ID", {
    timeZone: "Asia/Jakarta",
    day: "numeric",
    month: "long",
    year: "numeric"
  });
}
