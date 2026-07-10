import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { getTrendById, getRelatedTrends } from "@/lib/db";
import { getPlatform } from "@/lib/platforms";
import { SOURCE_LABEL, canEmbed } from "@/lib/embed";
import type { Platform } from "@/lib/types";
import TrendMedia from "@/components/TrendMedia";
import TrendListItem from "@/components/TrendListItem";
import AdSlot from "@/components/AdSlot";
import AffiliateBox from "@/components/AffiliateBox";
import SearchVolumeChart from "@/components/SearchVolumeChart";
import GoogleTrendsWidget from "@/components/GoogleTrendsWidget";

export const revalidate = 300;

export async function generateMetadata({
  params
}: {
  params: { platform: string; slug: string };
}): Promise<Metadata> {
  const meta = getPlatform(params.platform);
  if (!meta) return {};
  const trend = await getTrendById(meta.key as Platform, params.slug);
  if (!trend) return {};
  const desc =
    trend.aiSummary ??
    `${trend.title} sedang tren di ${meta.name} Indonesia. Cari tahu kenapa.`;
  return {
    title: `${trend.title} — kenapa lagi tren?`,
    description: desc.slice(0, 160),
    alternates: { canonical: `/${meta.key}/${params.slug}` },
    openGraph: {
      title: `${trend.title} · ${meta.name}`,
      description: desc.slice(0, 160),
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
        / <span className="text-gray-600">{trend.title}</span>
      </nav>

      {/* Judul */}
      <header className="mb-4">
        <span
          className="inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-semibold text-white"
          style={{ backgroundColor: meta.color }}
        >
          <span aria-hidden>{meta.icon}</span> {meta.name}
        </span>
        <h1 className="mt-2 text-2xl font-extrabold leading-tight text-ink sm:text-3xl">
          {trend.title}
        </h1>
        <p className="mt-1 text-sm text-gray-500">
          {trend.subtitle && (
            <span className="font-semibold text-gray-700">
              {trend.subtitle}
            </span>
          )}
          {trend.source ? ` · ${trend.source}` : ""}
        </p>
      </header>

      {/* Grafik minat pencarian (khusus Google Trends) */}
      {platform === "google" && (
        <section className="mb-5 rounded-2xl border border-gray-200 bg-white p-4 sm:p-5">
          <h2 className="mb-2 text-sm font-semibold text-gray-500">
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
      )}

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
        <section className="my-5 rounded-2xl border border-brand/20 bg-brand/5 p-5">
          <h2 className="flex items-center gap-2 text-base font-bold text-brand">
            <span aria-hidden>💡</span> Kenapa ini lagi tren?
          </h2>
          <p className="mt-2 text-[15px] leading-relaxed text-gray-800">
            {trend.aiSummary}
          </p>
        </section>
      )}

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
      <div className="my-5 border-t border-gray-100 pt-4">
        <a
          href={trend.url}
          target="_blank"
          rel="nofollow noopener noreferrer"
          className="text-sm text-gray-400 hover:text-brand"
        >
          {SOURCE_LABEL[platform]} ↗
        </a>
      </div>

      {/* Iklan in-content kedua */}
      <AdSlot slot={`detail-${platform}-bottom`} />

      {/* Trend terkait — navigasi internal (menambah page view) */}
      {related.length > 0 && (
        <section className="mt-8">
          <h2 className="mb-3 flex items-center justify-between text-lg font-extrabold text-ink">
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
