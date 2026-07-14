"""Isi kolom `image` di products.csv dari halaman produk asli.

Tokopedia/TikTok Shop memblokir bot, TAPI browser LOGIN Anda bisa membuka
halaman produk. Skrip ini membuka tiap affiliate_url di Chrome Anda (via CDP),
mengambil og:image (gambar produk resmi), lalu menuliskannya kembali ke
products.csv. Cukup dijalankan sekali (atau saat produk berubah).

Cara pakai (Windows, di folder collector):
  python start_chrome.py        # buka Chrome login + debug port 9222 (sekali)
  python enrich_products.py     # isi gambar ke products.csv
  # lalu commit & push products.csv (atau kirim file-nya)

Baris yang kolom `image`-nya sudah terisi akan dilewati.
"""
from __future__ import annotations

import csv
import os
import sys

os.environ.setdefault("BROWSER_CDP", "http://localhost:9222")

CSV_PATH = os.path.join(os.path.dirname(__file__), "products.csv")


def _extract_image(page) -> str | None:
    # 1) og:image (paling andal).
    for sel in (
        'meta[property="og:image"]',
        'meta[name="og:image"]',
        'meta[property="og:image:url"]',
    ):
        el = page.query_selector(sel)
        if el:
            v = el.get_attribute("content")
            if v and v.startswith("http"):
                return v
    # 2) fallback: gambar produk dari CDN marketplace.
    for sel in (
        'img[src*="images.tokopedia"]',
        'img[src*="tokopedia.net"]',
        'img[src*="tiktokcdn"]',
        'img[src*="ecombdimg"]',
    ):
        el = page.query_selector(sel)
        if el:
            v = el.get_attribute("src")
            if v and v.startswith("http"):
                return v
    return None


def main() -> None:
    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        print("Playwright belum terpasang. Jalankan: pip install playwright")
        sys.exit(1)
    from collectors import _browser

    if not os.path.exists(CSV_PATH):
        print("products.csv tidak ditemukan.")
        sys.exit(1)

    with open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames or []
        rows = list(reader)
    if "image" not in fields:
        fields = list(fields) + ["image"]

    filled = 0
    with sync_playwright() as p:
        ctx = _browser.get_context(p)
        page = ctx.new_page()
        for r in rows:
            if (r.get("image") or "").strip():
                continue
            url = (r.get("affiliate_url") or "").strip()
            if not url:
                continue
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=45000)
                page.wait_for_timeout(3000)
                img = _extract_image(page)
                if img:
                    r["image"] = img
                    filled += 1
                    print(f"OK  {r.get('title','')[:34]:34} -> {img[:60]}")
                else:
                    print(f"--  {r.get('title','')[:34]:34} (gambar tak ditemukan)")
            except Exception as exc:
                print(f"ERR {r.get('title','')[:34]:34} {exc}")
        try:
            page.close()
        except Exception:
            pass
        _browser.close_context(ctx)

    with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"\nSelesai: {filled} gambar diisi. Tersimpan di {CSV_PATH}")
    print("Langkah berikut: commit & push products.csv, atau kirim file-nya.")


if __name__ == "__main__":
    main()
