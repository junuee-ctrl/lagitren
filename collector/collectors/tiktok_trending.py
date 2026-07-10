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

    from . import _browser

    captured: list[dict] = []
    seen_urls: list[str] = []
    try:
        with sync_playwright() as p:
            ctx = _browser.get_context(p)
            page = ctx.new_page()

            def on_response(resp):
                url = resp.url
                # Tangkap SEMUA respons Creative Center API (diagnostik luas).
                if API_MARK in url:
                    seen_urls.append(url.split("?")[0])
                    try:
                        captured.append(resp.json())
                    except Exception:
                        pass

            page.on("response", on_response)
            page.goto(PAGE_URL, wait_until="load", timeout=60000)
            _browser.accept_cookies(page)

            # Poll sampai ~30 dtk: SPA butuh waktu memanggil API; scroll berkala.
            for _ in range(10):
                if any((c.get("data") or {}).get("list") for c in captured):
                    break
                page.wait_for_timeout(3000)
                try:
                    page.mouse.wheel(0, 1500)
                except Exception:
                    pass

            # Screenshot untuk inspeksi manual (login wall? region?).
            try:
                page.screenshot(path="tiktok_debug.png", full_page=False)
            except Exception:
                pass
            try:
                page.close()
            except Exception:
                pass
            _browser.close_context(ctx)
    except Exception as exc:
        LAST_DEBUG = f"browser error: {type(exc).__name__}: {str(exc)[:160]}"
        log.error("TikTok browser gagal: %s", exc)
        return []

    # Log endpoint yang benar-benar terpanggil (untuk debugging).
    uniq = sorted(set(seen_urls))
    log.info("TikTok endpoint terpanggil (%d): %s", len(uniq), uniq[:8])

    for payload in captured:
        trends = _parse(payload, limit)
        if trends:
            LAST_DEBUG = f"ok: {len(trends)} hashtag"
            log.info("TikTok: %d hashtag.", len(trends))
            return trends

    LAST_DEBUG = f"0 data. endpoints={uniq[:6]}"
    log.warning(
        "TikTok: tidak ada data. Respons API: %d, endpoint unik: %s. "
        "Cek tiktok_debug.png.",
        len(captured),
        uniq[:6],
    )
    return []
