import type { Trend } from "@/lib/types";
import TrendListItem from "./TrendListItem";

/**
 * Halaman Netflix: pisahkan Film dan Serial TV jadi dua daftar.
 * Kategori dibaca dari `extra.ott.kind` ("Film" / "Serial TV").
 */
function group(trends: Trend[]) {
  const films = trends.filter((t) => t.extra?.ott?.kind !== "Serial TV");
  const tv = trends.filter((t) => t.extra?.ott?.kind === "Serial TV");
  return { films, tv };
}

function List({
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
      <h2 className="mb-3 flex items-center gap-2 text-lg font-extrabold text-ink">
        <span aria-hidden>{icon}</span> {title}
        <span className="text-sm font-normal text-gray-400">
          · {items.length}
        </span>
      </h2>
      <div className="grid gap-2 sm:grid-cols-2">
        {items.map((t, i) => (
          // Nomor urut per-kategori (1..N), bukan peringkat gabungan.
          <TrendListItem key={t.id} trend={{ ...t, rank: i + 1 }} />
        ))}
      </div>
    </section>
  );
}

export default function NetflixSplit({ trends }: { trends: Trend[] }) {
  const { films, tv } = group(trends);
  return (
    <div className="space-y-4">
      <List title="Film Teratas" icon="🎬" items={films} />
      <List title="Serial TV Teratas" icon="📺" items={tv} />
    </div>
  );
}
