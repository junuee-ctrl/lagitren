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

import config
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
            debug = getattr(module, "LAST_DEBUG", "") or "kosong"
            db.log_run(platform, "ok", 0, str(debug)[:400], started)
            return 0

        # Cache ringkasan/artikel: pakai ulang bila judul tak berubah.
        cache: dict = (
            {}
            if config.SUMMARY_FORCE_REFRESH
            else db.fetch_existing_summaries([t.id for t in trends])
        )
        if do_summary and platform != "youtube":
            reused = 0
            for t in trends:
                if t.ai_summary:
                    continue
                prev = cache.get(t.id)
                if prev and prev.get("ai_summary") and prev.get("title") == t.title:
                    t.ai_summary = prev["ai_summary"]  # cache hit → tanpa LLM
                    reused += 1
                else:
                    context = getattr(t, "_context", "") or ""
                    t.ai_summary = summarize(platform, t.title, context)
            log.info(
                "%s: ringkasan %d baru, %d dari cache.",
                platform, len(trends) - reused, reused,
            )

        # ── Artikel terstruktur utk tren teratas (P1-3, hibrida) ──
        if do_summary and platform != "shopee" and config.ARTICLE_TOPN > 0:
            import json as _json
            from summarizer.ai_summary import generate_article
            from summarizer.news_lookup import fetch_related_news

            made = kept = 0
            for t in trends:
                if (t.rank or 99) > config.ARTICLE_TOPN:
                    continue
                prev = cache.get(t.id) or {}
                prev_article = None
                if prev.get("title") == t.title and prev.get("extra"):
                    try:
                        prev_article = (_json.loads(prev["extra"]) or {}).get(
                            "article"
                        )
                    except Exception:
                        prev_article = None
                if prev_article:
                    t.extra = {**(t.extra or {}), "article": prev_article}
                    # Berita lama ikut dipertahankan bila run ini tak membawa baru.
                    if not (t.extra or {}).get("news"):
                        try:
                            old_news = (_json.loads(prev["extra"]) or {}).get("news")
                            if old_news:
                                t.extra["news"] = old_news
                        except Exception:
                            pass
                    kept += 1
                    continue
                # Berita terkait: pakai punya collector (Google) atau cari sendiri.
                news_items = (t.extra or {}).get("news") or []
                if not news_items:
                    news_items = fetch_related_news(t.title)
                    if news_items:
                        t.extra = {**(t.extra or {}), "news": news_items}
                news_txt = " | ".join(n["title"] for n in news_items[:4])
                context = getattr(t, "_context", "") or ""
                art = generate_article(platform, t.title, context, news_txt)
                if art:
                    t.extra = {**(t.extra or {}), "article": art}
                    made += 1
            log.info("%s: artikel %d baru, %d dari cache.", platform, made, kept)
            extra_dbg = f"art:{made}+{kept}"
            if made == 0:
                from summarizer import ai_summary as _aisum
                err = getattr(_aisum, "LAST_ARTICLE_ERR", "")
                if err:
                    extra_dbg += f" ({err})"
            module.LAST_DEBUG = (
                f"{getattr(module, 'LAST_DEBUG', '') or ''} · {extra_dbg}"
            ).strip(" ·")

        count = db.save_trends(platform, trends)
        db.prune_mojibake(platform)  # bersihkan sisa judul rusak (P0-1)
        log.info("%s: %d item tersimpan.", platform, count)

        # Ping IndexNow utk URL BARU saja (id belum ada / judul berubah) — P2-1.
        try:
            import indexnow

            fresh = [
                indexnow.url_for(platform, t.id)
                for t in trends
                if t.id not in cache or (cache.get(t.id) or {}).get("title") != t.title
            ]
            if fresh:
                sent = indexnow.ping(fresh)
                if sent:
                    module.LAST_DEBUG = (
                        f"{getattr(module, 'LAST_DEBUG', '') or ''} · inow:{sent}"
                    ).strip(" ·")
        except Exception:
            pass  # ping opsional — jangan ganggu pipeline
        dbg = getattr(module, "LAST_DEBUG", "") or ""
        msg = f"sukses · {dbg}" if dbg else "sukses"
        db.log_run(platform, "ok", count, msg[:400], started)
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
