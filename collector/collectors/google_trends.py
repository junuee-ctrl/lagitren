"""Collector Google Trends Indonesia.

Sumber utama: RSS "Daily Trending Searches" Google Trends —
stabil, tanpa API key, dan tahan banting dibanding scraping HTML.

  https://trends.google.com/trending/rss?geo=ID

Mengembalikan list[Trend]. Ringkasan AI diisi oleh main.py.
"""
from __future__ import annotations

import logging
from xml.etree import ElementTree as ET

import requests

import config
from models import Trend
from .base import make_id

log = logging.getLogger("google")

RSS_URLS = [
    f"https://trends.google.com/trending/rss?geo={config.GEO}",
    # Endpoint lama sebagai cadangan.
    f"https://trends.google.com/trends/trendingsearches/daily/rss?geo={config.GEO}",
]

_NS = {"ht": "https://trends.google.com/trending/rss"}


def _fetch_rss() -> str | None:
    for url in RSS_URLS:
        try:
            resp = requests.get(
                url, headers={"User-Agent": config.USER_AGENT}, timeout=30
            )
            if resp.status_code == 200 and resp.text.strip():
                return resp.text
            log.warning("RSS %s -> HTTP %s", url, resp.status_code)
        except Exception as exc:
            log.warning("RSS %s gagal: %s", url, exc)
    return None


def _parse_traffic(text: str | None) -> int | None:
    """'5.000+' / '2rb+' / '1 jt+' -> perkiraan integer."""
    if not text:
        return None
    t = text.lower().replace("+", "").replace(",", "").replace(".", "").strip()
    mult = 1
    if "jt" in t or "juta" in t or "m" == t[-1:]:
        mult = 1_000_000
    elif "rb" in t or "k" in t:
        mult = 1_000
    digits = "".join(ch for ch in t if ch.isdigit())
    if not digits:
        return None
    try:
        return int(digits) * mult
    except ValueError:
        return None


def collect() -> list[Trend]:
    xml = _fetch_rss()
    if not xml:
        log.error("Tidak bisa mengambil RSS Google Trends.")
        return []

    try:
        root = ET.fromstring(xml)
    except ET.ParseError as exc:
        log.error("Gagal parse RSS: %s", exc)
        return []

    trends: list[Trend] = []
    items = root.findall(".//item")
    for rank, item in enumerate(items, start=1):
        title_el = item.find("title")
        title = (title_el.text or "").strip() if title_el is not None else ""
        if not title:
            continue

        # Approx traffic (khusus feed harian lama).
        traffic_el = item.find("ht:approx_traffic", _NS)
        traffic_txt = traffic_el.text if traffic_el is not None else None
        metric = _parse_traffic(traffic_txt)

        # Thumbnail berita terkait (opsional).
        pic_el = item.find("ht:picture", _NS)
        thumbnail = pic_el.text.strip() if pic_el is not None and pic_el.text else None

        # Berita terkait sebagai konteks untuk ringkasan AI.
        news_titles = [
            (n.text or "").strip()
            for n in item.findall("ht:news_item/ht:news_item_title", _NS)
        ]
        context = " | ".join(t for t in news_titles[:3] if t)

        search_url = (
            f"https://trends.google.co.id/trends/explore"
            f"?q={requests.utils.quote(title)}&geo={config.GEO}"
        )

        trends.append(
            Trend(
                id=make_id("google", title),
                platform="google",
                rank=rank,
                title=title,
                url=search_url,
                subtitle=(traffic_txt.strip() if traffic_txt else None),
                metric=metric,
                metric_label="pencarian" if metric else None,
                thumbnail=thumbnail,
                source="Google Trends ID",
                # Simpan konteks sementara di price? Tidak — kirim via return tuple.
            )
        )
        # Simpan konteks berita di atribut sementara (tidak masuk DB).
        trends[-1].__dict__["_context"] = context

    log.info("Google Trends: %d item.", len(trends))
    return trends[:20]
