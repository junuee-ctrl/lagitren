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

## 3. Login sekali (TikTok & Instagram)
Keduanya kini butuh sesi login. Login sekali, tersimpan di satu profil browser:
```bash
set BROWSER_HEADFUL=1            # Windows (Mac/Linux: export BROWSER_HEADFUL=1)
python login_browser.py
```
→ Dua tab terbuka (TikTok Creative Center & Instagram). Login di **keduanya**,
lalu tekan Enter di terminal. Sesi tersimpan di folder `.browser_profile`
(jangan di-commit).

## 4. Kumpulkan
```bash
python main.py tiktok
python main.py instagram
# atau sekaligus:
python main.py tiktok instagram
```
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
