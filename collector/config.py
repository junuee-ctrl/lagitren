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

# Shopee Affiliate Open API (produk + tautan afiliasi resmi)
SHOPEE_APP_ID = _get("SHOPEE_APP_ID")
SHOPEE_APP_SECRET = _get("SHOPEE_APP_SECRET")
SHOPEE_ENDPOINT = _get(
    "SHOPEE_ENDPOINT", "https://open-api.affiliate.shopee.co.id/graphql"
)
# Kata kunci kategori populer yang dipantau produk terlarisnya.
SHOPEE_KEYWORDS = [
    k.strip()
    for k in _get(
        "SHOPEE_KEYWORDS",
        "skincare,hp murah,fashion wanita,fashion pria,sepatu,"
        "aksesoris hp,peralatan rumah,gaming",
    ).split(",")
    if k.strip()
]

# TMDB (poster/sinopsis/rating untuk Netflix Top 10). Gratis di themoviedb.org.
TMDB_API_KEY = _get("TMDB_API_KEY")

# Telegram
TELEGRAM_BOT_TOKEN = _get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = _get("TELEGRAM_CHAT_ID")

# Umum
GEO = _get("GEO", "ID")
LANG = _get("LANG", "id")
DRY_RUN = _get("DRY_RUN", "0") in ("1", "true", "True", "yes")
# Ambil grafik minat pencarian via pytrends (best-effort; bisa diblokir Google).
FETCH_INTEREST = _get("FETCH_INTEREST", "1") in ("1", "true", "True", "yes")
# Coba Ollama untuk ringkasan (matikan di cloud tanpa GPU untuk hindari log spam).
USE_OLLAMA = _get("USE_OLLAMA", "1") in ("1", "true", "True", "yes")

# Cache ringkasan: gunakan kembali ringkasan tren yang tak berubah (hemat biaya
# LLM). Set SUMMARY_FORCE_REFRESH=1 untuk memaksa buat ulang semua ringkasan.
SUMMARY_FORCE_REFRESH = _get("SUMMARY_FORCE_REFRESH", "0") in ("1", "true", "True", "yes")

# ── Collector browser lokal (TikTok & Instagram) ────────────────
# Hashtag Instagram yang dipantau (dipisah koma). Diambil post teratasnya.
IG_HASHTAGS = [
    h.strip()
    for h in _get("IG_HASHTAGS", "viral,fyp,indonesia,beritaterkini,tiktok").split(",")
    if h.strip()
]
# Ambang suka minimum agar sebuah post IG dianggap "hits" (buang post recehan).
IG_MIN_LIKES = int(_get("IG_MIN_LIKES", "10000") or "10000")
# Satu profil browser persisten dipakai bersama (login TikTok & Instagram sekali).
BROWSER_PROFILE_DIR = _get("BROWSER_PROFILE_DIR", "./.browser_profile")
# Jalankan browser tampak (headful) — untuk login pertama kali.
BROWSER_HEADFUL = _get("BROWSER_HEADFUL", "0") in ("1", "true", "True", "yes")
# Sambungkan ke Chrome ASLI yang sudah login (CDP), mis. "http://localhost:9222".
# Ini cara paling andal: pakai sesi login Chrome Anda sendiri.
BROWSER_CDP = _get("BROWSER_CDP", "")

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36 LagiTrenBot/1.0"
)
