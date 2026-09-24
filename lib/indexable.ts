import type { TrendExtra } from "./types";

/**
 * Satu-satunya aturan yang menentukan apakah halaman detail tren boleh
 * diindeks mesin pencari. Dipakai BERSAMA oleh dua tempat:
 *   - app/[platform]/[slug]/page.tsx  → meta robots
 *   - app/sitemap.ts                  → daftar URL yang kita ajukan
 * Keduanya wajib memakai fungsi ini supaya sitemap tidak pernah mengajukan
 * URL yang halamannya sendiri menyatakan noindex.
 *
 * LATAR (22-24 September 2026): Search Console melaporkan 3.900 halaman
 * terindeks tetapi 2.791 lainnya berstatus "ditemukan - belum diindeks",
 * sementara tayangan pencarian turun ke nol. Isinya didominasi halaman tren
 * tipis, sedangkan tulisan sungguhan hanya puluhan. Kami berhenti mengajukan
 * semua URL dan hanya mengajukan yang benar-benar punya naskah.
 */

/** Panjang minimum naskah (gabungan) agar sebuah halaman tren layak diajukan. */
export const MIN_ARTICLE_CHARS = 200;

/** Cuplikan yang dipakai pra-saring di SQL; harus konsisten dgn fungsi di bawah. */
export const ARTICLE_SQL_HINT = '%"article"%';

export function trendIsIndexable(extra?: TrendExtra | null): boolean {
  const a = extra?.article;
  if (!a) return false;
  const text = [a.lead, a.apa, a.rame, a.penting]
    .filter((s): s is string => typeof s === "string" && s.trim().length > 0)
    .join(" ")
    .trim();
  return text.length >= MIN_ARTICLE_CHARS;
}
