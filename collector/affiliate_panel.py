"""Ambil daftar produk dari panel afiliasi TikTok Shop (Chrome yang sudah login).

Dijalankan di PC lokal, memakai Chrome asli lewat CDP — sama seperti collector
TikTok/Instagram/X. Hasilnya ditulis ke `collector/products.csv`, yang kemudian
dibaca collector `shopping_products` dan dikirim ke D1 pada run yang sama.

Dua mode:

  python affiliate_panel.py --discover "<URL panel>"
      Buka panel, rekam SEMUA respons JSON, lalu tulis laporan ke
      logs/panel_discovery.json + logs/panel_dump/*.json.
      Jalankan ini SEKALI dan kirimkan laporannya — dari situ endpoint
      produk bisa dipastikan, tanpa menebak selector.

  python affiliate_panel.py [--limit 20] [--dry-run]
      Mode normal (butuh PANEL_URL + PANEL_ENDPOINT terisi di bawah).

Prasyarat (sama dgn collector lokal lain):
  BROWSER_CDP=http://127.0.0.1:9222   dan Chrome dijalankan dengan
  --remote-debugging-port=9222 --profile-directory=chrome-lagitren
"""
from __future__ import annotations

import argparse
import csv
import json
import logging
import re
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

import config
from collectors import _browser

logging.basicConfig(level=logging.INFO, format="%(levelname)s [%(name)s] %(message)s")
log = logging.getLogger("panel")

ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / "products.csv"
LOG_DIR = ROOT / "logs"

# Diisi setelah mode --discover memastikan endpointnya.
PANEL_URL = ""
PANEL_ENDPOINT = ""          # potongan URL XHR yang memuat daftar produk
MAX_PRODUCTS = 20

FIELDS = ["rank", "title", "image", "price", "sales", "category",
          "shop", "commission", "commission_rate", "affiliate_url"]

# Kata kunci yang menandai sebuah respons JSON kemungkinan berisi daftar produk.
HINTS = ("product", "item", "commission", "sold", "sale", "gmv", "title")


def _rupiah(v) -> str:
    try:
        return "Rp" + f"{int(round(float(v))):,}".replace(",", ".")
    except Exception:
        return str(v or "")


# ---------------------------------------------------------------- discovery

