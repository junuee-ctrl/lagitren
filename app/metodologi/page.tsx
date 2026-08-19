import type { Metadata } from "next";
import Link from "next/link";
import PageShell from "@/components/PageShell";
import { SITE_NAME } from "@/lib/site";

export const metadata: Metadata = {
  title: "Metodologi",
  description:
    "Bagaimana Lagi Tren mengumpulkan data: sumber tiap platform, jadwal pengambilan, cara arsip peringkat dibangun, dan batasan datanya.",
  alternates: { canonical: "/metodologi" }
};

const SOURCES: Array<{ p: string; src: string; jadwal: string }> = [
  { p: "Google Trends", src: "RSS resmi Google Trends Indonesia (kata kunci yang sedang naik)", jadwal: "±10 menit" },
  { p: "YouTube", src: "YouTube Data API — daftar Trending resmi wilayah Indonesia", jadwal: "±1 jam" },
  { p: "TikTok", src: "TikTok Creative Center — hashtag populer wilayah Indonesia", jadwal: "±3 jam" },
  { p: "Instagram", src: "Unggahan populer pada tagar Indonesia terpilih", jadwal: "±3 jam" },
  { p: "X (Twitter)", src: "Daftar topik trending Indonesia (agregator publik) + tweet teratas", jadwal: "±3 jam" },
  { p: "Netflix", src: "Netflix Tudum — Top 10 resmi Indonesia", jadwal: "harian" },
  { p: "Produk", src: "Kurasi produk terlaris TikTok Shop (data penjualan publik)", jadwal: "harian" }
];

export default function MetodologiPage() {
  return (
    <PageShell
      title="Metodologi"
      subtitle="Dari mana angka-angka di situs ini berasal — dan apa batasnya."
    >
      <h2 className="text-lg font-bold text-ink dark:text-white">
        1. Sumber & jadwal pengumpulan
      </h2>
      <p>
        Sistem {SITE_NAME} mengambil data dari sumber publik tiap platform
        dengan jadwal berkala. Kami menghormati batasan tiap platform dan
        tidak menyalin konten berhak cipta — hanya mencatat judul, peringkat,
        metrik publik, dan tautan ke sumber asli.
      </p>
      <div className="not-prose my-4 overflow-x-auto rounded-2xl border border-gray-200 dark:border-white/10">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-gray-50 text-left dark:bg-white/5">
              <th className="px-4 py-2 font-semibold">Platform</th>
              <th className="px-4 py-2 font-semibold">Sumber</th>
              <th className="px-4 py-2 font-semibold">Jadwal</th>
            </tr>
          </thead>
          <tbody>
            {SOURCES.map((s) => (
              <tr key={s.p} className="border-t border-gray-100 dark:border-white/5">
                <td className="px-4 py-2 font-medium">{s.p}</td>
                <td className="px-4 py-2 text-gray-600 dark:text-gray-300">{s.src}</td>
                <td className="px-4 py-2 text-gray-600 dark:text-gray-300">{s.jadwal}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <h2 className="text-lg font-bold text-ink dark:text-white">
        2. Arsip peringkat — bahan baku analisis kami
      </h2>
      <p>
        Setiap kali pengumpulan berjalan, sistem menyimpan{" "}
        <strong>potret peringkat</strong> (siapa di posisi berapa, dengan
        metrik berapa, pada jam berapa). Dari arsip inilah kami bisa menjawab
        pertanyaan yang tidak dijawab platform mana pun: kapan sebuah topik
        pertama kali muncul, berapa lama ia bertahan, apakah ia menyebar dari
        satu platform ke platform lain, dan apa yang menghilang pekan ini.
        Analisis di bagian{" "}
        <Link href="/artikel" className="text-brand hover:underline">
          Artikel
        </Link>{" "}
        dibangun dari arsip ini.
      </p>

      <h2 className="text-lg font-bold text-ink dark:text-white">
        3. Ringkasan & artikel
      </h2>
      <p>
        Angka dihitung oleh kode dari database; AI membantu menuliskan
        narasinya berdasarkan lembar fakta, lalu redaksi memeriksa sebelum
        terbit. Pembagian kerja lengkapnya ada di{" "}
        <Link href="/kebijakan-editorial" className="text-brand hover:underline">
          Kebijakan Editorial
        </Link>
        .
      </p>

      <h2 className="text-lg font-bold text-ink dark:text-white">
        4. Batasan data — bacalah ini
      </h2>
      <p>
        Kejujuran soal batas lebih penting daripada kesan canggih. Data kami
        adalah <em>potret berkala</em>, bukan siaran langsung: tren yang naik
        dan turun di antara dua pengambilan bisa terlewat. Metrik (penayangan,
        suka, jumlah tweet) adalah angka publik saat pengambilan dan bisa
        berbeda saat kamu membukanya. Daftar Instagram bergantung pada tagar
        yang kami pantau, jadi tidak mencakup semua unggahan populer. Harga
        produk dapat berubah sewaktu-waktu. Bila pengumpulan suatu platform
        terganggu, situs menampilkan data terakhir yang berhasil beserta
        waktunya — bukan data kosong.
      </p>

      <h2 className="text-lg font-bold text-ink dark:text-white">
        5. Pertanyaan?
      </h2>
      <p>
        Kami senang ditanya soal metodologi. Kontak ada di halaman{" "}
        <Link href="/contact" className="text-brand hover:underline">
          Kontak
        </Link>
        .
      </p>
    </PageShell>
  );
}
