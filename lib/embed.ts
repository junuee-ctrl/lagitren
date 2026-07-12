import type { Platform, Trend } from "./types";

/** Ambil bagian slug dari id ("google:iphone-16-harga" -> "iphone-16-harga"). */
export function slugFromId(id: string): string {
  const idx = id.indexOf(":");
  return idx >= 0 ? id.slice(idx + 1) : id;
}

/** Bentuk id dari platform + slug. */
export function idFromSlug(platform: Platform, slug: string): string {
  return `${platform}:${slug}`;
}

const YT_ID = /^[a-zA-Z0-9_-]{11}$/;

/** Ekstrak ID video YouTube. Prioritas URL (v=) karena paling akurat. */
export function youtubeId(trend: Trend): string | null {
  // 1) Dari URL — sumber paling andal (tidak terpengaruh slugify).
  try {
    const u = new URL(trend.url);
    const v = u.searchParams.get("v");
    if (v && YT_ID.test(v)) return v;
    const m = u.pathname.match(/\/(embed|shorts)\/([a-zA-Z0-9_-]{11})/);
    if (m) return m[2];
    if (u.hostname.includes("youtu.be")) {
      const id = u.pathname.replace("/", "");
      if (YT_ID.test(id)) return id;
    }
  } catch {
    /* abaikan */
  }
  // 2) Fallback: slug (bila memang ID video mentah 11 karakter).
  const slug = slugFromId(trend.id);
  if (YT_ID.test(slug)) return slug;
  return null;
}

/** Apakah trend ini bisa di-embed & diputar di situs kita? */
export function canEmbed(trend: Trend): boolean {
  switch (trend.platform) {
    case "youtube":
      return youtubeId(trend) !== null;
    case "instagram":
      return /instagram\.com\/(p|reel|reels|tv)\//.test(trend.url);
    case "tiktok":
      return /tiktok\.com\/@[^/]+\/video\/\d+/.test(trend.url);
    case "twitter":
      return /(?:twitter|x)\.com\/[^/]+\/status\/\d+/.test(trend.url);
    default:
      return false;
  }
}

/** URL sumber asli untuk tautan sekunder ("lihat sumber"). */
export const SOURCE_LABEL: Record<Platform, string> = {
  google: "Buka di Google Trends",
  youtube: "Buka di YouTube",
  tiktok: "Buka di TikTok",
  instagram: "Buka di Instagram",
  shopee: "Buka di Shopee",
  twitter: "Buka di X",
  netflix: "Cari di Netflix"
};
