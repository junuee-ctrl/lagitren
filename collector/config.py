"""Muat konfigurasi dari environment (.env)."""
from __future__ import annotations

import os
from dotenv import load_dotenv

# Muat .env dari folder collector (BOM-safe: utf-8-sig).
load_dotenv(encoding="utf-8-sig")


def _get(key: str, default: str = "") -> str:
    return (os.getenv(key) or default).strip()


# Cloudflare D1
CF_ACCOUNT_ID = _get("CLOUDFLARE_ACCOUNT_ID")
CF_D1_DATABASE_ID = _get("CLOUDFLARE_D1_DATABASE_ID")
CF_API_TOKEN = _get("CLOUDFLARE_API_TOKEN")

# YouTube
YOUTUBE_API_KEY = _get("YOUTUBE_API_KEY")

# Ollama / Claude
OLLAMA_HOST = _get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = _get("OLLAMA_MODEL", "gemma2:9b")
ANTHROPIC_API_KEY = _get("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL = _get("ANTHROPIC_MODEL", "claude-haiku-4-5")

# Telegram
TELEGRAM_BOT_TOKEN = _get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = _get("TELEGRAM_CHAT_ID")

# Umum
GEO = _get("GEO", "ID")
LANG = _get("LANG", "id")
DRY_RUN = _get("DRY_RUN", "0") in ("1", "true", "True", "yes")
# Ambil grafik minat pencarian via pytrends (best-effort; bisa diblokir Google).
FETCH_INTEREST = _get("FETCH_INTEREST", "1") in ("1", "true", "True", "yes")

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36 LagiTrenBot/1.0"
)
