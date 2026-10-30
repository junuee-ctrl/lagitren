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

import html
import io
import re
import json
from pathlib import Path
import logging

import requests

import config
from models import Trend
from .base import make_id

log = logging.getLogger("netflix")

LAST_DEBUG = ""
_ENRICH_NOTE = ""  # diagnostik enrichment (status HTTP iTunes/TMDB pertama)

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


# --- Cadangan: halaman Tudum (HTML) -----------------------------------------
# File TSV kadang terlambat diperbarui dibanding halaman Tudum (insiden
# 2026-10-30: halaman sudah minggu 19–25 Okt, TSV masih minggu sebelumnya).
_TUDUM_PAGES = (
    ("Films", "https://www.netflix.com/tudum/top10/indonesia"),
    ("TV", "https://www.netflix.com/tudum/top10/indonesia/tv"),
)
_SEASON_RE = re.compile(
    r"\s*:\s*(Season\s+\d+|Limited Series|Part\s+\d+|Volume\s+\d+|"
    r"Musim\s+\d+|Book\s+\d+|Chapter\s+\d+|Collection\s+\d+)\s*$",
    re.I,
)
_WEEK_RE = re.compile(
    r"(\d{1,2})/(\d{1,2})/(\d{2,4})\s*[-\u2013]\s*(\d{1,2})/(\d{1,2})/(\d{2,4})"
)


def _strip_tags(h: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", " ", h)).replace("\xa0", " ").strip()


def parse_tudum_html(page: str, category: str) -> tuple[str, list[dict]]:
    """(week_end ISO, rows) dari HTML halaman Tudum. Murni (mudah diuji)."""
    week = ""
    m = _WEEK_RE.search(_strip_tags(page))
    if m:
        mo, d, y = int(m.group(4)), int(m.group(5)), int(m.group(6))
        y = y + 2000 if y < 100 else y
        week = f"{y:04d}-{mo:02d}-{d:02d}"
    rows: list[dict] = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", page, re.S | re.I):
        cells = [
            re.sub(r"\s+", " ", _strip_tags(c))
            for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S | re.I)
        ]
        cells = [c for c in cells if c]
        if len(cells) < 2 or not re.fullmatch(r"\d{1,2}", cells[0]):
            continue
        rank = int(cells[0])
        title = next((c for c in cells[1:] if re.search(r"[^\W\d_]", c)), "")
        if not title:
            continue
        nums = [c for c in cells[1:] if re.fullmatch(r"\d{1,3}", c)]
        season = ""
        if category == "TV":
            mm = _SEASON_RE.search(title)
            if mm:
                season = title
                title = title[: mm.start()].strip()
        rows.append({
            "week": week, "category": category, "rank": str(rank),
            "title": title, "season": season,
            "weeks_in_top10": nums[-1] if nums else "",
        })
    rows = [r for r in rows if 1 <= int(r["rank"]) <= 10]
    return week, rows


def _fetch_tudum_rows() -> tuple[str, list[dict]]:
    weeks, out = [], []
    for cat, url in _TUDUM_PAGES:
        try:
            r = requests.get(url, headers={"User-Agent": _BROWSER_UA}, timeout=40)
            if r.status_code != 200:
                log.info("Tudum %s -> HTTP %s", cat, r.status_code)
                continue
            wk, rows = parse_tudum_html(r.text, cat)
            log.info("Tudum %s: minggu %s, %d baris", cat, wk or "?", len(rows))
            if wk and len(rows) >= 5:
                weeks.append(wk)
                out.extend(rows)
        except Exception as exc:
            log.info("Tudum %s gagal: %s", cat, exc)
    if not out:
        return "", []
    latest = max(weeks)
    return latest, [r for r in out if r["week"] == latest]


def _is_tv(category: str) -> bool:
    return "tv" in (category or "").lower()


_LANG_LABEL = {
    "id": "Indonesia", "ko": "Korea", "th": "Thailand", "ja": "Jepang",
    "zh": "Tiongkok", "cn": "Tiongkok", "en": "berbahasa Inggris (AS/Inggris)",
    "es": "berbahasa Spanyol", "hi": "India", "tl": "Filipina", "fr": "Prancis",
    "de": "Jerman", "tr": "Turki", "ar": "berbahasa Arab", "pt": "berbahasa Portugis",
}


