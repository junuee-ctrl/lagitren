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
from urllib.parse import quote

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
# Kata kunci untuk mengenali endpoint data trending (struktur situs bisa berubah).
CAND_KEYS = ("trend", "hashtag", "popular", "radar", "rank")


def _fmt(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.0f}K"
    return str(n)


def _find_hashtag_list(payload) -> list[dict]:
    """Cari list item hashtag di mana pun dalam JSON (struktur bisa berubah)."""
    found: list[dict] = []

    def walk(obj):
        if isinstance(obj, list):
            if (
                obj
                and isinstance(obj[0], dict)
                and (
                    "hashtag_name" in obj[0]
                    or ("hashtag" in obj[0] and "video_views" in obj[0])
                )
            ):
                found.append(obj)  # type: ignore
            for v in obj:
                walk(v)
        elif isinstance(obj, dict):
            for v in obj.values():
                walk(v)

    walk(payload)
    return found[0] if found else []


def _num(item: dict, *keys) -> int:
    for k in keys:
        v = item.get(k)
        if isinstance(v, (int, float)):
            return int(v)
        if isinstance(v, str) and v.replace(".", "").isdigit():
            return int(float(v))
    return 0


def _parse(payload: dict, limit: int) -> list[Trend]:
    lst = (
        (payload.get("data") or {}).get("list")
        or (payload.get("items") if isinstance(payload.get("items"), list) else None)
        or _find_hashtag_list(payload)
    )
    out: list[Trend] = []
    for i, item in enumerate(lst or [], start=1):
        if not isinstance(item, dict):
            continue
        name = (
            item.get("hashtagName")
            or item.get("hashtag_name")
            or item.get("hashtag")
            or item.get("name")
            or item.get("title")
        )
        if not name:
            continue
        views = _num(item, "videoViews", "video_views", "views", "viewCnt", "playCnt")
        publish = _num(item, "publishCnt", "publish_cnt", "video_count", "postCnt")
        rank = _num(item, "rankIndex", "rank") or i
        subtitle = metric = label = None
        if views:
            subtitle, metric, label = f"{_fmt(views)} views", views, "views"
        elif publish:
            subtitle, metric, label = f"{_fmt(publish)} video", publish, "video"

        # popularityCurve -> interest (0-100) untuk grafik.
        interest: list[int] = []
        curve = item.get("popularityCurve") or item.get("trend")
        if isinstance(curve, list):
            for pt in curve:
                v = pt.get("value") if isinstance(pt, dict) else None
                if isinstance(v, (int, float)):
                    interest.append(int(round(v)))

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
                interest=interest,
            )
        )
        if len(out) >= limit:
            break
    out.sort(key=lambda t: t.rank)
    return out


def _extract_top_video(payload) -> dict | None:
    """Cari video paling banyak diputar dalam respons item_list TikTok."""
    best: dict | None = None
    best_plays = -1

    def walk(obj):
        nonlocal best, best_plays
        if isinstance(obj, dict):
            vid = obj.get("id") or obj.get("aweme_id")
            author = obj.get("author")
            stats = obj.get("stats") or obj.get("statsV2") or obj.get("statistics")
            if vid and isinstance(author, dict) and isinstance(stats, dict):
                uid = author.get("uniqueId") or author.get("unique_id")
                raw = (
                    stats.get("playCount")
                    or stats.get("play_count")
                    or stats.get("playCountStr")
                    or 0
                )
                try:
                    plays = int(raw)
                except (ValueError, TypeError):
                    plays = 0
                cover = None
                video = obj.get("video")
                if isinstance(video, dict):
                    cover = (
                        video.get("cover")
                        or video.get("originCover")
                        or video.get("dynamicCover")
                    )
                if uid and str(vid).isdigit() and plays > best_plays:
                    best_plays = plays
                    best = {
                        "url": f"https://www.tiktok.com/@{uid}/video/{vid}",
                        "author": uid,
                        "cover": cover,
                        "plays": plays,
                    }
            for v in obj.values():
                walk(v)
        elif isinstance(obj, list):
            for v in obj:
                walk(v)

    walk(payload)
    return best


def _fetch_top_video(page, hashtag: str) -> dict | None:
    """Buka halaman tag TikTok, intersep item_list, pilih video terlaris."""
    from . import _browser

    grabbed: list = []

    def on_resp(resp):
        low = resp.url.lower()
        if (
            "item_list" in low
            or "/api/challenge/" in low
            or "/api/search/general" in low
        ):
            try:
                grabbed.append(resp.json())
            except Exception:
                pass

    page.on("response", on_resp)
    try:
        page.goto(
            f"https://www.tiktok.com/tag/{quote(hashtag)}",
            wait_until="domcontentloaded",
            timeout=40000,
        )
        _browser.accept_cookies(page)
        page.wait_for_timeout(3500)
        try:
            page.mouse.wheel(0, 1600)
        except Exception:
            pass
        page.wait_for_timeout(2500)
    except Exception as exc:
        log.info("TikTok tag '%s' gagal: %s", hashtag, exc)
    finally:
        try:
            page.remove_listener("response", on_resp)
        except Exception:
            pass

    best = None
    for payload in grabbed:
        v = _extract_top_video(payload)
        if v and (best is None or v["plays"] > best["plays"]):
            best = v

    # Cadangan: JSON tertanam di HTML (SIGI_STATE / UNIVERSAL_DATA).
    if best is None:
        try:
            import json as _json
            import re as _re

            html = page.content()
            for marker in (
                "__UNIVERSAL_DATA_FOR_REHYDRATION__",
                "SIGI_STATE",
            ):
                m = _re.search(
                    marker + r'"[^>]*>(.*?)</script>', html, _re.DOTALL
                )
                if not m:
                    continue
                try:
                    v = _extract_top_video(_json.loads(m.group(1)))
                except Exception:
                    v = None
                if v:
                    best = v
                    break
        except Exception:
            pass
    return best


