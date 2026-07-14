"""Login sekali (TikTok Trends, Instagram, X) — profil 'chrome-lagitren'.

Ini hanyalah pintasan ke `start_chrome.py`, supaya login & crawl memakai
PROFIL YANG SAMA (chrome-lagitren). Menjaga agar sesi login benar-benar
terpakai saat `run_local.py` mengumpulkan data.

Jalankan:
  python login_browser.py     # buka 3 tab login → login di ketiganya
  # biarkan jendela terbuka, di terminal lain:
  python run_local.py
"""
from start_chrome import main

if __name__ == "__main__":
    main()
