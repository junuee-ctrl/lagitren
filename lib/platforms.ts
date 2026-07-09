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
    name: "Produk Lagi Dicari",
    icon: "🛒",
    color: "#EE4D2D",
    sectionTitle: "Produk Lagi Dicari",
    description:
      "Produk dan kata kunci yang paling banyak dicari di marketplace Indonesia — lengkap dengan tautan untuk cek harga.",
    refresh: "Diperbarui tiap 3 jam"
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
  }
};

/** Urutan tampil platform di homepage. */
export const PLATFORM_ORDER: Platform[] = [
  "google",
  "youtube",
  "tiktok",
  "instagram",
  "shopee",
  "twitter"
];

export function getPlatform(key: string): PlatformMeta | undefined {
  return PLATFORMS[key as Platform];
}
