"""Jalankan collector lokal (TikTok & Instagram) sekali — untuk penjadwalan.

Alur:
  1. Bila Chrome debug (port 9222) belum jalan, buka Chrome dgn profil
     'chrome-lagitren' (yang sudah login) di posisi layar tersembunyi.
  2. Jalankan collector tiktok & instagram via CDP.
  3. Tutup Chrome yang tadi dibuka.

Cocok untuk Windows Task Scheduler (lihat LOCAL_COLLECTOR.md).
Login TikTok & Instagram harus sudah tersimpan di profil (jalankan
`python login_browser.py` / `python start_chrome.py` sekali sebelumnya).
"""
import os
import socket
import subprocess
import sys
import time

# Pastikan collector memakai mode CDP.
os.environ.setdefault("BROWSER_CDP", "http://localhost:9222")
# Di lokal (browser login tersedia) → aktifkan pengambilan tweet teratas X.
os.environ.setdefault("TWITTER_WITH_TWEETS", "1")

from start_chrome import CANDIDATES  # noqa: E402

PORT = 9222


def _find_chrome():
    return next((c for c in CANDIDATES if os.path.exists(c)), None)


def _port_open(host: str, port: int) -> bool:
    with socket.socket() as s:
        s.settimeout(1)
        try:
            s.connect((host, port))
            return True
        except OSError:
            return False


def main() -> None:
    profile = os.path.expandvars(r"%USERPROFILE%\chrome-lagitren")
    if os.name != "nt":
        profile = os.path.expanduser("~/chrome-lagitren")

    proc = None
    if not _port_open("127.0.0.1", PORT):
        chrome = _find_chrome()
        if not chrome:
            print("Chrome tidak ditemukan.")
            sys.exit(1)
        proc = subprocess.Popen(
            [
                chrome,
                f"--remote-debugging-port={PORT}",
                f"--user-data-dir={profile}",
                "--window-position=-32000,-32000",  # sembunyikan jendela
                "--window-size=1280,900",
                "--no-first-run",
                "--no-default-browser-check",
            ]
        )
        for _ in range(30):
            if _port_open("127.0.0.1", PORT):
                break
            time.sleep(1)
        time.sleep(2)

    try:
        from main import run

        # X (Twitter) ikut di lokal agar dapat "tweet teratas" (butuh login).
        results = run(["tiktok", "instagram", "twitter"])
        print("Ringkasan:", results)
    finally:
        if proc:
            try:
                proc.terminate()
            except Exception:
                pass


if __name__ == "__main__":
    main()
