"""Pipeline pengumpulan Lagi Tren.

Alur per platform:
  1. collect()            -> ambil tren mentah
  2. summarize()          -> isi ringkasan AI "kenapa tren" (Bahasa Indonesia)
  3. D1Client.save_trends -> upsert ke Cloudflare D1 + buang yang usang
  4. Telegram             -> notifikasi sukses/gagal

Pemakaian:
  python main.py                 # jalankan semua platform sekali
  python main.py google youtube  # jalankan platform tertentu
"""
from __future__ import annotations

import logging
import sys

from models import now_iso
from collectors import REGISTRY
from database import D1Client
from summarizer import summarize
from notifier import telegram_bot

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("main")


def run_platform(platform: str, db: D1Client, do_summary: bool = True) -> int:
    module, _interval = REGISTRY[platform]
    started = now_iso()
    try:
        trends = module.collect()
        if not trends:
            log.info("%s: tidak ada item.", platform)
            db.log_run(platform, "ok", 0, "kosong", started)
            return 0

        if do_summary:
            for t in trends:
                context = getattr(t, "_context", "") or ""
                if not t.ai_summary:
                    t.ai_summary = summarize(platform, t.title, context)

        count = db.save_trends(platform, trends)
        log.info("%s: %d item tersimpan.", platform, count)
        db.log_run(platform, "ok", count, "sukses", started)
        return count
    except Exception as exc:
        log.exception("%s gagal: %s", platform, exc)
        db.log_run(platform, "error", 0, str(exc)[:200], started)
        telegram_bot.notify_error(platform, str(exc)[:200])
        return 0


def run(platforms: list[str], do_summary: bool = True) -> dict[str, int]:
    db = D1Client()
    results: dict[str, int] = {}
    for platform in platforms:
        if platform not in REGISTRY:
            log.warning("Platform tak dikenal: %s", platform)
            continue
        results[platform] = run_platform(platform, db, do_summary)
    total = sum(results.values())
    if total > 0:
        telegram_bot.notify_success(results)
    return results


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    no_ai = "--no-ai" in sys.argv[1:]
    targets = args if args else list(REGISTRY.keys())
    log.info("Menjalankan collector: %s", ", ".join(targets))
    summary = run(targets, do_summary=not no_ai)
    log.info("Selesai. Ringkasan: %s", summary)
