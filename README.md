# 🔥 Lagi Tren

**Apa yang lagi tren di Indonesia, cukup lihat satu situs.**

[lagitren.id](https://lagitren.id) mengumpulkan tren real-time dari Google
Trends, YouTube, TikTok, Instagram, Shopee, dan X (Twitter) di Indonesia,
lengkap dengan ringkasan AI berbahasa Indonesia yang menjelaskan **kenapa**
sesuatu sedang viral.

---

## Arsitektur

```
Collector Python (PC lokal, Jakarta)          Frontend (Cloudflare)
┌──────────────────────────────┐              ┌─────────────────────────┐
│ collectors/*  →  ringkasan AI │   REST API   │ Next.js (App Router)    │
│ (Ollama/Claude)               │ ───────────▶ │ baca D1 → render ISR    │
│         │                     │   tulis D1   │ AdSense + Affiliate     │
│         ▼                     │              └─────────────────────────┘
│  Cloudflare D1 (SQLite)  ◀────┼──────────────────────┘
└──────────────────────────────┘
```

- **Frontend**: Next.js 14 + Tailwind, dijalankan di Cloudflare via
  `@opennextjs/cloudflare`. Membaca tren dari D1; fallback ke data mock bila
  D1 kosong sehingga situs selalu tampil.
- **Collector**: skrip Python terjadwal di PC lokal. Lihat [`collector/`](./collector).
- **Database**: Cloudflare D1 (gratis, 5GB).

## Struktur repo

| Path | Isi |
|---|---|
| `app/` | Halaman: home, `[platform]`, legal (About/Contact/Privacy/Disclaimer/Affiliate), redirect afiliasi `go/shopee/[slug]`, sitemap & robots |
| `components/` | UI: `TrendCard`, `PlatformSection`, `AISummary`, `AffiliateBox`, `Header`, `Footer`, `AdSlot` |
| `lib/` | `types.ts`, `platforms.ts`, `db.ts` (D1 + fallback mock), `mock.ts`, `format.ts` |
| `db/` | `schema.sql`, `seed.sql` untuk Cloudflare D1 |
| `collector/` | Collector Python (Google/YouTube aktif; sisanya stub) |

## Mulai (frontend)

```bash
npm install
npm run dev          # http://localhost:3000 (pakai data mock)
npm run build        # build produksi Next.js
```

## Setup Cloudflare D1

```bash
# 1) Buat database (sekali)
npx wrangler d1 create lagitren-db
#    → tempel `database_id` yang muncul ke wrangler.toml

# 2) Terapkan skema
npm run db:migrate:remote
#    (opsional) data contoh:
npm run db:seed:remote
```

## Deploy ke Cloudflare

```bash
npm run cf:build     # bangun output OpenNext
npm run cf:preview   # pratinjau lokal di runtime workerd
npm run cf:deploy    # deploy ke Cloudflare
```

**Auto-deploy dari GitHub:** hubungkan repo `junuee-ctrl/lagitren` di dashboard
Cloudflare (Workers/Pages) dengan:
- Build command: `npm run cf:build`
- Deploy command / output: sesuai `@opennextjs/cloudflare` (`.open-next`)
- Tambahkan binding **D1** `DB → lagitren-db` dan variabel `NEXT_PUBLIC_SITE_URL`.

## Collector

Lihat [`collector/CLAUDE.md`](./collector/CLAUDE.md). Ringkas:

```bash
cd collector
pip install -r requirements.txt
cp .env.example .env      # isi kredensial (UTF-8 tanpa BOM)
python main.py            # kumpulkan semua platform sekali
python scheduler.py       # jalankan terjadwal
```

## Status

| Bagian | Status |
|---|---|
| Frontend (home, platform, legal, SEO) | ✅ |
| Skema D1 + klien baca (fallback mock) | ✅ |
| Collector Google Trends | ✅ (RSS) |
| Collector YouTube | ✅ (Data API) |
| Ringkasan AI (Ollama/Claude) | ✅ |
| Notifikasi Telegram | ✅ |
| Collector TikTok/Instagram/Shopee/X | 🔧 stub (minggu ke-3) |
| AdSense (slot placeholder siap) | 🔧 menunggu persetujuan |

---
© 2026 Lagi Tren.
