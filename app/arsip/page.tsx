import type { Metadata } from "next";
import Link from "next/link";
import { getArchivedTrends } from "@/lib/db";
import { dateKey, formatDateID } from "@/lib/format";
import type { Trend } from "@/lib/types";
import TrendListItem from "@/components/TrendListItem";
import AdSlot from "@/components/AdSlot";

// Segarkan berkala; arsip berubah pelan (saat tren lama diarsipkan).
export const revalidate = 1800; // 30 menit

export const metadata: Metadata = {
  title: "Arsip Tren — Yang Pernah Viral di Indonesia",
  description:
    "Kumpulan tren yang pernah ramai di Indonesia dari Google, YouTube, TikTok, Instagram, X, dan Shopee — diarsipkan per tanggal. Lihat kembali apa yang dulu sedang tren.",
  alternates: { canonical: "/arsip" }
};

function groupByDate(trends: Trend[]): { date: string; items: Trend[] }[] {
  const map = new Map<string, Trend[]>();
  for (const t of trends) {
    const key = dateKey(t.collectedAt) || "—";
    const arr = map.get(key);
    if (arr) arr.push(t);
    else map.set(key, [t]);
  }
  return [...map.entries()]
    .sort((a, b) => (a[0] < b[0] ? 1 : -1)) // tanggal terbaru dulu
    .map(([date, items]) => ({
      date,
      items: items.sort((a, b) => a.rank - b.rank)
    }));
}

export default async function ArchivePage() {
  const archived = await getArchivedTrends(300);
  const groups = groupByDate(archived);

  return (
    <div className="mx-auto max-w-3xl">
      <header className="mb-6">
        <nav className="mb-3 text-sm text-gray-400">
          <Link href="/" className="hover:text-brand">
            Beranda
          </Link>{" "}
          / <span className="text-gray-600">Arsip</span>
        </nav>
        <h1 className="text-2xl font-extrabold text-ink sm:text-3xl">
          🗂️ Arsip Tren
        </h1>
        <p className="mt-2 text-sm text-gray-500">
          Yang pernah ramai di Indonesia, diarsipkan per tanggal. Halaman ini
          tetap tersimpan meski trennya sudah lewat — siapa tahu Anda ingin
          menengok lagi.
        </p>
      </header>

      <AdSlot slot="arsip-top" />

      {groups.length === 0 ? (
        <div className="mt-6 rounded-2xl border border-dashed border-gray-300 bg-white p-8 text-center">
          <p className="text-sm text-gray-500">
            Belum ada arsip. Tren yang sedang berlangsung akan muncul di sini
            setelah tidak lagi aktif.
          </p>
          <Link
            href="/"
            className="mt-3 inline-block text-sm font-semibold text-brand hover:underline"
          >
            Lihat yang lagi tren sekarang →
          </Link>
        </div>
      ) : (
        <div className="mt-4 space-y-8">
          {groups.map((g) => (
            <section key={g.date}>
              <h2 className="mb-3 flex items-center gap-2 text-sm font-bold uppercase tracking-wide text-gray-500">
                <span aria-hidden>📅</span> {formatDateID(g.date)}
                <span className="font-normal normal-case text-gray-400">
                  · {g.items.length} tren
                </span>
              </h2>
              <div className="grid gap-2 sm:grid-cols-2">
                {g.items.map((t) => (
                  <TrendListItem key={t.id} trend={t} showPlatform />
                ))}
              </div>
            </section>
          ))}
        </div>
      )}
    </div>
  );
}
