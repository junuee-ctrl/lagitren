"""Collector Produk Afiliasi (TikTok Shop / Tokopedia) via Google Sheet.

Alih-alih API (TikTok Shop tak menyediakan pembuatan tautan afiliasi publik
semudah Shopee), produk dikurasi manual di Google Sheet lalu disinkron
otomatis ke situs. Cukup HTTP fetch CSV — jalan di cloud, tanpa browser.

Cara pakai:
  1. Buat Google Sheet dengan kolom (baris pertama = header):
       title, image, price, sales, category, affiliate_url  (opsional: id, shop, commission)
  2. File → Share → Publish to web → pilih sheet, format CSV → salin URL.
  3. Simpan URL itu ke variable SHOPPING_SHEET_CSV (GitHub Actions Variables).

Kolom minimal wajib: title + affiliate_url. Sisanya opsional.
"""
from __future__ import annotations

import csv
import io
import logging
import re

import requests

import config
from models import Trend
from .base import make_id

log = logging.getLogger("shopping")

LAST_DEBUG = ""


def _num(text: str | None) -> int | None:
    """Parse jumlah terjual: '396.1K'->396100, '1.2jt'->1200000, '12.500'->12500.

    Bila ADA sufiks (K/rb/jt) → titik/koma dianggap DESIMAL (gaya '396.1K').
    Bila TANPA sufiks → titik/koma dianggap pemisah RIBUAN (gaya Indonesia).
    """
    if not text:
        return None
    t = str(text).lower().strip()
    m = re.search(r"([\d.,]+)\s*(k|rb|ribu|m|jt|juta)?", t)
    if not m:
        return None
    numstr, suffix = m.group(1), (m.group(2) or "")
    try:
        if suffix:
            numstr = numstr.replace(",", ".")
            parts = numstr.split(".")
            if len(parts) > 2:  # banyak titik → yang terakhir desimal
                numstr = "".join(parts[:-1]) + "." + parts[-1]
            val = float(numstr)
        else:
            val = float(numstr.replace(".", "").replace(",", ""))
    except ValueError:
        return None
    mult = {
        "k": 1_000, "rb": 1_000, "ribu": 1_000,
        "m": 1_000_000, "jt": 1_000_000, "juta": 1_000_000,
    }.get(suffix, 1)
    return int(val * mult)


def _fmt_sales(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}jt terjual".replace(".0", "")
    if n >= 1_000:
        return f"{n / 1_000:.0f}rb terjual"
    return f"{n} terjual"


def _get(row: dict, *keys: str) -> str:
    for k in keys:
        for rk in row:
            if rk and rk.strip().lower() == k:
                v = (row[rk] or "").strip()
                if v:
                    return v
    return ""


def collect() -> list[Trend]:
    global LAST_DEBUG
    url = config.SHOPPING_SHEET_CSV
    if not url:
        LAST_DEBUG = "SHOPPING_SHEET_CSV belum diisi (link CSV Google Sheet)"
        log.info("Shopping: %s — dilewati.", LAST_DEBUG)
        return []

    try:
        r = requests.get(url, timeout=30, headers={"User-Agent": config.USER_AGENT})
        r.raise_for_status()
        text = r.text
    except Exception as exc:
        LAST_DEBUG = f"gagal ambil sheet: {exc}"
        log.error("Shopping: %s", LAST_DEBUG)
        return []

    rows = list(csv.DictReader(io.StringIO(text)))
    trends: list[Trend] = []
    for i, row in enumerate(rows, start=1):
        title = _get(row, "title", "nama", "product", "produk")
        link = _get(row, "affiliate_url", "link", "url", "tautan")
        if not title or not link:
            continue

        image = _get(row, "image", "img", "gambar", "thumbnail") or None
        price_txt = _get(row, "price", "harga")
        category = _get(row, "category", "kategori")
        shop = _get(row, "shop", "toko", "store") or None
        rank_txt = _get(row, "rank", "peringkat")
        pid = _get(row, "id", "item_id", "product_id")
        sales = _num(_get(row, "sales", "monthly_sales", "terjual", "penjualan"))

        try:
            rank = int(rank_txt) if rank_txt else i
        except ValueError:
            rank = i

        subtitle = _fmt_sales(sales) if sales else None

        t = Trend(
            id=make_id("shopee", pid or title),
            platform="shopee",
            rank=rank,
            title=title,
            url=link,
            subtitle=subtitle,
            metric=sales,
            metric_label="terjual" if sales else None,
            thumbnail=image,
            source=shop,
            price=price_txt or None,
            affiliate_url=link,
            hashtags=[category.lower()] if category else [],
        )
        # Konteks AI ("kenapa diminati").
        bits = [f"Produk: {title}"]
        if price_txt:
            bits.append(f"harga {price_txt}")
        if sales:
            bits.append(f"{sales} terjual")
        if category:
            bits.append(f"kategori {category}")
        t.__dict__["_context"] = ", ".join(bits)
        trends.append(t)
        if len(trends) >= 30:
            break

    if not trends:
        LAST_DEBUG = f"sheet terbaca tapi 0 produk valid (cek kolom title & affiliate_url) dari {len(rows)} baris"
        log.warning("Shopping: %s", LAST_DEBUG)
        return []

    trends.sort(key=lambda x: x.rank)
    LAST_DEBUG = f"{len(trends)} produk dari Google Sheet"
    log.info("Shopping (TikTok Shop): %d produk.", len(trends))
    return trends
