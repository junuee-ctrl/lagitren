"""Collector Netflix Top 10 Indonesia (OTT) — sumber resmi Tudum.

Netflix mempublikasikan daftar Top 10 mingguan RESMI per negara di Tudum,
termasuk file data massal (TSV/XLSX). Kita ambil file negara, saring
Indonesia (ID), pakai minggu terbaru, lalu (opsional) perkaya poster/sinopsis
via TMDB.

  Data : https://www.netflix.com/tudum/top10/data/all-weeks-countries.tsv
  TMDB : butuh TMDB_API_KEY (gratis, daftar di themoviedb.org)

Tanpa TMDB → tetap jalan (judul + peringkat, tanpa poster/sinopsis).
Bila IP diblokir Netflix (mis. sebagian runner cloud) → kembalikan [] aman;
jalankan collector ini dari PC lokal (IP rumah) bila perlu.
"""
from __future__ import annotations

import io
import logging

import requests

import config
from models import Trend
from .base import make_id

log = logging.getLogger("netflix")

LAST_DEBUG = ""

_BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)

_TSV_URL = "https://www.netflix.com/tudum/top10/data/all-weeks-countries.tsv"
_XLSX_URL = "https://www.netflix.com/tudum/top10/data/all-weeks-countries.xlsx"

_SEARCH_URL = "https://www.netflix.com/id/search?q={q}"
_TMDB_SEARCH = "https://api.themoviedb.org/3/search/{kind}"
_TMDB_IMG = "https://image.tmdb.org/t/p/w500{path}"
_ITUNES_URL = "https://itunes.apple.com/search"


def _fetch_tsv() -> str | None:
    """Ambil file TSV negara (utama). XLSX sebagai cadangan."""
    try:
        r = requests.get(_TSV_URL, headers={"User-Agent": _BROWSER_UA}, timeout=40)
        if r.status_code == 200 and r.text.strip():
            return r.text
        log.info("Netflix TSV -> HTTP %s", r.status_code)
    except Exception as exc:
        log.info("Netflix TSV gagal: %s", exc)
    # Cadangan: XLSX (butuh openpyxl).
    try:
        import openpyxl  # type: ignore

        r = requests.get(_XLSX_URL, headers={"User-Agent": _BROWSER_UA}, timeout=60)
        if r.status_code != 200:
            log.info("Netflix XLSX -> HTTP %s", r.status_code)
            return None
        wb = openpyxl.load_workbook(io.BytesIO(r.content), read_only=True)
        ws = wb.active
        rows = ws.iter_rows(values_only=True)
        header = next(rows)
        lines = ["\t".join("" if c is None else str(c) for c in header)]
        for row in rows:
            lines.append("\t".join("" if c is None else str(c) for c in row))
        return "\n".join(lines)
    except Exception as exc:
        log.info("Netflix XLSX gagal: %s", exc)
    return None


def parse_country_rows(tsv: str, iso2: str = "ID") -> list[dict]:
    """Saring baris satu negara pada MINGGU TERBARU. Murni (mudah diuji)."""
    lines = tsv.replace("\r", "").split("\n")
    if not lines:
        return []
    header = [h.strip().lower() for h in lines[0].split("\t")]
    idx = {name: i for i, name in enumerate(header)}

    def col(row: list[str], name: str) -> str:
        i = idx.get(name)
        return row[i].strip() if i is not None and i < len(row) else ""

    rows: list[dict] = []
    for line in lines[1:]:
        if not line.strip():
            continue
        parts = line.split("\t")
        if col(parts, "country_iso2").upper() != iso2.upper():
            continue
        rows.append(
            {
                "week": col(parts, "week"),
                "category": col(parts, "category"),
                "rank": col(parts, "weekly_rank"),
                "title": col(parts, "show_title"),
                "season": col(parts, "season_title"),
                "weeks_in_top10": col(parts, "cumulative_weeks_in_top10"),
            }
        )
    if not rows:
        return []
    latest = max(r["week"] for r in rows if r["week"])
    return [r for r in rows if r["week"] == latest and r["title"]]


def _is_tv(category: str) -> bool:
    return "tv" in (category or "").lower()


def _tmdb_enrich(title: str, is_tv: bool) -> dict:
    """Cari poster, sinopsis (id-ID), rating, genre via TMDB. Best-effort."""
    if not config.TMDB_API_KEY:
        return {}
    kind = "tv" if is_tv else "movie"
    try:
        r = requests.get(
            _TMDB_SEARCH.format(kind=kind),
            params={
                "api_key": config.TMDB_API_KEY,
                "query": title,
                "language": "id-ID",
                "include_adult": "false",
                "region": "ID",
            },
            timeout=20,
        )
        r.raise_for_status()
        results = r.json().get("results") or []
        if not results:
            return {}
        top = results[0]
        out: dict = {}
        if top.get("poster_path"):
            out["poster"] = _TMDB_IMG.format(path=top["poster_path"])
        overview = (top.get("overview") or "").strip()
        if overview:
            out["synopsis"] = overview
        va = top.get("vote_average")
        if isinstance(va, (int, float)) and va > 0:
            out["rating"] = round(float(va), 1)
        return out
    except Exception as exc:
        log.info("TMDB '%s' gagal: %s", title, exc)
        return {}


