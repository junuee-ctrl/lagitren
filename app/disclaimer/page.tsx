import type { Metadata } from "next";
import PageShell from "@/components/PageShell";

export const metadata: Metadata = {
  title: "Disclaimer",
  description:
    "Disclaimer Lagi Tren mengenai akurasi data tren dan konten dari platform pihak ketiga.",
  alternates: { canonical: "/disclaimer" }
};

export default function DisclaimerPage() {
  return (
    <PageShell title="Disclaimer" subtitle="Terakhir diperbarui: 9 Juli 2026">
      <p>
        Konten di Lagi Tren (lagitren.id) disusun berdasarkan data publik yang
        tersedia di berbagai platform seperti Google, YouTube, TikTok,
        Instagram, marketplace Indonesia, dan X (Twitter). Kami berupaya
        menyajikan informasi seakurat mungkin, namun{" "}
        <strong>kami tidak menjamin keakuratan, kelengkapan, atau ketepatan
        waktu</strong> dari informasi tersebut.
      </p>
      <p>
        Data tren berubah dengan cepat. Angka, peringkat, harga, dan ringkasan
        yang ditampilkan merupakan gambaran pada saat pengumpulan data dan dapat
        berbeda dengan kondisi terkini di platform sumber. Harga produk{" "}
        <strong>dapat berubah sewaktu-waktu</strong>.
      </p>
      <p>
        Ringkasan &ldquo;kenapa tren&rdquo; dibuat dengan bantuan kecerdasan
        buatan (AI)
        untuk memberikan konteks singkat, dan mungkin mengandung ketidaktepatan.
        Untuk informasi resmi, silakan merujuk langsung ke platform sumber
        melalui tautan yang kami sediakan.
      </p>
      <p>
        Lagi Tren tidak berafiliasi secara resmi dengan Google, YouTube,
        TikTok, Instagram, Shopee, Tokopedia, X, maupun platform lain yang
        disebutkan, kecuali dinyatakan sebagai program afiliasi (lihat halaman{" "}
        <a href="/affiliate" className="text-brand hover:underline">
          Afiliasi
        </a>
        ). Semua merek dagang adalah milik pemiliknya masing-masing.
      </p>
      <p>
        Keputusan apa pun yang Anda ambil berdasarkan informasi di situs ini
        adalah tanggung jawab Anda sendiri. Kami tidak bertanggung jawab atas
        kerugian yang timbul dari penggunaan informasi di situs ini.
      </p>
    </PageShell>
  );
}
