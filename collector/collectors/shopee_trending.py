"""Collector Produk Lagi Dicari — Shopee Affiliate Open API (resmi).

Memakai API afiliasi resmi Shopee (GraphQL) sehingga:
  - data produk sah (nama, harga, gambar, jumlah terjual, rating), dan
  - `offerLink` sudah berupa TAUTAN AFILIASI yang bisa menghasilkan komisi
    (terikat ke App ID afiliasi Anda) — tidak perlu generateShortLink lagi.

Butuh kredensial (daftar di Shopee Affiliate Open Platform):
  SHOPEE_APP_ID, SHOPEE_APP_SECRET

Tanpa kredensial → collector melewati diri (kembalikan []), situs tetap jalan.

Tanda tangan permintaan:
  Authorization: SHA256 Credential={AppId}, Timestamp={ts}, Signature={sign}
  sign = sha256_hex(AppId + Timestamp + Payload + Secret)
  (Payload = string JSON body PERSIS seperti yang dikirim.)
"""
from __future__ import annotations

import hashlib
import json
import logging
import time

import requests

import config
from models import Trend
from .base import make_id

log = logging.getLogger("shopee")

# Diagnostik terakhir (dibaca main.py bila 0 item).
LAST_DEBUG = ""

_QUERY = """
query productOfferV2($keyword: String, $limit: Int, $page: Int, $sortType: Int) {
  productOfferV2(keyword: $keyword, limit: $limit, page: $page, sortType: $sortType) {
    nodes {
      itemId
      productName
      priceMin
      priceMax
      sales
      imageUrl
      offerLink
      productLink
      shopName
      ratingStar
      priceDiscountRate
      commissionRate
    }
  }
}
""".strip()


def _endpoint() -> str:
    return config.SHOPEE_ENDPOINT or "https://open-api.affiliate.shopee.co.id/graphql"


def _headers(payload: str) -> dict:
    ts = int(time.time())
    base = f"{config.SHOPEE_APP_ID}{ts}{payload}{config.SHOPEE_APP_SECRET}"
    sign = hashlib.sha256(base.encode("utf-8")).hexdigest()
    return {
        "Content-Type": "application/json",
        "Authorization": (
            f"SHA256 Credential={config.SHOPEE_APP_ID}, "
            f"Timestamp={ts}, Signature={sign}"
        ),
    }


def _post(keyword: str, limit: int) -> list[dict]:
    """Satu panggilan productOfferV2 untuk satu kata kunci."""
    body = {
        "query": _QUERY,
        "variables": {
            "keyword": keyword,
            "limit": limit,
            "page": 1,
            # 2 = urut berdasarkan penjualan (paling laris) pada skema afiliasi.
            "sortType": 2,
        },
    }
    # PENTING: tanda tangani string JSON yang PERSIS dikirim.
    payload = json.dumps(body, ensure_ascii=False, separators=(",", ":"))
    resp = requests.post(
        _endpoint(), data=payload.encode("utf-8"), headers=_headers(payload), timeout=30
    )
    if resp.status_code != 200:
        raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:200]}")
    data = resp.json()
    if data.get("errors"):
        raise RuntimeError(f"GraphQL error: {str(data['errors'])[:200]}")
    return (data.get("data", {}).get("productOfferV2", {}) or {}).get("nodes", []) or []


def _fmt_price(pmin: str | None, pmax: str | None) -> str | None:
    def num(v):
        try:
            return int(round(float(v)))
        except (TypeError, ValueError):
            return None

    a, b = num(pmin), num(pmax)
    if a is None and b is None:
        return None
    if a is not None and b is not None and a != b:
        return f"Rp {a:,.0f} – Rp {b:,.0f}".replace(",", ".")
    v = a if a is not None else b
    return f"Rp {v:,.0f}".replace(",", ".")


def collect() -> list[Trend]:
    global LAST_DEBUG
    if not (config.SHOPEE_APP_ID and config.SHOPEE_APP_SECRET):
        LAST_DEBUG = "kredensial Shopee (SHOPEE_APP_ID/SECRET) belum diisi"
        log.info("Shopee: %s — dilewati.", LAST_DEBUG)
        return []

    seen: dict[str, dict] = {}
    errors: list[str] = []
    for kw in config.SHOPEE_KEYWORDS:
        try:
            nodes = _post(kw, limit=8)
            for n in nodes:
                iid = str(n.get("itemId") or "")
                name = (n.get("productName") or "").strip()
                offer = (n.get("offerLink") or "").strip()
                if not iid or not name or not offer:
                    continue
                # Simpan yang penjualannya tertinggi bila duplikat antar kata kunci.
                prev = seen.get(iid)
                if prev is None or (n.get("sales") or 0) > (prev.get("sales") or 0):
                    seen[iid] = n
        except Exception as exc:
            errors.append(f"{kw}: {exc}")
            log.info("Shopee '%s' gagal: %s", kw, exc)
        time.sleep(0.4)

    products = sorted(
        seen.values(), key=lambda n: int(n.get("sales") or 0), reverse=True
    )[:20]

    if not products:
        LAST_DEBUG = " | ".join(errors)[:400] or "tidak ada produk"
        log.warning("Shopee: 0 produk. %s", LAST_DEBUG)
        return []

    trends: list[Trend] = []
    for rank, n in enumerate(products, start=1):
        name = (n.get("productName") or "").strip()
        sales = int(n.get("sales") or 0)
        rating = n.get("ratingStar")
        discount = n.get("priceDiscountRate")
        shop = (n.get("shopName") or "").strip() or None
        price = _fmt_price(n.get("priceMin"), n.get("priceMax"))

        subtitle = None
        if sales:
            subtitle = f"{sales:,}+ terjual".replace(",", ".")

        t = Trend(
            id=make_id("shopee", name),
            platform="shopee",
            rank=rank,
            title=name,
            url=(n.get("productLink") or n.get("offerLink") or "").strip(),
            subtitle=subtitle,
            metric=sales or None,
            metric_label="terjual" if sales else None,
            thumbnail=(n.get("imageUrl") or "").strip() or None,
            source=shop,
            price=price,
            affiliate_url=(n.get("offerLink") or "").strip(),
        )
        # Konteks untuk ringkasan AI (kenapa produk ini diminati).
        bits = [f"Produk: {name}"]
        if price:
            bits.append(f"harga {price}")
        if sales:
            bits.append(f"{sales} terjual")
        if discount:
            bits.append(f"diskon {discount}%")
        if rating:
            bits.append(f"rating {rating}")
        if shop:
            bits.append(f"toko {shop}")
        t.__dict__["_context"] = ", ".join(bits)
        trends.append(t)

    LAST_DEBUG = f"{len(trends)} produk dari {len(config.SHOPEE_KEYWORDS)} kata kunci"
    log.info("Shopee: %d produk.", len(trends))
    return trends
