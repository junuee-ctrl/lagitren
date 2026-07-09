import type { Metadata } from "next";
import PageShell from "@/components/PageShell";

export const metadata: Metadata = {
  title: "Pengungkapan Afiliasi",
  description:
    "Pengungkapan afiliasi Lagi Tren: beberapa tautan produk adalah tautan afiliasi.",
  alternates: { canonical: "/affiliate" }
};

export default function AffiliatePage() {
  return (
    <PageShell
      title="Pengungkapan Afiliasi"
      subtitle="Transparansi soal tautan afiliasi di Lagi Tren."
    >
      <p>
        Beberapa tautan di situs ini adalah <strong>tautan afiliasi</strong>.
        Artinya, kami dapat menerima komisi jika Anda membeli produk melalui
        tautan tersebut, <strong>tanpa biaya tambahan bagi Anda</strong>. Harga
        yang Anda bayar tetap sama.
      </p>
      <p>
        Komisi ini membantu kami menjaga Lagi Tren tetap gratis dan terus
        memperbarui data tren dari berbagai platform. Kami hanya menautkan
        produk yang relevan dengan tren yang sedang ramai, dan keputusan
        pembelian sepenuhnya ada di tangan Anda.
      </p>
      <p>
        Kami dapat berpartisipasi dalam program afiliasi seperti Shopee
        Affiliate, Lazada, dan sejenisnya. Tautan afiliasi biasanya ditandai
        dengan tombol seperti &ldquo;Cek Harga di Shopee&rdquo; atau keterangan
        bahwa itu adalah tautan afiliasi.
      </p>
      <p>
        Perlu diingat bahwa <strong>harga dan ketersediaan produk dapat berubah
        sewaktu-waktu</strong>. Selalu periksa detail produk, harga, dan ulasan
        di platform tujuan sebelum melakukan pembelian.
      </p>
      <p>
        Ada pertanyaan tentang afiliasi atau kerja sama? Hubungi kami di{" "}
        <a href="mailto:halo@lagitren.id" className="text-brand hover:underline">
          halo@lagitren.id
        </a>
        .
      </p>
    </PageShell>
  );
}
