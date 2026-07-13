/* eslint-disable @next/next/no-img-element */
import Link from "next/link";
import type { Trend } from "@/lib/types";
import { slugFromId } from "@/lib/embed";

/**
 * Halaman Netflix: pisahkan Film dan Serial TV, tampilkan sebagai GRID POSTER.
 * Kategori dibaca dari `extra.ott.kind` ("Film" / "Serial TV").
 */
function group(trends: Trend[]) {
  const films = trends.filter((t) => t.extra?.ott?.kind !== "Serial TV");
  const tv = trends.filter((t) => t.extra?.ott?.kind === "Serial TV");
  return { films, tv };
}

function PosterCard({ trend, rank }: { trend: Trend; rank: number }) {
  const href = `/netflix/${slugFromId(trend.id)}`;
  const rating = trend.extra?.ott?.rating;
  return (
    <Link href={href} className="group block">
      <div className="relative aspect-[2/3] overflow-hidden rounded-xl bg-gray-200 shadow-sm ring-1 ring-black/5 transition-all duration-200 group-hover:-translate-y-1 group-hover:shadow-xl group-hover:shadow-brand/10 dark:bg-night-soft dark:ring-white/10">
        {trend.thumbnail ? (
          <img
            src={trend.thumbnail}
            alt={trend.title}
            loading="lazy"
            className="h-full w-full object-cover"
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center p-2 text-center text-xs font-semibold text-gray-400">
            {trend.title}
          </div>
        )}
        {/* Peringkat */}
        <span className="absolute left-1.5 top-1.5 grid h-6 min-w-[24px] place-items-center rounded-lg bg-netflix px-1 text-xs font-extrabold text-white shadow">
          {rank}
        </span>
        {/* Rating */}
        {typeof rating === "number" && (
          <span className="absolute bottom-1.5 right-1.5 rounded-md bg-black/70 px-1.5 py-0.5 text-[11px] font-bold text-amber-300 backdrop-blur">
            ⭐ {rating}
          </span>
        )}
      </div>
      <h3 className="mt-1.5 line-clamp-2 text-xs font-semibold leading-tight text-ink transition-colors group-hover:text-brand dark:text-gray-100 sm:text-sm">
        {trend.title}
      </h3>
    </Link>
  );
}

function Grid({
  title,
  icon,
  items
}: {
  title: string;
  icon: string;
  items: Trend[];
}) {
  if (items.length === 0) return null;
  return (
    <section className="py-3">
      <h2 className="mb-3 flex items-center gap-2 text-lg font-extrabold text-ink dark:text-white">
        <span aria-hidden>{icon}</span> {title}
        <span className="text-sm font-normal text-gray-400">
          · {items.length}
        </span>
      </h2>
      <div className="grid grid-cols-3 gap-3 sm:grid-cols-4 md:grid-cols-5">
        {items.map((t, i) => (
          <PosterCard key={t.id} trend={t} rank={i + 1} />
        ))}
      </div>
    </section>
  );
}

export default function NetflixSplit({ trends }: { trends: Trend[] }) {
  const { films, tv } = group(trends);
  return (
    <div className="space-y-6">
      <Grid title="Film Teratas" icon="🎬" items={films} />
      <Grid title="Serial TV Teratas" icon="📺" items={tv} />
    </div>
  );
}
