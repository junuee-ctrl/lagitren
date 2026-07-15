export type Platform =
  | "google"
  | "youtube"
  | "tiktok"
  | "instagram"
  | "shopee"
  | "twitter"
  | "netflix"
  | "bioskop";

export interface Trend {
  /** ID unik stabil (platform + slug/source id) untuk upsert. */
  id: string;
  platform: Platform;
  /** Peringkat dalam platform (1 = paling atas). */
  rank: number;
  /** Judul utama: kata kunci / judul video / hashtag / nama produk. */
  title: string;
  /** Baris info sekunder opsional, mis. "↑ 5000%" atau "2.5M views". */
  subtitle?: string;
  /** Nilai metrik mentah (search volume, views, tweet count, dll.). */
  metric?: number;
  /** Label metrik, mis. "views", "pencarian", "tweet". */
  metricLabel?: string;
  /** Ringkasan AI "kenapa lagi tren" dalam Bahasa Indonesia (maks 3 baris). */
  aiSummary?: string;
  /** Tautan ke sumber asli di platform. */
  url: string;
  /** URL thumbnail opsional (YouTube/TikTok/Instagram/Shopee). */
  thumbnail?: string;
  /** Sumber tambahan, mis. nama channel / akun. */
  source?: string;
  /** Hashtag terkait. */
  hashtags?: string[];
  /** Tautan afiliasi (khusus produk Shopee/Tokopedia). */
  affiliateUrl?: string;
  /** Rentang harga produk, mis. "Rp 15 juta". */
  price?: string;
  /**
   * Deret minat pencarian (khusus Google Trends) untuk grafik volume.
   * Nilai relatif 0–100 seperti Google Trends "interest over time".
   */
  interest?: number[];
  /** Konteks kaya per-platform (berita Google, komentar YouTube, dll.). */
  extra?: TrendExtra;
  /** true = sedang tren; false = arsip (sudah tidak aktif). */
  isCurrent?: boolean;
  /** Waktu pengumpulan (ISO string / epoch). */
  collectedAt: string;
}

/** Satu tautan berita terkait (khusus Google Trends). */
export interface TrendNews {
  title: string;
  url: string;
  source?: string;
}

/** Satu komentar unggulan (khusus YouTube). */
export interface TrendComment {
  author?: string;
  text: string;
  likes?: number;
}

/** Info OTT/streaming (khusus Netflix Top 10). */
export interface TrendOtt {
  /** "Film" atau "Serial TV". */
  kind?: string;
  /** Rating penonton (TMDB), 0–10. */
  rating?: number;
  /** Sinopsis singkat (Bahasa Indonesia bila tersedia). */
  synopsis?: string;
  /** Jumlah minggu berturut di Top 10. */
  weeks?: string | number;
  /** Peringkat mingguan di kategorinya. */
  rank?: string | number;
}

/** Satu tweet teratas (khusus X/Twitter). */
export interface TrendTweet {
  url: string;
  retweets?: number;
  likes?: number;
}

/** Info video representatif (khusus TikTok). */
export interface TrendTiktok {
  videoUrl?: string;
  author?: string;
  plays?: number;
}

/** Data konteks kaya yang disimpan di kolom `extra` (JSON). */
export interface TrendExtra {
  /** Berita terkait teratas (Google Trends). */
  news?: TrendNews[];
  /** Komentar terbaik (YouTube). */
  comments?: TrendComment[];
  /** Info OTT (Netflix Top 10). */
  ott?: TrendOtt;
  /** Tweet teratas (X/Twitter). */
  tweets?: TrendTweet[];
  /** Video representatif (TikTok). */
  tiktok?: TrendTiktok;
}

export interface PlatformMeta {
  key: Platform;
  /** Nama tampil, mis. "Google Trends". */
  name: string;
  /** Emoji ikon sederhana. */
  icon: string;
  /** Warna aksen (hex). */
  color: string;
  /** Judul section di homepage. */
  sectionTitle: string;
  /** Deskripsi singkat untuk halaman detail & SEO. */
  description: string;
  /** Frekuensi pembaruan untuk ditampilkan. */
  refresh: string;
}
