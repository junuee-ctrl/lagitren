/**
 * ID penerbit Google AdSense.
 * Bisa dioverride lewat env NEXT_PUBLIC_ADSENSE_CLIENT; default ke ID situs.
 * (ID penerbit bersifat publik — muncul di source halaman.)
 */
export const ADSENSE_CLIENT =
  process.env.NEXT_PUBLIC_ADSENSE_CLIENT || "ca-pub-2000492494761637";
