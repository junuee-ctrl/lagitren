# Collector Lokal (TikTok & Instagram) — PC di Jakarta

TikTok & Instagram memblokir akses otomatis dari server cloud (butuh tanda
tangan / login). Solusinya: jalankan collector di **PC lokal** (IP rumah +
browser sungguhan via Playwright). Data ditulis ke D1 yang sama, sehingga
muncul di situs bersama Google/YouTube/X.

> Google/YouTube/X tetap dikumpulkan otomatis di cloud (GitHub Actions).
> Yang perlu dijalankan lokal hanya **tiktok** dan **instagram**.

## 1. Pasang (sekali)
```bash
cd collector
python -m venv .venv
.venv\Scripts\activate            # Windows (Mac/Linux: source .venv/bin/activate)
pip install -r requirements-local.txt
playwright install chromium
```

## 2. Konfigurasi `.env`
Salin `.env.example` → `.env`, isi minimal (agar bisa menulis ke D1):
```
CLOUDFLARE_ACCOUNT_ID=...
CLOUDFLARE_D1_DATABASE_ID=...       # id database lagitren-db
CLOUDFLARE_API_TOKEN=...            # token dengan izin D1 Edit
GEO=ID
```
(ID database bisa dilihat: `npx wrangler d1 list`.)

## 3. TikTok — langsung jalan
```bash
python main.py tiktok
```
Browser headless membuka TikTok Creative Center, menangkap data hashtag
trending Indonesia, lalu menyimpannya ke D1.

## 4. Instagram — login sekali dulu
Instagram butuh sesi login. Jalankan sekali dengan jendela terlihat:
```bash
set BROWSER_HEADFUL=1                # Windows (Mac/Linux: export BROWSER_HEADFUL=1)
python -c "from collectors import instagram_trending as ig; ig.login()"
```
→ Login Instagram di jendela yang terbuka, lalu tekan Enter di terminal.
Sesi tersimpan di folder `.ig_profile` (jangan di-commit).

Setelah itu:
```bash
python main.py instagram
```
Hashtag yang dipantau diatur lewat `IG_HASHTAGS` di `.env`
(default: `viral,fyp,indonesia,beritaterkini,tiktok`).

## 5. Otomatis berkala (opsional)
- **Windows Task Scheduler**: buat task menjalankan
  `...\.venv\Scripts\python.exe main.py tiktok instagram` tiap 3–6 jam.
- Atau biarkan `python scheduler.py` berjalan (menjadwalkan semua platform;
  di PC lokal ini termasuk tiktok & instagram).

## Catatan
- Ini metode tidak resmi & bisa berubah bila TikTok/Instagram mengubah situsnya.
  Bila hasil kosong, cek pesan debug di `https://lagitren.id/api/collect-debug`.
- Jangan commit `.env` dan folder `.ig_profile`.
