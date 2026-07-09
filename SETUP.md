# Setup Deploy Otomatis (sekali saja)

Setelah langkah ini, **setiap push ke `main` otomatis**: build → buat/migrasi
D1 → deploy ke Cloudflare. Tidak perlu perintah manual lagi.

## 1. Buat Cloudflare API Token

Cloudflare Dashboard → **My Profile → API Tokens → Create Token → Create Custom Token**.

Beri izin berikut (minimal):

| Tipe | Item | Izin |
|---|---|---|
| Account | **Workers Scripts** | Edit |
| Account | **D1** | Edit |
| Account | **Account Settings** | Read |
| Zone (opsional, untuk domain) | **Workers Routes** | Edit |

Salin token yang muncul (hanya tampil sekali).

Catat juga **Account ID** (Dashboard → sidebar akun, atau halaman Workers).

## 2. Tambahkan Secret di GitHub

Repo `junuee-ctrl/lagitren` → **Settings → Secrets and variables → Actions → New repository secret**. Tambahkan dua:

- `CLOUDFLARE_API_TOKEN` = token dari langkah 1
- `CLOUDFLARE_ACCOUNT_ID` = Account ID Anda

## 3. Jalankan deploy pertama

Buka tab **Actions** di repo → workflow **"Deploy ke Cloudflare"** → **Run workflow**
(atau cukup push commit apa pun ke `main`).

Workflow akan:
1. Membuat database D1 `lagitren-db` bila belum ada, dan mengisi `database_id`
   ke `wrangler.toml` secara otomatis.
2. Menerapkan skema (`db/schema.sql`).
3. Build OpenNext + `wrangler deploy`.

Setelah sukses, situs live di URL `*.workers.dev` (lihat log step Deploy).

## 4. Hubungkan domain lagitren.id (sekali, di dashboard)

Cloudflare Dashboard → **Workers & Pages → lagitren → Settings → Domains & Routes
→ Add → Custom domain** → `lagitren.id` (dan `www.lagitren.id`).
Karena DNS sudah di Cloudflare, sertifikat SSL otomatis.

## 5. Isi data

- Data awal memakai mock (situs langsung tampil).
- Untuk data nyata: jalankan collector di PC lokal (lihat `collector/CLAUDE.md`).
  Isi `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_D1_DATABASE_ID`, `CLOUDFLARE_API_TOKEN`
  di `collector/.env`, lalu `python main.py`.

---
Setelah setup ini selesai, alur pengembangan: **ubah kode → push → live otomatis.**
