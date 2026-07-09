"""Collector Instagram Hits (Indonesia).

API resmi Instagram terbatas. Rencana awal: kurasi manual/semi-otomatis,
lalu bertahap otomatis (scraping reels populer per hashtag ID).
Stub sementara mengembalikan [].
"""
from __future__ import annotations

import logging

from models import Trend

log = logging.getLogger("instagram")


def collect() -> list[Trend]:
    log.info("Instagram collector belum diaktifkan (stub).")
    return []
