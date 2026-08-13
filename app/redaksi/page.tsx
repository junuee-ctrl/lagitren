import type { Metadata } from "next";
import PageShell from "@/components/PageShell";
import {
  AUTHOR_NAME,
  AUTHOR_ROLE,
  CONTACT_EMAIL,
  SITE_URL
} from "@/lib/site";

export const metadata: Metadata = {
  title: "Redaksi",
  description:
    "Siapa di balik Lagi Tren — redaksi, metodologi kurasi tren, dan cara menghubungi kami.",
  alternates: { canonical: "/redaksi" }
};

export default function RedaksiPage() {
  return (
    <PageShell
      title="Redaksi"
      subtitle="Siapa di balik Lagi Tren dan bagaimana kami bekerja."
    >
      {/* Profil editor */}
      <section className="not-prose my-4 flex items-center gap-4 rounded-2xl border border-gray-200 bg-white p-5 dark:border-white/10 dark:bg-night-card">
        <span
          aria-hidden
          className="grid h-16 w-16 shrink-0 place-items-center rounded-2xl bg-gradient-to-br from-brand to-accent text-2xl font-extrabold text-white"
        >
          {AUTHOR_NAME.split(" ").map((w) => w[0]).join("")}
        </span>
        <div>
          <p className="text-lg font-extrabold text-ink dark:text-white">
            {AUTHOR_NAME}
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {AUTHOR_ROLE} · Berbasis di Jakarta
          </p>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Kontak:{" "}
            <a
              href={`mailto:${CONTACT_EMAIL}`}
              className="text-brand hover:underline"
            >
              {CONTACT_EMAIL}
            </a>
          </p>
        </div>
      </section>

      <p>
        <strong>Arka Pradana</strong> (nama pena) adalah editor dan kurator di
        balik Lagi Tren. Ia memantau tren lintas platform di Indonesia setiap
        hari, menyetel sistem pengumpulan data kami, dan memeriksa kualitas
        ringkasan sebelum tampil di situs.
      </p>

      <h2 className="text-lg font-bold text-ink dark:text-white">
        Bagaimana konten kami dibuat
      </h2>
      <p>
        Data tren dikumpulkan otomatis dari sumber publik — Google Trends,
        YouTube Trending, TikTok Creative Center, Instagram, Netflix Top 10,
        dan X (Twitter) — dengan jadwal berkala (15 menit hingga harian,
        tergantung platform). Setiap tren kemudian diberi ringkasan berbahasa
        Indonesia yang dibuat dengan bantuan AI dan difokuskan menjawab satu
        hal: <em>kenapa ini sedang ramai?</em>
      </p>
      <p>
        Kami tidak menyalin konten berhak cipta. Setiap kartu tren menautkan ke
        sumber aslinya, dan angka (penayangan, suka, penjualan) berasal dari
        data publik platform terkait pada saat pengumpulan.
      </p>

      <h2 className="text-lg font-bold text-ink dark:text-white">Koreksi</h2>
      <p>
        Menemukan data yang keliru atau ringkasan yang tidak akurat? Kirim
        email ke{" "}
        <a
          href={`mailto:${CONTACT_EMAIL}`}
          className="text-brand hover:underline"
        >
          {CONTACT_EMAIL}
        </a>{" "}
        — kami meninjau dan memperbaikinya secepat mungkin.
      </p>

      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "ProfilePage",
            mainEntity: {
              "@type": "Person",
              name: AUTHOR_NAME,
              jobTitle: AUTHOR_ROLE,
              email: CONTACT_EMAIL,
              url: `${SITE_URL}/redaksi`,
              worksFor: { "@id": `${SITE_URL}/#organization` }
            }
          })
        }}
      />
    </PageShell>
  );
}
