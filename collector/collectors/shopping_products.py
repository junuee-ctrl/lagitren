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
import os
import re
from datetime import datetime, timedelta, timezone

import requests

import config
from models import Trend
from .base import make_id

log = logging.getLogger("shopping")

LAST_DEBUG = ""

# products.csv 의 collected_at 이 이보다 오래되면 D1을 덮어쓰지 않는다.
# (로컬 패널 수집이 멈춘 동안 같은 원본을 다시 읽어 '방금 수집'으로 기록하던
#  문제 방지. 기록이 없으면 watchdog 이 _last_ok 로 정지를 감지한다.)
MAX_AGE_HOURS = 48


def _collected_at(rows: list[dict]) -> tuple[str | None, datetime | None]:
    """CSV 의 collected_at (가장 최근 값). 컬럼이 없으면 (None, None)."""
    best: datetime | None = None
    raw: str | None = None
    for row in rows:
        v = _get(row, "collected_at")
        if not v:
            continue
        try:
            d = datetime.fromisoformat(v.replace("Z", "+00:00"))
        except ValueError:
            continue
        if d.tzinfo is None:
            d = d.replace(tzinfo=timezone.utc)
        if best is None or d > best:
            best, raw = d, v
    return raw, best


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


def _load_csv_text() -> tuple[str | None, str]:
    """Sumber produk: Google Sheet (bila SHOPPING_SHEET_CSV diisi) → else file
    lokal repo (collector/products.csv). Kembalikan (teks, sumber)."""
    url = config.SHOPPING_SHEET_CSV
    if url:
        try:
            r = requests.get(
                url, timeout=30, headers={"User-Agent": config.USER_AGENT}
            )
            r.raise_for_status()
            return r.text, "google-sheet"
        except Exception as exc:
            log.error("Shopping: gagal ambil sheet: %s", exc)
            return None, f"gagal ambil sheet: {exc}"
    # Fallback: file lokal yang di-commit di repo.
    local = os.path.join(os.path.dirname(__file__), "..", "products.csv")
    if os.path.exists(local):
        with open(local, encoding="utf-8-sig") as f:
            return f.read(), "products.csv lokal"
    return None, "tidak ada sumber produk (SHOPPING_SHEET_CSV / products.csv)"


def collect() -> list[Trend]:
    global LAST_DEBUG
    text, source = _load_csv_text()
    if not text:
        LAST_DEBUG = source
        log.info("Shopping: %s — dilewati.", LAST_DEBUG)
        return []

    rows = list(csv.DictReader(io.StringIO(text)))

    ts_raw, ts = _collected_at(rows)
    stamp = ""
    if ts is not None:
        age = datetime.now(timezone.utc) - ts
        if age > timedelta(hours=MAX_AGE_HOURS):
            LAST_DEBUG = (
                f"basi: {source} dikumpulkan {ts.isoformat(timespec='minutes')} "
                f"({age.total_seconds() / 3600:.0f} jam > {MAX_AGE_HOURS}) — D1 tidak ditimpa"
            )
            log.warning("Shopping: %s", LAST_DEBUG)
            return []
        stamp = ts.astimezone(timezone.utc).isoformat()
    else:
        log.warning("Shopping: kolom collected_at tidak ada (%s) — waktu sumber tak diketahui.", source)

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
        if stamp:
            # Waktu ASLI pengumpulan, bukan waktu run cloud ini.
            t.collected_at = stamp
        trends.append(t)
        if len(trends) >= 30:
            break

    if not trends:
        LAST_DEBUG = f"sheet terbaca tapi 0 produk valid (cek kolom title & affiliate_url) dari {len(rows)} baris"
        log.warning("Shopping: %s", LAST_DEBUG)
        return []

    trends.sort(key=lambda x: x.rank)
    LAST_DEBUG = f"{len(trends)} produk ({source}; sumber {ts_raw or 'tanpa collected_at'})"
    log.info("Shopping (TikTok Shop): %d produk (%s).", len(trends), source)
    return trends
