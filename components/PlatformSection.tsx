import Link from "next/link";
import type { Platform, Trend } from "@/lib/types";
import { PLATFORMS } from "@/lib/platforms";
import TrendListItem from "./TrendListItem";

/**
 * Section satu platform: judul + daftar ringkas.
 * Setiap item menautkan ke halaman detail internal (bukan keluar situs).
 */
export default function PlatformSection({
  platform,
  trends,
  showAll = false
}: {
  platform: Platform;
  trends: Trend[];
  /** true di halaman detail platform (sembunyikan tombol "lihat semua"). */
  showAll?: boolean;
}) {
  const meta = PLATFORMS[platform];
  if (trends.length === 0) return null;

  return (
    <section id={platform} className="scroll-mt-20 py-5">
      <div className="mb-3.5 flex items-end justify-between gap-3">
        <div className="flex items-center gap-3">
          <span
            className="grid h-11 w-11 place-items-center rounded-2xl text-xl shadow-sm ring-1 ring-inset"
            style={{
              backgroundColor: `${meta.color}1f`,
              color: meta.color,
              boxShadow: `0 4px 14px ${meta.color}22`
            }}
            aria-hidden
          >
            {meta.icon}
          </span>
          <div>
            <h2 className="text-lg font-extrabold tracking-tight text-ink dark:text-white sm:text-xl">
              {meta.sectionTitle}
            </h2>
            <p className="mt-0.5 flex items-center gap-1 text-xs text-gray-400 dark:text-gray-500">
              <span
                className="inline-block h-1.5 w-1.5 rounded-full"
                style={{ backgroundColor: meta.color }}
                aria-hidden
              />
              {meta.refresh}
            </p>
          </div>
        </div>

        {!showAll && (
          <Link
            href={`/${platform}`}
            className="group shrink-0 rounded-full px-3 py-1.5 text-sm font-semibold text-brand transition hover:bg-brand/10 dark:hover:bg-brand/15"
          >
            Lihat semua{" "}
            <span className="inline-block transition group-hover:translate-x-0.5">
              →
            </span>
          </Link>
        )}
      </div>

      <div className="grid gap-2.5 sm:grid-cols-2">
        {trends.map((t) => (
          <TrendListItem key={t.id} trend={t} />
        ))}
      </div>
    </section>
  );
}
