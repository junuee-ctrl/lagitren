"""Mesin intelijen tren — dasar untuk Laporan Intelijen Tren (B2B).

Semua angka di sini DIHITUNG DARI ARSIP `trend_snapshots`. Tidak ada nilai
yang dikarang: bila sebuah dimensi tidak dapat diukur dari data kami
(mis. demografi audiens), dimensi itu TIDAK dikeluarkan di sini.

Yang dihasilkan per tren:
  - riwayat peringkat harian (untuk grafik garis waktu)
  - velocity   : perbaikan peringkat pada jendela terakhir
  - persistence: jumlah hari berbeda muncul di papan
  - peak       : peringkat terbaik yang pernah dicapai
  - lintas platform: klaster topik yang muncul di >1 platform
  - Trend Score: komposit 0–100 dari empat komponen di atas
  - tahap daur hidup: naik | puncak | turun | stabil

Dua metode pengelompokan lintas platform, keduanya deterministik:
  1. `literal` — irisan token judul (nama, tajuk, tagar yang berulang).
  2. `tema`    — kamus tema yang kami kelola (mis. bencana alam), sehingga
                 "#abuvulkanik", "berita gempa hari ini", dan "Cincin Api"
                 dikenali sebagai satu topik meski teksnya berbeda.

Pemakaian:
  python intel.py            # jendela 7 hari (default)
  python intel.py 14         # jendela 14 hari
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone

from database import D1Client

# ── kamus tema (IP kami; deterministik & bisa diaudit) ────────────────
THEMES: dict[str, list[str]] = {
    "Bencana alam": [
        "vulkanik", "erupsi", "gunung", "gempa", "tsunami", "banjir", "longsor",
        "karhutla", "asap", "abu", "bmkg", "magma", "siaga", "evakuasi",
        "cincin api", "ring of fire", "bencana", "kebakaran",
    ],
    "K-pop & idol": [
        "kpop", "k-pop", "enhypen", "nct", "blackpink", "jennie", "lisa",
        "bigbang", "comeback", "twice", "seventeen", "bts", "aespa",
        "hearts2hearts", "cortis", "girls generation", "mv", "idol",
    ],
    "Sepak bola": [
        "liga", "persib", "persija", "persebaya", "persik", "timnas", "piala",
        "madrid", "barcelona", "arsenal", "juventus", "milan", "fc", "vs",
        "bola", "gol", "mu ", "psm", "bhayangkara",
    ],
    "Bantuan sosial": [
        "bansos", "pkh", "bpnt", "desil", "dtsen", "kemensos", "bantuan",
        "kartu prakerja", "pencairan", "subsidi",
    ],
    "Belanja & promo": [
        "diskon", "promo", "gajian", "checkout", "shopee", "tokopedia",
        "flash sale", "gratis ongkir", "voucher", "harbolnas", "cod",
    ],
    "Tontonan & sinetron": [
        "sinetron", "trailer", "film", "netflix", "drama", "episode", "series",
        "bioskop", "tayang",
    ],
    "Musik & lagu": [
        "lagu", "official music", "lyrics", "cover", "dangdut", "koplo",
        "single", "album", "remix",
    ],
    "Keuangan & kripto": [
        "crypto", "kripto", "bitcoin", "binance", "saham", "ihsg", "rupiah",
        "emas", "bank", "investasi",
    ],
    "Politik & kebijakan": [
        "presiden", "menteri", "dpr", "ruu", "prabowo", "kabinet", "demo",
        "gubernur", "kpk", "pemilu", "pajak",
    ],
    "Game & esports": [
        "mlbb", "mpl", "mobile legends", "free fire", "pubg", "gangstar",
        "gameplay", "esports", "game",
    ],
}

STOP = {
    "yang", "dan", "di", "ke", "dari", "untuk", "dengan", "pada", "ini", "itu",
    "ada", "tidak", "bisa", "akan", "sudah", "saat", "hari", "baru", "lebih",
    "the", "of", "in", "to", "for", "and", "a", "is", "on", "official", "video",
    "full", "live", "new", "part", "feat", "ft", "mv", "vs",
}


def _rows(data) -> list[dict]:
    res = data.get("result")
    return (res[0].get("results") or []) if isinstance(res, list) and res else []


def tokens(title: str) -> set[str]:
    t = re.sub(r"[#_]", " ", (title or "").lower())
    t = re.sub(r"[^a-z0-9\s]", " ", t)
    return {w for w in t.split() if len(w) >= 4 and w not in STOP}


_THEME_RE = {
    name: re.compile(r"\b(?:" + "|".join(re.escape(k.strip()) for k in keys) + r")\b")
    for name, keys in THEMES.items()
}


def theme_of(title: str) -> str | None:
    """Tema dari kamus, dicocokkan pada BATAS KATA.

    Penting: pencocokan substring keliru ("sabun" mengandung "abu",
    "mainan anak" mengandung "anak" seperti "anak krakatau"), sehingga
    produk kecantikan sempat masuk klaster bencana. Batas kata mencegahnya.
    """
    t = re.sub(r"[#_]", " ", (title or "").lower())
    t = re.sub(r"[^a-z0-9\s]", " ", t)
    for name, rx in _THEME_RE.items():
        if rx.search(t):
            return name
    return None


def _stage(series: list[dict]) -> str:
    """Tahap daur hidup dari deret peringkat harian (angka kecil = lebih baik)."""
    ranks = [s["best_rank"] for s in series if s.get("best_rank") is not None]
    if len(ranks) < 2:
        return "baru"
    best = min(ranks)
    first_half = ranks[: max(1, len(ranks) // 2)]
    last_half = ranks[max(1, len(ranks) // 2):]
    avg_a = sum(first_half) / len(first_half)
    avg_b = sum(last_half) / len(last_half)
    if ranks[-1] == best and avg_b < avg_a:
        return "puncak"
    if avg_b < avg_a - 0.5:
        return "naik"
    if avg_b > avg_a + 0.5:
        return "turun"
    return "stabil"


def _velocity(series: list[dict]) -> int:
    """0–35. Perbaikan peringkat + bonus kemunculan baru."""
    ranks = [s["best_rank"] for s in series if s.get("best_rank") is not None]
    if not ranks:
        return 0
    if len(ranks) == 1:
        return 18  # baru muncul: momentum belum terukur, nilai tengah
    delta = ranks[0] - ranks[-1]          # positif = naik peringkat
    v = 18 + delta * 2.2
    return int(max(0, min(35, round(v))))


def _persistence(days_on: int, window: int) -> int:
    """0–25. Proporsi hari muncul dalam jendela."""
    return int(round(min(25, 25 * days_on / max(1, window))))


def _peak(best_rank: int | None) -> int:
    """0–15. Peringkat terbaik yang dicapai."""
    if not best_rank:
        return 0
    if best_rank == 1:
        return 15
    if best_rank <= 3:
        return 12
    if best_rank <= 5:
        return 9
    if best_rank <= 10:
        return 6
    return 3


def build(db: D1Client, window: int = 7) -> dict:
    raw = _rows(db.query(
        "SELECT trend_id, platform, title, MIN(rank) AS best_rank, "
        "date(snapshot_at) AS day, COUNT(*) AS samples "
        f"FROM trend_snapshots WHERE snapshot_at >= datetime('now', '-{int(window)} days') "
        "GROUP BY trend_id, day ORDER BY trend_id, day", []))

    per: dict[str, dict] = {}
    for r in raw:
        tid = r["trend_id"]
        e = per.setdefault(tid, {
            "trend_id": tid, "platform": r["platform"], "title": r["title"],
            "daily": [],
        })
        e["daily"].append({"day": r["day"], "best_rank": r["best_rank"]})

    trends = []
    for e in per.values():
        series = sorted(e["daily"], key=lambda d: d["day"])
        best = min((s["best_rank"] for s in series), default=None)
        vel = _velocity(series)
        pers = _persistence(len(series), window)
        pk = _peak(best)
        trends.append({
            **e,
            "daily": series,
            "first_seen": series[0]["day"],
            "last_seen": series[-1]["day"],
            "days_on": len(series),
            "best_rank": best,
            "current_rank": series[-1]["best_rank"],
            "stage": _stage(series),
            "score_parts": {"velocity": vel, "persistence": pers, "peak": pk},
            "theme": theme_of(e["title"]),
        })

    # ── klaster lintas platform ──────────────────────────────────────
    clusters: list[dict] = []
    seen_keys: set[frozenset] = set()

    # Kategori (tema) BUKAN sinyal lintas platform — ia menunjukkan bobot
    # kategori dalam sepekan. Disimpan terpisah agar tidak disalahartikan
    # sebagai "satu topik yang menyeberang platform".
    by_theme: dict[str, list[dict]] = defaultdict(list)
    for t in trends:
        if t["theme"]:
            by_theme[t["theme"]].append(t)
    categories = []
    for name, group in by_theme.items():
        per_plat: dict[str, int] = defaultdict(int)
        for g in group:
            per_plat[g["platform"]] += 1
        categories.append({
            "label": name,
            "n_trends": len(group),
            "platforms": dict(sorted(per_plat.items(), key=lambda kv: -kv[1])),
            "top": sorted(group, key=lambda g: g["best_rank"] or 99)[:5],
        })
    categories.sort(key=lambda c: -c["n_trends"])

    # literal: hanya token DISTINGTIF yang boleh menautkan dua tren.
    # Token umum ("anak", "2026", "sticky") muncul di banyak judul tak
    # berkaitan dan menghasilkan klaster palsu, jadi token yang dipakai di
    # lebih dari MAX_DF tren dibuang lebih dulu.
    MAX_DF = 6
    tok_raw = {t["trend_id"]: tokens(t["title"]) for t in trends}
    df: dict[str, int] = defaultdict(int)
    for s_ in tok_raw.values():
        for w in s_:
            df[w] += 1
    tok = {
        tid: {w for w in ws if df[w] <= MAX_DF and not w.isdigit()}
        for tid, ws in tok_raw.items()
    }

    seen: set[str] = set()
    for a in trends:
        if a["trend_id"] in seen or not tok[a["trend_id"]]:
            continue
        grp = [a]
        for b in trends:
            if b["trend_id"] == a["trend_id"] or b["platform"] == a["platform"]:
                continue
            shared_ab = tok[a["trend_id"]] & tok[b["trend_id"]]
            strong = len(shared_ab) >= 2 or any(
                df[w] <= 2 and len(w) >= 6 for w in shared_ab
            )
            if strong:
                grp.append(b)
        plats = sorted({g["platform"] for g in grp})
        if len(plats) < 2:
            continue
        key = frozenset(g["trend_id"] for g in grp)
        if key in seen_keys:
            continue
        seen_keys.add(key)
        for g in grp:
            seen.add(g["trend_id"])
        shared = set.intersection(*[tok[g["trend_id"]] for g in grp]) or set()
        clusters.append({
            "label": " · ".join(sorted(shared)[:3]) or a["title"][:40],
            "method": "entitas", "platforms": plats,
            "members": sorted(grp, key=lambda g: g["best_rank"] or 99)[:6],
        })

    # skor lintas platform (0–25) diberikan ke anggota klaster
    cross_of: dict[str, int] = {}
    for c in clusters:
        pts = min(25, 8 * len(c["platforms"]))
        for m in c["members"]:
            cross_of[m["trend_id"]] = max(cross_of.get(m["trend_id"], 0), pts)

    for t in trends:
        t["score_parts"]["cross_platform"] = cross_of.get(t["trend_id"], 0)
        t["score"] = sum(t["score_parts"].values())

    trends.sort(key=lambda t: -t["score"])
    clusters.sort(key=lambda c: (-len(c["platforms"]), c["label"]))

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "window_days": window,
        "scoring": {
            "velocity": "0-35 · perbaikan peringkat dalam jendela",
            "cross_platform": "0-25 · jumlah platform tempat topik muncul",
            "persistence": "0-25 · jumlah hari berbeda muncul di papan",
            "peak": "0-15 · peringkat terbaik yang dicapai",
        },
        "radar": trends[:25],
        "cross_platform": clusters[:10],
        "categories": categories[:10],
        "total_trends": len(trends),
    }


def main() -> None:
    db = D1Client()
    if not db._configured():
        print("D1 tidak dikonfigurasi.", file=sys.stderr)
        sys.exit(1)
    window = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 7
    print(json.dumps(build(db, window), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
