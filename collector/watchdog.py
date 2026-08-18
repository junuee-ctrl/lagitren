"""Anjing penjaga (watchdog) SEMUA sumber — jalan di CLOUD tiap run collect.

Pasca-insiden 2026-08-18 (Playwright lokal menggantung 13j40m tanpa alarm):
watchdog diperluas dari 2 platform lokal → SEMUA platform, dengan ambang
per-sumber = periode jadwal × 3 (spes. P0-8). Workflow collect.yml jalan
tiap ±10 menit, jadi pemeriksaan efektifnya rapat.

Perilaku:
  - Sumber basi (> ambang) → kirim peringatan Telegram (bahasa Korea).
  - Anti-spam: peringatan ulang utk kondisi sama ditunda 6 jam; tapi bila ada
    sumber BARU yang ikut basi, alert langsung dikirim lagi.
  - Sumber yang tadinya basi lalu segar kembali → kirim pesan "복구됨".
  - Status terakhir disimpan sebagai baris 'watchdog' di collection_runs
    dengan prefix "stale=a,b|" agar bisa dibandingkan antar-run.

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

# Ambang basi per platform (jam) = periode jadwal × 3.
#   google/youtube: cron cloud ±1 jam → 3 jam
#   instagram/tiktok/twitter: PC lokal tiap 3 jam → 9 jam
#   netflix/shopee: harian → 72 jam
THRESHOLD_HOURS: dict[str, int] = {
    "google": 3,
    "youtube": 3,
    "instagram": 9,
    "tiktok": 9,
    "twitter": 9,
    "netflix": 72,
    "shopee": 72,
}
REALERT_HOURS = 6
KST = timezone(timedelta(hours=7))  # tampilkan waktu dalam WIB


def _parse_ts(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00")).astimezone(
            timezone.utc
        )
    except Exception:
        return None


def _rows(data) -> list[dict]:
    res = data.get("result")
    return res[0].get("results") if isinstance(res, list) and res else []


def _last_ok(db: D1Client, platform: str) -> datetime | None:
    data = db.query(
        "SELECT MAX(started_at) AS t FROM collection_runs "
        "WHERE platform = ? AND status = 'ok' AND item_count > 0",
        [platform],
    )
    rows = _rows(data)
    return _parse_ts(rows[0].get("t") if rows else None)


def _last_err(db: D1Client, platform: str) -> str | None:
    """Pesan run terakhir bila BUKAN ok (untuk isi alert)."""
    data = db.query(
        "SELECT status, message FROM collection_runs WHERE platform = ? "
        "ORDER BY started_at DESC LIMIT 1",
        [platform],
    )
    rows = _rows(data)
    if rows and rows[0].get("status") != "ok":
        msg = rows[0].get("message") or rows[0].get("status")
        return str(msg)[:120]
    return None


def _prev_state(db: D1Client) -> tuple[set[str], datetime | None]:
    """(set platform basi pada run watchdog terakhir, waktu alert terakhir)."""
    data = db.query(
        "SELECT started_at, message, status FROM collection_runs "
        "WHERE platform = 'watchdog' ORDER BY started_at DESC LIMIT 20",
        [],
    )
    prev_stale: set[str] | None = None
    last_alert: datetime | None = None
    for r in _rows(data):
        msg = str(r.get("message") or "")
        if prev_stale is None and msg.startswith("stale="):
            names = msg.split("|", 1)[0][len("stale="):]
            prev_stale = {n for n in names.split(",") if n}
        if last_alert is None and str(r.get("status", "")).startswith("alert"):
            last_alert = _parse_ts(r.get("started_at"))
        if prev_stale is not None and last_alert is not None:
            break
    return prev_stale or set(), last_alert


def main() -> None:
    if "--test" in sys.argv:
        ok = telegram_bot.send("🔔 라기트렌 알림 테스트 — 텔레그램 연결 정상! 앞으로 수집기 이상 시 이 채널로 경고가 와요.")
        print("terkirim" if ok else "GAGAL (cek TELEGRAM_BOT_TOKEN/CHAT_ID)")
        return

    db = D1Client()
    if not db._configured():
        log.info("D1 tidak dikonfigurasi — lewati.")
        return

    now = datetime.now(timezone.utc)
    stale: dict[str, str] = {}  # platform -> deskripsi
    for p, hours in THRESHOLD_HOURS.items():
        last = _last_ok(db, p)
        if last is None or (now - last) > timedelta(hours=hours):
            if last is None:
                desc = "기록 없음"
            else:
                ago = (now - last).total_seconds() / 3600
                desc = f"마지막 성공 {last.astimezone(KST):%d일 %H:%M} WIB ({ago:.0f}시간 전, 기준 {hours}h)"
            err = _last_err(db, p)
            if err:
                desc += f" · 최근 에러: {err}"
            stale[p] = desc

    prev_stale, last_alert = _prev_state(db)
    cur = set(stale)
    state_tag = "stale=" + ",".join(sorted(cur))

    # 1) 복구 알림: 이전엔 basi, 지금은 segar.
    recovered = sorted(prev_stale - cur)
    if recovered:
        msg = "✅ <b>수집기 복구됨</b> — " + ", ".join(recovered) + " 다시 정상 수집 중."
        sent = telegram_bot.send(msg)
        db.log_run(
            "watchdog", "recovered" if sent else "recovered-gagal", len(recovered),
            (state_tag + "|recovered=" + ",".join(recovered))[:400], now_iso(),
        )
        log.info("Recovery %s: %s", "terkirim" if sent else "GAGAL", recovered)

    if not cur:
        if not recovered:
            log.info("Semua sumber segar.")
        return

    # 2) Anti-spam: kondisi sama < 6 jam → tunda; sumber BARU basi → kirim.
    new_stale = cur - prev_stale
    if not new_stale and last_alert and (now - last_alert) < timedelta(hours=REALERT_HOURS):
        log.info("Sudah alert %.1f jam lalu (kondisi sama) — tunda.",
                 (now - last_alert).total_seconds() / 3600)
        return

    lines = [f"• <b>{p}</b>: {d}" for p, d in sorted(stale.items())]
    msg = (
        "⚠️ <b>수집기 멈춤 감지</b>\n" + "\n".join(lines) +
        "\n\n로컬(instagram/tiktok/twitter)이면 자카르타 PC에서 "
        "<code>py -u run_local.py</code> 실행 또는 LagiTrenCollect 작업 확인. "
        "클라우드(google/youtube/netflix/shopee)면 GitHub Actions 확인."
    )
    sent = telegram_bot.send(msg)
    db.log_run(
        "watchdog", "alert" if sent else "alert-gagal", len(cur),
        (state_tag + "|" + "; ".join(f"{p}:{d}" for p, d in stale.items()))[:400],
        now_iso(),
    )
    log.info("Alert %s: %s", "terkirim" if sent else "GAGAL", sorted(cur))


if __name__ == "__main__":
    main()
