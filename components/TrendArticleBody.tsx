import type { TrendArticle } from "@/lib/types";

/**
 * Artikel terstruktur (P1-3): lead + 3 bagian bersub-judul.
 * Menggantikan kotak ringkasan 3 kalimat pada tren teratas.
 */
export default function TrendArticleBody({
  article
}: {
  article: TrendArticle;
}) {
  const sections: Array<[string, string | undefined]> = [
    ["Apa yang terjadi?", article.apa],
    ["Kenapa ini rame?", article.rame],
    ["Kenapa penting buat kamu?", article.penting]
  ];

  return (
    <section className="my-5 rounded-2xl border border-brand/25 bg-gradient-to-br from-brand/10 to-accent/10 p-5 dark:border-brand/30 dark:from-brand/15 dark:to-accent/10 sm:p-6">
      {article.lead && (
        <p className="text-[16px] font-semibold leading-relaxed text-ink dark:text-white">
          {article.lead}
        </p>
      )}
      {sections.map(
        ([heading, body]) =>
          body && (
            <div key={heading} className="mt-4">
              <h2 className="flex items-center gap-2 text-base font-bold text-brand dark:text-brand-light">
                {heading}
              </h2>
              <p className="mt-1.5 text-[15px] leading-relaxed text-gray-800 dark:text-gray-200">
                {body}
              </p>
            </div>
          )
      )}
    </section>
  );
}
