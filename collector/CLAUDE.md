# Lagi Tren — Collector (Python)

Collector berjalan di **PC lokal (Jakarta)**, mengumpulkan tren, membuat
ringkasan AI, lalu menulis ke **Cloudflare D1** via REST API.

## Menjalankan
```bash
cd collector
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # lalu isi nilainya (UTF-8 tanpa BOM!)

python main.py                # semua platform, sekali jalan
python main.py google         # satu platform
python main.py google --no-ai # tanpa ringkasan AI
DRY_RUN=1 python main.py google   # tanpa menulis ke D1 (uji coba)

python scheduler.py           # jalankan terjadwal (berkala) terus-menerus
```

## Struktur
- `collectors/` — satu modul per platform, tiap modul: `collect() -> list[Trend]`.
  - `google_trends.py` — **aktif** (RSS Google Trends, tanpa API key).
  - `youtube_trending.py` — **aktif** (butuh `YOUTUBE_API_KEY`).
  - `tiktok/instagram/shopee/twitter` — stub (prioritas minggu ke-3).
- `summarizer/` — `ai_summary.py` (Ollama→Claude), `prompts.py` (prompt Bahasa Indonesia).
- `database/db_client.py` — klien D1 (upsert + prune + log run).
- `notifier/telegram_bot.py` — notifikasi status.
- `main.py` — pipeline. `scheduler.py` — penjadwalan.
- `models.py` — dataclass `Trend` (memetakan tabel D1 `trends`).

## Menambah collector baru
1. Buat `collectors/<nama>.py` dengan fungsi `collect() -> list[Trend]`.
2. Gunakan `make_id("<platform>", <kunci-unik>)` agar UPSERT stabil.
3. (Opsional) simpan konteks untuk AI di `trend.__dict__["_context"] = "..."`.
4. Daftarkan di `collectors/__init__.py` → `REGISTRY`.

## Aturan
- Hormati rate limit & kebijakan tiap platform.
- Jangan menyalin konten berhak cipta — ringkasan + tautan saja.
- `.env` UTF-8 tanpa BOM, jangan pernah di-commit.
- Ringkasan AI: Bahasa Indonesia, maksimal 3 kalimat, hindari klaim berlebihan.
