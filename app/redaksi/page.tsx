import type { Metadata } from "next";
import Link from "next/link";
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
    "Siapa di balik Lagi Tren — tim redaksi, peran AI dalam produksi konten, dan prosedur koreksi kami.",
  alternates: { canonical: "/redaksi" }
};

export default function RedaksiPage() {
  return (
    <PageShell
      title="Redaksi"
      subtitle="Siapa di balik Lagi Tren dan bagaimana kami bekerja."
    >
      {/* Identitas penerbit */}
      <section className="not-prose my-4 flex items-center gap-4 rounded-2xl border border-gray-200 bg-white p-5 dark:border-white/10 dark:bg-night-card">
        <span
          aria-hidden
          className="grid h-16 w-16 shrink-0 place-items-center rounded-2xl bg-gradient-to-br from-brand to-accent text-2xl font-extrabold text-white"
        >
          LT
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
        Lagi Tren dikelola oleh <strong>{AUTHOR_NAME}</strong> — tim kecil yang
        berbasis di Jakarta. Kami membangun dan mengoperasikan sistem
        pengumpulan data tren lintas platform, menyusun analisis dari arsip
        data kami sendiri, dan memeriksa kualitas setiap konten sebelum tampil
        di situs. Kami sengaja tidak memakai nama pena atau profil fiktif:
        seluruh konten diterbitkan atas nama tim redaksi.
      </p>

      <h2 className="text-lg font-bold text-ink dark:text-white">
        Peran AI — dan batasnya
      </h2>
      <p>
        Kami terbuka soal ini: sebagian proses produksi konten Lagi Tren
        dibantu kecerdasan buatan (AI). Pembagiannya jelas:
      </p>
      <p>
        <strong>Angka dan fakta dihitung oleh sistem kami</strong> dari data
        yang kami kumpulkan sendiri (peringkat, perubahan posisi, lama bertahan
        di daftar tren) — AI tidak pernah diminta &ldquo;mengarang&rdquo;
        angka. <strong>AI membantu menuliskan</strong> ringkasan dan draf
        artikel berdasarkan fakta tersebut, lalu{" "}
        <strong>redaksi memeriksa</strong> hasilnya sebelum terbit. Konten yang
        tidak lolos pemeriksaan tidak diterbitkan. Rincian teknisnya kami
        jelaskan di halaman{" "}
        <Link href="/metodologi" className="text-brand hover:underline">
          Metodologi
        </Link>{" "}
        dan{" "}
        <Link
          href="/kebijakan-editorial"
          className="text-brand hover:underline"
        >
          Kebijakan Editorial
        </Link>
        .
      </p>

      <h2 className="text-lg font-bold text-ink dark:text-white">
        Bagaimana data kami dikumpulkan
      </h2>
      <p>
        Data tren dikumpulkan otomatis dari sumber publik — Google Trends,
        YouTube Trending, TikTok Creative Center, Instagram, Netflix Top 10,
        dan X (Twitter) — dengan jadwal berkala (10 menit hingga harian,
        tergantung platform). Kami tidak menyalin konten berhak cipta; setiap
        kartu tren menautkan ke sumber aslinya, dan angka (penayangan, suka,
        penjualan) berasal dari data publik platform terkait pada saat
        pengumpulan.
      </p>

      <h2 className="text-lg font-bold text-ink dark:text-white">Koreksi</h2>
      <p>
        Menemukan data yang keliru atau tulisan yang tidak akurat? Kirim email
        ke{" "}
        <a
          href={`mailto:${CONTACT_EMAIL}`}
          className="text-brand hover:underline"
        >
          {CONTACT_EMAIL}
        </a>{" "}
        — kami meninjau dalam 2×24 jam dan mencantumkan catatan perbaikan pada
        konten yang dikoreksi.
      </p>

      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "AboutPage",
            mainEntity: {
              "@type": "Organization",
              name: AUTHOR_NAME,
              email: CONTACT_EMAIL,
              url: `${SITE_URL}/redaksi`,
              parentOrganization: { "@id": `${SITE_URL}/#organization` }
            }
          })
        }}
      />
    </PageShell>
  );
}