def _tmdb_enrich(title: str, is_tv: bool) -> dict:
    """Cari poster, sinopsis, rating via TMDB. Best-effort.

    Sinopsis diambil id-ID; bila kosong (banyak film Indonesia belum punya
    terjemahan) → fallback ke en-US supaya kolom sinopsis tetap terisi.
    """
    if not config.TMDB_API_KEY:
        return {}
    kind = "tv" if is_tv else "movie"

    # Judul alternatif: judul utuh, lalu bagian sebelum ":" / " - "
    # (mis. "Adili Idola Celebrity Roast: Reza Arap" -> "Adili Idola Celebrity Roast").
    queries = [title]
    for sep in (":", " - "):
        if sep in title:
            base = title.split(sep)[0].strip()
            if base and base not in queries:
                queries.append(base)

    def _search(lang: str) -> dict | None:
        first = None
        for q in queries:
            for k in (kind, "movie" if kind == "tv" else "tv"):
                r = requests.get(
                    _TMDB_SEARCH.format(kind=k),
                    params={
                        "api_key": config.TMDB_API_KEY,
                        "query": q,
                        "language": lang,
                        "include_adult": "false",
                        "region": "ID",
                    },
                    timeout=20,
                )
                r.raise_for_status()
                results = r.json().get("results") or []
                if results and first is None:
                    first = results[0]
                # Utamakan hasil yang punya poster.
                for res in results[:5]:
                    if res.get("poster_path"):
                        return res
        return first

    try:
        top = _search("id-ID")
        if not top:
            return {}
        out: dict = {}
        if top.get("poster_path"):
            out["poster"] = _TMDB_IMG.format(path=top["poster_path"])
        overview = (top.get("overview") or "").strip()
        if not overview:
            en = _search("en-US")
            if en:
                overview = (en.get("overview") or "").strip()
        if overview:
            out["synopsis"] = overview[:500]
        va = top.get("vote_average")
        if isinstance(va, (int, float)) and va > 0:
            out["rating"] = round(float(va), 1)
        lang = (top.get("original_language") or "").lower()
        if lang:
            out["origin"] = _LANG_LABEL.get(lang, lang.upper())
        return out
    except Exception as exc:
        log.info("TMDB '%s' gagal: %s", title, exc)
        return {}


def _itunes_enrich(title: str, is_tv: bool) -> dict:
    """Poster & deskripsi via iTunes Search API — TANPA kunci/pendaftaran.

    Cadangan bila TMDB tidak tersedia. Deskripsi iTunes sering berbahasa
    Inggris; poster tetap berguna sebagai thumbnail.
    """
    global _ENRICH_NOTE
    media = "tvShow" if is_tv else "movie"
    for country in ("ID", "US"):
        try:
            r = requests.get(
                _ITUNES_URL,
                params={"term": title, "media": media, "limit": 1, "country": country},
                headers={"User-Agent": _BROWSER_UA},
                timeout=20,
            )
            if not _ENRICH_NOTE:
                _ENRICH_NOTE = f"itunes {country} http={r.status_code}"
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
            if not _ENRICH_NOTE:
                _ENRICH_NOTE = f"itunes err={type(exc).__name__}"
            log.info("iTunes '%s' gagal: %s", title, exc)
    return {}


def _wikipedia_enrich(title: str, is_tv: bool) -> dict:
    """Poster + sinopsis Bahasa Indonesia via Wikipedia — TANPA kunci.

    Pakai generator=search agar judul film/serial Indonesia lebih mudah cocok.
    Cakupan konten Indonesia jauh lebih baik daripada iTunes.
    """
    global _ENRICH_NOTE
    hint = "seri televisi" if is_tv else "film"
    for lang in ("id", "en"):
        try:
            r = requests.get(
                f"https://{lang}.wikipedia.org/w/api.php",
                params={
                    "action": "query",
                    "format": "json",
                    "generator": "search",
                    "gsrsearch": f"{title} {hint}",
                    "gsrlimit": 1,
                    "prop": "pageimages|extracts",
                    "piprop": "thumbnail",
                    "pithumbsize": 500,
                    "exintro": 1,
                    "explaintext": 1,
                    "redirects": 1,
                },
                headers={"User-Agent": _BROWSER_UA},
                timeout=20,
            )
            if not _ENRICH_NOTE:
                _ENRICH_NOTE = f"wiki {lang} http={r.status_code}"
            if r.status_code != 200:
                continue
            pages = (r.json().get("query") or {}).get("pages") or {}
            if not pages:
                continue
            page = next(iter(pages.values()))
            out: dict = {}
            thumb = (page.get("thumbnail") or {}).get("source")
            if thumb:
                out["poster"] = thumb
            extract = (page.get("extract") or "").strip()
            if extract:
                out["synopsis"] = extract[:500]
            # Tolak halaman yang bukan tentang film/serial (mis. foto aktris).
            low = extract.lower()[:400]
            if not any(w in low for w in ("film", "serial", "seri ", "series", "drama", "sinetron", "acara", "movie", "anime", "dokumenter", "documentary", "reality")):
                log.info("Wikipedia '%s': halaman bukan film/serial, poster diabaikan", title)
                out.pop("poster", None)
                continue
            if out.get("poster"):  # butuh poster; kalau cuma teks, coba sumber lain
                return out
        except Exception as exc:
            if not _ENRICH_NOTE:
                _ENRICH_NOTE = f"wiki err={type(exc).__name__}"
            log.info("Wikipedia '%s' gagal: %s", title, exc)
    return {}


