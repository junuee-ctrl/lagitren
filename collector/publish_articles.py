"""Terbitkan artikel dari content/artikel/*.json ke tabel D1 `articles`.

Dipakai untuk:
  - artikel Panduan (tulisan tangan, disimpan di repo), dan
  - hasil pipeline generator (artikel_writer) setelah lolos QC.

Pemakaian:
  python publish_articles.py            # semua file di ../content/artikel/
  python publish_articles.py <slug>     # satu artikel saja

QC minimum sebelum terbit (spes. rencana AdSense 4-1):
  - lead + body >= 1.200 karakter
  - >= 3 subjudul
  - slug unik (upsert: file yang sama memperbarui, bukan menduplikasi)
"""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

from database import D1Client

logging.basicConfig(level=logging.INFO, format="%(levelname)s [%(name)s] %(message)s")
log = logging.getLogger("artikel")

CONTENT_DIR = Path(__file__).resolve().parent.parent / "content" / "artikel"
MIN_CHARS = 1200
MIN_SECTIONS = 3

DDL = (
    "CREATE TABLE IF NOT EXISTS articles ("
    "slug TEXT PRIMARY KEY, title TEXT NOT NULL, category TEXT NOT NULL, "
    "lead TEXT NOT NULL, body TEXT NOT NULL, facts TEXT, hero_image TEXT, "
    "status TEXT NOT NULL DEFAULT 'published', published_at TEXT NOT NULL, "
    "updated_at TEXT NOT NULL DEFAULT (datetime('now')))",
    "CREATE INDEX IF NOT EXISTS idx_articles_pub ON articles (status, published_at)",
)

UPSERT = """
INSERT INTO articles (slug, title, category, lead, body, facts, hero_image, status, published_at, updated_at)
VALUES (?, ?, ?, ?, ?, ?, ?, 'published', ?, datetime('now'))
ON CONFLICT(slug) DO UPDATE SET
  title=excluded.title, category=excluded.category, lead=excluded.lead,
  body=excluded.body, facts=excluded.facts, hero_image=excluded.hero_image,
  status='published', updated_at=datetime('now');
"""


def _qc(doc: dict) -> list[str]:
    """Kembalikan daftar masalah; kosong = lolos."""
    problems: list[str] = []
    sections = doc.get("sections") or []
    total = len(doc.get("lead") or "") + sum(
        len(p) for s in sections for p in (s.get("paragraphs") or [])
    )
    if total < MIN_CHARS:
        problems.append(f"terlalu pendek ({total} < {MIN_CHARS} karakter)")
    if len(sections) < MIN_SECTIONS:
        problems.append(f"subjudul kurang ({len(sections)} < {MIN_SECTIONS})")
    for key in ("slug", "title", "category", "lead", "published_at"):
        if not doc.get(key):
            problems.append(f"field '{key}' kosong")
    return problems


def publish(paths: list[Path]) -> None:
    db = D1Client()
    if not db._configured():
        log.error("D1 tidak dikonfigurasi (CLOUDFLARE_*).")
        sys.exit(1)
    for stmt in DDL:
        try:
            db.query(stmt)
        except Exception:
            pass

    ok = skipped = 0
    for path in paths:
        doc = json.loads(path.read_text(encoding="utf-8"))
        problems = _qc(doc)
        if problems:
            log.warning("LEWATI %s: %s", path.name, "; ".join(problems))
            skipped += 1
            continue
        body = json.dumps(
            {
                "sections": doc.get("sections") or [],
                "sources": doc.get("sources") or [],
                "related": doc.get("related") or [],
                **({"dataCard": doc["dataCard"]} if doc.get("dataCard") else {}),
            },
            ensure_ascii=False,
        )
        facts = json.dumps(doc.get("facts"), ensure_ascii=False) if doc.get("facts") else None
        db.query(
            UPSERT,
            [
                doc["slug"], doc["title"], doc["category"], doc["lead"],
                body, facts, doc.get("hero_image"), doc["published_at"],
            ],
        )
        log.info("Terbit: /artikel/%s (%s)", doc["slug"], doc["category"])
        ok += 1
    log.info("Selesai: %d terbit, %d dilewati.", ok, skipped)
    if ok == 0 and skipped > 0:
        sys.exit(1)


def main() -> None:
    if not CONTENT_DIR.exists():
        log.error("Folder %s tidak ada.", CONTENT_DIR)
        sys.exit(1)
    want = [a for a in sys.argv[1:] if not a.startswith("-")]
    paths = sorted(CONTENT_DIR.glob("*.json"))
    if want:
        paths = [p for p in paths if p.stem in want]
    if not paths:
        log.error("Tidak ada artikel yang cocok.")
        sys.exit(1)
    publish(paths)


if __name__ == "__main__":
    main()
