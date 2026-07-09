import { getHomepageTrends } from "@/lib/db";
import { PLATFORM_ORDER } from "@/lib/platforms";
import PlatformSection from "@/components/PlatformSection";
import AdSlot from "@/components/AdSlot";
import type { Platform, Trend } from "@/lib/types";

// ISR: halaman diregenerasi berkala agar tren selalu segar.
export const revalidate = 1800; // 30 menit

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
      <section className="mb-4 rounded-3xl bg-gradient-to-br from-brand to-orange-500 px-6 py-10 text-white sm:px-10 sm:py-14">
        <h1 className="max-w-2xl text-2xl font-extrabold leading-tight sm:text-4xl">
          Apa yang lagi tren di Indonesia hari ini?
        </h1>
        <p className="mt-3 max-w-xl text-sm text-white/90 sm:text-base">
          Kami kumpulkan tren real-time dari Google, YouTube, TikTok, Instagram,
          Shopee, dan X — lengkap dengan ringkasan AI kenapa sesuatu sedang
          viral. Satu halaman, semua yang lagi ramai.
        </p>
        <div className="mt-5 flex flex-wrap gap-2">
          {PLATFORM_ORDER.map((key) => (
            <a
              key={key}
              href={`#${key}`}
              className="rounded-full bg-white/15 px-3 py-1.5 text-sm font-medium backdrop-blur transition hover:bg-white/25"
            >
              {key.charAt(0).toUpperCase() + key.slice(1)}
            </a>
          ))}
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
