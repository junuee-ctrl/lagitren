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

## 3. Login sekali (TikTok Trends, Instagram, X)
Semua butuh sesi login. Login sekali; tersimpan di profil `chrome-lagitren`
(PROFIL YANG SAMA dipakai saat crawl → login pasti terpakai):
```bash
python start_chrome.py        # (sama: python login_browser.py)
```
→ Tiga tab terbuka: **TikTok Trends**, **Instagram**, **X**. Login di ketiganya.
Untuk TikTok, login penuh membuka daftar 20 hashtag (tanpa login hanya ~3).
Biarkan jendela TERBUKA lalu lanjut ke langkah 4 (terminal lain).

## 4. Kumpulkan (satu perintah)
```bash
python run_local.py           # tiktok + instagram + x sekaligus, via profil login
```
Atau per-platform: `python main.py tiktok` / `instagram` / `twitter`.
Hashtag Instagram yang dipantau diatur lewat `IG_HASHTAGS` di `.env`
(default: `viral,fyp,indonesia,beritaterkini,tiktok`).

## 5. Otomatis berkala (Windows Task Scheduler)
Gunakan `run_local.py` — ia membuka Chrome (profil yang sudah login) secara
tersembunyi, mengumpulkan tiktok+instagram, lalu menutup Chrome. Jadi tidak
perlu menjaga jendela Chrome tetap terbuka.

Uji dulu manual:
```powershell
cd C:\lagitren\collector
python run_local.py
```

Bila berhasil, jadwalkan tiap 3 jam (jalankan PowerShell sebagai biasa):
```powershell
schtasks /Create /SC HOURLY /MO 3 /TN "LagiTrenCollect" ^
  /TR "cmd /c cd /d C:\lagitren\collector && python run_local.py >> collect.log 2>&1" /F
```
- Ubah `/MO 3` untuk interval jam yang berbeda.
- Hapus/lihat: `schtasks /Delete /TN LagiTrenCollect /F` · `schtasks /Query /TN LagiTrenCollect`
- PC harus menyala saat jadwal berjalan. Login TikTok/Instagram tersimpan di
  profil `%USERPROFILE%\chrome-lagitren` (login sekali via `start_chrome.py`).
- Log tiap run tersimpan di `collect.log`.

## Catatan
- Ini metode tidak resmi & bisa berubah bila TikTok/Instagram mengubah situsnya.
  Bila hasil kosong, cek pesan debug di `https://lagitren.id/api/collect-debug`.
- Jangan commit `.env` dan folder `.ig_profile`.
