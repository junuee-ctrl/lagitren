# Mengaktifkan Google AdSense

Kode iklan sudah tertanam. Setelah punya **ID penerbit** dari AdSense,
iklan aktif otomatis — tidak perlu ubah kode.

## 1. Daftar AdSense
1. Buka https://www.google.com/adsense , daftar dengan situs **lagitren.id**.
2. AdSense memberi **ID penerbit** berbentuk `ca-pub-XXXXXXXXXXXXXXXX`.

## 2. Masukkan ID penerbit ke GitHub
Repo `junuee-ctrl/lagitren` → **Settings → Secrets and variables → Actions →
tab Variables → New repository variable**:
- Name: `ADSENSE_CLIENT`
- Value: `ca-pub-XXXXXXXXXXXXXXXX`

Lalu jalankan ulang deploy (push apa saja, atau Actions → Deploy → Run workflow).
Setelah deploy:
- Script AdSense termuat di `<head>` semua halaman (juga untuk verifikasi situs).
- `https://lagitren.id/ads.txt` otomatis berisi baris penerbit Anda.

## 3. Menampilkan iklan
Dua cara (bisa dipakai bersama):

**a) Auto Ads (paling mudah)** — di dashboard AdSense, aktifkan *Auto ads* untuk
lagitren.id. Google menempatkan iklan otomatis. Cukup langkah 1–2.

**b) Unit iklan manual (kontrol posisi)** — buat *Ad unit* di AdSense, salin
angka **data-ad-slot**, lalu isi ke komponen `<AdSlot adSlot="123..." />` pada
titik yang diinginkan (homepage & halaman detail sudah punya beberapa `<AdSlot>`).

## Catatan
- Persetujuan AdSense butuh konten memadai + halaman About/Contact/Privacy/
  Disclaimer/Affiliate — semuanya sudah ada.
- Sebelum `ADSENSE_CLIENT` diisi, `<AdSlot>` menampilkan placeholder "Ruang Iklan".
