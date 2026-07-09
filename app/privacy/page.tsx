import type { Metadata } from "next";
import PageShell from "@/components/PageShell";

export const metadata: Metadata = {
  title: "Kebijakan Privasi",
  description:
    "Kebijakan privasi Lagi Tren: bagaimana kami menggunakan cookie, iklan, dan alat analitik.",
  alternates: { canonical: "/privacy" }
};

export default function PrivacyPage() {
  return (
    <PageShell
      title="Kebijakan Privasi"
      subtitle="Terakhir diperbarui: 9 Juli 2026"
    >
      <p>
        Kebijakan Privasi ini menjelaskan bagaimana Lagi Tren (lagitren.id)
        mengumpulkan, menggunakan, dan melindungi informasi saat Anda mengakses
        situs kami.
      </p>

      <h2 className="text-lg font-bold text-ink">Informasi yang Kami Kumpulkan</h2>
      <p>
        Kami tidak mewajibkan Anda membuat akun untuk menggunakan Lagi Tren.
        Informasi yang dikumpulkan bersifat non-pribadi dan agregat, seperti
        data kunjungan halaman melalui alat analitik. Jika Anda menghubungi
        kami, kami menyimpan email dan isi pesan Anda hanya untuk keperluan
        membalas.
      </p>

      <h2 className="text-lg font-bold text-ink">Cookie</h2>
      <p>
        Situs ini dapat menggunakan cookie untuk memahami cara pengunjung
        menggunakan situs dan untuk menampilkan iklan yang relevan. Anda dapat
        menonaktifkan cookie melalui pengaturan browser, meskipun beberapa
        fitur mungkin tidak berfungsi optimal.
      </p>

      <h2 className="text-lg font-bold text-ink">Iklan Pihak Ketiga</h2>
      <p>
        Kami dapat menampilkan iklan dari Google AdSense dan jaringan pihak
        ketiga lainnya. Penyedia ini dapat menggunakan cookie untuk menayangkan
        iklan berdasarkan kunjungan Anda ke situs ini dan situs lain. Anda dapat
        mempelajari dan mengatur preferensi iklan Google melalui{" "}
        <a
          href="https://policies.google.com/technologies/ads"
          target="_blank"
          rel="noopener noreferrer"
          className="text-brand hover:underline"
        >
          Kebijakan Iklan Google
        </a>
        .
      </p>

      <h2 className="text-lg font-bold text-ink">Analitik</h2>
      <p>
        Kami dapat menggunakan alat analitik (misalnya analitik privasi atau
        Google Analytics) untuk memahami tren penggunaan secara agregat. Data
        ini tidak digunakan untuk mengidentifikasi individu.
      </p>

      <h2 className="text-lg font-bold text-ink">Tautan Eksternal</h2>
      <p>
        Lagi Tren berisi tautan ke platform pihak ketiga (Google, YouTube,
        TikTok, Instagram, marketplace, X). Kami tidak bertanggung jawab atas
        praktik privasi situs-situs tersebut. Silakan baca kebijakan privasi
        mereka masing-masing.
      </p>

      <h2 className="text-lg font-bold text-ink">Perubahan Kebijakan</h2>
      <p>
        Kebijakan ini dapat diperbarui sewaktu-waktu. Perubahan akan
        dipublikasikan di halaman ini beserta tanggal pembaruan.
      </p>

      <h2 className="text-lg font-bold text-ink">Hubungi Kami</h2>
      <p>
        Untuk pertanyaan terkait privasi, hubungi kami di{" "}
        <a href="mailto:halo@lagitren.id" className="text-brand hover:underline">
          halo@lagitren.id
        </a>
        .
      </p>
    </PageShell>
  );
}
