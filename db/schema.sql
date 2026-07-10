-- Lagi Tren — Skema Cloudflare D1
-- Jalankan: wrangler d1 execute lagitren-db --remote --file=./db/schema.sql
--
-- Satu tabel `trends` menyimpan snapshot tren terbaru per platform.
-- Collector Python melakukan UPSERT berdasarkan `id` (platform:slug/source-id),
-- sehingga baris lama tergantikan data terbaru tanpa duplikasi.

CREATE TABLE IF NOT EXISTS trends (
  id            TEXT PRIMARY KEY,          -- mis. "google:iphone-16-harga"
  platform      TEXT NOT NULL,             -- google|youtube|tiktok|instagram|shopee|twitter
  rank          INTEGER NOT NULL DEFAULT 0,-- peringkat dalam platform (1 = teratas)
  title         TEXT NOT NULL,             -- kata kunci / judul / hashtag / nama produk
  subtitle      TEXT,                      -- mis. "↑ 5000%" / "2.5M views"
  metric        INTEGER,                   -- nilai numerik (views, pencarian, dll.)
  metric_label  TEXT,                      -- label metrik ("views", "pencarian", ...)
  ai_summary    TEXT,                      -- ringkasan AI "kenapa lagi tren" (Bahasa Indonesia)
  url           TEXT NOT NULL,             -- tautan ke sumber asli
  thumbnail     TEXT,                      -- URL gambar (opsional)
  source        TEXT,                      -- nama channel/akun (opsional)
  hashtags      TEXT,                      -- JSON array string, mis. '["apple","gadget"]'
  affiliate_url TEXT,                      -- tautan afiliasi (khusus produk)
  price         TEXT,                      -- rentang harga produk (opsional)
  interest      TEXT,                      -- JSON array minat pencarian (khusus Google), mis. '[10,20,100]'
  is_current    INTEGER NOT NULL DEFAULT 1, -- 1 = sedang tren; 0 = arsip (tetap disimpan utk SEO)
  collected_at  TEXT NOT NULL,             -- ISO 8601 waktu pengumpulan
  updated_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Indeks untuk query homepage & halaman detail.
CREATE INDEX IF NOT EXISTS idx_trends_platform_rank
  ON trends (platform, rank);

CREATE INDEX IF NOT EXISTS idx_trends_current
  ON trends (platform, is_current, rank);

CREATE INDEX IF NOT EXISTS idx_trends_updated
  ON trends (updated_at);

CREATE INDEX IF NOT EXISTS idx_trends_collected_at
  ON trends (collected_at);

-- (Opsional) Riwayat pengumpulan untuk pemantauan/telegram & analitik.
CREATE TABLE IF NOT EXISTS collection_runs (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  platform     TEXT NOT NULL,
  status       TEXT NOT NULL,              -- ok | error
  item_count   INTEGER NOT NULL DEFAULT 0,
  message      TEXT,
  started_at   TEXT NOT NULL,
  finished_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_runs_platform_time
  ON collection_runs (platform, finished_at);
