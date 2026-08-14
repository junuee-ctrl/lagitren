"""Anjing penjaga (watchdog) koleksi LOKAL — jalan di CLOUD (P2+).

Masalah yang dijaga: kolektor lokal (PC Jakarta: instagram, tiktok) bisa
mati DIAM-DIAM (mis. alias `python` rusak, PC mati, Chrome logout). Situs
tetap tampak hidup karena data lama terus disajikan.

Solusi: workflow cloud (yang pasti hidup) memeriksa kapan terakhir platform
lokal SUKSES mengumpulkan (tabel collection_runs di D1). Bila lebih lama
dari STALE_ALERT_HOURS → kirim peringatan Telegram. Anti-spam: peringatan
berikutnya baru dikirim setelah 24 jam (dicatat sbg baris 'watchdog').

Pemakaian:
  python watchdog.py          # cek & kirim alert bila basi
  python watchdog.py --test   # kirim pesan uji ke Telegram (cek konfigurasi)
"""
from __future__ import annotations

import logging
import sys
from datetime import datetime, timedelta, timezone

import config
from database import D1Client
from models import now_iso
from notifier import telegram_bot

logging.basicConfig(level=logging.INFO, format="%(levelname)s [%(name)s] %(message)s")
log = logging.getLogger("watchdog")

# Platform yang dikumpulkan oleh PC LOKAL (bukan cloud).
LOCAL_PLATFORMS = ["instagram", "tiktok"]
STALE_HOURS = int(getattr(config, "STALE_ALERT_HOURS", 0) or 12)
REALERT_HOURS = 24


def _parse_ts(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00")).astimezone(
            timezone.utc
        )
    except Exception:
        return None


def _last_ok(db: D1Client, platform: str) -> datetime | None:
    data = db.query(
        "SELECT MAX(started_at) AS t FROM collection_runs "
        "WHERE platform = ? AND status = 'ok' AND item_count > 0",
        [platform],
    )
    res = data.get("result")
    rows = res[0].get("results") if isinstance(res, list) and res else []
    return _parse_ts(rows[0].get("t") if rows else None)


def main() -> None:
    if "--test" in sys.argv:
        ok = telegram_bot.send("🔔 Uji watchdog Lagi Tren — konfigurasi Telegram OK.")
        print("terkirim" if ok else "GAGAL (cek TELEGRAM_BOT_TOKEN/CHAT_ID)")
        return

    db = D1Client()
    if not db._configured():
        log.info("D1 tidak dikonfigurasi — lewati.")
        return

    now = datetime.now(timezone.utc)
    stale: list[str] = []
    for p in LOCAL_PLATFORMS:
        last = _last_ok(db, p)
        if last is None or (now - last) > timedelta(hours=STALE_HOURS):
            ago = "belum pernah" if last is None else f"{(now - last).total_seconds() / 3600:.0f} jam lalu"
            stale.append(f"{p} (terakhir sukses: {ago})")

    if not stale:
        log.info("Semua kolektor lokal segar (< %d jam).", STALE_HOURS)
        return

    # Anti-spam: sudah alert dalam 24 jam terakhir?
    data = db.query(
        "SELECT MAX(started_at) AS t FROM collection_runs WHERE platform = 'watchdog'",
        [],
    )
    res = data.get("result")
    rows = res[0].get("results") if isinstance(res, list) and res else []
    prev = _parse_ts(rows[0].get("t") if rows else None)
    if prev and (now - prev) < timedelta(hours=REALERT_HOURS):
        log.info("Sudah alert %.0f jam lalu — tunda.", (now - prev).total_seconds() / 3600)
        return

    msg = (
        "⚠️ <b>Kolektor lokal macet</b> — "
        + "; ".join(stale)
        + f"\nAmbang: {STALE_HOURS} jam. Cek PC Jakarta: jalankan "
        "<code>py run_local.py</code> di C:\\lagitren\\collector "
        "(pastikan Chrome login & jadwal LagiTrenCollect aktif)."
    )
    sent = telegram_bot.send(msg)
    db.log_run("watchdog", "alert" if sent else "alert-gagal", len(stale), "; ".join(stale)[:400], now_iso())
    log.info("Alert %s: %s", "terkirim" if sent else "GAGAL", stale)


if __name__ == "__main__":
    main()
