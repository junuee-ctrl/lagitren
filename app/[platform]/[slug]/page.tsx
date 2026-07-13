import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { getTrendById, getRelatedTrends } from "@/lib/db";
import { getPlatform } from "@/lib/platforms";
import { SOURCE_LABEL, canEmbed } from "@/lib/embed";
import { formatDateID } from "@/lib/format";
import type { Platform } from "@/lib/types";
import TrendMedia from "@/components/TrendMedia";
import TrendListItem from "@/components/TrendListItem";
import AdSlot from "@/components/AdSlot";
import AffiliateBox from "@/components/AffiliateBox";
import SearchVolumeChart from "@/components/SearchVolumeChart";
import GoogleTrendsWidget from "@/components/GoogleTrendsWidget";
import TrendContext from "@/components/TrendContext";
import PlatformIcon from "@/components/PlatformIcon";

export const revalidate = 300;

// Frasa sesuai cara orang mencari, per platform.
const INTENT: Record<Platform, string> = {
  google: "kenapa banyak dicari?",
  youtube: "kenapa viral?",
  tiktok: "kenapa viral?",
  instagram: "kenapa viral?",
  shopee: "kenapa banyak dicari?",
  twitter: "kenapa jadi perbincangan?",
  netflix: "kenapa ramai ditonton?"
};

export async function generateMetadata({
  params
}: {
  params: { platform: string; slug: string };
}): Promise<Metadata> {
  const meta = getPlatform(params.platform);
  if (!meta) return {};
  const trend = await getTrendById(meta.key as Platform, params.slug);
  if (!trend) return {};

  const intent = INTENT[meta.key as Platform] ?? "kenapa lagi tren?";
  const title = `${trend.title} — ${intent} | ${meta.name} Indonesia`;
  const desc = (
    trend.aiSummary
      ? `${trend.title}: ${trend.aiSummary}`
      : `Kenapa "${trend.title}" sedang tren di ${meta.name} Indonesia hari ini? Simak ringkasannya di Lagi Tren.`
  ).slice(0, 160);

  return {
    title,
    description: desc,
    alternates: { canonical: `/${meta.key}/${params.slug}` },
    keywords: [
      trend.title,
      `${trend.title} ${meta.name}`,
      `kenapa ${trend.title} viral`,
      `${trend.title} indonesia`,
      ...(trend.hashtags ?? [])
    ],
    openGraph: {
      type: "article",
      title,
      description: desc,
      images: trend.thumbnail ? [{ url: trend.thumbnail }] : undefined
    }
  };
}

