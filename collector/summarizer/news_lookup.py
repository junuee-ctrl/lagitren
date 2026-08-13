"""Cari berita terkait via Google News RSS (P1-3).

Dipakai agar SEMUA platform (bukan cuma Google Trends) punya tautan berita
di halaman detail — bahan artikel + nilai E-E-A-T.
"""
from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from urllib.parse import quote

import requests

import config

log = logging.getLogger("news")


def fetch_related_news(query: str, limit: int = 4) -> list[dict]:
    """[{title, url, source}] dari Google News Indonesia. [] bila gagal."""
    q = (query or "").strip().lstrip("#")
    if len(q) < 3:
        return []
    url = (
        "https://news.google.com/rss/search?"
        f"q={quote(q)}&hl=id&gl=ID&ceid=ID:id"
    )
    try:
        resp = requests.get(
            url, timeout=15, headers={"User-Agent": config.USER_AGENT}
        )
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
    except Exception as exc:
        log.info("News lookup gagal utk '%s': %s", q[:30], exc)
        return []

    out: list[dict] = []
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        source = (item.findtext("source") or "").strip() or None
        if title and link:
            out.append({"title": title, "url": link, "source": source})
        if len(out) >= limit:
            break
    return out
