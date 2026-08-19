import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { getArticle, getArticles } from "@/lib/db";
import { KATEGORI_COLOR, KATEGORI_LABEL, formatTanggal } from "@/lib/artikel";
import {
  AUTHOR_NAME,
  SITE_URL,
  authorRef,
  publisherRef,
  toIso
} from "@/lib/site";
import AdSlot from "@/components/AdSlot";
import { AD_SLOTS } from "@/lib/adsense";

export const revalidate = 1800;

type Props = { params: { slug: string } };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const a = await getArticle(params.slug);
  if (!a) return { title: "Artikel tidak ditemukan" };
  const og = `/og/artikel/${a.slug}`;
  return {
    title: a.title,
    description: a.lead.slice(0, 160),
    alternates: { canonical: `/artikel/${a.slug}` },
    openGraph: {
      type: "article",
      title: a.title,
      description: a.lead.slice(0, 200),
      url: `${SITE_URL}/artikel/${a.slug}`,
      images: [{ url: og, width: 1200, height: 630 }]
    },
    twitter: {
      card: "summary_large_image",
      title: a.title,
      description: a.lead.slice(0, 200),
      images: [og]
    }
  };
}

export default async function ArtikelDetailPage({ params }: Props) {
  const a = await getArticle(params.slug);
  if (!a) notFound();

  const others = (await getArticles(7)).filter((x) => x.slug !== a.slug).slice(0, 3);
  const articleBody = [
    a.lead,
    ...a.sections.flatMap((s) => [s.heading, ...s.paragraphs])
  ].join("\n\n");

  return (
    <article className="mx-auto max-w-2xl py-4">
      {/* breadcrumb */}
      <nav className="text-xs text-gray-400 dark:text-gray-500">
        <Link href="/" className="hover:text-brand">
          Beranda
        </Link>{" "}
        ›{" "}
        <Link href="/artikel" className="hover:text-brand">
          Artikel
        </Link>{" "}
        › <span className="text-gray-500 dark:text-gray-400">{KATEGORI_LABEL[a.category]}</span>
      </nav>

      <div className="mt-3 flex items-center gap-3 text-xs">
        <span
          className="rounded-full px-2.5 py-0.5 font-semibold text-white"
          style={{ backgroundColor: KATEGORI_COLOR[a.category] }}
        >
          {KATEGORI_LABEL[a.category]}
        </span>
      </div>

      <h1 className="mt-3 text-2xl font-extrabold leading-snug text-ink dark:text-white sm:text-3xl">
        {a.title}
      </h1>

      <p className="mt-3 text-sm text-gray-500 dark:text-gray-400">
        Oleh{" "}
        <Link href="/redaksi" className="font-medium text-brand hover:underline">
          {AUTHOR_NAME}
        </Link>{" "}
        · Terbit {formatTanggal(a.publishedAt)}
        {a.updatedAt && a.updatedAt.slice(0, 10) !== a.publishedAt.slice(0, 10)
          ? ` · Diperbarui ${formatTanggal(a.updatedAt)}`
          : ""}
      </p>

      <p className="mt-5 text-[17px] font-medium leading-relaxed text-gray-800 dark:text-gray-100">
        {a.lead}
      </p>

      {/* kartu data */}
      {a.dataCard && Object.keys(a.dataCard).length > 0 && (
        <div className="not-prose mt-5 grid grid-cols-2 gap-3 rounded-2xl border border-gray-200 bg-gray-50 p-4 text-sm dark:border-white/10 dark:bg-white/5 sm:grid-cols-4">
          {Object.entries(a.dataCard).map(([k, v]) => (
            <div key={k}>
              <p className="text-xs text-gray-400 dark:text-gray-500">{k}</p>
              <p className="font-bold text-ink dark:text-white">{v}</p>
            </div>
          ))}
        </div>
      )}

      <AdSlot slot="artikel-detail-top" adSlot={AD_SLOTS.atas} />

      <div className="mt-6 space-y-7 text-[15px] leading-relaxed text-gray-700 dark:text-gray-200">
        {a.sections.map((s) => (
          <section key={s.heading}>
            <h2 className="mb-2 text-lg font-bold text-ink dark:text-white">
              {s.heading}
            </h2>
            <div className="space-y-3">
              {s.paragraphs.map((p, i) => (
                <p key={i}>{p}</p>
              ))}
            </div>
          </section>
        ))}
      </div>

      {/* sumber eksternal */}
      {a.sources.length > 0 && (
        <section className="mt-8 rounded-2xl border border-gray-200 p-4 dark:border-white/10">
          <h2 className="text-sm font-bold text-ink dark:text-white">
            Sumber & bacaan lanjut
          </h2>
          <ul className="mt-2 space-y-1.5 text-sm">
            {a.sources.map((s) => (
              <li key={s.url}>
                <a
                  href={s.url}
                  target="_blank"
                  rel="noopener nofollow"
                  className="text-brand hover:underline"
                >
                  {s.title}
                </a>
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* tautan internal terkait */}
      {a.related.length > 0 && (
        <section className="mt-6">
          <h2 className="text-sm font-bold text-ink dark:text-white">
            Terkait di Lagi Tren
          </h2>
          <ul className="mt-2 flex flex-wrap gap-2 text-sm">
            {a.related.map((path) => (
              <li key={path}>
                <Link
                  href={path}
                  className="inline-block rounded-full border border-gray-200 px-3 py-1 text-gray-600 transition hover:border-brand hover:text-brand dark:border-white/10 dark:text-gray-300"
                >
                  {path.replace(/^\//, "").replace(/-/g, " ").replace(/\//g, " › ")}
                </Link>
              </li>
            ))}
          </ul>
        </section>
      )}

      <AdSlot slot="artikel-detail-bottom" adSlot={AD_SLOTS.bawah} />

      {/* artikel lain */}
      {others.length > 0 && (
        <section className="mt-10">
          <h2 className="text-lg font-bold text-ink dark:text-white">
            Artikel lainnya
          </h2>
          <ul className="mt-3 space-y-3">
            {others.map((o) => (
              <li key={o.slug}>
                <Link
                  href={`/artikel/${o.slug}`}
                  className="block rounded-xl border border-gray-200 p-4 transition hover:border-brand/40 dark:border-white/10"
                >
                  <p className="text-xs text-gray-400">{KATEGORI_LABEL[o.category]}</p>
                  <p className="mt-0.5 font-semibold text-ink dark:text-white">
                    {o.title}
                  </p>
                </Link>
              </li>
            ))}
          </ul>
        </section>
      )}

      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify([
            {
              "@context": "https://schema.org",
              "@type": "Article",
              headline: a.title,
              description: a.lead,
              articleBody,
              image: [`${SITE_URL}/og/artikel/${a.slug}`],
              datePublished: toIso(a.publishedAt),
              dateModified: toIso(a.updatedAt) ?? toIso(a.publishedAt),
              author: authorRef(),
              publisher: publisherRef(),
              mainEntityOfPage: `${SITE_URL}/artikel/${a.slug}`
            },
            {
              "@context": "https://schema.org",
              "@type": "BreadcrumbList",
              itemListElement: [
                { "@type": "ListItem", position: 1, name: "Beranda", item: SITE_URL },
                { "@type": "ListItem", position: 2, name: "Artikel", item: `${SITE_URL}/artikel` },
                { "@type": "ListItem", position: 3, name: a.title, item: `${SITE_URL}/artikel/${a.slug}` }
              ]
            }
          ])
        }}
      />
    </article>
  );
}
