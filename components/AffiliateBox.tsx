import type { Trend } from "@/lib/types";

/**
 * Kotak afiliasi untuk produk (Shopee/Tokopedia) atau produk terkait
 * dari tren lain. Selalu diberi label agar transparan (syarat AdSense &
 * etika afiliasi).
 */
export default function AffiliateBox({ trend }: { trend: Trend }) {
  const href = trend.affiliateUrl ?? trend.url;
  return (
    <div className="mt-3 rounded-xl border border-shopee/30 bg-shopee/5 p-3 dark:border-shopee/40 dark:bg-shopee/10">
      <p className="text-xs font-semibold text-shopee">🛒 Produk terkait</p>
      {trend.price && (
        <p className="mt-1 text-sm font-semibold text-ink dark:text-white">
          {trend.price}
        </p>
      )}
      <a
        href={href}
        target="_blank"
        rel="nofollow sponsored noopener noreferrer"
        className="mt-2 inline-flex items-center gap-1 rounded-full bg-shopee px-3 py-1.5 text-sm font-semibold text-white transition hover:opacity-90"
      >
        Cek Harga di Shopee →
      </a>
      <p className="mt-2 text-[11px] leading-snug text-gray-400">
        Tautan afiliasi. Harga dapat berubah sewaktu-waktu.
      </p>
    </div>
  );
}
