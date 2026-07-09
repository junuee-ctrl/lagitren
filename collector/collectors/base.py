"""Utilitas bersama untuk semua collector."""
from __future__ import annotations

import re
import unicodedata


def slugify(text: str, max_len: int = 60) -> str:
    """Ubah teks jadi slug aman untuk ID (huruf-kecil, tanda hubung)."""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text[:max_len] or "item"


def make_id(platform: str, key: str) -> str:
    """ID stabil per item, mis. 'google:iphone-16-harga'."""
    return f"{platform}:{slugify(key)}"
