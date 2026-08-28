"""Pilih platform CLOUD yang perlu dikumpulkan pada run ini (self-healing).

Latar: jadwal GitHub Actions bersifat best-effort — saat GitHub bermasalah
(mis. insiden 26-27 Agu 2026) cron per-workflow bisa terlewat berjam-jam.
Solusi: SETIAP kali workflow collect utama kebetulan jalan, periksa apakah
sumber cloud lain sudah basi; bila ya, ikutkan di run ini juga.

Keluaran: daftar platform dipisah spasi di stdout, mis. "google youtube".
Selalu memuat "google". Gagal query → "google" saja (aman).
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

# platform -> basi bila terakhir sukses lebih lama dari N jam
STALE_HOURS = {
    "youtube": 2,
    "netflix": 26,
    "shopee": 26,
}


def main() -> None:
    picks = ["google"]
    try:
        from database import D1Client

        db = D1Client()
        if db._configured():
            now = datetime.now(timezone.utc)
            for p, hours in STALE_HOURS.items():
                try:
                    data = db.query(
                        "SELECT MAX(started_at) AS t FROM collection_runs "
                        "WHERE platform = ? AND status = 'ok' AND item_count > 0",
                        [p],
                    )
                    res = data.get("result")
                    rows = res[0].get("results") if isinstance(res, list) and res else []
                    t = rows[0].get("t") if rows else None
                    last = (
                        datetime.fromisoformat(str(t).replace("Z", "+00:00")).astimezone(timezone.utc)
                        if t else None
                    )
                    if last is None or (now - last) > timedelta(hours=hours):
                        picks.append(p)
                except Exception:
                    pass
    except Exception:
        pass
    print(" ".join(picks))


if __name__ == "__main__":
    main()
