import type { Metadata } from "next";
import Link from "next/link";
import { CONTACT_EMAIL, SITE_URL } from "@/lib/site";

export const revalidate = 86400;

export const metadata: Metadata = {
  title: "Indonesia Weekly Trend Intelligence — Laporan Tren untuk Brand & Agensi",
  description:
    "Laporan intelijen tren mingguan dari arsip peringkat 7 platform (Google, YouTube, TikTok, Instagram, X, Netflix, TikTok Shop). Trend Score, kurva daur hidup, dan rekomendasi Fakta → Interpretasi → Rekomendasi. Unduh contoh gratis.",
  alternates: { canonical: "/laporan" },
  openGraph: {
    title: "Indonesia Weekly Trend Intelligence — Lagi Tren Riset",
    description:
      "Arsip peringkat 7 platform, dirangkum jadi laporan intelijen mingguan untuk brand & agensi. Unduh contoh gratis.",
    url: `${SITE_URL}/laporan`,
    images: [{ url: "/og/site", width: 1200, height: 630 }]
  }
};

const ISI = [
  {
    n: "01",
    t: "Ringkasan eksekutif",
    d: "Lima temuan pekan ini, masing-masing dipecah menjadi Fakta → Interpretasi → Rekomendasi, dengan label DO / DON'T / WATCH."
  },
  {
    n: "02",
    t: "Trend Radar",
    d: "Tabel skor 0–100 tiap topik (kecepatan, lintas platform, ketahanan, puncak) plus riwayat peringkat hariannya."
  },
  {
    n: "03",
    t: "Kurva daur hidup & kategori",
    d: "Grafik pergerakan peringkat — naik, memuncak, bertahan, menurun — dan bobot tema pekan ini."
  },
  {
    n: "04",
    t: "Untuk agensi",
    d: "5 tren yang perlu diketahui klien, 3 yang aman diaktifkan, 2 yang sudah jenuh, 1 yang layak dipantau."
  },
  {
    n: "05",
    t: "Trend Alert siap kirim klien",
    d: "Halaman berdiri sendiri berisi alasan, momentum, jendela waktu, dan tindakan — paket Agency bisa memasang logo sendiri."
  },
  {
    n: "06",
    t: "Metodologi & batasan",
    d: "Sumber tiap platform, jadwal pengambilan, dan apa yang TIDAK bisa dijawab data kami."
  }
];

const TIERS = [
  {
    nm: "Gratis",
    price: "Rp0",
    unit: "",
    items: ["Ringkasan mingguan via email", "3 temuan utama", "Tanpa akses arsip"],
    hi: false
  },
  {
    nm: "Pro",
    price: "Rp299.000",
    unit: "/bulan",
    items: [
      "Laporan lengkap PDF tiap pekan",
      "Trend Radar + kurva daur hidup",
      "Akses arsip peringkat 7 platform",
      "1 permintaan kata kunci / bulan",
      "Tahunan Rp2.990.000 (hemat 2 bulan)"
    ],
    hi: true
  },
  {
    nm: "Agency",
    price: "Rp1.490.000",
    unit: "/bulan",
    items: [
      "White-label: logo & warna agensi Anda",
      "Halaman Trend Alert siap kirim ke klien",
      "Semua fitur Pro, hingga 5 pengguna",
      "Pantauan 10 kata kunci / brand",
      "Rekap bulanan + sesi tanya-jawab 30 menit"
    ],
    hi: false
  },
  {
    nm: "Data",
    price: "mulai Rp4,9 jt",
    unit: "/bulan",
    items: ["Ekspor data mentah (CSV)", "Akses API arsip", "Cakupan sesuai kebutuhan"],
    hi: false
  }
];

const FAQ = [
  {
    q: "Apa bedanya dengan Google Trends yang gratis?",
    a: "Google Trends menunjukkan pencarian hari ini dan hanya satu platform. Kami menyimpan potret peringkat tujuh platform setiap kali pengumpulan berjalan, sehingga bisa menjawab sejak kapan sebuah topik naik, berapa lama bertahan, dan apakah ia muncul di platform lain pada waktu yang sama."
  },
  {
    q: "Datanya dari mana?",
    a: "Seluruhnya dari sumber publik resmi tiap platform — RSS Google Trends, YouTube Data API, TikTok Creative Center, Top 10 Netflix (Tudum), dan lainnya. Rincian jadwal dan batasannya kami tulis terbuka di halaman Metodologi."
  },
  {
    q: "Apakah laporannya ditulis AI?",
    a: "Angka dihasilkan pipeline otomatis dari basis data kami sendiri — bukan dikarang model bahasa. Tim redaksi bertanggung jawab atas interpretasi dan rekomendasi, yang dibantu perangkat AI dalam penyusunan draf dan diperiksa sebelum terbit. Kebijakan lengkap ada di halaman Kebijakan Editorial."
  },
  {
    q: "Bisa dikirim ke klien dengan identitas agensi kami?",
    a: "Bisa, di paket Agency. Halaman Trend Alert dan sampul laporan dapat memakai logo dan warna agensi Anda, sehingga bisa diteruskan ke klien apa adanya. Kami sertakan satu edisi ber-logo sebagai contoh sebelum Anda memutuskan."
  },
  {
    q: "Bisa minta pantauan kata kunci khusus brand kami?",
    a: "Bisa, mulai paket Pro (1 kata kunci per bulan) dan lebih luas di paket Agency (10 kata kunci). Kirim daftar kata kuncinya lewat email dan kami masukkan ke laporan berikutnya."
  }
];

