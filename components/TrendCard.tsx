/* eslint-disable @next/next/no-img-element */
import type { Trend } from "@/lib/types";
import { PLATFORMS } from "@/lib/platforms";
import { formatMetric } from "@/lib/format";
import AISummary from "./AISummary";
import AffiliateBox from "./AffiliateBox";

const PLATFORM_LINK_LABEL: Record<string, string> = {
  google: "Lihat di Google",
  youtube: "Tonton di YouTube",
  tiktok: "Lihat di TikTok",
  instagram: "Lihat di Instagram",
  shopee: "Cek di Shopee",
  twitter: "Lihat di X"
};

export default function TrendCard({ trend }: { trend: Trend }) {
  const meta = PLATFORMS[trend.platform];
  const linkLabel = PLATFORM_LINK_LABEL[trend.platform] ?? "Lihat sumber";
  const hasThumb = Boolean(trend.thumbnail);
  const isProduct = trend.platform === "shopee";

  return (
    <article
      className="card flex flex-col overflow-hidden"
      style={{ borderTopColor: meta.color, borderTopWidth: 3 }}
    >
      {hasThumb && (
        <a
          href={trend.url}
          target="_blank"
          rel="noopener noreferrer"
          className="relative block aspect-video overflow-hidden bg-gray-100"
        >
          <img
            src={trend.thumbnail}
            alt={trend.title}
            loading="lazy"
            className="h-full w-full object-cover transition duration-300 hover:scale-105"
          />
        </a>
      )}

      <div className="flex flex-1 flex-col p-4">
        <div className="flex items-center gap-2">
          <span
            className="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-semibold text-white"
            style={{ backgroundColor: meta.color }}
          >
            <span aria-hidden>{meta.icon}</span>
            {meta.name}
          </span>
          <span className="ml-auto text-xs font-medium text-gray-400">
            #{trend.rank}
          </span>
        </div>

        <h3 className="mt-2 text-base font-bold leading-snug text-ink">
          <a
            href={trend.url}
            target="_blank"
            rel="noopener noreferrer"
            className="transition hover:text-brand"
          >
            {trend.title}
          </a>
        </h3>

        <div className="mt-1 flex flex-wrap items-center gap-x-2 gap-y-0.5 text-sm text-gray-500">
          {trend.subtitle && (
            <span className="font-semibold text-gray-700">
              {trend.subtitle}
            </span>
          )}
          {trend.metric != null && !trend.subtitle && (
            <span>
              {formatMetric(trend.metric)} {trend.metricLabel}
            </span>
          )}
          {trend.source && <span>· {trend.source}</span>}
        </div>

        <AISummary text={trend.aiSummary} />

        {isProduct && trend.affiliateUrl ? (
          <AffiliateBox trend={trend} />
        ) : (
          <a
            href={trend.url}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-3 inline-flex w-fit items-center gap-1 text-sm font-semibold text-brand transition hover:gap-2"
          >
            🔗 {linkLabel} →
          </a>
        )}

        {/* Kotak afiliasi tambahan untuk tren non-produk yang punya produk terkait */}
        {!isProduct && trend.affiliateUrl && <AffiliateBox trend={trend} />}

        {trend.hashtags && trend.hashtags.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-1.5">
            {trend.hashtags.map((h) => (
              <span key={h} className="chip">
                #{h}
              </span>
            ))}
          </div>
        )}
      </div>
    </article>
  );
}