export default async function TrendDetailPage({
  params
}: {
  params: { platform: string; slug: string };
}) {
  const meta = getPlatform(params.platform);
  if (!meta) notFound();
  const platform = meta.key as Platform;

  const trend = await getTrendById(platform, params.slug);
  if (!trend) notFound();

  const related = await getRelatedTrends(platform, trend.id, 6);
  const isProduct = platform === "shopee";
  const embeddable = canEmbed(trend);

  return (
    <article className="mx-auto max-w-3xl">
      {/* Breadcrumb */}
      <nav className="mb-4 text-sm text-gray-400">
        <Link href="/" className="hover:text-brand">
          Beranda
        </Link>{" "}
        /{" "}
        <Link href={`/${platform}`} className="hover:text-brand">
          {meta.name}
        </Link>{" "}
        /{" "}
        <span className="text-gray-600 dark:text-gray-300">{trend.title}</span>
      </nav>

      {/* Judul */}
      <header className="mb-4">
        <span
          className="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold text-white shadow-sm"
          style={{ backgroundColor: meta.color }}
        >
          <PlatformIcon platform={platform} className="h-3 w-3" mono />
          {meta.name}
        </span>
        <h1 className="mt-3 text-2xl font-extrabold leading-tight text-ink dark:text-white sm:text-3xl">
          {trend.title}
        </h1>
        <p className="mt-1.5 text-sm text-gray-500 dark:text-gray-400">
          {trend.subtitle && (
            <span className="font-semibold text-gray-700 dark:text-gray-200">
              {trend.subtitle}
            </span>
          )}
          {trend.source ? ` · ${trend.source}` : ""}
        </p>
      </header>

      {/* Banner arsip: jujur bahwa tren ini sudah lewat (jaga kesegaran konten) */}
      {trend.isCurrent === false && (
        <div className="mb-5 flex flex-wrap items-center gap-x-2 gap-y-1 rounded-xl border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800 dark:border-amber-500/30 dark:bg-amber-500/10 dark:text-amber-300">
          <span aria-hidden>🗂️</span>
          <span>
            Tren ini sudah tidak aktif — terakhir tren pada{" "}
            <strong>{formatDateID(trend.collectedAt)}</strong>.
          </span>
          <Link
            href={`/${platform}`}
            className="font-semibold text-brand hover:underline"
          >
            Lihat yang lagi tren →
          </Link>
        </div>
      )}

      {/* Grafik popularitas / minat pencarian */}
      {platform === "google" ? (
        <section className="mb-5 rounded-2xl border border-gray-200 bg-white p-4 dark:border-white/10 dark:bg-night-card sm:p-5">
          <h2 className="mb-2 text-sm font-semibold text-gray-500 dark:text-gray-400">
            📈 Minat pencarian dari waktu ke waktu
          </h2>
          {trend.interest && trend.interest.length > 1 ? (
            <>
              <SearchVolumeChart data={trend.interest} color={meta.color} />
              <p className="mt-1 text-xs text-gray-400">
                Nilai relatif (0–100) berdasarkan data Google Trends.
              </p>
            </>
          ) : (
            <GoogleTrendsWidget keyword={trend.title} />
          )}
        </section>
      ) : platform !== "tiktok" &&
        trend.interest &&
        trend.interest.length > 1 ? (
        // TikTok: grafik populer dilewati — utamakan embed video (di bawah).
        <section className="mb-5 rounded-2xl border border-gray-200 bg-white p-4 dark:border-white/10 dark:bg-night-card sm:p-5">
          <h2 className="mb-2 text-sm font-semibold text-gray-500 dark:text-gray-400">
            📈 Popularitas dari waktu ke waktu
          </h2>
          <SearchVolumeChart data={trend.interest} color={meta.color} />
          <p className="mt-1 text-xs text-gray-400">Nilai relatif (0–100).</p>
        </section>
      ) : null}

      {/* Media utama — diputar/ditampilkan DI SITUS kita */}
      {(embeddable || trend.thumbnail) && (
        <div className="mb-5">
          <TrendMedia trend={trend} />
        </div>
      )}

      {/* Iklan in-content (di atas lipatan konten) */}
      <AdSlot slot={`detail-${platform}-top`} />

      {/* Penjelasan "kenapa tren" — bintang utama, khususnya Google */}
      {trend.aiSummary && (
        <section className="my-5 rounded-2xl border border-brand/25 bg-gradient-to-br from-brand/10 to-accent/10 p-5 dark:border-brand/30 dark:from-brand/15 dark:to-accent/10">
          <h2 className="flex items-center gap-2 text-base font-bold text-brand dark:text-brand-light">
            <span aria-hidden>💡</span> Kenapa ini lagi tren?
          </h2>
          <p className="mt-2 text-[15px] leading-relaxed text-gray-800 dark:text-gray-200">
            {trend.aiSummary}
          </p>
        </section>
      )}

      {/* Konteks kaya: berita terkait (Google) / komentar terbaik (YouTube) */}
      <TrendContext trend={trend} />

      {/* Produk / afiliasi (sumber pendapatan) */}
      {trend.affiliateUrl && (
        <div className="my-5">
          <AffiliateBox trend={trend} />
        </div>
      )}

      {/* Hashtag */}
      {trend.hashtags && trend.hashtags.length > 0 && (
        <div className="my-4 flex flex-wrap gap-1.5">
          {trend.hashtags.map((h) => (
            <span key={h} className="chip">
              #{h}
            </span>
          ))}
        </div>
      )}

      {/* Tautan sumber — sekunder, dikecilkan agar tidak menarik keluar */}
      <div className="my-5 border-t border-gray-100 pt-4 dark:border-white/10">
        <a
          href={trend.url}
          target="_blank"
          rel="nofollow noopener noreferrer"
          className="text-sm text-gray-400 hover:text-brand dark:text-gray-500"
        >
          {SOURCE_LABEL[platform]} ↗
        </a>
      </div>

      {/* Iklan in-content kedua */}
      <AdSlot slot={`detail-${platform}-bottom`} />

      {/* Trend terkait — navigasi internal (menambah page view) */}
      {related.length > 0 && (
        <section className="mt-8">
          <h2 className="mb-3 flex items-center justify-between text-lg font-extrabold text-ink dark:text-white">
            <span>Lagi tren di {meta.name}</span>
            <Link
              href={`/${platform}`}
              className="text-sm font-semibold text-brand hover:underline"
            >
              Lihat semua →
            </Link>
          </h2>
          <div className="grid gap-2 sm:grid-cols-2">
            {related.map((t) => (
              <TrendListItem key={t.id} trend={t} />
            ))}
          </div>
        </section>
      )}

      {/* Structured data */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "Article",
            headline: trend.title,
            description: trend.aiSummary ?? trend.title,
            inLanguage: "id-ID",
            image: trend.thumbnail ? [trend.thumbnail] : undefined,
            about: meta.name
          })
        }}
      />
    </article>
  );
}
