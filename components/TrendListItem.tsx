/* eslint-disable @next/next/no-img-element */
import Link from "next/link";
import type { Trend } from "@/lib/types";
import { PLATFORMS } from "@/lib/platforms";
import { slugFromId } from "@/lib/embed";
import { formatMetric } from "@/lib/format";

/**
 * Baris list ringkas untuk homepage & halaman platform.
 * SELALU menautkan ke halaman detail INTERNAL (/[platform]/[slug]),
 * bukan ke platform sumber — supaya pengguna tetap di situs kita.
 */
export default function TrendListItem({
  trend,
  showPlatform = false
}: {
  trend: Trend;
  showPlatform?: boolean;
}) {
  const meta = PLATFORMS[trend.platform];
  const href = `/${trend.platform}/${slugFromId(trend.id)}`;
  const metric =
    trend.subtitle ||
    (trend.metric != null
      ? `${formatMetric(trend.metric)} ${trend.metricLabel ?? ""}`.trim()
      : "");

  return (
    <Link
      href={href}
      className="group flex min-w-0 items-center gap-3 rounded-xl border border-gray-200 bg-white p-3 transition hover:border-brand/50 hover:shadow-sm"
    >
      <span
        className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg text-xs font-bold text-white"
        style={{ backgroundColor: meta.color }}
        aria-hidden
      >
        {trend.rank}
      </span>

      {trend.thumbnail && (
        <img
          src={trend.thumbnail}
          alt=""
          loading="lazy"
          className="h-12 w-16 shrink-0 rounded-md object-cover"
        />
      )}

      <div className="min-w-0 flex-1">
        <h3 className="truncate text-sm font-semibold text-ink group-hover:text-brand">
          {trend.title}
        </h3>
        <p className="mt-0.5 truncate text-xs text-gray-500">
          {showPlatform && (
            <span className="mr-1" style={{ color: meta.color }}>
              {meta.icon} {meta.name} ·
            </span>
          )}
          {metric}
          {trend.source ? ` · ${trend.source}` : ""}
        </p>
      </div>

      <span
        className="shrink-0 text-gray-300 transition group-hover:translate-x-0.5 group-hover:text-brand"
        aria-hidden
      >
        →
      </span>
    </Link>
  );
}
