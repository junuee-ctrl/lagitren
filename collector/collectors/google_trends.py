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


def _downsample(vals: list[int], target: int = 30) -> list[int]:
    """Kurangi jumlah titik agar grafik ringkas."""
    if len(vals) <= target:
        return vals
    step = len(vals) / target
    return [vals[int(i * step)] for i in range(target)]


def _fetch_interest(keywords: list[str], max_kw: int = 8) -> dict[str, list[int]]:
    """Ambil deret minat pencarian (interest over time) per kata kunci.

    Best-effort: butuh pytrends + pandas, dan bisa diblokir/rate-limit oleh
    Google (429) terutama dari IP datacenter. Kegagalan tidak menghentikan
    pengumpulan — kata kunci tanpa data hanya tidak punya grafik.
    """
    out: dict[str, list[int]] = {}
    try:
        from pytrends.request import TrendReq  # type: ignore
    except Exception as exc:
        log.info("pytrends tidak tersedia: %s", exc)
        return out

    import time

    try:
        py = TrendReq(hl="id-ID", tz=420, timeout=(10, 25), retries=1, backoff_factor=0.6)
    except Exception as exc:
        log.info("pytrends init gagal: %s", exc)
        return out

    for kw in keywords[:max_kw]:
        try:
            py.build_payload([kw], geo=config.GEO, timeframe="now 7-d")
            df = py.interest_over_time()
            if df is not None and not df.empty and kw in df.columns:
                vals = [int(v) for v in df[kw].tolist()]
                if any(v > 0 for v in vals):
                    out[kw] = _downsample(vals, 30)
        except Exception as exc:
            log.info("pytrends gagal untuk '%s': %s", kw, exc)
        time.sleep(1.0)

    log.info("pytrends: %d/%d kata kunci dapat grafik.", len(out), min(len(keywords), max_kw))
    return out


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

        # Berita terkait: judul + tautan + sumber (untuk ditampilkan & konteks AI).
        news_items: list[dict] = []
        for n in item.findall("ht:news_item", _NS):
            nt_el = n.find("ht:news_item_title", _NS)
            nu_el = n.find("ht:news_item_url", _NS)
            ns_el = n.find("ht:news_item_source", _NS)
            nt = (nt_el.text or "").strip() if nt_el is not None else ""
            nu = (nu_el.text or "").strip() if nu_el is not None else ""
            ns = (ns_el.text or "").strip() if ns_el is not None else ""
            if nt and nu:
                entry = {"title": nt, "url": nu}
                if ns:
                    entry["source"] = ns
                news_items.append(entry)
        news_items = news_items[:3]
        context = " | ".join(n["title"] for n in news_items)

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
                extra={"news": news_items} if news_items else {},
            )
        )
        # Simpan konteks berita di atribut sementara (tidak masuk DB).
        trends[-1].__dict__["_context"] = context

    trends = trends[:20]

    # Lengkapi grafik minat pencarian (best-effort).
    if config.FETCH_INTEREST and trends:
        kw_map = _fetch_interest([t.title for t in trends])
        for t in trends:
            if t.title in kw_map:
                t.interest = kw_map[t.title]

    log.info("Google Trends: %d item.", len(trends))
    return trends