export default function LaporanPage() {
  const subject = encodeURIComponent("Langganan Laporan Tren Mingguan");
  const body = encodeURIComponent(
    "Halo Tim Lagitren,\n\nSaya tertarik berlangganan Laporan Tren Mingguan.\n\nNama:\nBrand/Agensi:\nPaket yang diminati:\n\nTerima kasih."
  );

  return (
    <div className="mx-auto max-w-3xl py-4">
      {/* Hero */}
      <section className="relative overflow-hidden rounded-[28px] bg-gradient-to-br from-brand via-accent-grape to-accent px-6 py-10 text-white shadow-xl shadow-brand/20 sm:px-9 sm:py-12">
        <div
          className="pointer-events-none absolute -right-16 -top-16 h-56 w-56 rounded-full bg-white/20 blur-3xl"
          aria-hidden
        />
        <div className="relative">
          <span className="inline-block rounded-full bg-white/20 px-3 py-1 text-xs font-semibold uppercase tracking-widest backdrop-blur">
            Lagi Tren · Riset
          </span>
          <h1 className="mt-4 text-3xl font-extrabold leading-[1.12] tracking-tight sm:text-4xl">
            Apa yang naik, berapa lama bertahan,
            <br />
            dan apa yang harus dilakukan.
          </h1>
          <p className="mt-4 max-w-xl text-sm text-white/90 sm:text-base">
            <b>Indonesia Weekly Trend Intelligence</b> — laporan mingguan untuk brand
            dan agensi, disusun dari arsip peringkat tujuh platform yang kami rekam
            sendiri setiap hari. Tiap topik datang dengan skor, kurva peringkat, dan
            tindakan yang disarankan.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <a
              href="/laporan-contoh.pdf"
              className="inline-flex items-center gap-2 rounded-full bg-white px-5 py-2.5 text-sm font-bold text-brand transition hover:-translate-y-0.5"
            >
              ⬇ Unduh contoh gratis (PDF)
            </a>
            <a
              href={`mailto:${CONTACT_EMAIL}?subject=${subject}&body=${body}`}
              className="inline-flex items-center gap-2 rounded-full bg-white/15 px-5 py-2.5 text-sm font-bold ring-1 ring-white/30 backdrop-blur transition hover:bg-white/25"
            >
              Mulai berlangganan
            </a>
          </div>
          <p className="mt-4 text-xs text-white/75">
            Edisi contoh: 8–14 September 2026 · 9.453 potret peringkat · 7 platform
          </p>
        </div>
      </section>

      {/* Kenapa berbeda */}
      <section className="mt-10">
        <h2 className="text-xl font-extrabold text-ink dark:text-white">
          Kenapa laporan ini berbeda
        </h2>
        <div className="mt-4 grid gap-3 sm:grid-cols-3">
          {[
            {
              t: "Arsip, bukan potret",
              d: "Platform hanya menampilkan daftar hari ini. Kami menyimpan peringkatnya tiap pengumpulan sejak Agustus 2026."
            },
            {
              t: "Tujuh platform sekaligus",
              d: "Pencarian, video, hashtag, percakapan, tontonan, dan belanja — dalam satu tabel yang bisa dibandingkan."
            },
            {
              t: "Skor, bukan kesan",
              d: "Tiap topik diberi Trend Score 0–100 dari kecepatan, ketahanan, dan puncaknya — lalu satu rekomendasi DO / DON'T / WATCH."
            }
          ].map((c) => (
            <div
              key={c.t}
              className="rounded-2xl border border-gray-200 bg-white p-5 dark:border-white/10 dark:bg-night-card"
            >
              <p className="font-bold text-ink dark:text-white">{c.t}</p>
              <p className="mt-1.5 text-sm text-gray-600 dark:text-gray-300">{c.d}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Isi laporan */}
      <section className="mt-10">
        <h2 className="text-xl font-extrabold text-ink dark:text-white">Isi laporan</h2>
        <ul className="mt-4 space-y-3">
          {ISI.map((s) => (
            <li
              key={s.n}
              className="flex gap-4 rounded-2xl border border-gray-200 p-4 dark:border-white/10"
            >
              <span className="text-sm font-extrabold text-brand">{s.n}</span>
              <div>
                <p className="font-bold text-ink dark:text-white">{s.t}</p>
                <p className="mt-1 text-sm text-gray-600 dark:text-gray-300">{s.d}</p>
              </div>
            </li>
          ))}
        </ul>
        <p className="mt-4 text-sm text-gray-500 dark:text-gray-400">
          Ingin melihat bentuk aslinya?{" "}
          <a href="/laporan-contoh.pdf" className="font-semibold text-brand hover:underline">
            Unduh edisi contoh (PDF, 7 halaman)
          </a>{" "}
          — tanpa perlu mendaftar.
        </p>
      </section>

      {/* Berapa waktu yang dihemat */}
      <section className="mt-10 rounded-2xl border border-gray-200 bg-gray-50 p-6 dark:border-white/10 dark:bg-white/5">
        <h2 className="text-xl font-extrabold text-ink dark:text-white">
          Berapa waktu yang dihemat
        </h2>
        <p className="mt-2 text-sm leading-relaxed text-gray-600 dark:text-gray-300">
          Membuka tujuh papan tren satu per satu, mencatat peringkatnya, lalu
          merapikannya menjadi materi rapat memakan beberapa jam kerja strategist
          setiap pekan — dan hasilnya tetap tanpa riwayat, karena platform tidak
          menyimpan peringkat kemarin. Paket Pro menggantikan pekerjaan itu dengan
          satu berkas yang sudah berisi angka, grafik, dan rekomendasi; paket Agency
          menambahkan halaman yang bisa langsung diteruskan ke klien dengan logo Anda.
        </p>
      </section>

      {/* Harga */}
      <section className="mt-10">
        <h2 className="text-xl font-extrabold text-ink dark:text-white">Paket & harga</h2>
        <p className="mt-1.5 text-sm text-gray-500 dark:text-gray-400">
          Dua edisi pertama gratis untuk paket Pro. Tanpa kontrak — berhenti kapan saja.
        </p>
        <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {TIERS.map((t) => (
            <div
              key={t.nm}
              className={
                t.hi
                  ? "rounded-2xl border-2 border-brand bg-brand/5 p-5"
                  : "rounded-2xl border border-gray-200 p-5 dark:border-white/10"
              }
            >
              {t.hi && (
                <span className="mb-2 inline-block rounded-full bg-brand px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide text-white">
                  Paling diminati
                </span>
              )}
              <p className="font-extrabold text-ink dark:text-white">{t.nm}</p>
              <p className="mt-1 text-lg font-extrabold text-brand">
                {t.price}
                <span className="text-xs font-semibold text-gray-400">{t.unit}</span>
              </p>
              <ul className="mt-3 space-y-1.5 text-xs text-gray-600 dark:text-gray-300">
                {t.items.map((i) => (
                  <li key={i} className="flex gap-1.5">
                    <span className="text-accent">✓</span>
                    <span>{i}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
        <p className="mt-3 text-xs text-gray-400">
          Harga belum termasuk pajak bila diperlukan. Pembayaran via transfer bank; faktur tersedia
          untuk paket Agency dan Data.
        </p>
      </section>

      {/* FAQ */}
      <section className="mt-10">
        <h2 className="text-xl font-extrabold text-ink dark:text-white">
          Pertanyaan yang sering muncul
        </h2>
        <div className="mt-4 space-y-3">
          {FAQ.map((f) => (
            <div
              key={f.q}
              className="rounded-2xl border border-gray-200 p-5 dark:border-white/10"
            >
              <p className="font-bold text-ink dark:text-white">{f.q}</p>
              <p className="mt-1.5 text-sm text-gray-600 dark:text-gray-300">{f.a}</p>
            </div>
          ))}
        </div>
        <p className="mt-4 text-sm text-gray-500 dark:text-gray-400">
          Selengkapnya soal cara kami bekerja:{" "}
          <Link href="/metodologi" className="text-brand hover:underline">
            Metodologi
          </Link>{" "}
          ·{" "}
          <Link href="/kebijakan-editorial" className="text-brand hover:underline">
            Kebijakan Editorial
          </Link>
        </p>
      </section>

      {/* CTA */}
      <section className="mt-10 rounded-[28px] bg-gradient-to-br from-brand to-accent-grape px-6 py-9 text-white sm:px-9">
        <h2 className="text-2xl font-extrabold">Mulai dari edisi pekan depan</h2>
        <p className="mt-2 max-w-xl text-sm text-white/90">
          Kirim email berisi nama brand/agensi dan paket yang diminati. Kami balas dengan
          edisi contoh lengkap dan detail pembayaran dalam 1×24 jam kerja.
        </p>
        <a
          href={`mailto:${CONTACT_EMAIL}?subject=${subject}&body=${body}`}
          className="mt-5 inline-flex rounded-full bg-white px-6 py-3 text-sm font-bold text-brand transition hover:-translate-y-0.5"
        >
          {CONTACT_EMAIL}
        </a>
      </section>

      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "FAQPage",
            mainEntity: FAQ.map((f) => ({
              "@type": "Question",
              name: f.q,
              acceptedAnswer: { "@type": "Answer", text: f.a }
            }))
          })
        }}
      />
    </div>
  );
}
