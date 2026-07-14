/* eslint-disable @next/next/no-img-element */
import type { Trend } from "@/lib/types";

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
          <a
            key={p.id}
            href={p.affiliateUrl ?? p.url}
            target="_blank"
            rel="nofollow sponsored noopener noreferrer"
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
                <div className="flex h-full w-full items-center justify-center p-2 text-center text-[11px] font-medium text-gray-400">
                  {p.title}
                </div>
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
          </a>
        ))}
      </div>
      <p className="mt-3 text-[11px] text-gray-400">
        Tautan afiliasi. Harga dapat berubah sewaktu-waktu.
      </p>
    </section>
  );
}
