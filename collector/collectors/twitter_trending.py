"""Collector X (Twitter) Trending Indonesia.

Sumber: trends24.in/indonesia — situs publik yang menampilkan daftar tren
Twitter/X per negara (topik + perkiraan jumlah tweet). Gratis, tanpa API key.

Mengembalikan list[Trend]. Ringkasan AI diisi oleh main.py.
"""
from __future__ import annotations

import logging
import re
from urllib.parse import quote

import requests

import config
from models import Trend
from .base import make_id

log = logging.getLogger("twitter")

URL = "https://trends24.in/indonesia/"


def _parse_count(text: str | None) -> int | None:
    """'125K tweets' / '1.2M Tweets' / '80 rb' -> integer."""
    if not text:
        return None
    t = text.lower().replace(",", "").strip()
    m = re.search(r"([\d.]+)\s*(k|m|rb|jt|juta)?", t)
    if not m:
        return None
    try:
        num = float(m.group(1))
    except ValueError:
        return None
    unit = m.group(2) or ""
    mult = {"k": 1_000, "rb": 1_000, "m": 1_000_000, "jt": 1_000_000, "juta": 1_000_000}.get(
        unit, 1
    )
    return int(num * mult)


def collect(limit: int = 20) -> list[Trend]:
    try:
        from bs4 import BeautifulSoup  # type: ignore
    except Exception as exc:
        log.warning("beautifulsoup4 tidak tersedia: %s", exc)
        return []

    try:
        resp = requests.get(
            URL, headers={"User-Agent": config.USER_AGENT}, timeout=30
        )
        resp.raise_for_status()
    except Exception as exc:
        log.error("Gagal ambil trends24: %s", exc)
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    # Kartu paling atas = paling baru.
    card = soup.select_one("ol.trend-card__list") or soup.select_one(".trend-card__list")
    if not card:
        log.warning("Struktur trends24 berubah — daftar tren tidak ditemukan.")
        return []

    trends: list[Trend] = []
    seen: set[str] = set()
    for li in card.find_all("li"):
        a = li.find("a")
        if not a:
            continue
        topic = a.get_text(strip=True)
        if not topic or topic in seen:
            continue
        seen.add(topic)

        count_el = li.select_one(".tweet-count") or li.select_one("[class*=count]")
        count_txt = count_el.get_text(strip=True) if count_el else None
        metric = _parse_count(count_txt)

        rank = len(trends) + 1
        is_tag = topic.startswith("#")
        tag_clean = topic.lstrip("#")
        subtitle = None
        if metric:
            subtitle = f"{count_txt}" if count_txt else None

        t = Trend(
            id=make_id("twitter", topic),
            platform="twitter",
            rank=rank,
            title=topic,
            url=f"https://twitter.com/search?q={quote(topic)}",
            subtitle=subtitle,
            metric=metric,
            metric_label="tweet" if metric else None,
            hashtags=[tag_clean.lower()] if is_tag else [],
        )
        trends.append(t)
        if len(trends) >= limit:
            break

    log.info("X (Twitter): %d tren.", len(trends))
    return trends
