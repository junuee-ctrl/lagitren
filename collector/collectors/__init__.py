"""Registry collector per platform.

Setiap modul mengekspor fungsi `collect() -> list[Trend]`.
"""
from . import (
    google_trends,
    youtube_trending,
    tiktok_trending,
    instagram_trending,
    shopee_trending,
    twitter_trending,
)

# platform -> (modul, jeda pembaruan dalam menit)
REGISTRY = {
    "google": (google_trends, 60),
    "youtube": (youtube_trending, 60),
    "tiktok": (tiktok_trending, 180),
    "instagram": (instagram_trending, 360),
    "shopee": (shopee_trending, 180),
    "twitter": (twitter_trending, 30),
}

__all__ = ["REGISTRY"]
