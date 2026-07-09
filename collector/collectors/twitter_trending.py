"""Collector X (Twitter) Trending Indonesia.

Rencana (prioritas minggu ke-3): scraping trends24.in/indonesia atau X API.
Untuk sekarang stub yang mengembalikan [] agar pipeline tetap jalan.

Contoh sumber:
  https://trends24.in/indonesia/
Parse blok tren teratas -> hashtag/topik + perkiraan volume tweet.
"""
from __future__ import annotations

import logging

from models import Trend

log = logging.getLogger("twitter")


def collect() -> list[Trend]:
    log.info("Twitter collector belum diaktifkan (stub).")
    return []
