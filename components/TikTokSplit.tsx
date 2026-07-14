/* eslint-disable @next/next/no-img-element */
import Link from "next/link";
import type { Trend } from "@/lib/types";
import { PLATFORMS } from "@/lib/platforms";
import { slugFromId } from "@/lib/embed";
import { formatMetric } from "@/lib/format";
import TrendListItem from "./TrendListItem";

/**
 * Halaman TikTok: pisahkan menjadi dua bagian —
 *  1) "Video lagi viral" → grid video representatif (hashtag yang punya video).
 *  2) "Hashtag lagi tren" → daftar peringkat hashtag.
 * Peringkat DIBERI ULANG 1..N per bagian sesuai urutan tampil, supaya nomor
 * selalu rapi (memperbaiki bug peringkat aneh mulai dari 21).
 */
const TIKTOK_COLOR = PLATFORMS.tiktok.color;

/** Hashtag ini punya video representatif (bisa di-embed) → tampil di grid video. */
function hasVideo(t: Trend): boolean {
  return Boolean(t.extra?.tiktok?.videoUrl) || /\/video\//.test(t.url);
}

function VideoCard({ trend, rank }: { trend: Trend; rank: number }) {
  const href = `/tiktok/${slugFromId(trend.id)}`;
  const plays = trend.extra?.tiktok?.plays ?? trend.metric;
  return (
    <Link href={href} className="group block">
      <div className="relative aspect-[9/16] overflow-hidden rounded-xl bg-gray-200 shadow-sm ring-1 ring-black/5 transition-all duration-200 group-hover:-translate-y-1 group-hover:shadow-xl group-hover:shadow-brand/10 dark:bg-night-soft dark:ring-white/10">
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
        <span
          className="absolute left-1.5 top-1.5 grid h-6 min-w-[24px] place-items-center rounded-lg px-1 text-xs font-extrabold text-white shadow"
          style={{ backgroundColor: TIKTOK_COLOR }}
        >
          {rank}
        </span>
        <span className="pointer-events-none absolute inset-0 grid place-items-center">
          <span
            className="grid h-11 w-11 place-items-center rounded-full bg-black/45 text-lg text-white backdrop-blur transition group-hover:scale-110"
            aria-hidden
          >
            ▶
          </span>
        </span>
        {typeof plays === "number" && plays > 0 && (
          <span className="absolute bottom-1.5 right-1.5 rounded-md bg-black/70 px-1.5 py-0.5 text-[11px] font-bold text-white backdrop-blur">
            ▶ {formatMetric(plays)}
          </span>
        )}
      </div>
      <h3 className="mt-1.5 line-clamp-2 text-xs font-semibold leading-tight text-ink transition-colors group-hover:text-brand dark:text-gray-100 sm:text-sm">
        {trend.title}
      </h3>
    </Link>
  );
}

export default function TikTokSplit({ trends }: { trends: Trend[] }) {
  const videos = trends.filter(hasVideo);
  const hashtags = trends;

  return (
    <div className="space-y-8">
      {videos.length > 0 && (
        <section className="py-3">
          <h2 className="mb-3 flex items-center gap-2 text-lg font-extrabold text-ink dark:text-white">
            <span aria-hidden>🎬</span> Video lagi viral
            <span className="text-sm font-normal text-gray-400">
              · {videos.length}
            </span>
          </h2>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4">
            {videos.map((t, i) => (
              <VideoCard key={t.id} trend={t} rank={i + 1} />
            ))}
          </div>
        </section>
      )}

      <section className="py-3">
        <h2 className="mb-3 flex items-center gap-2 text-lg font-extrabold text-ink dark:text-white">
          <span aria-hidden>#️⃣</span> Hashtag lagi tren
          <span className="text-sm font-normal text-gray-400">
            · {hashtags.length}
          </span>
        </h2>
        <div className="grid gap-2.5 sm:grid-cols-2">
          {hashtags.map((t, i) => (
            <TrendListItem
              key={t.id}
              trend={{ ...t, rank: i + 1, thumbnail: undefined }}
            />
          ))}
        </div>
      </section>
    </div>
  );
}
