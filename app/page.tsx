import { getHomepageTrends } from "@/lib/db";
import { PLATFORM_ORDER, PLATFORMS } from "@/lib/platforms";
import PlatformSection from "@/components/PlatformSection";
import AdSlot from "@/components/AdSlot";
import type { Platform, Trend } from "@/lib/types";

// ISR: halaman diregenerasi berkala agar tren selalu segar.
export const revalidate = 300; // 5 menit

// Sisipkan iklan setelah platform ke-2 dan ke-4.
const AD_AFTER = new Set<number>([1, 3]);

export default async function HomePage() {
  const trends = await getHomepageTrends(4);
  const byPlatform = new Map<Platform, Trend[]>();
  for (const t of trends) {
    const list = byPlatform.get(t.platform) ?? [];
    list.push(t);
    byPlatform.set(t.platform, list);
  }

  return (
    <>
      {/* Hero */}
      <section className="relative mb-6 overflow-hidden rounded-[28px] bg-gradient-to-br from-brand via-accent to-accent-grape px-6 py-11 text-white shadow-xl shadow-brand/20 sm:px-10 sm:py-16">
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
            Tren real-time dari Google, YouTube, TikTok, Instagram, Netflix,
            Shopee, dan X — plus ringkasan AI kenapa sesuatu sedang viral. Satu
            halaman, semua yang lagi ramai.
          </p>
          <div className="mt-6 flex flex-wrap gap-2">
            {PLATFORM_ORDER.map((key) => (
              <a
                key={key}
                href={`#${key}`}
                className="inline-flex items-center gap-1.5 rounded-full bg-white/15 px-3.5 py-1.5 text-sm font-semibold ring-1 ring-white/20 backdrop-blur transition hover:-translate-y-0.5 hover:bg-white/25"
              >
                <span aria-hidden>{PLATFORMS[key].icon}</span>
                {PLATFORMS[key].name.split(" ")[0]}
              </a>
            ))}
          </div>
        </div>
      </section>

      {PLATFORM_ORDER.map((platform, i) => (
        <div key={platform}>
          <PlatformSection
            platform={platform}
            trends={byPlatform.get(platform) ?? []}
          />
          {AD_AFTER.has(i) && <AdSlot slot={`home-${i}`} />}
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
