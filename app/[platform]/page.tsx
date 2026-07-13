import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { getTrendsByPlatform } from "@/lib/db";
import { PLATFORMS, PLATFORM_ORDER, getPlatform } from "@/lib/platforms";
import PlatformSection from "@/components/PlatformSection";
import NetflixSplit from "@/components/NetflixSplit";
import PlatformIcon from "@/components/PlatformIcon";
import AdSlot from "@/components/AdSlot";
import type { Platform } from "@/lib/types";

export const revalidate = 300; // 5 menit

export function generateStaticParams() {
  return PLATFORM_ORDER.map((platform) => ({ platform }));
}

const DATE_ID = new Intl.DateTimeFormat("id-ID", {
  day: "numeric",
  month: "long",
  year: "numeric",
  timeZone: "Asia/Jakarta"
});

export function generateMetadata({
  params
}: {
  params: { platform: string };
}): Metadata {
  const meta = getPlatform(params.platform);
  if (!meta) return {};
  const today = DATE_ID.format(new Date());
  const title = `${meta.name} Indonesia Hari Ini — ${today}`;
  return {
    title,
    description: meta.description,
    alternates: { canonical: `/${meta.key}` },
    openGraph: { title: `${title} · Lagi Tren`, description: meta.description }
  };
}

export default async function PlatformPage({
  params
}: {
  params: { platform: string };
}) {
  const meta = getPlatform(params.platform);
  if (!meta) notFound();

  const platform = meta.key as Platform;
  const trends = await getTrendsByPlatform(platform, 20);
  const today = DATE_ID.format(new Date());

  return (
    <>
      <nav className="mb-4 text-sm text-gray-400">
        <a href="/" className="hover:text-brand">
          Beranda
        </a>{" "}
        / <span className="text-gray-600">{meta.name}</span>
      </nav>

      <header
        className="mb-6 rounded-2xl p-6 text-white"
        style={{ backgroundColor: meta.color }}
      >
        <h1 className="flex items-center gap-2.5 text-2xl font-extrabold sm:text-3xl">
          <span className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-white/20 backdrop-blur">
            <PlatformIcon platform={platform} className="h-5 w-5" mono />
          </span>
          {meta.name} Indonesia
        </h1>
        <p className="mt-1 text-sm text-white/90">Hari ini · {today}</p>
        <p className="mt-3 max-w-2xl text-sm text-white/90">
          {meta.description}
        </p>
      </header>

      <AdSlot slot={`${platform}-top`} />

      {trends.length > 0 ? (
        platform === "netflix" ? (
          <NetflixSplit trends={trends} />
        ) : (
          <PlatformSection platform={platform} trends={trends} showAll />
        )
      ) : (
        <div className="rounded-2xl border border-dashed border-gray-300 bg-white p-8 text-center">
          <p className="text-3xl" aria-hidden>
            ⏳
          </p>
          <p className="mt-2 font-semibold text-ink">
            Data {meta.name} sedang dikumpulkan
          </p>
          <p className="mt-1 text-sm text-gray-500">
            Tren untuk platform ini akan segera muncul di sini. Coba lagi
            beberapa saat lagi.
          </p>
        </div>
      )}

      {/* Navigasi ke platform lain */}
      <section className="mt-10 border-t border-gray-200 pt-6">
        <h2 className="mb-3 text-sm font-semibold text-gray-500">
          Platform lainnya
        </h2>
        <div className="flex flex-wrap gap-2">
          {PLATFORM_ORDER.filter((k) => k !== platform).map((k) => (
            <a
              key={k}
              href={`/${k}`}
              className="inline-flex items-center gap-1.5 rounded-full border border-gray-200 bg-white px-3 py-1.5 text-sm font-medium text-gray-600 transition hover:border-brand hover:text-brand dark:border-white/10 dark:bg-night-card dark:text-gray-300 dark:hover:border-brand"
            >
              <PlatformIcon platform={k} className="h-4 w-4" />
              {PLATFORMS[k].name}
            </a>
          ))}
        </div>
      </section>

      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            name: `${meta.name} Indonesia Hari Ini`,
            inLanguage: "id-ID",
            about: meta.name
          })
        }}
      />
    </>
  );
}