def _itunes_enrich(title: str, is_tv: bool) -> dict:
    """Poster & deskripsi via iTunes Search API — TANPA kunci/pendaftaran.

    Cadangan bila TMDB tidak tersedia. Deskripsi iTunes sering berbahasa
    Inggris; poster tetap berguna sebagai thumbnail.
    """
    media = "tvShow" if is_tv else "movie"
    for country in ("ID", "US"):
        try:
            r = requests.get(
                _ITUNES_URL,
                params={"term": title, "media": media, "limit": 1, "country": country},
                headers={"User-Agent": _BROWSER_UA},
                timeout=20,
            )
            if r.status_code != 200:
                continue
            results = r.json().get("results") or []
            if not results:
                continue
            top = results[0]
            out: dict = {}
            art = top.get("artworkUrl100") or top.get("artworkUrl60") or ""
            if art:
                out["poster"] = art.replace("100x100bb", "600x600bb").replace(
                    "60x60bb", "600x600bb"
                )
            desc = (top.get("longDescription") or top.get("shortDescription") or "").strip()
            if desc:
                out["synopsis"] = desc[:500]
            if out:
                return out
        except Exception as exc:
            log.info("iTunes '%s' gagal: %s", title, exc)
    return {}


def _enrich(title: str, is_tv: bool) -> dict:
    """Perkaya poster/sinopsis: TMDB (bila ada kunci) → iTunes (tanpa kunci)."""
    if config.TMDB_API_KEY:
        info = _tmdb_enrich(title, is_tv)
        if info.get("poster") or info.get("synopsis"):
            return info
    return _itunes_enrich(title, is_tv)


def collect(limit: int = 20) -> list[Trend]:
    global LAST_DEBUG
    tsv = _fetch_tsv()
    if not tsv:
        LAST_DEBUG = "tidak bisa mengambil data Tudum (IP mungkin diblokir; coba lokal)"
        log.warning("Netflix: %s", LAST_DEBUG)
        return []

    rows = parse_country_rows(tsv, "ID")
    if not rows:
        LAST_DEBUG = "tidak ada baris Indonesia pada data Tudum"
        log.warning("Netflix: %s", LAST_DEBUG)
        return []

    # Film dulu (rank naik), lalu serial TV.
    def sort_key(r: dict):
        try:
            rk = int(r["rank"])
        except (ValueError, TypeError):
            rk = 999
        return (_is_tv(r["category"]), rk)

    rows.sort(key=sort_key)
    rows = rows[:limit]

    trends: list[Trend] = []
    for i, r in enumerate(rows, start=1):
        is_tv = _is_tv(r["category"])
        title = r["title"].strip()
        kind_label = "Serial TV" if is_tv else "Film"

        info = _enrich(title, is_tv)

        # Subtitle: jenis · rating · minggu di Top 10.
        bits = [kind_label]
        if info.get("rating"):
            bits.append(f"⭐ {info['rating']}")
        try:
            wk = int(r.get("weeks_in_top10") or 0)
            if wk > 0:
                bits.append(f"{wk} mgg di Top 10")
        except (ValueError, TypeError):
            pass
        subtitle = " · ".join(bits)

        t = Trend(
            id=make_id("netflix", title),
            platform="netflix",
            rank=i,
            title=title,
            url=_SEARCH_URL.format(q=requests.utils.quote(title)),
            subtitle=subtitle,
            metric=None,
            thumbnail=info.get("poster"),
            source="Netflix Indonesia",
            extra={"ott": {
                "kind": kind_label,
                "rating": info.get("rating"),
                "synopsis": info.get("synopsis"),
                "weeks": r.get("weeks_in_top10"),
                "rank": r.get("rank"),
            }},
        )
        # Konteks AI: sinopsis + posisi → "kenapa rame di Netflix".
        ctx = [f"{kind_label} peringkat {r.get('rank')} Netflix Indonesia."]
        if info.get("synopsis"):
            ctx.append(info["synopsis"])
        t.__dict__["_context"] = " ".join(ctx)[:500]
        trends.append(t)

    LAST_DEBUG = f"{len(trends)} judul (minggu {rows[0]['week']})"
    log.info("Netflix: %d judul.", len(trends))
    return trends
