# Lagi Tren — Aturan Proyek

## Situs
- **lagitren.id** — agregator tren real-time Indonesia.
- Target: pengguna Indonesia 18–40 tahun. Bahasa situs: **Bahasa Indonesia**.
- Platform sumber: Google Trends, YouTube, TikTok, Instagram, Shopee, X (Twitter).
- Tagline: *Rekomendasi, review, dan info terbaru yang lagi tren.*

## Infrastruktur
- **Frontend**: Next.js 14 (App Router) + Tailwind CSS → Cloudflare (via `@opennextjs/cloudflare`).
- **Database**: **Cloudflare D1** (SQLite). Binding `DB` (lihat `wrangler.toml`).
- **Backend (collector)**: Python di PC lokal (Jakarta) → tulis ke D1 via REST API.
- **AI ringkasan**: Ollama lokal (utama) / Claude Haiku (fallback).
- **Repo**: `junuee-ctrl/lagitren`. **Hosting**: Cloudflare (GitHub auto-deploy).
- **Monetisasi**: Google AdSense + Shopee Affiliate.

## Struktur
- `app/` — halaman (home, `[platform]`, halaman legal, `go/shopee/[slug]` redirect afiliasi).
- `components/` — UI (TrendCard, PlatformSection, AISummary, AffiliateBox, dll.).
- `lib/` — `types.ts`, `platforms.ts`, `db.ts` (baca D1 + fallback mock), `mock.ts`, `format.ts`.
- `db/` — `schema.sql`, `seed.sql` untuk D1.
- `collector/` — collector Python (lihat `collector/CLAUDE.md`).

## Aturan Data & Konten
- Ambil dari **data publik** tiap platform; hormati kebijakan & rate limit.
- **Jangan** menyalin konten berhak cipta → cukup ringkasan + tautan ke sumber.
- Setiap kartu tren WAJIB menautkan ke sumber aslinya.

## Aturan Ringkasan AI
- Ditulis dalam **Bahasa Indonesia**, maksimal **3 kalimat**, fokus "kenapa tren".
- **Dilarang**: "100% terbukti", "pasti berhasil", "dijamin aman".
- Bila menyebut produk/harga → sertakan "harga dapat berubah sewaktu-waktu".

## Aturan Teknis
- Data diakses lewat `lib/db.ts`. Bila D1 kosong/tak tersedia → fallback ke `lib/mock.ts`
  supaya situs tetap tampil (dev & preview).
- Warna per platform via `PLATFORMS[...].color` (inline style), bukan kelas dinamis Tailwind.
- ISR: halaman `revalidate = 1800` (30 menit).
- `.env` (collector) disimpan **UTF-8 tanpa BOM**; jangan commit.

## Halaman wajib (syarat AdSense)
About, Contact, Privacy, Disclaimer, Affiliate Disclosure — semuanya sudah ada di `app/`.
