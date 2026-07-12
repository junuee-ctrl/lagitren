import type { Trend } from "@/lib/types";

/**
 * Konteks kaya per-platform yang dibaca DI SITUS (menambah kedalaman konten
 * & page view untuk SEO/iklan):
 *   - Google : berita terkait teratas (judul + sumber, tautan keluar).
 *   - YouTube: komentar terbaik penonton.
 */
export default function TrendContext({ trend }: { trend: Trend }) {
  const news = trend.extra?.news ?? [];
  const comments = trend.extra?.comments ?? [];
  const ott = trend.extra?.ott;
  const hasOtt = !!(ott && (ott.synopsis || ott.rating || ott.weeks));

  if (news.length === 0 && comments.length === 0 && !hasOtt) return null;

  return (
    <>
      {hasOtt && (
        <section className="my-5 rounded-2xl border border-gray-200 bg-white p-5">
          <h2 className="flex items-center gap-2 text-base font-bold text-ink">
            <span aria-hidden>🍿</span> Tentang tontonan ini
          </h2>
          <div className="mt-2 flex flex-wrap items-center gap-2 text-sm">
            {ott?.kind && (
              <span className="rounded-full bg-gray-100 px-2.5 py-0.5 font-medium text-gray-700">
                {ott.kind}
              </span>
            )}
            {typeof ott?.rating === "number" && (
              <span className="rounded-full bg-amber-50 px-2.5 py-0.5 font-medium text-amber-700">
                ⭐ {ott.rating}/10
              </span>
            )}
            {ott?.weeks && Number(ott.weeks) > 0 && (
              <span className="rounded-full bg-gray-100 px-2.5 py-0.5 font-medium text-gray-700">
                {ott.weeks} minggu di Top 10
              </span>
            )}
          </div>
          {ott?.synopsis && (
            <p className="mt-3 text-[15px] leading-relaxed text-gray-800">
              {ott.synopsis}
            </p>
          )}
        </section>
      )}

      {news.length > 0 && (
        <section className="my-5 rounded-2xl border border-gray-200 bg-white p-5">
          <h2 className="flex items-center gap-2 text-base font-bold text-ink">
            <span aria-hidden>📰</span> Berita terkait
          </h2>
          <ul className="mt-3 space-y-3">
            {news.map((n, i) => (
              <li key={`${n.url}-${i}`} className="flex gap-3">
                <span className="mt-0.5 text-sm font-bold text-gray-300">
                  {i + 1}
                </span>
                <div className="min-w-0">
                  <a
                    href={n.url}
                    target="_blank"
                    rel="nofollow noopener noreferrer"
                    className="text-[15px] font-medium leading-snug text-gray-800 hover:text-brand"
                  >
                    {n.title}
                  </a>
                  {n.source && (
                    <p className="mt-0.5 text-xs text-gray-400">{n.source} ↗</p>
                  )}
                </div>
              </li>
            ))}
          </ul>
          <p className="mt-3 text-xs text-gray-400">
            Rangkuman tautan berita dari sumber pihak ketiga.
          </p>
        </section>
      )}

      {comments.length > 0 && (
        <section className="my-5 rounded-2xl border border-gray-200 bg-white p-5">
          <h2 className="flex items-center gap-2 text-base font-bold text-ink">
            <span aria-hidden>💬</span> Komentar penonton terbaik
          </h2>
          <ul className="mt-3 space-y-3">
            {comments.map((c, i) => (
              <li
                key={i}
                className="rounded-xl bg-gray-50 p-3 text-sm text-gray-800"
              >
                <p className="leading-relaxed">{c.text}</p>
                <p className="mt-1.5 flex items-center gap-2 text-xs text-gray-400">
                  {c.author && <span className="font-medium">{c.author}</span>}
                  {typeof c.likes === "number" && c.likes > 0 && (
                    <span>👍 {c.likes.toLocaleString("id-ID")}</span>
                  )}
                </p>
              </li>
            ))}
          </ul>
        </section>
      )}
    </>
  );
}
