"""Collector Produk Lagi Dicari (Shopee/Tokopedia).

Rencana (prioritas minggu ke-3): Shopee Affiliate API atau scraping
autocomplete/kata kunci populer. Setiap item wajib punya affiliate_url
(via redirect lagitren.id/go/shopee/<slug>) dan catatan harga.
Stub sementara mengembalikan [].
"""
from __future__ import annotations

import logging

from models import Trend
from .base import slugify

log = logging.getLogger("shopee")


def affiliate_link(keyword: str) -> str:
    """Bangun URL redirect afiliasi internal dari kata kunci produk."""
    return f"https://lagitren.id/go/shopee/{slugify(keyword)}"


def collect() -> list[Trend]:
    log.info("Shopee collector belum diaktifkan (stub).")
    return []
