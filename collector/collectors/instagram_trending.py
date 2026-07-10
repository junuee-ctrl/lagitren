"""Collector Instagram — via browser (Playwright), LOKAL & EKSPERIMENTAL.

Instagram tidak punya "trending" resmi dan memblokir akses non-login. Strategi:
buka beberapa hashtag populer di browser yang SUDAH LOGIN (profil persisten),
intersep respons API hashtag Instagram, lalu ambil post teratas (yang bisa
di-embed di situs kita).

Login sekali:
  BROWSER_HEADFUL=1 python -c "from collectors import instagram_trending as ig; ig.login()"
  (jendela browser terbuka → login Instagram → tutup. Sesi tersimpan di .ig_profile)

Lalu kumpulkan:
  python main.py instagram

Di cloud / tanpa Playwright: mengembalikan [] dengan aman.
"""
from __future__ import annotations

import json
import logging
from urllib.parse import quote

import config
from models import Trend
from .base import make_id

log = logging.getLogger("instagram")

LAST_DEBUG: str = ""


def _extract_posts(payload: dict) -> list[dict]:
    """Ambil daftar node post dari berbagai bentuk respons IG."""
    posts: list[dict] = []

    def walk(obj):
        if isinstance(obj, dict):
            # node post biasanya punya 'code' (shortcode) / 'shortcode'
            code = obj.get("code") or obj.get("shortcode")
            if code and (obj.get("image_versions2") or obj.get("thumbnail_src") or obj.get("display_url")):
                posts.append(obj)
            for v in obj.values():
                walk(v)
        elif isinstance(obj, list):
            for v in obj:
                walk(v)

    walk(payload)
    return posts


def _post_to_trend(node: dict, tag: str, rank: int) -> Trend | None:
    code = node.get("code") or node.get("shortcode")
    if not code:
        return None
    # caption
    caption = ""
    cap = node.get("caption")
    if isinstance(cap, dict):
        caption = cap.get("text", "")
    elif isinstance(cap, str):
        caption = cap
    likes = int(node.get("like_count") or node.get("edge_liked_by", {}).get("count", 0) or 0)
    # thumbnail
    thumb = node.get("thumbnail_src") or node.get("display_url")
    if not thumb:
        iv = node.get("image_versions2", {}).get("candidates") or []
        if iv:
            thumb = iv[0].get("url")

    title = (caption.strip().split("\n")[0] or f"Postingan #{tag}")[:90]
    return Trend(
        id=make_id("instagram", code),
        platform="instagram",
        rank=rank,
        title=title,
        url=f"https://www.instagram.com/p/{code}/",
        subtitle=f"{likes:,} suka" if likes else None,
        metric=likes or None,
        metric_label="suka" if likes else None,
        thumbnail=thumb,
        hashtags=[tag.lower()],
    )


def collect(limit: int = 15) -> list[Trend]:
    global LAST_DEBUG
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except Exception as exc:
        LAST_DEBUG = f"playwright tidak terpasang: {exc}"
        log.info("Playwright tidak tersedia — Instagram hanya jalan di PC lokal.")
        return []

    from . import _browser

    all_trends: list[Trend] = []
    seen: set[str] = set()
    try:
        with sync_playwright() as p:
            ctx = _browser.get_context(p)
            page = ctx.new_page()
            captured: list[dict] = []

            def on_response(resp):
                u = resp.url
                if "/api/v1/tags/" in u or ("graphql" in u and "tag" in u.lower()):
                    try:
                        captured.append(resp.json())
                    except Exception:
                        pass

            page.on("response", on_response)

            per_tag = max(2, limit // max(1, len(config.IG_HASHTAGS)))
            for tag in config.IG_HASHTAGS:
                captured.clear()
                try:
                    page.goto(
                        f"https://www.instagram.com/explore/tags/{quote(tag)}/",
                        wait_until="domcontentloaded",
                        timeout=45000,
                    )
                    page.wait_for_timeout(4000)
                except Exception as exc:
                    log.info("IG tag %s gagal: %s", tag, exc)
                    continue

                nodes: list[dict] = []
                for payload in captured:
                    nodes.extend(_extract_posts(payload))
                rank = len(all_trends) + 1
                added = 0
                for node in nodes:
                    t = _post_to_trend(node, tag, rank)
                    if t and t.id not in seen:
                        seen.add(t.id)
                        all_trends.append(t)
                        rank += 1
                        added += 1
                        if added >= per_tag:
                            break
                if len(all_trends) >= limit:
                    break

            try:
                page.close()
            except Exception:
                pass
            _browser.close_context(ctx)
    except Exception as exc:
        LAST_DEBUG = f"browser error: {type(exc).__name__}: {str(exc)[:160]}"
        log.error("Instagram browser gagal: %s", exc)
        return []

    # peringkat ulang & batasi
    for i, t in enumerate(all_trends[:limit], start=1):
        t.rank = i
    all_trends = all_trends[:limit]
    LAST_DEBUG = f"ok: {len(all_trends)} post dari {len(config.IG_HASHTAGS)} hashtag"
    log.info("Instagram: %d post.", len(all_trends))
    return all_trends