_OVERRIDES_PATH = Path(__file__).resolve().parent.parent / "poster_overrides.json"


def _poster_override(title: str) -> str | None:
    """Poster manual (poster_overrides.json) — menang atas sumber otomatis."""
    try:
        data = json.loads(_OVERRIDES_PATH.read_text(encoding="utf-8"))
    except Exception:
        return None
    t = (title or "").strip().lower()
    best = None
    for key, url in data.items():
        if key.startswith("_") or not isinstance(url, str):
            continue
        if t == key or t.startswith(key):
            if best is None or len(key) > len(best[0]):
                best = (key, url)
    return best[1] if best else None


def _enrich(title: str, is_tv: bool) -> dict:
    """Perkaya poster/sinopsis, semua opsional & tanpa henti kalau gagal.

    Urutan: TMDB (bila ada kunci; terbaik) → Wikipedia ID (tanpa kunci,
    sinopsis Indonesia) → iTunes (tanpa kunci, cakupan internasional).
    Poster manual (poster_overrides.json) selalu dipakai bila ada.
    """
    manual = _poster_override(title)
    if manual:
        info = _enrich_auto(title, is_tv)
        info["poster"] = manual
        return info
    return _enrich_auto(title, is_tv)


def _enrich_auto(title: str, is_tv: bool) -> dict:
    if config.TMDB_API_KEY:
        info = _tmdb_enrich(title, is_tv)
        if info.get("poster") or info.get("synopsis"):
            return info
    wiki = _wikipedia_enrich(title, is_tv)
    if wiki.get("poster"):
        return wiki
    itunes = _itunes_enrich(title, is_tv)
    merged = dict(itunes)
    if wiki.get("synopsis") and not merged.get("synopsis"):
        merged["synopsis"] = wiki["synopsis"]
    return merged


def collect(limit: int = 20) -> list[Trend]:
    global LAST_DEBUG, _ENRICH_NOTE
    _ENRICH_NOTE = ""
    tsv = _fetch_tsv()
    rows = parse_country_rows(tsv, "ID") if tsv else []
    tsv_week = max((r["week"] for r in rows), default="")
    log.info("Netflix TSV: minggu %s, %d baris", tsv_week or "-", len(rows))

    # Halaman Tudum sering lebih baru dari TSV → pakai bila minggunya lebih baru.
    page_week, page_rows = _fetch_tudum_rows()
    if page_rows and page_week > tsv_week:
        log.info("Netflix: pakai halaman Tudum (minggu %s > TSV %s)", page_week, tsv_week or "-")
        rows = page_rows

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
        if info.get("origin"):
            bits.append(info["origin"])
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
        if info.get("origin"):
            ctx.append(f"Asal/bahasa: {info['origin']}.")
        if info.get("synopsis"):
            ctx.append(info["synopsis"])
        t.__dict__["_context"] = " ".join(ctx)[:500]
        trends.append(t)

    posters = sum(1 for t in trends if t.thumbnail)
    LAST_DEBUG = (
        f"{len(trends)} judul (minggu {rows[0]['week']}), "
        f"{posters} poster; {_ENRICH_NOTE or 'no-enrich'}"
    )
    log.info("Netflix: %d judul, %d poster. %s", len(trends), posters, _ENRICH_NOTE)
    missing = [t.title for t in trends if not t.thumbnail]
    if missing:
        log.warning("POSTER KOSONG (%d): %s -> tambahkan ke collector/poster_overrides.json", len(missing), " | ".join(missing))
    return trends
