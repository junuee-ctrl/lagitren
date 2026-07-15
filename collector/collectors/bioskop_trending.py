"""Collector Bioskop Indonesia — film yang sedang tayang (TMDB now_playing).

Sumber: TMDB /movie/now_playing?region=ID (butuh TMDB_API_KEY, gratis).
Diurutkan berdasarkan popularitas TMDB. Menyediakan poster, sinopsis, rating,
genre, dan asal negara. Tanpa TMDB_API_KEY -> kembalikan [] aman.

CATATAN: ini "peringkat POPULARITAS film di bioskop" (metrik TMDB), BUKAN
angka penonton/box office resmi. Data & poster milik TMDB (cantumkan atribusi).
"""
from __future__ import annotations

import logging

import requests

import config
from models import Trend
from .base import make_id

log = logging.getLogger("bioskop")
LAST_DEBUG = ""

_NOW_PLAYING = "https://api.themoviedb.org/3/movie/now_playing"
_TMDB_IMG = "https://image.tmdb.org/t/p/w500{path}"
_MOVIE_URL = "https://www.themoviedb.org/movie/{id}"

_GENRE = {
    28: "Action", 12: "Adventure", 16: "Animation", 35: "Comedy", 80: "Crime",
    99: "Documentary", 18: "Drama", 10751: "Family", 14: "Fantasy", 36: "History",
    27: "Horror", 10402: "Music", 9648: "Mystery", 10749: "Romance",
    878: "Science Fiction", 53: "Thriller", 10752: "War", 37: "Western",
    10770: "TV Movie",
}

_LANG_LABEL = {
    "id": "Indonesia", "ko": "Korea", "th": "Thailand", "ja": "Jepang",
    "zh": "Tiongkok", "cn": "Tiongkok", "en": "AS/Inggris", "es": "Spanyol",
    "hi": "India", "tl": "Filipina", "fr": "Prancis", "de": "Jerman",
    "tr": "Turki", "ar": "Arab", "pt": "Portugis", "it": "Italia",
}


def _genres(ids) -> str:
    names = [_GENRE[i] for i in (ids or []) if i in _GENRE]
    return " / ".join(names[:2])


def collect(limit: int = 15) -> list[Trend]:
    global LAST_DEBUG
    if not config.TMDB_API_KEY:
        LAST_DEBUG = "TMDB_API_KEY kosong (hanya jalan di cloud)"
        log.info("Bioskop: TMDB_API_KEY tidak ada -> dilewati.")
        return []
    try:
        r = requests.get(
            _NOW_PLAYING,
            params={
                "api_key": config.TMDB_API_KEY,
                "region": config.GEO,
                "language": "id-ID",
                "page": 1,
            },
            timeout=25,
        )
        r.raise_for_status()
        results = r.json().get("results") or []
    except Exception as exc:
        LAST_DEBUG = f"gagal: {type(exc).__name__}"
        log.info("Bioskop: gagal ambil now_playing: %s", exc)
        return []

    results.sort(key=lambda m: m.get("popularity") or 0, reverse=True)

    out: list[Trend] = []
    for i, m in enumerate(results[:limit], start=1):
        title = (m.get("title") or m.get("original_title") or "").strip()
        if not title:
            continue
        mid = m.get("id")
        overview = (m.get("overview") or "").strip()
        va = m.get("vote_average")
        rating = round(float(va), 1) if isinstance(va, (int, float)) and va > 0 else None
        pop = int(m.get("popularity") or 0)
        genre = _genres(m.get("genre_ids"))
        lang = (m.get("original_language") or "").lower()
        origin = _LANG_LABEL.get(lang, lang.upper()) if lang else None

        bits = ["Film"]
        if genre:
            bits.append(genre)
        if origin:
            bits.append(origin)
        if rating:
            bits.append(f"⭐ {rating}")
        subtitle = " · ".join(bits)

        t = Trend(
            id=make_id("bioskop", title),
            platform="bioskop",
            rank=i,
            title=title,
            url=_MOVIE_URL.format(id=mid) if mid else "https://www.themoviedb.org/",
            subtitle=subtitle,
            metric=pop or None,
            metric_label="popularitas",
            thumbnail=_TMDB_IMG.format(path=m["poster_path"]) if m.get("poster_path") else None,
            source="TMDB · Bioskop Indonesia",
            extra={"ott": {"kind": "Film", "rating": rating, "synopsis": overview or None}},
        )
        ctx = [f"Film yang sedang tayang di bioskop Indonesia (peringkat populer {i})."]
        if genre:
            ctx.append(f"Genre: {genre}.")
        if origin:
            ctx.append(f"Asal/bahasa: {origin}.")
        if overview:
            ctx.append(overview)
        t.__dict__["_context"] = " ".join(ctx)[:500]
        out.append(t)

    LAST_DEBUG = f"{len(out)} film (now_playing ID), {sum(1 for t in out if t.thumbnail)} poster"
    log.info("Bioskop: %s", LAST_DEBUG)
    return out
