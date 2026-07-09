import type { Metadata } from "next";
import PageShell from "@/components/PageShell";

export const metadata: Metadata = {
  title: "Tentang Kami",
  description:
    "Lagi Tren adalah platform yang mengumpulkan informasi trending dari berbagai platform di Indonesia dalam satu halaman.",
  alternates: { canonical: "/about" }
};

export default function AboutPage() {
  return (
    <PageShell
      title="Tentang Kami"
      subtitle="Apa itu Lagi Tren dan apa yang kami lakukan."
    >
      <p>
        <strong>Lagi Tren</strong> (lagitren.id) adalah platform yang
        mengumpulkan informasi <em>trending</em> dari berbagai platform seperti
        Google, YouTube, TikTok, Instagram, dan marketplace Indonesia. Kami
        membantu Anda mengetahui apa yang sedang viral dan banyak dicari saat
        ini — semuanya dalam satu halaman.
      </p>
      <p>
        Untuk setiap tren, kami menyertakan ringkasan singkat berbahasa
        Indonesia yang dibuat dengan bantuan AI, agar Anda cepat memahami{" "}
        <em>kenapa</em> sesuatu sedang ramai dibicarakan. Konten asli tetap
        berada di platform sumbernya, dan kami selalu menyertakan tautan ke
        sumber tersebut.
      </p>
      <h2 className="text-lg font-bold text-ink">Kenapa Lagi Tren?</h2>
      <p>
        Informasi tren tersebar di banyak aplikasi. Alih-alih membuka satu per
        satu, Lagi Tren merangkumnya dalam satu tampilan yang mudah dipindai —
        dirancang mobile-first untuk pengguna Indonesia.
      </p>
      <h2 className="text-lg font-bold text-ink">Sumber Data</h2>
      <p>
        Data dikumpulkan dari data publik masing-masing platform (Google Trends,
        YouTube Trending, TikTok, Instagram, marketplace, dan X/Twitter) secara
        berkala. Kami menghormati kebijakan dan batasan tiap platform, serta
        tidak menyalin konten berhak cipta — hanya menautkan dan meringkas.
      </p>
      <p>
        Ada pertanyaan atau masukan? Hubungi kami melalui halaman{" "}
        <a href="/contact" className="text-brand hover:underline">
          Kontak
        </a>
        .
      </p>
    </PageShell>
  );
}
