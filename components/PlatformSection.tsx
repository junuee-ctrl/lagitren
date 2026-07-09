import Link from "next/link";
import type { Platform, Trend } from "@/lib/types";
import { PLATFORMS } from "@/lib/platforms";
import TrendCard from "./TrendCard";

export default function PlatformSection({
  platform,
  trends,
  showAll = false
}: {
  platform: Platform;
  trends: Trend[];
  /** true di halaman detail (sembunyikan tombol "lihat semua"). */
  showAll?: boolean;
}) {
  const meta = PLATFORMS[platform];
  if (trends.length === 0) return null;

  return (
    <section id={platform} className="scroll-mt-20 py-4">
      <div className="mb-4 flex items-end justify-between gap-3">
        <div>
          <h2 className="flex items-center gap-2 text-lg font-extrabold text-ink sm:text-xl">
            <span
              className="inline-flex h-8 w-8 items-center justify-center rounded-lg text-lg"
              style={{ backgroundColor: `${meta.color}1a`, color: meta.color }}
              aria-hidden
            >
              {meta.icon}
            </span>
            {meta.sectionTitle}
          </h2>
          <p className="mt-0.5 text-xs text-gray-400">{meta.refresh}</p>
        </div>

        {!showAll && (
          <Link
            href={`/${platform}`}
            className="shrink-0 text-sm font-semibold text-brand hover:underline"
          >
            Lihat semua →
          </Link>
        )}
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {trends.map((t) => (
          <TrendCard key={t.id} trend={t} />
        ))}
      </div>
    </section>
  );
}
