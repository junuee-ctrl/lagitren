"""Lembar fakta (factsheet) dari arsip D1 — bahan baku artikel /artikel.

Prinsip (rencana AdSense §2): SEMUA angka dihitung di sini oleh kode.
AI (artikel_writer) hanya menuliskan narasi dari lembar fakta ini dan
dilarang menambah informasi lain.

Sumber: tabel `trend_snapshots` (potret peringkat tiap run — mulai terisi
2026-08-18) dan `trends` (kondisi terkini). Analisis mingguan baru bermakna
setelah snapshot terkumpul >= 7 hari.

Pemakaian:
  python factsheet.py weekly            # cetak lembar fakta mingguan (JSON)
  python factsheet.py trend google:xxx  # lembar fakta satu tren
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone

from database import D1Client

PLATFORMS = ["google", "youtube", "instagram", "tiktok", "twitter", "netflix", "shopee"]


def _rows(data) -> list[dict]:
    res = data.get("result")
    return (res[0].get("results") or []) if isinstance(res, list) and res else []


def _norm_title(t: str) -> str:
    return " ".join((t or "").lower().replace("#", "").split())


def snapshot_coverage(db: D1Client) -> dict:
    """Berapa hari data snapshot yang sudah terkumpul (gerbang kelayakan)."""
    rows = _rows(db.query(
        "SELECT MIN(snapshot_at) AS first, MAX(snapshot_at) AS last, COUNT(*) AS n "
        "FROM trend_snapshots", []))
    r = rows[0] if rows else {}
    days = 0.0
    if r.get("first") and r.get("last"):
        try:
            f = datetime.fromisoformat(str(r["first"]))
            l = datetime.fromisoformat(str(r["last"]))
            days = (l - f).total_seconds() / 86400
        except Exception:
            days = 0.0
    return {"first": r.get("first"), "last": r.get("last"),
            "rows": r.get("n", 0), "days": round(days, 1)}


def weekly_facts(db: D1Client) -> dict:
    """Fakta 7 hari terakhir per platform + lintas platform."""
    facts: dict = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "window_days": 7,
        "coverage": snapshot_coverage(db),
        "platforms": {},
    }

    for p in PLATFORMS:
        # Top saat ini.
        top_now = _rows(db.query(
            "SELECT title, rank, metric FROM trends "
            "WHERE platform = ? AND is_current = 1 ORDER BY rank LIMIT 5", [p]))
        # Pendatang baru: pertama terlihat dalam 7 hari terakhir.
        newcomers = _rows(db.query(
            "SELECT title, MIN(snapshot_at) AS first_seen, MIN(rank) AS best_rank "
            "FROM trend_snapshots WHERE platform = ? "
            "GROUP BY trend_id "
            "HAVING first_seen >= datetime('now', '-7 days') "
            "ORDER BY best_rank LIMIT 10", [p]))
        # Paling awet: hari berbeda terbanyak dalam 7 hari terakhir.
        stayers = _rows(db.query(
            "SELECT title, COUNT(DISTINCT date(snapshot_at)) AS days_on, MIN(rank) AS best_rank "
            "FROM trend_snapshots WHERE platform = ? "
            "AND snapshot_at >= datetime('now', '-7 days') "
            "GROUP BY trend_id ORDER BY days_on DESC, best_rank LIMIT 5", [p]))
        facts["platforms"][p] = {
            "top_now": top_now,
            "newcomers_7d": newcomers,
            "longest_running_7d": stayers,
        }

    # Lintas platform: judul (dinormalkan) muncul di >= 2 platform dlm 7 hari.
    cross = _rows(db.query(
        "SELECT LOWER(REPLACE(title,'#','')) AS t, "
        "COUNT(DISTINCT platform) AS n_platform, "
        "GROUP_CONCAT(DISTINCT platform) AS platforms, MIN(rank) AS best_rank "
        "FROM trend_snapshots WHERE snapshot_at >= datetime('now', '-7 days') "
        "GROUP BY t HAVING n_platform >= 2 "
        "ORDER BY n_platform DESC, best_rank LIMIT 15", []))
    facts["cross_platform_7d"] = cross
    return facts


def trend_facts(db: D1Client, trend_id: str) -> dict:
    """Fakta satu tren: kapan muncul, peringkat terbaik, lintasan harian."""
    meta = _rows(db.query(
        "SELECT platform, title, rank, metric, metric_label, url "
        "FROM trends WHERE id = ?", [trend_id]))
    series = _rows(db.query(
        "SELECT date(snapshot_at) AS day, MIN(rank) AS best_rank, "
        "MAX(metric) AS max_metric, COUNT(*) AS samples "
        "FROM trend_snapshots WHERE trend_id = ? "
        "GROUP BY day ORDER BY day", [trend_id]))
    title = meta[0]["title"] if meta else None
    cross: list[dict] = []
    if title:
        cross = _rows(db.query(
            "SELECT platform, MIN(snapshot_at) AS first_seen, MIN(rank) AS best_rank "
            "FROM trend_snapshots WHERE LOWER(REPLACE(title,'#','')) = ? "
            "GROUP BY platform ORDER BY first_seen", [_norm_title(title)]))
    return {
        "trend_id": trend_id,
        "meta": meta[0] if meta else None,
        "first_seen": series[0]["day"] if series else None,
        "days_on_list": len(series),
        "best_rank": min((s["best_rank"] for s in series), default=None),
        "daily": series,
        "cross_platform": cross,
    }


def main() -> None:
    db = D1Client()
    if not db._configured():
        print("D1 tidak dikonfigurasi.", file=sys.stderr)
        sys.exit(1)
    mode = sys.argv[1] if len(sys.argv) > 1 else "weekly"
    if mode == "trend" and len(sys.argv) > 2:
        out = trend_facts(db, sys.argv[2])
    else:
        out = weekly_facts(db)
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
