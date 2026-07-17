/* eslint-disable @next/next/no-img-element */
import type { Trend } from "@/lib/types";
import AffiliateLink from "./AffiliateLink";

// Ubin cadangan saat gambar produk belum ada: emoji + gradien per kategori,
// supaya kartu tetap terlihat rapi (bukan kotak abu-abu kosong).
const CAT_TILE: Record<string, { emoji: string; from: string; to: string }> = {
  beauty: { emoji: "💄", from: "#FF7AB6", to: "#E6007A" },
  fashion: { emoji: "👗", from: "#8B3DD6", to: "#5B21B6" },
  gadget: { emoji: "🎮", from: "#38BDF8", to: "#2563EB" },
  food: { emoji: "🍜", from: "#FBBF24", to: "#EA580C" },
  home: { emoji: "🏠", from: "#34D399", to: "#059669" },
  health: { emoji: "🩺", from: "#2DD4BF", to: "#0D9488" },
  mom_baby: { emoji: "🍼", from: "#FDA4AF", to: "#E11D48" }
};

function tileFor(trend: Trend) {
  const key = (trend.hashtags?.[0] || "").toLowerCase();
  return CAT_TILE[key] ?? { emoji: "🛍️", from: "#FE5C8D", to: "#FE2C55" };
}

/**
 * Produk afiliasi TikTok Shop yang relevan dengan tren (dicocokkan kategori).
 * Muncul di halaman detail non-produk → peluang belanja yang kontekstual.
 */
export default function RelatedProducts({ products }: { products: Trend[] }) {
  if (!products || products.length === 0) return null;
  return (
    <section className="my-5 rounded-2xl border border-shopee/25 bg-shopee/5 p-5 dark:border-shopee/30 dark:bg-shopee/10">
      <h2 className="flex items-center gap-2 text-base font-bold text-ink dark:text-white">
        <span aria-hidden>🛍️</span> Produk terkait di TikTok Shop
      </h2>
      <div className="mt-3 grid gap-3 sm:grid-cols-3">
        {products.map((p) => (
          <AffiliateLink
            key={p.id}
            href={p.affiliateUrl ?? p.url}
            name={p.title}
            id={p.id}
            category={p.hashtags?.[0]}
            className="group flex flex-col overflow-hidden rounded-xl border border-gray-200 bg-white transition hover:-translate-y-0.5 hover:shadow-md dark:border-white/10 dark:bg-night-card"
          >
            <div className="aspect-square w-full overflow-hidden bg-gray-100 dark:bg-night-soft">
              {p.thumbnail ? (
                <img
                  src={p.thumbnail}
                  alt={p.title}
                  loading="lazy"
                  className="h-full w-full object-cover"
                />
              ) : (
                (() => {
                  const t = tileFor(p);
                  return (
                    <div
                      className="flex h-full w-full flex-col items-center justify-center gap-1 p-2 text-center"
                      style={{
                        backgroundImage: `linear-gradient(135deg, ${t.from}, ${t.to})`
                      }}
                    >
                      <span className="text-2xl drop-shadow-sm" aria-hidden>
                        {t.emoji}
                      </span>
                      <span className="line-clamp-2 text-[10px] font-semibold leading-tight text-white/95">
                        {p.title}
                      </span>
                    </div>
                  );
                })()
              )}
            </div>
            <div className="flex flex-1 flex-col p-2.5">
              <p className="line-clamp-2 text-xs font-medium text-ink dark:text-gray-100">
                {p.title}
              </p>
              {p.price && (
                <p className="mt-1 text-sm font-bold text-shopee">{p.price}</p>
              )}
              <span className="mt-2 inline-flex items-center justify-center rounded-full bg-shopee px-2 py-1 text-[11px] font-semibold text-white group-hover:opacity-90">
                Beli di TikTok Shop
              </span>
            </div>
          </AffiliateLink>
        ))}
      </div>
      <p className="mt-3 text-[11px] text-gray-400">
        Tautan afiliasi. Harga dapat berubah sewaktu-waktu.
      </p>
    </section>
  );
}
