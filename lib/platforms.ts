import type { Platform, PlatformMeta } from "./types";

export const PLATFORMS: Record<Platform, PlatformMeta> = {
  google: {
    key: "google",
    name: "Google Trends",
    icon: "🔍",
    color: "#4285F4",
    sectionTitle: "Google Trends",
    description:
      "Kata kunci pencarian yang sedang naik daun di Google Indonesia — apa yang paling banyak dicari orang saat ini.",
    refresh: "Diperbarui tiap 1 jam"
  },
  youtube: {
    key: "youtube",
    name: "YouTube Trending",
    icon: "🎬",
    color: "#FF0000",
    sectionTitle: "YouTube Trending",
    description:
      "Video yang sedang populer dan naik daun di YouTube Indonesia — dari musik, hiburan, hingga berita.",
    refresh: "Diperbarui tiap 1 jam"
  },
  tiktok: {
    key: "tiktok",
    name: "TikTok Viral",
    icon: "🎵",
    color: "#010101",
    sectionTitle: "TikTok Viral",
    description:
      "Video dan hashtag yang sedang viral di TikTok — tren, sound, dan challenge yang lagi ramai.",
    refresh: "Diperbarui tiap 3 jam"
  },
  instagram: {
    key: "instagram",
    name: "Instagram Hits",
    icon: "📸",
    color: "#E4405F",
    sectionTitle: "Instagram Hits",
    description:
      "Reels dan postingan yang sedang populer di Instagram Indonesia.",
    refresh: "Diperbarui tiap 6 jam"
  },
  shopee: {
    key: "shopee",
    name: "Produk Viral",
    icon: "🛍️",
    color: "#FE2C55",
    sectionTitle: "Produk Viral",
    description:
      "Produk terlaris & viral di TikTok Shop / Tokopedia Indonesia — pilihan editor, lengkap dengan tautan belanja.",
    refresh: "Diperbarui berkala"
  },
  twitter: {
    key: "twitter",
    name: "X (Twitter) Trending",
    icon: "💬",
    color: "#000000",
    sectionTitle: "X (Twitter) Trending",
    description:
      "Topik dan hashtag yang sedang trending di X (Twitter) Indonesia.",
    refresh: "Diperbarui tiap 30 menit"
  },
  netflix: {
    key: "netflix",
    name: "Netflix Top 10",
    icon: "🍿",
    color: "#E50914",
    sectionTitle: "Netflix Top 10",
    description:
      "Film dan serial paling banyak ditonton di Netflix Indonesia minggu ini — daftar Top 10 resmi.",
    refresh: "Dicek tiap hari"
  }
};

/** Urutan tampil platform di homepage. */
export const PLATFORM_ORDER: Platform[] = [
  "google",
  "youtube",
  "netflix",
  "instagram",
  "tiktok",
  "twitter",
  "shopee"
];

export function getPlatform(key: string): PlatformMeta | undefined {
  return PLATFORMS[key as Platform];
}
