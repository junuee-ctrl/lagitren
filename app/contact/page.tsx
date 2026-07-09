import type { Metadata } from "next";
import PageShell from "@/components/PageShell";

export const metadata: Metadata = {
  title: "Kontak",
  description: "Hubungi tim Lagi Tren untuk pertanyaan, masukan, atau kerja sama.",
  alternates: { canonical: "/contact" }
};

const CONTACT_EMAIL = "halo@lagitren.id";

export default function ContactPage() {
  return (
    <PageShell
      title="Kontak"
      subtitle="Punya pertanyaan, masukan, atau tawaran kerja sama? Kami senang mendengarnya."
    >
      <p>
        Cara tercepat menghubungi kami adalah melalui email di{" "}
        <a
          href={`mailto:${CONTACT_EMAIL}`}
          className="font-semibold text-brand hover:underline"
        >
          {CONTACT_EMAIL}
        </a>
        . Kami berusaha membalas dalam 1–3 hari kerja.
      </p>

      <form
        action={`mailto:${CONTACT_EMAIL}`}
        method="post"
        encType="text/plain"
        className="not-prose space-y-4 rounded-2xl border border-gray-200 bg-white p-5"
      >
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-ink">
            Nama
          </label>
          <input
            id="name"
            name="Nama"
            type="text"
            required
            className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-brand focus:outline-none focus:ring-2 focus:ring-brand/30"
            placeholder="Nama Anda"
          />
        </div>
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-ink">
            Email
          </label>
          <input
            id="email"
            name="Email"
            type="email"
            required
            className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-brand focus:outline-none focus:ring-2 focus:ring-brand/30"
            placeholder="email@contoh.com"
          />
        </div>
        <div>
          <label
            htmlFor="subject"
            className="block text-sm font-medium text-ink"
          >
            Subjek
          </label>
          <input
            id="subject"
            name="Subjek"
            type="text"
            className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-brand focus:outline-none focus:ring-2 focus:ring-brand/30"
            placeholder="Topik pesan"
          />
        </div>
        <div>
          <label
            htmlFor="message"
            className="block text-sm font-medium text-ink"
          >
            Pesan
          </label>
          <textarea
            id="message"
            name="Pesan"
            rows={5}
            required
            className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-brand focus:outline-none focus:ring-2 focus:ring-brand/30"
            placeholder="Tulis pesan Anda di sini..."
          />
        </div>
        <button type="submit" className="btn-brand w-full sm:w-auto">
          Kirim Pesan
        </button>
        <p className="text-xs text-gray-400">
          Tombol di atas akan membuka aplikasi email Anda. Anda juga bisa
          langsung menulis ke {CONTACT_EMAIL}.
        </p>
      </form>
    </PageShell>
  );
}
