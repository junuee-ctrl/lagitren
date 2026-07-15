"""Registry collector per platform.

Setiap modul mengekspor fungsi `collect() -> list[Trend]`.
"""
from . import (
    google_trends,
    youtube_trending,
    tiktok_trending,
    instagram_trending,
    shopping_products,
    twitter_trending,
    netflix_trending,
)

# platform -> (modul, jeda pembaruan dalam menit)
# Catatan: slot "shopee" kini diisi produk afiliasi TikTok Shop/Tokopedia
# (via Google Sheet). Kunci "shopee" dipertahankan agar tak perlu migrasi DB.
REGISTRY = {
    "google": (google_trends, 60),
    "youtube": (youtube_trending, 60),
    "tiktok": (tiktok_trending, 180),
    "instagram": (instagram_trending, 360),
    "shopee": (shopping_products, 360),
    "twitter": (twitter_trending, 30),
    "netflix": (netflix_trending, 1440),  # mingguan (Tudum rilis tiap Selasa)
}

__all__ = ["REGISTRY"]
