import type { Metadata } from "next";
import Link from "next/link";
import PageShell from "@/components/PageShell";
import { CONTACT_EMAIL, SITE_NAME } from "@/lib/site";

export const metadata: Metadata = {
  title: "Kebijakan Editorial",
  description:
    "Bagaimana konten Lagi Tren dibuat: sumber data, peran AI, standar kualitas sebelum terbit, dan prosedur koreksi.",
  alternates: { canonical: "/kebijakan-editorial" }
};

export default function KebijakanEditorialPage() {
  return (
    <PageShell
      title="Kebijakan Editorial"
      subtitle="Standar yang kami pegang untuk setiap konten yang terbit di Lagi Tren."
    >
      <h2 className="text-lg font-bold text-ink dark:text-white">
        1. Prinsip dasar
      </h2>
      <p>
        Semua konten {SITE_NAME} berangkat dari <strong>data yang kami
        kumpulkan sendiri</strong> — arsip tren lintas platform yang kami
        rekam sejak awal 2026. Kami tidak menulis topik yang tidak didukung
        data kami, dan tidak menyalin konten media lain. Bila mengutip berita
        eksternal, kami mencantumkan sumber dan tautannya.
      </p>

      <h2 className="text-lg font-bold text-ink dark:text-white">
        2. Peran AI — transparansi penuh
      </h2>
      <p>
        Kami menggunakan AI dalam produksi konten, dengan pembagian kerja yang
        ketat:
      </p>
      <p>
        <strong>Yang dihitung sistem (bukan AI):</strong> semua angka —
        peringkat, perubahan posisi, lama bertahan di daftar, kemunculan
        lintas platform — dihitung oleh kode dari database kami. AI tidak
        pernah diminta menghasilkan angka, tanggal, atau kutipan.
      </p>
      <p>
        <strong>Yang dikerjakan AI:</strong> menuliskan draf ringkasan dan
        artikel <em>hanya berdasarkan lembar fakta</em> yang disiapkan sistem.
        Instruksi kami eksplisit: informasi di luar lembar fakta tidak boleh
        dipakai; yang tidak diketahui ditulis sebagai &ldquo;data tidak
        tersedia&rdquo;.
      </p>
      <p>
        <strong>Yang dikerjakan redaksi:</strong> memeriksa draf sebelum
        terbit — kesesuaian angka dengan data, ada tidaknya klaim tanpa
        sumber, dan kelayakan baca. Draf yang gagal pemeriksaan tidak
        diterbitkan.
      </p>

      <h2 className="text-lg font-bold text-ink dark:text-white">
        3. Standar sebelum terbit
      </h2>
      <p>
        Artikel harus memuat temuan dari data kami sendiri (bukan sekadar
        menceritakan ulang yang sudah ada di tempat lain), mencantumkan sumber
        eksternal untuk klaim di luar data kami, dan bebas dari kalimat
        berlebihan seperti &ldquo;100% terbukti&rdquo; atau &ldquo;dijamin&rdquo;.
        Penyebutan produk dan harga selalu disertai catatan bahwa harga dapat
        berubah sewaktu-waktu. Klaim tentang orang nyata wajib merujuk sumber
        tepercaya — bila tidak ada, tidak ditulis.
      </p>

      <h2 className="text-lg font-bold text-ink dark:text-white">
        4. Independensi & monetisasi
      </h2>
      <p>
        Situs ini dibiayai iklan dan komisi afiliasi (lihat{" "}
        <Link href="/affiliate" className="text-brand hover:underline">
          Affiliate Disclosure
        </Link>
        ). Pengiklan dan program afiliasi <strong>tidak memengaruhi</strong>{" "}
        isi daftar tren maupun artikel: peringkat produk di halaman Produk
        disusun dari data penjualan publik, bukan bayaran penempatan.
      </p>

      <h2 className="text-lg font-bold text-ink dark:text-white">
        5. Koreksi & pembaruan
      </h2>
      <p>
        Laporan kekeliruan bisa dikirim ke{" "}
        <a href={`mailto:${CONTACT_EMAIL}`} className="text-brand hover:underline">
          {CONTACT_EMAIL}
        </a>
        . Kami meninjau dalam 2×24 jam. Kesalahan substansial diperbaiki
        dengan catatan koreksi pada halaman terkait; kesalahan ketik
        diperbaiki langsung. Setiap halaman tren dan artikel menampilkan waktu
        pembaruan terakhirnya.
      </p>

      <h2 className="text-lg font-bold text-ink dark:text-white">
        6. Rujukan lain
      </h2>
      <p>
        Cara kerja teknis pengumpulan data dijelaskan di halaman{" "}
        <Link href="/metodologi" className="text-brand hover:underline">
          Metodologi
        </Link>
        ; siapa kami di halaman{" "}
        <Link href="/redaksi" className="text-brand hover:underline">
          Redaksi
        </Link>
        .
      </p>
    </PageShell>
  );
}
