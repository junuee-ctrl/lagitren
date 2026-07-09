"""Penjadwal berkala untuk collector (APScheduler).

Setiap platform punya interval sendiri (lihat collectors.REGISTRY).
Jalankan proses ini terus-menerus di PC lokal (Jakarta):

  python scheduler.py

Alternatif Windows: pakai Task Scheduler memanggil `python main.py <platform>`.
"""
from __future__ import annotations

import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

from collectors import REGISTRY
from main import run
from notifier import telegram_bot

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("scheduler")


def main() -> None:
    sched = BlockingScheduler(timezone="Asia/Jakarta")

    for platform, (_module, interval_min) in REGISTRY.items():
        sched.add_job(
            run,
            trigger=IntervalTrigger(minutes=interval_min),
            args=[[platform]],
            id=f"collect_{platform}",
            name=f"Collect {platform} tiap {interval_min}m",
            max_instances=1,
            coalesce=True,
            misfire_grace_time=300,
        )
        log.info("Terjadwal: %s tiap %d menit.", platform, interval_min)

    # Jalankan sekali saat start agar DB langsung terisi.
    log.info("Menjalankan pengumpulan awal...")
    run(list(REGISTRY.keys()))

    telegram_bot.send("🚀 Scheduler Lagi Tren aktif.", silent=True)
    log.info("Scheduler berjalan. Tekan Ctrl+C untuk berhenti.")
    try:
        sched.start()
    except (KeyboardInterrupt, SystemExit):
        log.info("Scheduler dihentikan.")


if __name__ == "__main__":
    main()
