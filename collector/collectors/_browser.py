"""Helper browser bersama (Playwright) untuk collector lokal TikTok & Instagram.

Satu profil persisten menyimpan login kedua situs sekaligus.
"""
from __future__ import annotations

import logging

import config

log = logging.getLogger("browser")

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)


def persistent_context(p, headful: bool | None = None):
    """Buka context browser persisten (menyimpan cookie/login antar-run).

    Pakai Google Chrome asli (channel="chrome") bila terpasang — jauh lebih
    kecil kemungkinan dideteksi sebagai bot dibanding Chromium bawaan.
    """
    if headful is None:
        headful = config.BROWSER_HEADFUL
    common = dict(
        user_data_dir=config.BROWSER_PROFILE_DIR,
        headless=not headful,
        locale="id-ID",
        viewport={"width": 1360, "height": 900},
        args=["--disable-blink-features=AutomationControlled"],
    )
    # UA hanya di-set untuk Chromium; dgn channel chrome biarkan UA asli.
    try:
        return p.chromium.launch_persistent_context(channel="chrome", **common)
    except Exception as exc:
        log.info("Chrome asli tidak tersedia (%s), pakai Chromium.", exc)
        return p.chromium.launch_persistent_context(user_agent=UA, **common)


def accept_cookies(page) -> None:
    """Klik tombol persetujuan cookie bila ada (berbagai variasi teks)."""
    labels = [
        "Allow all", "Accept all", "Accept all cookies", "Izinkan semua",
        "Terima semua", "I Agree", "Agree", "Setuju",
    ]
    for lab in labels:
        try:
            btn = page.get_by_role("button", name=lab, exact=False)
            if btn and btn.count() > 0:
                btn.first.click(timeout=2500)
                page.wait_for_timeout(800)
                return
        except Exception:
            continue


def login() -> None:
    """Buka browser tampak untuk login TikTok & Instagram sekali.

    Jalankan:
      set BROWSER_HEADFUL=1   (Windows)
      python login_browser.py
    """
    from playwright.sync_api import sync_playwright  # type: ignore

    with sync_playwright() as p:
        ctx = persistent_context(p, headful=True)
        tt = ctx.new_page()
        tt.goto(
            "https://ads.tiktok.com/business/creativecenter/inspiration/popular/"
            "hashtag/pc/en?region=ID",
            timeout=60000,
        )
        ig = ctx.new_page()
        ig.goto("https://www.instagram.com/accounts/login/", timeout=60000)
        print(
            "\n>> Login di KEDUA tab yang terbuka:\n"
            "   1) Tab TikTok Creative Center (klik 'Log in or sign up')\n"
            "   2) Tab Instagram\n"
            ">> Setelah selesai login keduanya, tekan Enter di sini untuk menyimpan sesi."
        )
        try:
            input()
        except EOFError:
            tt.wait_for_timeout(120000)
        ctx.close()
        print(">> Sesi tersimpan. Sekarang bisa jalankan: python main.py tiktok instagram")
