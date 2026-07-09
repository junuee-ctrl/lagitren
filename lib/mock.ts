import type { Trend } from "./types";

/**
 * Data contoh (mock) yang dipakai saat database D1 belum terhubung
 * atau belum ada data (mis. pengembangan lokal, preview build).
 * Setelah collector Python berjalan, data nyata dari D1 menggantikan ini.
 */

const now = "2026-07-09T08:00:00.000Z";

export const MOCK_TRENDS: Trend[] = [
  // ── Google Trends ──────────────────────────────────────────────
  {
    id: "google:iphone-16-harga",
    platform: "google",
    rank: 1,
    title: "iPhone 16 harga",
    subtitle: "↑ 5000%",
    metric: 200000,
    metricLabel: "pencarian",
    aiSummary:
      "Apple resmi mengumumkan harga iPhone 16 untuk pasar Indonesia mulai Rp 15 jutaan. Banyak netizen membandingkan spesifikasinya dengan Samsung Galaxy S24. Harga dapat berubah sewaktu-waktu.",
    url: "https://trends.google.co.id/trends/explore?q=iphone%2016%20harga&geo=ID",
    source: "Google Trends ID",
    hashtags: ["apple", "smartphone", "gadget"],
    affiliateUrl: "https://lagitren.id/go/shopee/iphone-16",
    price: "Mulai Rp 15 juta",
    interest: [8, 10, 9, 12, 15, 22, 40, 70, 100],
    collectedAt: now
  },
  {
    id: "google:hasil-liga-1",
    platform: "google",
    rank: 2,
    title: "hasil Liga 1",
    subtitle: "↑ 2000%",
    metric: 100000,
    metricLabel: "pencarian",
    aiSummary:
      "Pertandingan Liga 1 akhir pekan ini berakhir dramatis dengan gol di menit akhir. Pendukung ramai mencari skor dan klasemen terbaru.",
    url: "https://trends.google.co.id/trends/explore?q=hasil%20liga%201&geo=ID",
    source: "Google Trends ID",
    hashtags: ["liga1", "sepakbola", "bola"],
    interest: [20, 18, 22, 25, 30, 45, 80, 100],
    collectedAt: now
  },
  {
    id: "google:harga-emas-hari-ini",
    platform: "google",
    rank: 3,
    title: "harga emas hari ini",
    subtitle: "↑ 900%",
    metric: 80000,
    metricLabel: "pencarian",
    aiSummary:
      "Harga emas Antam bergerak naik mengikuti pasar global. Investor ritel memantau harga harian sebelum membeli. Harga dapat berubah sewaktu-waktu.",
    url: "https://trends.google.co.id/trends/explore?q=harga%20emas%20hari%20ini&geo=ID",
    source: "Google Trends ID",
    hashtags: ["emas", "investasi", "antam"],
    interest: [30, 35, 32, 40, 45, 55, 70, 100],
    collectedAt: now
  },
  {
    id: "google:cuaca-jakarta",
    platform: "google",
    rank: 4,
    title: "cuaca Jakarta",
    subtitle: "↑ 450%",
    metric: 60000,
    metricLabel: "pencarian",
    aiSummary:
      "BMKG memperkirakan hujan disertai angin kencang di Jabodetabek. Warga mencari prakiraan cuaca sebelum bepergian.",
    url: "https://trends.google.co.id/trends/explore?q=cuaca%20jakarta&geo=ID",
    source: "Google Trends ID",
    hashtags: ["cuaca", "bmkg", "jakarta"],
    interest: [40, 42, 38, 45, 50, 60, 80, 100],
    collectedAt: now
  },

  // ── YouTube Trending ───────────────────────────────────────────
  {
    // CATATAN DEMO: memakai video publik nyata agar embed & judul cocok.
    // Collector akan menggantinya dengan video trending Indonesia asli.
    id: "youtube:9bZkp7q19f0",
    platform: "youtube",
    rank: 1,
    title: "PSY - GANGNAM STYLE (강남스타일) M/V",
    subtitle: "2.5M views",
    metric: 2500000,
    metricLabel: "views",
    aiSummary:
      "Video musik legendaris PSY ini kembali ramai diputar setelah dipakai dalam sebuah tren tarian di media sosial. Nostalgia membuat penonton lama ikut menonton ulang.",
    url: "https://www.youtube.com/watch?v=9bZkp7q19f0",
    thumbnail: "https://i.ytimg.com/vi/9bZkp7q19f0/mqdefault.jpg",
    source: "officialpsy",
    hashtags: ["kpop", "psy", "musik"],
    collectedAt: now
  },
  {
    id: "youtube:dQw4w9WgXcQ",
    platform: "youtube",
    rank: 2,
    title: "Rick Astley - Never Gonna Give You Up (Official Video)",
    subtitle: "1.2M views",
    metric: 1200000,
    metricLabel: "views",
    aiSummary:
      "Fenomena 'rickroll' membuat video klasik ini terus kedatangan penonton baru. Banyak kreator memakainya untuk lelucon di media sosial.",
    url: "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    thumbnail: "https://i.ytimg.com/vi/dQw4w9WgXcQ/mqdefault.jpg",
    source: "Rick Astley",
    hashtags: ["musik", "rickroll", "viral"],
    collectedAt: now
  },
  {
    id: "youtube:jNQXAC9IVRw",
    platform: "youtube",
    rank: 3,
    title: "Me at the zoo",
    subtitle: "890K views",
    metric: 890000,
    metricLabel: "views",
    aiSummary:
      "Video pertama yang pernah diunggah ke YouTube ini kembali dibicarakan karena nilai sejarahnya. Banyak yang penasaran menonton awal mula platform video terbesar dunia.",
    url: "https://www.youtube.com/watch?v=jNQXAC9IVRw",
    thumbnail: "https://i.ytimg.com/vi/jNQXAC9IVRw/mqdefault.jpg",
    source: "jawed",
    hashtags: ["sejarah", "youtube", "viral"],
    collectedAt: now
  },

  // ── TikTok Viral ───────────────────────────────────────────────
  {
    // CATATAN DEMO: memakai video publik nyata agar embed tampil.
    id: "tiktok:doggface-cranberry",
    platform: "tiktok",
    rank: 1,
    title: "Naik skateboard sambil minum jus cranberry",
    subtitle: "80M views",
    metric: 80000000,
    metricLabel: "views",
    aiSummary:
      "Video santai seorang pria meluncur dengan skateboard sambil menikmati jus ini menjadi salah satu tren TikTok paling ikonik. Banyak yang meniru gaya santainya.",
    url: "https://www.tiktok.com/@420doggface208/video/6876424179084709126",
    hashtags: ["dreams", "vibes", "fyp"],
    collectedAt: now
  },
  {
    id: "tiktok:hashtag-outfitkerja",
    platform: "tiktok",
    rank: 2,
    title: "#OutfitKerja",
    subtitle: "9.8M views",
    metric: 9800000,
    metricLabel: "views",
    aiSummary:
      "Tren berbagi inspirasi gaya berpakaian ke kantor sedang ramai. Banyak pengguna memadukan item lokal dengan harga terjangkau.",
    url: "https://www.tiktok.com/tag/outfitkerja",
    hashtags: ["outfitkerja", "ootd", "fashion"],
    collectedAt: now
  },
  {
    id: "tiktok:sound-viral",
    platform: "tiktok",
    rank: 3,
    title: "Sound viral lagu dangdut remix",
    subtitle: "7.1M views",
    metric: 7100000,
    metricLabel: "views",
    aiSummary:
      "Remix lagu dangdut klasik menjadi backsound favorit untuk video transisi. Popularitasnya melonjak setelah dipakai beberapa selebgram.",
    url: "https://www.tiktok.com/",
    hashtags: ["dangdut", "sound", "viral"],
    collectedAt: now
  },

  // ── Instagram Hits ─────────────────────────────────────────────
  {
    // CATATAN DEMO: memakai postingan publik nyata agar embed tampil.
    id: "instagram:reels-1",
    platform: "instagram",
    rank: 1,
    title: "Foto telur pemecah rekor dunia (world_record_egg)",
    subtitle: "56 jt suka",
    metric: 56000000,
    metricLabel: "suka",
    aiSummary:
      "Foto sebutir telur ini memecahkan rekor jumlah suka terbanyak di Instagram dan menjadi fenomena global. Netizen ramai ikut menyukai dan membagikannya.",
    url: "https://www.instagram.com/p/BsOGulcndj-/",
    hashtags: ["worldrecordegg", "viral", "instagram"],
    collectedAt: now
  },
  {
    id: "instagram:reels-2",
    platform: "instagram",
    rank: 2,
    title: "Tutorial makeup natural untuk sehari-hari",
    subtitle: "2.1M plays",
    metric: 2100000,
    metricLabel: "plays",
    aiSummary:
      "Tutorial makeup simpel dengan produk lokal ini populer di kalangan pengguna muda. Banyak yang menyimpannya sebagai referensi.",
    url: "https://www.instagram.com/explore/",
    hashtags: ["makeup", "beauty", "tutorial"],
    collectedAt: now
  },

  // ── Shopee / Produk ────────────────────────────────────────────
  {
    id: "shopee:tws-earbuds",
    platform: "shopee",
    rank: 1,
    title: "TWS Earbuds Bluetooth 5.3",
    subtitle: "⭐ 4.8 · 10rb+ terjual",
    metric: 10000,
    metricLabel: "terjual",
    aiSummary:
      "Earbuds nirkabel dengan harga terjangkau ini banyak dicari karena kualitas suara yang dinilai baik di kelasnya. Harga dapat berubah sewaktu-waktu.",
    url: "https://shopee.co.id/search?keyword=tws%20earbuds",
    thumbnail: "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=480&q=70",
    hashtags: ["gadget", "audio", "earbuds"],
    affiliateUrl: "https://lagitren.id/go/shopee/tws-earbuds",
    price: "Rp 89.000 – Rp 150.000",
    collectedAt: now
  },
  {
    id: "shopee:skincare-serum",
    platform: "shopee",
    rank: 2,
    title: "Serum Vitamin C Brightening",
    subtitle: "⭐ 4.9 · 25rb+ terjual",
    metric: 25000,
    metricLabel: "terjual",
    aiSummary:
      "Serum wajah lokal ini sedang naik daun setelah banyak diulas di media sosial. Cocok untuk yang mencari perawatan kulit terjangkau. Harga dapat berubah sewaktu-waktu.",
    url: "https://shopee.co.id/search?keyword=serum%20vitamin%20c",
    thumbnail: "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=480&q=70",
    hashtags: ["skincare", "beauty", "serum"],
    affiliateUrl: "https://lagitren.id/go/shopee/serum-vitamin-c",
    price: "Rp 45.000 – Rp 120.000",
    collectedAt: now
  },
  {
    id: "shopee:kipas-angin",
    platform: "shopee",
    rank: 3,
    title: "Kipas Angin Portable Rechargeable",
    subtitle: "⭐ 4.7 · 8rb+ terjual",
    metric: 8000,
    metricLabel: "terjual",
    aiSummary:
      "Kipas portable yang bisa diisi ulang ini laris di musim panas. Praktis dibawa bepergian. Harga dapat berubah sewaktu-waktu.",
    url: "https://shopee.co.id/search?keyword=kipas%20angin%20portable",
    thumbnail: "https://images.unsplash.com/photo-1565374392739-dec5e7e08e4e?w=480&q=70",
    hashtags: ["gadget", "rumah", "musimpanas"],
    affiliateUrl: "https://lagitren.id/go/shopee/kipas-portable",
    price: "Rp 55.000 – Rp 99.000",
    collectedAt: now
  },

  // ── X (Twitter) Trending ───────────────────────────────────────
  {
    // CATATAN DEMO: memakai tweet publik nyata (tweet pertama di Twitter) agar embed tampil.
    id: "twitter:first-tweet",
    platform: "twitter",
    rank: 1,
    title: "\"just setting up my twttr\"",
    subtitle: "125rb tweet",
    metric: 125000,
    metricLabel: "kutipan",
    aiSummary:
      "Tweet pertama dalam sejarah Twitter ini kembali ramai dibicarakan warganet. Banyak yang menautkannya sebagai bagian dari nostalgia media sosial.",
    url: "https://twitter.com/jack/status/20",
    hashtags: ["twitter", "sejarah", "viral"],
    collectedAt: now
  },
  {
    id: "twitter:film-lokal",
    platform: "twitter",
    rank: 2,
    title: "Film Lokal Baru",
    subtitle: "88rb tweet",
    metric: 88000,
    metricLabel: "tweet",
    aiSummary:
      "Sebuah film Indonesia yang baru tayang menuai banyak perbincangan positif. Penonton membagikan kesan dan rekomendasi menonton.",
    url: "https://twitter.com/search?q=film%20lokal",
    hashtags: ["film", "bioskop", "review"],
    collectedAt: now
  },
  {
    id: "twitter:konser",
    platform: "twitter",
    rank: 3,
    title: "#WarThemConcert",
    subtitle: "64rb tweet",
    metric: 64000,
    metricLabel: "tweet",
    aiSummary:
      "Perang tiket konser musisi internasional yang akan tampil di Jakarta membuat tagar ini trending. Penggemar berbagi tips war tiket.",
    url: "https://twitter.com/search?q=konser",
    hashtags: ["konser", "tiket", "jakarta"],
    collectedAt: now
  }
];

export function mockTrendsByPlatform(platform: string): Trend[] {
  return MOCK_TRENDS.filter((t) => t.platform === platform).sort(
    (a, b) => a.rank - b.rank
  );
}
