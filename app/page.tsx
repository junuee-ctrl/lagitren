import Link from "next/link";
import { getArticles, getHomepageTrends } from "@/lib/db";
import { PLATFORM_ORDER, PLATFORMS } from "@/lib/platforms";
import { KATEGORI_LABEL, formatTanggal } from "@/lib/artikel";
import PlatformSection from "@/components/PlatformSection";
import PlatformIcon from "@/components/PlatformIcon";
import AdSlot from "@/components/AdSlot";
import { AD_SLOTS } from "@/lib/adsense";
import type { Platform, Trend } from "@/lib/types";

// ISR: halaman diregenerasi berkala agar tren selalu segar.
export const dynamic = "force-dynamic";

// Sisipkan iklan setelah platform ke-2 dan ke-4.
const AD_AFTER = new Set<number>([1, 3]);

export default async function HomePage() {
  const [trends, artikel] = await Promise.all([
    getHomepageTrends(4),
    getArticles(3)
  ]);
  const byPlatform = new Map<Platform, Trend[]>();
  for (const t of trends) {
    const list = byPlatform.get(t.platform) ?? [];
    list.push(t);
    byPlatform.set(t.platform, list);
  }

  return (
    <>
      {/* Hero */}
      <section className="relative mb-6 overflow-hidden rounded-[28px] bg-gradient-to-br from-brand via-accent-grape to-accent px-6 py-11 text-white shadow-xl shadow-brand/20 sm:px-10 sm:py-16">
        {/* Blob dekoratif */}
        <div
          className="pointer-events-none absolute -right-16 -top-16 h-64 w-64 rounded-full bg-white/20 blur-3xl"
          aria-hidden
        />
        <div
          className="pointer-events-none absolute -bottom-24 left-1/3 h-64 w-64 animate-float-slow rounded-full bg-accent-grape/40 blur-3xl"
          aria-hidden
        />

        <div className="relative">
          <span className="inline-flex items-center gap-1.5 rounded-full bg-white/20 px-3 py-1 text-xs font-semibold backdrop-blur">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-white opacity-75" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-white" />
            </span>
            REAL-TIME · diperbarui otomatis
          </span>

          <h1 className="mt-4 max-w-2xl text-3xl font-extrabold leading-[1.1] tracking-tight sm:text-5xl">
            Apa yang lagi{" "}
            <span className="whitespace-nowrap">tren di Indonesia</span> hari
            ini? 🔥
          </h1>
          <p className="mt-4 max-w-xl text-sm text-white/90 sm:text-base">
            Tren real-time dari Google, YouTube, Instagram, TikTok, Netflix,
            dan X — plus produk viral TikTok Shop dan ringkasan AI kenapa
            sesuatu sedang ramai. Satu halaman, semua yang lagi ramai.
          </p>
          <div className="mt-6 flex flex-wrap gap-2">
            {PLATFORM_ORDER.map((key) => (
              <a
                key={key}
                href={`#${key}`}
                className="inline-flex items-center gap-1.5 rounded-full bg-white/15 px-3.5 py-1.5 text-sm font-semibold ring-1 ring-white/20 backdrop-blur transition hover:-translate-y-0.5 hover:bg-white/25"
              >
                <PlatformIcon platform={key} className="h-4 w-4" mono />
                {PLATFORMS[key].name.split(" ")[0]}
              </a>
            ))}
          </div>
        </div>
      </section>

      {/* Artikel & analisis terbaru */}
      {artikel.length > 0 && (
        <section className="mb-8">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="text-xl font-extrabold text-ink dark:text-white">
              ✍️ Artikel & Analisis
            </h2>
            <Link
              href="/artikel"
              className="text-sm font-semibold text-brand hover:underline"
            >
              Lihat semua →
            </Link>
          </div>
          <div className="grid gap-3 sm:grid-cols-3">
            {artikel.map((a) => (
              <Link
                key={a.slug}
                href={`/artikel/${a.slug}`}
                className="block rounded-2xl border border-gray-200 bg-white p-4 transition hover:border-brand/40 hover:shadow-sm dark:border-white/10 dark:bg-night-card"
              >
                <p className="text-xs font-semibold text-brand">
                  {KATEGORI_LABEL[a.category]}
                </p>
                <p className="mt-1 line-clamp-2 font-bold leading-snug text-ink dark:text-white">
                  {a.title}
                </p>
                <p className="mt-1 text-xs text-gray-400 dark:text-gray-500">
                  {formatTanggal(a.publishedAt)}
                </p>
              </Link>
            ))}
          </div>
        </section>
      )}

      {PLATFORM_ORDER.map((platform, i) => (
        <div key={platform}>
          <PlatformSection
            platform={platform}
            trends={byPlatform.get(platform) ?? []}
          />
          {AD_AFTER.has(i) && (
            <AdSlot slot={`home-${i}`} adSlot={AD_SLOTS.beranda} />
          )}
        </div>
      ))}

      {/* Structured data */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "WebSite",
            name: "Lagi Tren",
            url: process.env.NEXT_PUBLIC_SITE_URL ?? "https://lagitren.id",
            description:
              "Agregator tren real-time Indonesia dari berbagai platform.",
            inLanguage: "id-ID"
          })
        }}
      />
    </>
  );
}