def discover(url: str, wait_s: int = 25) -> None:
    """Rekam semua respons JSON saat panel dibuka, lalu tulis laporannya."""
    LOG_DIR.mkdir(exist_ok=True)
    dump_dir = LOG_DIR / "panel_dump"
    dump_dir.mkdir(exist_ok=True)
    for old in dump_dir.glob("*.json"):
        old.unlink()

    seen: list[dict] = []

    with sync_playwright() as p:
        ctx = _browser.get_context(p)
        page = ctx.new_page()

        def on_response(resp):
            try:
                ct = (resp.headers or {}).get("content-type", "")
                if "json" not in ct.lower():
                    return
                body = resp.text()
            except Exception:
                return
            if len(body) < 200:
                return
            low = body.lower()
            score = sum(1 for h in HINTS if h in low)
            if score < 3:
                return
            idx = len(seen)
            name = f"{idx:02d}_{re.sub(r'[^a-z0-9]+', '-', resp.url.split('?')[0].lower())[-70:]}.json"
            try:
                (dump_dir / name).write_text(body[:400_000], encoding="utf-8")
            except Exception:
                pass
            seen.append({
                "url": resp.url.split("?")[0],
                "status": resp.status,
                "bytes": len(body),
                "hint_score": score,
                "file": name,
                "sample_keys": _top_keys(body),
            })

        page.on("response", on_response)
        log.info("Membuka %s ...", url)
        page.goto(url, wait_until="load", timeout=60_000)
        # Panel memuat daftar lewat XHR & lazy-scroll — gulirkan beberapa kali.
        for _ in range(6):
            page.mouse.wheel(0, 1800)
            page.wait_for_timeout(1500)
        page.wait_for_timeout(wait_s * 1000 // 6)
        try:
            page.remove_listener("response", on_response)
        except Exception:
            pass
        log.info("URL akhir: %s", page.url)
        _browser.close_context(ctx)

    seen.sort(key=lambda r: (-r["hint_score"], -r["bytes"]))
    report = {"opened": url, "captured": len(seen), "responses": seen[:40]}
    out = LOG_DIR / "panel_discovery.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    log.info("Selesai. %d respons JSON tersimpan.", len(seen))
    log.info("Laporan : %s", out)
    log.info("Isi dump: %s", dump_dir)
    for r in seen[:8]:
        log.info("  skor %d  %7d B  %s", r["hint_score"], r["bytes"], r["url"])


def _top_keys(body: str, limit: int = 14) -> list[str]:
    try:
        data = json.loads(body)
    except Exception:
        return []
    keys: list[str] = []

    def walk(o, depth=0):
        if len(keys) >= limit or depth > 4:
            return
        if isinstance(o, dict):
            for k, v in o.items():
                if k not in keys:
                    keys.append(k)
                walk(v, depth + 1)
        elif isinstance(o, list) and o:
            walk(o[0], depth + 1)

    walk(data)
    return keys[:limit]


# ------------------------------------------------------------------ scrape

def scrape(limit: int = MAX_PRODUCTS) -> list[dict]:
    if not PANEL_URL or not PANEL_ENDPOINT:
        log.error("PANEL_URL/PANEL_ENDPOINT belum diisi — jalankan --discover dulu.")
        sys.exit(2)

    payloads: list[dict] = []
    with sync_playwright() as p:
        ctx = _browser.get_context(p)
        page = ctx.new_page()

        def on_response(resp):
            if PANEL_ENDPOINT not in resp.url:
                return
            try:
                payloads.append(resp.json())
            except Exception:
                pass

        page.on("response", on_response)
        page.goto(PANEL_URL, wait_until="load", timeout=60_000)
        deadline = time.time() + 45
        while time.time() < deadline and _count(payloads) < limit:
            page.mouse.wheel(0, 1800)
            page.wait_for_timeout(1500)
        try:
            page.remove_listener("response", on_response)
        except Exception:
            pass
        _browser.close_context(ctx)

    rows = _parse(payloads, limit)
    if not rows:
        log.error("0 produk terbaca — struktur panel mungkin berubah; jalankan --discover lagi.")
        sys.exit(3)
    return rows


def _count(payloads) -> int:
    return sum(len(_items(p)) for p in payloads)


def _items(payload) -> list[dict]:
    """Cari list-of-dict terpanjang yang tiap elemennya punya judul produk."""
    best: list[dict] = []

    def walk(o, depth=0):
        nonlocal best
        if depth > 6:
            return
        if isinstance(o, list) and o and isinstance(o[0], dict):
            if any(k in o[0] for k in ("title", "product_name", "productName", "name")):
                if len(o) > len(best):
                    best = o
        if isinstance(o, dict):
            for v in o.values():
                walk(v, depth + 1)
        elif isinstance(o, list):
            for v in o[:50]:
                walk(v, depth + 1)

    walk(payload)
    return best


def _pick(d: dict, *keys):
    for k in keys:
        if k in d and d[k] not in (None, ""):
            return d[k]
    return None


def _parse(payloads: list[dict], limit: int) -> list[dict]:
    rows, seen = [], set()
    for payload in payloads:
        for it in _items(payload):
            title = str(_pick(it, "title", "product_name", "productName", "name") or "").strip()
            url = str(_pick(it, "affiliate_url", "share_link", "shareLink", "url", "link") or "").strip()
            if not title or title in seen:
                continue
            seen.add(title)
            rate = _pick(it, "commission_rate", "commissionRate", "rate")
            try:
                rate_pct = f"{round(float(rate) * (100 if float(rate) <= 1 else 1))}%"
            except Exception:
                rate_pct = str(rate or "")
            rows.append({
                "rank": len(rows) + 1,
                "title": title[:92],
                "image": str(_pick(it, "image", "cover", "coverUrl", "thumbnail") or ""),
                "price": _rupiah(_pick(it, "price", "min_price", "sale_price")),
                "sales": str(_pick(it, "sales", "sold_count", "soldCount", "sale_cnt") or ""),
                "category": str(_pick(it, "category", "category_name", "categoryName") or "").lower(),
                "shop": str(_pick(it, "shop", "shop_name", "shopName", "seller") or ""),
                "commission": _rupiah(_pick(it, "commission", "commission_amount", "commissionAmount")),
                "commission_rate": rate_pct,
                "affiliate_url": url,
            })
            if len(rows) >= limit:
                return rows
    return rows


def write_csv(rows: list[dict]) -> None:
    with CSV_PATH.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    log.info("Ditulis %d produk ke %s", len(rows), CSV_PATH)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--discover", metavar="URL", help="rekam respons JSON panel, lalu berhenti")
    ap.add_argument("--limit", type=int, default=MAX_PRODUCTS)
    ap.add_argument("--dry-run", action="store_true", help="tampilkan hasil, jangan tulis CSV")
    a = ap.parse_args()

    if not config.BROWSER_CDP:
        log.error("BROWSER_CDP belum diset di .env — panel butuh Chrome yang sudah login.")
        log.error("Tambahkan baris:  BROWSER_CDP=http://127.0.0.1:9222")
        sys.exit(2)

    if not _browser.cdp_alive():
        log.error("=" * 66)
        log.error("Chrome belum berjalan dengan port debug %s.", _browser.cdp_url())
        log.error("Jalankan start_chrome_cdp.bat (di folder collector), tunggu")
        log.error("jendela Chrome terbuka, pastikan partner.tiktokshop.com sudah")
        log.error("login, lalu ulangi perintah ini. Chrome harus TETAP terbuka.")
        log.error("=" * 66)
        sys.exit(4)

    if a.discover:
        discover(a.discover)
        return

    rows = scrape(a.limit)
    for r in rows:
        log.info("%2d %-9s %8s %4s | %s", r["rank"], r["category"][:9],
                 r["commission"], r["commission_rate"], r["title"][:50])
    missing = [r["rank"] for r in rows if not r["affiliate_url"]]
    if missing:
        log.warning("Baris tanpa tautan afiliasi: %s", missing)
    if a.dry_run:
        log.info("--dry-run: CSV tidak ditulis.")
        return
    write_csv(rows)


if __name__ == "__main__":
    main()
