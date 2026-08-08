/**
 * ID penerbit Google AdSense.
 * Bisa dioverride lewat env NEXT_PUBLIC_ADSENSE_CLIENT; default ke ID situs.
 * (ID penerbit bersifat publik — muncul di source halaman.)
 */
export const ADSENSE_CLIENT =
  process.env.NEXT_PUBLIC_ADSENSE_CLIENT || "ca-pub-4312945092715398";

/**
 * ID unit iklan (data-ad-slot) dari AdSense. Satu ID boleh dipakai ulang
 * di beberapa posisi.
 * - atas   : konten atas (detail atas, daftar platform atas, arsip atas)
 * - bawah  : konten bawah (detail bawah)
 * - beranda: sisipan di feed beranda
 */
export const AD_SLOTS = {
  atas: "8570552286",
  bawah: "9799873479",
  beranda: "3574476554"
} as const;
