/* eslint-disable @next/next/no-img-element */
import Link from "next/link";
import type { Trend } from "@/lib/types";
import { PLATFORMS, platformHref } from "@/lib/platforms";
import { slugFromId } from "@/lib/embed";
import PlatformIcon from "./PlatformIcon";

/**
 * Kartu tren ber-thumbnail (P2-2) — menaikkan klik "tren terkait"
 * dibanding daftar teks. Tanpa gambar → ubin gradien warna platform.
 */
export default function TrendCardMini({
  trend,
  showPlatform = false
}: {
  trend: Trend;
  showPlatform?: boolean;
}) {
  const meta = PLATFORMS[trend.platform];
  const href = `${platformHref(trend.platform)}/${slugFromId(trend.id)}`;

  return (
    <Link
      href={href}
      className="group flex flex-col overflow-hidden rounded-xl border border-gray-200 bg-white transition hover:-translate-y-0.5 hover:border-brand/40 hover:shadow-md dark:border-white/10 dark:bg-night-card"
    >
      <div className="relative aspect-[16/9] w-full overflow-hidden bg-gray-100 dark:bg-night-soft">
        {trend.thumbnail ? (
          <img
            src={trend.thumbnail}
            alt=""
            loading="lazy"
            className="h-full w-full object-cover transition group-hover:scale-[1.03]"
          />
        ) : (
          <div
            className="flex h-full w-full items-center justify-center p-3 text-center"
            style={{
              backgroundImage: `linear-gradient(135deg, ${meta.color}e6, ${meta.color}99)`
            }}
          >
            <span className="line-clamp-2 text-sm font-bold leading-snug text-white drop-shadow-sm">
              {trend.title}
            </span>
          </div>
        )}
        {showPlatform && (
          <span
            className="absolute left-2 top-2 inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-semibold text-white shadow-sm"
            style={{ backgroundColor: meta.color }}
          >
            <PlatformIcon platform={trend.platform} className="h-2.5 w-2.5" mono />
            {meta.name.split(" ")[0]}
          </span>
        )}
      </div>
      <div className="flex flex-1 flex-col p-2.5">
        <p className="line-clamp-2 text-[13px] font-semibold leading-snug text-ink group-hover:text-brand dark:text-gray-100">
          {trend.title}
        </p>
        {trend.subtitle && (
          <p className="mt-1 truncate text-[11px] text-gray-400 dark:text-gray-500">
            {trend.subtitle}
          </p>
        )}
      </div>
    </Link>
  );
}
