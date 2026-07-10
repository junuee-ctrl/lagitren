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
    top_hosts = sorted(all_hosts.items(), key=lambda x: -x[1])[:8]
    log.info("Host respons (total %d): %s", sum(all_hosts.values()), top_hosts)
    log.info("Kandidat endpoint JSON (%d):", len(candidates))
    for path, keys in candidates[:12]:
        log.info("   %s  keys=%s", path, keys)
    # Log contoh 1 item mentah agar tahu nama field sebenarnya.
    import json as _json
    for payload in captured:
        items = payload.get("items") if isinstance(payload, dict) else None
        if not items:
            lst = _find_hashtag_list(payload)
            items = lst if lst else None
        if items:
            log.info("Contoh item: %s", _json.dumps(items[0], ensure_ascii=False)[:600])
            break
    for ru in req_urls[:6]:
        log.info("REQ: %s", ru[:400])

    # Prioritas: respons Indonesia dulu, baru sisanya.
    for payload in captured_id + captured:
        trends = _parse(payload, limit)
        if trends:
            src = "ID" if payload in captured_id else "non-ID"
            LAST_DEBUG = f"ok: {len(trends)} hashtag ({src})"
            log.info("TikTok: %d hashtag (%s).", len(trends), src)
            return trends

    LAST_DEBUG = f"0 data. endpoints={uniq[:6]}"
    log.warning(
        "TikTok: tidak ada data. Respons API: %d, endpoint unik: %s. "
        "Cek tiktok_debug.png.",
        len(captured),
        uniq[:6],
    )
    return []
