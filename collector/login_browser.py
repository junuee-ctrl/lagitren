"""Login sekali untuk TikTok & Instagram (sesi tersimpan di profil browser).

Jalankan (Windows PowerShell/CMD):
  set BROWSER_HEADFUL=1
  python login_browser.py

Dua tab akan terbuka (TikTok Creative Center & Instagram). Login di keduanya,
lalu tekan Enter di terminal. Setelah itu:
  python main.py tiktok instagram
"""
from collectors import _browser

if __name__ == "__main__":
    _browser.login()
