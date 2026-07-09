-- Lagi Tren — Data contoh untuk D1 (opsional)
-- Jalankan: wrangler d1 execute lagitren-db --remote --file=./db/seed.sql
-- Berguna untuk menguji tampilan sebelum collector Python berjalan.

DELETE FROM trends;

INSERT INTO trends
  (id, platform, rank, title, subtitle, metric, metric_label, ai_summary, url, thumbnail, source, hashtags, affiliate_url, price, collected_at)
VALUES
  ('google:iphone-16-harga', 'google', 1, 'iPhone 16 harga', '↑ 5000%', 200000, 'pencarian',
   'Apple resmi mengumumkan harga iPhone 16 untuk pasar Indonesia mulai Rp 15 jutaan. Banyak netizen membandingkan dengan Samsung Galaxy S24. Harga dapat berubah sewaktu-waktu.',
   'https://trends.google.co.id/trends/explore?q=iphone%2016%20harga&geo=ID', NULL, 'Google Trends ID',
   '["apple","smartphone","gadget"]', 'https://lagitren.id/go/shopee/iphone-16', 'Mulai Rp 15 juta', '2026-07-09T08:00:00.000Z'),

  ('google:hasil-liga-1', 'google', 2, 'hasil Liga 1', '↑ 2000%', 100000, 'pencarian',
   'Pertandingan Liga 1 akhir pekan ini berakhir dramatis dengan gol di menit akhir. Pendukung ramai mencari skor dan klasemen terbaru.',
   'https://trends.google.co.id/trends/explore?q=hasil%20liga%201&geo=ID', NULL, 'Google Trends ID',
   '["liga1","sepakbola","bola"]', NULL, NULL, '2026-07-09T08:00:00.000Z'),

  ('youtube:demo-video-1', 'youtube', 1, 'Konser Amal Musisi Indonesia — Full Performance', '2.5M views', 2500000, 'views',
   'Video konser amal yang menampilkan sederet musisi papan atas Indonesia ini viral karena momen kolaborasi tak terduga di panggung.',
   'https://www.youtube.com/feed/trending', 'https://images.unsplash.com/photo-1470229722913-7c0e2dbbafd3?w=480&q=70', 'Channel Musik ID',
   '["musik","konser","viral"]', NULL, NULL, '2026-07-09T08:00:00.000Z'),

  ('tiktok:hashtag-jajananviral', 'tiktok', 1, '#JajananViral', '15M views', 15000000, 'views',
   'Tren ini bermula dari kreator yang mereview jajanan kaki lima dengan gaya kocak. Kini banyak pengguna ikut membuat konten serupa.',
   'https://www.tiktok.com/tag/jajananviral', NULL, NULL,
   '["jajananviral","kuliner","fyp"]', NULL, NULL, '2026-07-09T08:00:00.000Z'),

  ('instagram:reels-1', 'instagram', 1, 'Reels wisata tersembunyi di Yogyakarta', '3.4M plays', 3400000, 'plays',
   'Reels yang menampilkan destinasi wisata alam yang belum ramai di Yogyakarta ini banyak dibagikan.',
   'https://www.instagram.com/explore/', NULL, NULL,
   '["wisata","jogja","traveling"]', NULL, NULL, '2026-07-09T08:00:00.000Z'),

  ('shopee:tws-earbuds', 'shopee', 1, 'TWS Earbuds Bluetooth 5.3', '⭐ 4.8 · 10rb+ terjual', 10000, 'terjual',
   'Earbuds nirkabel dengan harga terjangkau ini banyak dicari karena kualitas suara yang dinilai baik di kelasnya. Harga dapat berubah sewaktu-waktu.',
   'https://shopee.co.id/search?keyword=tws%20earbuds', 'https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=480&q=70', NULL,
   '["gadget","audio","earbuds"]', 'https://lagitren.id/go/shopee/tws-earbuds', 'Rp 89.000 – Rp 150.000', '2026-07-09T08:00:00.000Z'),

  ('twitter:timnas', 'twitter', 1, '#Timnas', '125rb tweet', 125000, 'tweet',
   'Warganet ramai membahas performa Timnas Indonesia menjelang laga penting. Tagar ini dipenuhi dukungan dan analisis pertandingan.',
   'https://twitter.com/search?q=%23Timnas', NULL, NULL,
   '["timnas","sepakbola","indonesia"]', NULL, NULL, '2026-07-09T08:00:00.000Z');
