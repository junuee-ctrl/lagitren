import type { Metadata } from "next";
import Link from "next/link";
import { getArticles } from "@/lib/db";
import { KATEGORI_COLOR, KATEGORI_LABEL, formatTanggal } from "@/lib/artikel";
import { SITE_URL } from "@/lib/site";
import AdSlot from "@/components/AdSlot";
import { AD_SLOTS } from "@/lib/adsense";

export const revalidate = 1800;

export const metadata: Metadata = {
  title: "Artikel & Analisis Tren",
  description:
    "Analisis tren Indonesia dari arsip data Lagi Tren sendiri: rekap mingguan, kenapa sesuatu viral, dan panduan memahami tren lintas platform.",
  alternates: { canonical: "/artikel" },
  openGraph: {
    images: [{ url: "/og/artikel", width: 1200, height: 630 }]
  }
};

export default async function ArtikelPage() {
  const articles = await getArticles(50);

  return (
    <div className="mx-auto max-w-3xl py-4">
      <h1 className="text-2xl font-extrabold text-ink dark:text-white sm:text-3xl">
        Artikel & Analisis
      </h1>
      <p className="mt-2 text-gray-500 dark:text-gray-400">
        Ditulis dari arsip data tren kami sendiri — rekap mingguan, analisis
        kenapa sesuatu viral, dan panduan memahami tren. Cara kerjanya di
        halaman{" "}
        <Link href="/metodologi" className="text-brand hover:underline">
          Metodologi
        </Link>
        .
      </p>

      <AdSlot slot="artikel-top" adSlot={AD_SLOTS.atas} />

      {articles.length === 0 ? (
        <p className="mt-10 text-gray-500 dark:text-gray-400">
          Artikel pertama sedang disiapkan — kembali lagi sebentar lagi.
        </p>
      ) : (
        <ul className="mt-8 space-y-5">
          {articles.map((a) => (
            <li key={a.slug}>
              <Link
                href={`/artikel/${a.slug}`}
                className="block rounded-2xl border border-gray-200 bg-white p-5 transition hover:border-brand/40 hover:shadow-sm dark:border-white/10 dark:bg-night-card"
              >
                <div className="flex items-center gap-3 text-xs">
                  <span
                    className="rounded-full px-2.5 py-0.5 font-semibold text-white"
                    style={{ backgroundColor: KATEGORI_COLOR[a.category] }}
                  >
                    {KATEGORI_LABEL[a.category]}
                  </span>
                  <span className="text-gray-400 dark:text-gray-500">
                    {formatTanggal(a.publishedAt)}
                  </span>
                </div>
                <h2 className="mt-2 text-lg font-bold leading-snug text-ink dark:text-white">
                  {a.title}
                </h2>
                <p className="mt-1.5 line-clamp-2 text-sm text-gray-600 dark:text-gray-300">
                  {a.lead}
                </p>
              </Link>
            </li>
          ))}
        </ul>
      )}

      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "ItemList",
            itemListElement: articles.slice(0, 20).map((a, i) => ({
              "@type": "ListItem",
              position: i + 1,
              url: `${SITE_URL}/artikel/${a.slug}`,
              name: a.title
            }))
          })
        }}
      />
    </div>
  );
}
