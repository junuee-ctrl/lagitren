"""Jalankan Google Chrome ASLI dengan remote debugging (untuk collector CDP).

Buka Chrome dengan profil khusus 'chrome-lagitren' + port 9222. Login TikTok &
Instagram sekali di jendela ini (login manual = tidak terdeteksi bot). Biarkan
jendela terbuka saat menjalankan `python main.py tiktok instagram`.

  python start_chrome.py

Lalu di .env pastikan:  BROWSER_CDP=http://localhost:9222
"""
import os
import subprocess
import sys

CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "google-chrome",
]

def main() -> None:
    chrome = next((c for c in CANDIDATES if os.path.exists(c)), None)
    if not chrome:
        print("Chrome tidak ditemukan. Pasang Google Chrome dulu, atau edit path di file ini.")
        sys.exit(1)
    profile = os.path.expandvars(r"%USERPROFILE%\chrome-lagitren")
    if os.name != "nt":
        profile = os.path.expanduser("~/chrome-lagitren")
    # Buka 3 tab login sekaligus (TikTok Trends, Instagram, X).
    login_tabs = [
        "https://ads.tiktok.com/creative/creativeCenter/trends/hashtag?region=ID&period=7",
        "https://www.instagram.com/accounts/login/",
        "https://x.com/login",
    ]
    subprocess.Popen(
        [chrome, "--remote-debugging-port=9222", f"--user-data-dir={profile}"]
        + login_tabs
    )
    print("Chrome debug berjalan di port 9222.")
    print("Profil:", profile)
    print(">> Login di KETIGA tab: 1) TikTok Trends  2) Instagram  3) X (Twitter).")
    print(">> Biarkan jendela TERBUKA, lalu di terminal lain jalankan: python run_local.py")


if __name__ == "__main__":
    main()
