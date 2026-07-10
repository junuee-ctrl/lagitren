"""Collector TikTok Trending Indonesia.

Sumber: TikTok Creative Center — API publik (tidak resmi) yang dipakai situs
Creative Center untuk menampilkan hashtag populer per negara.

  https://ads.tiktok.com/creative_radar_api/v1/popular_trend/hashtag/list

Best-effort: TikTok kadang memperketat akses (butuh signature). Bila gagal,
mengembalikan [] tanpa menghentikan pipeline.
"""
from __future__ import annotations

import logging

import requests

import config
from models import Trend
from .base import make_id

log = logging.getLogger("tiktok")

API = "https://ads.tiktok.com/creative_radar_api/v1/popular_trend/hashtag/list"


def _fmt(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.0f}K"
    return str(n)


def collect(limit: int = 20) -> list[Trend]:
    params = {
        "period": "7",          # 7 hari terakhir
        "page": "1",
        "limit": str(limit),
        "country_code": config.GEO,  # ID
        "sort_by": "popular",
    }
    headers = {
        "User-Agent": config.USER_AGENT,
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/en",
        "Origin": "https://ads.tiktok.com",
        "Accept-Language": "id-ID,id;q=0.9,en;q=0.8",
    }
    try:
        resp = requests.get(API, params=params, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        log.warning("Creative Center gagal (mungkin butuh signature): %s", exc)
        return []

    if data.get("code") not in (0, None):
        log.warning("Creative Center code=%s msg=%s", data.get("code"), data.get("msg"))
        return []

    lst = (data.get("data") or {}).get("list") or []
    trends: list[Trend] = []
    for i, item in enumerate(lst, start=1):
        name = item.get("hashtag_name")
        if not name:
            continue
        views = int(item.get("video_views") or 0)
        publish = int(item.get("publish_cnt") or 0)
        rank = int(item.get("rank") or i)

        subtitle = None
        metric = None
        if views:
            subtitle = f"{_fmt(views)} views"
            metric = views
        elif publish:
            subtitle = f"{_fmt(publish)} video"
            metric = publish

        trends.append(
            Trend(
                id=make_id("tiktok", name),
                platform="tiktok",
                rank=rank,
                title=f"#{name}",
                url=f"https://www.tiktok.com/tag/{name}",
                subtitle=subtitle,
                metric=metric,
                metric_label="views" if views else ("video" if publish else None),
                hashtags=[name.lower()],
            )
        )
        if len(trends) >= limit:
            break

    trends.sort(key=lambda t: t.rank)
    log.info("TikTok: %d hashtag.", len(trends))
    return trends
