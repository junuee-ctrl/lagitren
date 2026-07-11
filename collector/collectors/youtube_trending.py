"""Collector YouTube Trending Indonesia (YouTube Data API v3).

Membutuhkan YOUTUBE_API_KEY. Endpoint:
  GET /youtube/v3/videos?chart=mostPopular&regionCode=ID
"""
from __future__ import annotations

import logging

import requests

import config
from models import Trend
from .base import make_id

log = logging.getLogger("youtube")

API_URL = "https://www.googleapis.com/youtube/v3/videos"
COMMENTS_URL = "https://www.googleapis.com/youtube/v3/commentThreads"


def _fmt_views(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M views"
    if n >= 1_000:
        return f"{n / 1_000:.0f}K views"
    return f"{n} views"


def _fetch_top_comments(video_id: str, max_comments: int = 3) -> list[dict]:
    """Ambil komentar terbaik (paling relevan) satu video.

    Best-effort: komentar bisa dinonaktifkan (403) → kembalikan list kosong.
    Setiap komentar 1 unit kuota commentThreads, jadi hemat: hanya top-N video.
    """
    params = {
        "part": "snippet",
        "videoId": video_id,
        "order": "relevance",
        "maxResults": max_comments,
        "textFormat": "plainText",
        "key": config.YOUTUBE_API_KEY,
    }
    try:
        resp = requests.get(COMMENTS_URL, params=params, timeout=20)
        if resp.status_code == 403:
            # Komentar dinonaktifkan / tidak diizinkan — normal, lewati.
            return []
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        log.info("Komentar %s gagal: %s", video_id, exc)
        return []

    out: list[dict] = []
    for item in data.get("items", []):
        top = (
            item.get("snippet", {})
            .get("topLevelComment", {})
            .get("snippet", {})
        )
        text = (top.get("textDisplay") or top.get("textOriginal") or "").strip()
        if not text:
            continue
        # Ringkas komentar yang terlalu panjang.
        if len(text) > 280:
            text = text[:277].rstrip() + "…"
        entry: dict = {"text": text}
        author = (top.get("authorDisplayName") or "").strip()
        if author:
            entry["author"] = author
        likes = top.get("likeCount")
        if isinstance(likes, int) and likes > 0:
            entry["likes"] = likes
        out.append(entry)
    return out


def collect(max_results: int = 15, comment_top_n: int = 12) -> list[Trend]:
    if not config.YOUTUBE_API_KEY:
        log.warning("YOUTUBE_API_KEY kosong — lewati YouTube.")
        return []

    params = {
        "part": "snippet,statistics",
        "chart": "mostPopular",
        "regionCode": config.GEO,
        "maxResults": max_results,
        "hl": config.LANG,
        "key": config.YOUTUBE_API_KEY,
    }
    try:
        resp = requests.get(API_URL, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        log.error("YouTube API gagal: %s", exc)
        return []

    trends: list[Trend] = []
    for rank, item in enumerate(data.get("items", []), start=1):
        vid = item.get("id")
        sn = item.get("snippet", {})
        st = item.get("statistics", {})
        title = (sn.get("title") or "").strip()
        if not vid or not title:
            continue

        views = int(st.get("viewCount", 0) or 0)
        thumbs = sn.get("thumbnails", {})
        thumb = (
            thumbs.get("medium", {}).get("url")
            or thumbs.get("high", {}).get("url")
            or thumbs.get("default", {}).get("url")
        )
        tags = sn.get("tags", []) or []

        t = Trend(
            # JANGAN slugify: ID video YouTube case-sensitive & bisa mengandung
            # '_' / '-'. Slugify akan merusaknya → embed gagal. Pakai apa adanya
            # (aman untuk URL path).
            id=f"youtube:{vid}",
            platform="youtube",
            rank=rank,
            title=title,
            url=f"https://www.youtube.com/watch?v={vid}",
            subtitle=_fmt_views(views) if views else None,
            metric=views or None,
            metric_label="views" if views else None,
            thumbnail=thumb,
            source=sn.get("channelTitle"),
            hashtags=[t.lower() for t in tags[:3]],
        )
        t.__dict__["_context"] = (sn.get("description") or "")[:300]
        # Komentar terbaik (hanya untuk video peringkat atas → hemat kuota).
        if rank <= comment_top_n:
            comments = _fetch_top_comments(vid, max_comments=3)
            if comments:
                t.extra = {**(t.extra or {}), "comments": comments}
                # Perkaya konteks AI dengan cuplikan komentar teratas.
                top_texts = " / ".join(c["text"] for c in comments[:2])
                if top_texts:
                    t.__dict__["_context"] += f"\n[Komentar teratas] {top_texts}"
        trends.append(t)

    log.info("YouTube: %d video.", len(trends))
    return trends
