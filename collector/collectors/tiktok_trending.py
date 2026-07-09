"""Collector TikTok Viral (Indonesia).

Rencana (prioritas minggu ke-3): TikTok Creative Center (hashtag & video
populer per region ID) atau API tidak resmi. Hormati rate limit.
Stub sementara mengembalikan [].
"""
from __future__ import annotations

import logging

from models import Trend

log = logging.getLogger("tiktok")


def collect() -> list[Trend]:
    log.info("TikTok collector belum diaktifkan (stub).")
    return []