def _enrich_videos(page, trends: list[Trend]) -> int:
    """Lampirkan video representatif ke hashtag teratas (untuk embed di situs)."""
    top_n = min(config.TIKTOK_VIDEO_TOPN, len(trends))
    enriched = 0
    for t in trends[:top_n]:
        tag = t.hashtags[0] if t.hashtags else t.title.lstrip("#")
        v = _fetch_top_video(page, tag)
        if v:
            t.url = v["url"]  # jadi bisa di-embed (canEmbed cek pola /video/)
            if v.get("cover"):
                t.thumbnail = v["cover"]
            t.extra = {
                **(t.extra or {}),
                "tiktok": {
                    "videoUrl": v["url"],
                    "author": v.get("author"),
                    "plays": v.get("plays"),
                },
            }
            enriched += 1
    log.info("TikTok: %d/%d hashtag dapat video.", enriched, top_n)
    return enriched


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
    result: list[Trend] = []
    try:
        with sync_playwright() as p:
            ctx = _browser.get_context(p)
            page = ctx.new_page()

            all_hosts: dict[str, int] = {}
            candidates: list[tuple[str, list[str]]] = []  # (path, top-level keys)
            captured_id: list[dict] = []  # respons khusus countryCode=ID

            def on_response(resp):
                url = resp.url
                try:
                    host = url.split("/")[2]
                    all_hosts[host] = all_hosts.get(host, 0) + 1
                except Exception:
                    pass
                low = url.lower()
                # Endpoint kandidat: JSON dari ads.tiktok.com / byteoversea yg
                # url-nya memuat kata kunci trending.
                is_cand = ("ads.tiktok.com" in low or "byteoversea" in low) and any(
                    k in low for k in CAND_KEYS
                )
                if API_MARK in low or is_cand:
                    path = url.split("?")[0]
                    seen_urls.append(path)
                    try:
                        j = resp.json()
                        captured.append(j)
                        keys = list(j.keys())[:6] if isinstance(j, dict) else ["<non-dict>"]
                        candidates.append((path, keys))
                        # Utamakan respons untuk Indonesia (countryCode=ID).
                        try:
                            body = (resp.request.post_data or "").replace(" ", "")
                        except Exception:
                            body = ""
                        if '"countryCode":"ID"' in body:
                            captured_id.append(j)
                    except Exception:
                        pass

            req_urls: list[str] = []

            def on_request(req):
                if "GetHashtagList" in req.url or "trendsTcc" in req.url:
                    req_urls.append(req.url)
                    body = ""
                    try:
                        body = (req.post_data or "")[:300]
                    except Exception:
                        pass
                    if body:
                        req_urls.append("POSTDATA:" + body)

            page.on("request", on_request)
            page.on("response", on_response)
            page.goto(PAGE_URL, wait_until="load", timeout=60000)
            _browser.accept_cookies(page)
            log.info("URL akhir halaman: %s", page.url)

            # Poll sampai ~30 dtk: SPA butuh waktu memanggil API; scroll berkala.
            for _ in range(10):
                if any((c.get("data") or {}).get("list") for c in captured):
                    break
                page.wait_for_timeout(3000)
                try:
                    page.mouse.wheel(0, 1500)
                except Exception:
                    pass

            # Parse daftar hashtag (browser MASIH terbuka untuk enrich video).
            for payload in captured_id + captured:
                parsed = _parse(payload, limit)
                if parsed:
                    result = parsed
                    src = "ID" if payload in captured_id else "non-ID"
                    LAST_DEBUG = f"ok: {len(result)} hashtag ({src})"
                    log.info("TikTok: %d hashtag (%s).", len(result), src)
                    break

            # Lampirkan video representatif (kalau berhasil dapat hashtag).
            if result:
                try:
                    vids = _enrich_videos(page, result)
                    LAST_DEBUG = f"{LAST_DEBUG}, {vids} video"
                except Exception as exc:
                    log.info("TikTok enrich video gagal (diabaikan): %s", exc)
                    LAST_DEBUG = f"{LAST_DEBUG}, video err:{type(exc).__name__}"

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
        return result

    if result:
        return result

    # --- Tidak ada data → keluarkan diagnostik lengkap ---
    uniq = sorted(set(seen_urls))
    log.warning("TikTok: tidak ada data. Cek tiktok_debug.png.")
    log.info("  endpoint terpanggil (%d): %s", len(uniq), uniq[:8])
    top_hosts = sorted(all_hosts.items(), key=lambda x: -x[1])[:6]
    log.info("  host respons: %s", top_hosts)
    log.info("  kandidat JSON (%d): %s", len(candidates), [c[0] for c in candidates[:6]])
    import json as _json
    for payload in captured:
        items = payload.get("items") if isinstance(payload, dict) else None
        if not items:
            items = _find_hashtag_list(payload) or None
        if items:
            log.info("  contoh item: %s", _json.dumps(items[0], ensure_ascii=False)[:400])
            break
    for ru in req_urls[:6]:
        log.info("  REQ: %s", ru[:300])
    LAST_DEBUG = f"0 data. endpoints={uniq[:6]}"
    return []
