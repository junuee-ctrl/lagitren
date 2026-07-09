export type Platform =
  | "google"
  | "youtube"
  | "tiktok"
  | "instagram"
  | "shopee"
  | "twitter";

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
  /** Waktu pengumpulan (ISO string / epoch). */
  collectedAt: string;
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
