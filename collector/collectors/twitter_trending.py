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


def _extract_top_tweets(payload, limit: int) -> list[dict]:
    """Cari tweet dengan (retweet+like) terbanyak dari respons SearchTimeline X."""
    found: list[dict] = []

    def walk(obj):
        if isinstance(obj, dict):
            legacy = obj.get("legacy")
            if isinstance(legacy, dict) and (
                "full_text" in legacy or "retweet_count" in legacy
            ):
                sid = legacy.get("id_str") or obj.get("rest_id")
                rt = legacy.get("retweet_count") or 0
                fav = legacy.get("favorite_count") or 0
                # Cari screen_name di user_results terdekat.
                screen = None
                core = obj.get("core") or {}
                res = (core.get("user_results") or {}).get("result") or {}
                for holder in (res.get("legacy"), res.get("core"), res):
                    if isinstance(holder, dict) and holder.get("screen_name"):
                        screen = holder["screen_name"]
                        break
                if sid:
                    try:
                        rt, fav = int(rt or 0), int(fav or 0)
                    except (ValueError, TypeError):
                        rt, fav = 0, 0
                    found.append(
                        {"id": str(sid), "screen": screen, "rt": rt, "fav": fav}
                    )
            for v in obj.values():
                walk(v)
        elif isinstance(obj, list):
            for v in obj:
                walk(v)

    walk(payload)
    # Dedup + urut berdasarkan keterlibatan.
    uniq: dict[str, dict] = {}
    for t in found:
        cur = uniq.get(t["id"])
        if not cur or (t["rt"] + t["fav"]) > (cur["rt"] + cur["fav"]):
            uniq[t["id"]] = t
    ranked = sorted(uniq.values(), key=lambda t: t["rt"] + t["fav"], reverse=True)
    out: list[dict] = []
    for t in ranked:
        screen = t.get("screen") or "i"
        out.append(
            {
                "url": f"https://twitter.com/{screen}/status/{t['id']}",
                "retweets": t["rt"],
                "likes": t["fav"],
            }
        )
        if len(out) >= limit:
            break
    return out


def _fetch_tweets_for(page, query: str, limit: int) -> list[dict]:
    """Buka pencarian X (tab 'Top'), intersep SearchTimeline, ambil tweet teratas."""
    from . import _browser

    grabbed: list = []

    def on_resp(resp):
        low = resp.url.lower()
        if "searchtimeline" in low or "adaptive.json" in low:
            try:
                grabbed.append(resp.json())
            except Exception:
                pass

    page.on("response", on_resp)
    try:
        page.goto(
            f"https://x.com/search?q={quote(query)}&f=top",
            wait_until="domcontentloaded",
            timeout=40000,
        )
        _browser.accept_cookies(page)
        page.wait_for_timeout(4000)
        try:
            page.mouse.wheel(0, 1200)
        except Exception:
            pass
        page.wait_for_timeout(2500)
    except Exception as exc:
        log.info("X search '%s' gagal: %s", query, exc)
    finally:
        try:
            page.remove_listener("response", on_resp)
        except Exception:
            pass

    for payload in grabbed:
        tweets = _extract_top_tweets(payload, limit)
        if tweets:
            return tweets
    return []


def _enrich_tweets(trends: list[Trend]) -> None:
    """Lampirkan tweet teratas ke tren X teratas (butuh browser login)."""
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except Exception:
        log.info("Playwright tak tersedia — lewati enrich tweet X.")
        return
    from . import _browser

    top_n = min(config.TWITTER_TWEET_TOPN, len(trends))
    try:
        with sync_playwright() as p:
            ctx = _browser.get_context(p)
            page = ctx.new_page()
            got = 0
            for t in trends[:top_n]:
                tweets = _fetch_tweets_for(page, t.title, config.TWITTER_TWEETS_PER)
                if tweets:
                    t.extra = {**(t.extra or {}), "tweets": tweets}
                    got += 1
            try:
                page.close()
            except Exception:
                pass
            _browser.close_context(ctx)
            log.info("X: %d/%d tren dapat tweet.", got, top_n)
    except Exception as exc:
        log.info("X enrich tweet gagal (diabaikan): %s", exc)


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

    # Opsional: perkaya dengan tweet teratas (butuh browser login → lokal).
    if config.TWITTER_WITH_TWEETS and trends:
        _enrich_tweets(trends)

    log.info("X (Twitter): %d tren.", len(trends))
    return trends
