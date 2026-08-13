"""Ping IndexNow untuk URL tren BARU (P2-1).

IndexNow memberi tahu Bing/Yandex/Seznam/Naver secara instan bahwa ada URL
baru/berubah — melengkapi sitemap (Google tidak memakai IndexNow; untuk
Google, sitemap lastmod + news-sitemap sudah menangani).

Kunci diverifikasi mesin pencari lewat file publik:
  https://lagitren.id/{KEY}.txt  (isi = KEY; ada di folder public/ repo)
"""
from __future__ import annotations

import logging

import requests

import config

log = logging.getLogger("indexnow")

HOST = "lagitren.id"
ENDPOINT = "https://api.indexnow.org/indexnow"


def _public_slug(platform: str) -> str:
    # Key internal "shopee" tampil sebagai /produk di URL publik.
    return "produk" if platform == "shopee" else platform


def url_for(platform: str, trend_id: str) -> str:
    slug = trend_id.split(":", 1)[-1]
    return f"https://{HOST}/{_public_slug(platform)}/{slug}"


def ping(urls: list[str]) -> int:
    """Kirim daftar URL (maks 100). Kembalikan jumlah terkirim (0 bila gagal)."""
    key = config.INDEXNOW_KEY
    if not key or not urls:
        return 0
    batch = urls[:100]
    try:
        resp = requests.post(
            ENDPOINT,
            json={
                "host": HOST,
                "key": key,
                "keyLocation": f"https://{HOST}/{key}.txt",
                "urlList": batch,
            },
            timeout=15,
            headers={"Content-Type": "application/json; charset=utf-8"},
        )
        # 200/202 = diterima. 4xx = masalah kunci/format.
        if resp.status_code in (200, 202):
            log.info("IndexNow: %d URL dikirim.", len(batch))
            return len(batch)
        log.warning("IndexNow status %s: %s", resp.status_code, resp.text[:120])
        return 0
    except Exception as exc:
        log.info("IndexNow gagal (diabaikan): %s", exc)
        return 0
