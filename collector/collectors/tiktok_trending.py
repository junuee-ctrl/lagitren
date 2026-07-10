"""Collector TikTok Trending Indonesia — via browser (Playwright), LOKAL.

TikTok Creative Center memerlukan request bertanda tangan (anti-bot). Cara
paling andal & bebas-maintenance: buka halamannya di browser sungguhan,
biarkan JS TikTok menandatangani sendiri, lalu INTERSEP respons API-nya.

Dijalankan di PC lokal (IP rumah + browser). Di cloud (tanpa Playwright)
fungsi ini mengembalikan [] dengan aman.

Prasyarat lokal:
  pip install -r requirements-local.txt
  playwright install chromium
"""
from __future__ import annotations

import logging

import config
from models import Trend
from .base import make_id

log = logging.getLogger("tiktok")

LAST_DEBUG: str = ""

PAGE_URL = (
    "https://ads.tiktok.com/business/creativecenter/inspiration/popular/"
    f"hashtag/pc/en?region={config.GEO}"
)
API_MARK = "creative_radar_api"
LIST_MARK = "hashtag/list"


def _fmt(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.0f}K"
    return str(n)


def _parse(payload: dict, limit: int) -> list[Trend]:
    lst = (payload.get("data") or {}).get("list") or []
    out: list[Trend] = []
    for i, item in enumerate(lst, start=1):
        name = item.get("hashtag_name")
        if not name:
            continue
        views = int(item.get("video_views") or 0)
        publish = int(item.get("publish_cnt") or 0)
        rank = int(item.get("rank") or i)
        subtitle = metric = label = None
        if views:
            subtitle, metric, label = f"{_fmt(views)} views", views, "views"
        elif publish:
            subtitle, metric, label = f"{_fmt(publish)} video", publish, "video"
        out.append(
            Trend(
                id=make_id("tiktok", name),
                platform="tiktok",
                rank=rank,
                title=f"#{name}",
                url=f"https://www.tiktok.com/tag/{name}",
                subtitle=subtitle,
                metric=metric,
                metric_label=label,
                hashtags=[name.lower()],
            )
        )
        if len(out) >= limit:
            break
    out.sort(key=lambda t: t.rank)
    return out


def collect(limit: int = 20) -> list[Trend]:
    global LAST_DEBUG
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except Exception as exc:
        LAST_DEBUG = f"playwright tidak terpasang: {exc}"
        log.info("Playwright tidak tersedia — TikTok hanya jalan di PC lokal.")
        return []

    captured: list[dict] = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            ctx = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
                ),
                locale="en-US",
            )
            page = ctx.new_page()

            def on_response(resp):
                url = resp.url
                if API_MARK in url and LIST_MARK in url:
                    try:
                        captured.append(resp.json())
                    except Exception:
                        pass

            page.on("response", on_response)
            page.goto(PAGE_URL, wait_until="domcontentloaded", timeout=60000)
            # beri waktu API trending terpanggil & (jika perlu) scroll.
            page.wait_for_timeout(6000)
            try:
                page.mouse.wheel(0, 2000)
                page.wait_for_timeout(3000)
            except Exception:
                pass
            browser.close()
    except Exception as exc:
        LAST_DEBUG = f"browser error: {type(exc).__name__}: {str(exc)[:160]}"
        log.error("TikTok browser gagal: %s", exc)
        return []

    for payload in captured:
        trends = _parse(payload, limit)
        if trends:
            LAST_DEBUG = f"ok: {len(trends)} dari {len(captured)} respons"
            log.info("TikTok: %d hashtag.", len(trends))
            return trends

    LAST_DEBUG = f"tidak ada data (respons ditangkap: {len(captured)})"
    log.warning("TikTok: tidak ada data trending tertangkap.")
    return []
