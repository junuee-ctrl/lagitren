import type { Metadata } from "next";
import Link from "next/link";
import PageShell from "@/components/PageShell";
import { CONTACT_EMAIL, SITE_NAME, SITE_URL } from "@/lib/site";

export const metadata: Metadata = {
  title: "Syarat & Ketentuan",
  description:
    "Syarat dan ketentuan penggunaan situs Lagi Tren — hak & kewajiban pengguna, batasan tanggung jawab, dan hak kekayaan intelektual.",
  alternates: { canonical: "/syarat" }
};

export default function SyaratPage() {
  return (
    <PageShell
      title="Syarat & Ketentuan"
      subtitle="Berlaku sejak 18 Agustus 2026. Dengan mengakses situs ini, kamu menyetujui ketentuan di bawah."
    >
      <h2 className="text-lg font-bold text-ink dark:text-white">
        1. Tentang layanan
      </h2>
      <p>
        {SITE_NAME} ({SITE_URL}) adalah situs informasi yang menampilkan data
        tren dari berbagai platform publik beserta analisis dan artikel yang
        kami susun dari arsip data kami sendiri. Layanan disediakan gratis,
        apa adanya (<em>as is</em>), dan dapat berubah sewaktu-waktu tanpa
        pemberitahuan.
      </p>

      <h2 className="text-lg font-bold text-ink dark:text-white">
        2. Akurasi informasi
      </h2>
      <p>
        Data tren (peringkat, jumlah penayangan, harga produk) berasal dari
        data publik platform terkait pada saat pengumpulan dan{" "}
        <strong>dapat berubah sewaktu-waktu</strong>. Kami berupaya menjaga
        akurasi (lihat{" "}
        <Link href="/kebijakan-editorial" className="text-brand hover:underline">
          Kebijakan Editorial
        </Link>
        ), namun tidak menjamin data selalu mutakhir atau bebas galat.
        Informasi di situs ini bukan nasihat finansial, kesehatan, atau hukum.
      </p>

      <h2 className="text-lg font-bold text-ink dark:text-white">
        3. Tautan pihak ketiga & afiliasi
      </h2>
      <p>
        Situs ini memuat tautan ke platform pihak ketiga dan{" "}
        <strong>tautan afiliasi</strong> (mis. TikTok Shop) — kami dapat
        menerima komisi dari pembelian melalui tautan tersebut tanpa biaya
        tambahan bagimu (rincian di halaman{" "}
        <Link href="/affiliate" className="text-brand hover:underline">
          Affiliate Disclosure
        </Link>
        ). Konten, harga, dan ketersediaan di situs pihak ketiga berada di
        luar kendali dan tanggung jawab kami.
      </p>

      <h2 className="text-lg font-bold text-ink dark:text-white">
        4. Kekayaan intelektual
      </h2>
      <p>
        Artikel, analisis, dan kompilasi data yang kami susun dilindungi hak
        cipta {SITE_NAME}. Kamu boleh mengutip sebagian dengan mencantumkan
        sumber dan tautan aktif ke halaman terkait. Merek dagang, logo, dan
        konten platform pihak ketiga adalah milik pemiliknya masing-masing;
        kami hanya menautkan dan meringkas, tidak menyalin konten berhak
        cipta.
      </p>

      <h2 className="text-lg font-bold text-ink dark:text-white">
        5. Penggunaan yang dilarang
      </h2>
      <p>
        Dilarang melakukan scraping massal yang membebani server, menyalin
        ulang konten secara sistematis, atau menggunakan situs ini untuk
        aktivitas melawan hukum. Kami dapat membatasi akses yang melanggar.
      </p>

      <h2 className="text-lg font-bold text-ink dark:text-white">
        6. Batasan tanggung jawab
      </h2>
      <p>
        Sepanjang diizinkan hukum yang berlaku di Indonesia, {SITE_NAME} tidak
        bertanggung jawab atas kerugian yang timbul dari penggunaan atau
        ketidaktersediaan situs, termasuk keputusan yang diambil berdasarkan
        informasi di dalamnya.
      </p>

      <h2 className="text-lg font-bold text-ink dark:text-white">
        7. Perubahan & kontak
      </h2>
      <p>
        Ketentuan ini dapat diperbarui; versi terbaru selalu tersedia di
        halaman ini beserta tanggal berlakunya. Pertanyaan? Hubungi{" "}
        <a href={`mailto:${CONTACT_EMAIL}`} className="text-brand hover:underline">
          {CONTACT_EMAIL}
        </a>
        . Ketentuan ini diatur oleh hukum Republik Indonesia.
      </p>
    </PageShell>
  );
}
