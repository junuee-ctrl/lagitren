/* eslint-disable @next/next/no-img-element */
import Link from "next/link";
import type { Trend } from "@/lib/types";
import { PLATFORMS, platformHref } from "@/lib/platforms";
import { slugFromId } from "@/lib/embed";
import { formatMetric } from "@/lib/format";
import PlatformIcon from "./PlatformIcon";

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
  const href = `${platformHref(trend.platform)}/${slugFromId(trend.id)}`;
  const metric =
    trend.subtitle ||
    (trend.metric != null
      ? `${formatMetric(trend.metric)} ${trend.metricLabel ?? ""}`.trim()
      : "");

  return (
    <Link
      href={href}
      className="group flex min-w-0 items-center gap-3 rounded-2xl border border-gray-200 bg-white p-3 transition-all duration-200 hover:-translate-y-0.5 hover:border-brand/40 hover:shadow-md hover:shadow-brand/5 dark:border-white/10 dark:bg-night-card dark:hover:border-brand/40"
    >
      <span
        className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl text-xs font-extrabold text-white shadow-sm"
        style={{
          backgroundColor: meta.color,
          boxShadow: `0 3px 10px ${meta.color}40`
        }}
        aria-hidden
      >
        {trend.rank}
      </span>

      {trend.thumbnail && (
        <img
          src={trend.thumbnail}
          alt=""
          loading="lazy"
          className="h-12 w-16 shrink-0 rounded-lg object-cover ring-1 ring-black/5 dark:ring-white/10"
        />
      )}

      <div className="min-w-0 flex-1">
        <h3 className="truncate text-sm font-semibold text-ink transition-colors group-hover:text-brand dark:text-gray-100">
          {trend.title}
        </h3>
        <p className="mt-0.5 truncate text-xs text-gray-500 dark:text-gray-400">
          {showPlatform && (
            <span
              className="mr-1 inline-flex items-center gap-1 align-middle font-medium"
              style={{ color: meta.color }}
            >
              <PlatformIcon platform={trend.platform} className="h-3 w-3" />
              {meta.name} ·
            </span>
          )}
          {metric}
          {trend.source ? ` · ${trend.source}` : ""}
        </p>
      </div>

      <span
        className="shrink-0 text-gray-300 transition group-hover:translate-x-0.5 group-hover:text-brand dark:text-gray-600"
        aria-hidden
      >
        →
      </span>
    </Link>
  );
}
