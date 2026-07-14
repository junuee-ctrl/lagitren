import type { Trend } from "./types";

/**
 * Pencocokan produk afiliasi (TikTok Shop) ke tren berdasarkan kategori.
 * Dipakai halaman detail: mis. tren skincare → tampilkan produk kategori beauty.
 */

// Kategori kanonik → kata kunci (Indonesia + Inggris).
const CATEGORY_KEYWORDS: Record<string, string[]> = {
  beauty: [
    "beauty", "kecantikan", "skincare", "kosmetik", "makeup", "serum",
    "sabun", "cream", "krim", "glow", "wajah", "kulit", "bedak", "lipstik",
    "parfum", "toner", "sunscreen", "moisturizer", "rambut", "shampoo",
    "body", "whitening", "acne", "jerawat", "niacinamide"
  ],
  fashion: [
    "fashion", "baju", "hijab", "dress", "sepatu", "sandal", "tas", "celana",
    "kemeja", "jaket", "outfit", "gamis", "kaos", "kerudung", "busana",
    "pakaian", "sneakers", "jam tangan", "aksesoris"
  ],
  gadget: [
    "gadget", "hp", "smartphone", "iphone", "samsung", "xiaomi", "laptop",
    "charger", "earphone", "headset", "tws", "case", "powerbank",
    "elektronik", "kamera", "keyboard", "mouse", "gaming"
  ],
  food: [
    "makanan", "snack", "kuliner", "minuman", "kopi", "coklat", "cemilan",
    "food", "resep", "masak", "camilan", "keripik", "bumbu"
  ],
  home: [
    "rumah", "dapur", "peralatan", "furniture", "dekorasi", "home",
    "kitchen", "perabot", "sprei", "bantal", "lampu", "storage"
  ],
  mom_baby: [
    "bayi", "baby", "anak", "popok", "diapers", "mainan", "ibu", "maternity",
    "stroller", "asi"
  ],
  health: [
    "kesehatan", "vitamin", "suplemen", "obat", "herbal", "madu", "diet",
    "health", "masker"
  ]
};

/** Deteksi kategori kanonik dari teks bebas (judul/hashtag/kategori sheet). */
export function detectCategory(text: string): string | null {
  const t = (text || "").toLowerCase();
  if (!t.trim()) return null;
  // 1) cocok langsung dengan nama kategori kanonik.
  for (const key of Object.keys(CATEGORY_KEYWORDS)) {
    if (t.includes(key)) return key;
  }
  // 2) cocok via kata kunci.
  for (const [key, words] of Object.entries(CATEGORY_KEYWORDS)) {
    if (words.some((w) => t.includes(w))) return key;
  }
  return null;
}

/** Produk yang relevan dengan sebuah tren (berdasarkan kategori). */
export function relatedProducts(
  trend: Trend,
  products: Trend[],
  limit = 3
): Trend[] {
  const cat = detectCategory(
    [trend.title, ...(trend.hashtags ?? [])].join(" ")
  );
  if (!cat || products.length === 0) return [];
  const matched = products.filter((p) => {
    const pcat = detectCategory(
      [(p.hashtags ?? []).join(" "), p.title].join(" ")
    );
    return pcat === cat;
  });
  return matched.slice(0, limit);
}
