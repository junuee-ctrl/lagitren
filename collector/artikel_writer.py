"""Generator artikel /artikel — Claude Sonnet + lembar fakta (factsheet).

Alur (rencana AdSense §5):
  factsheet.py (angka dari D1)  →  Sonnet menulis narasi dari fakta SAJA
  →  QC otomatis  →  simpan draf JSON ke content/artikel/  →  review
  →  publish_articles.py menerbitkan ke D1.

Draf TIDAK langsung terbit: hasil ditulis sebagai file JSON (artefak
workflow / commit) supaya ada langkah pemeriksaan manusia (§4-2).

Pemakaian:
  python artikel_writer.py rekap              # rekap mingguan (butuh snapshot >= 6 hari)
  python artikel_writer.py analisis <trend_id>  # analisis 1 tren viral
Env:
  ANTHROPIC_API_KEY  (wajib)
  ARTIKEL_MODEL      (default: claude-sonnet-4-5)
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

import config
from database import D1Client
from factsheet import snapshot_coverage, trend_facts, weekly_facts

MODEL = os.environ.get("ARTIKEL_MODEL", "claude-sonnet-4-5")
OUT_DIR = Path(__file__).resolve().parent.parent / "content" / "artikel"
MIN_CHARS = 1200
MIN_SECTIONS = 3

SYSTEM = """Kamu penulis data-jurnalisme untuk lagitren.id (Bahasa Indonesia, nada santai-informatif, sapaan "kamu").

ATURAN MUTLAK:
1. Gunakan HANYA fakta & angka dari LEMBAR FAKTA yang diberikan. DILARANG menambah angka, tanggal, nama, atau kutipan dari pengetahuanmu sendiri.
2. Yang tidak ada di lembar fakta → tulis "data tidak tersedia" atau jangan disinggung.
3. Hindari kalimat kosong ("banyak faktor yang memengaruhi", "menarik untuk disimak"), hindari clickbait, hindari klaim "pasti/terbukti/dijamin".
4. Sebut sumber data sebagai "arsip Lagi Tren" bila merujuk angka internal.
5. Keluaran HARUS JSON valid persis sesuai skema yang diminta, tanpa teks lain."""

SCHEMA_HINT = """Skema keluaran (JSON murni, tanpa markdown fence):
{
  "slug": "kebab-case-maks-6-kata",
  "title": "Judul spesifik, boleh berupa pertanyaan, maks 70 karakter",
  "lead": "2-3 kalimat berisi kesimpulan utama (bukan basa-basi pembuka)",
  "sections": [
    {"heading": "…", "paragraphs": ["…", "…"]},
    …minimal 3 section, total teks 1200-1800 karakter…
  ],
  "dataCard": {"label": "nilai", …maks 4 pasangan, dari lembar fakta…}
}"""


def _claude(prompt: str) -> str:
    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": config.ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": MODEL,
            "max_tokens": 2500,
            "system": SYSTEM,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=120,
    )
    resp.raise_for_status()
    return "".join(
        b.get("text", "") for b in resp.json().get("content", []) if b.get("type") == "text"
    )


def _parse(raw: str) -> dict | None:
    raw = raw.strip()
    raw = re.sub(r"^```(json)?|```$", "", raw, flags=re.M).strip()
    m = re.search(r"\{.*\}", raw, re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(0), strict=False)
    except Exception:
        return None


def _qc(doc: dict) -> list[str]:
    problems = []
    secs = doc.get("sections") or []
    total = len(doc.get("lead") or "") + sum(
        len(p) for s in secs for p in (s.get("paragraphs") or [])
    )
    if total < MIN_CHARS:
        problems.append(f"pendek ({total}<{MIN_CHARS})")
    if len(secs) < MIN_SECTIONS:
        problems.append(f"section kurang ({len(secs)})")
    if not doc.get("slug") or not doc.get("title") or not doc.get("lead"):
        problems.append("field wajib kosong")
    banned = ["100% terbukti", "pasti berhasil", "dijamin"]
    text = json.dumps(doc, ensure_ascii=False).lower()
    for b in banned:
        if b in text:
            problems.append(f"frasa terlarang: {b}")
    return problems


def _save_draft(doc: dict, category: str, facts: dict, related: list[str]) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    doc["category"] = category
    doc["related"] = related
    doc["facts"] = facts
    doc.setdefault("sources", [])
    doc["published_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    path = OUT_DIR / f"{doc['slug']}.json"
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def gen_rekap(db: D1Client) -> None:
    cov = snapshot_coverage(db)
    if cov["days"] < 6:
        print(f"Snapshot baru {cov['days']} hari (<6) — rekap mingguan belum layak. "
              "Coba lagi setelah arsip terkumpul.")
        sys.exit(0)
    facts = weekly_facts(db)
    prompt = (
        "Tulis REKAP MINGGUAN tren Indonesia dari lembar fakta ini. Fokus: apa yang "
        "paling ramai per platform, pendatang baru, yang paling awet, dan tren yang "
        "muncul lintas platform. " + SCHEMA_HINT +
        "\n\nLEMBAR FAKTA:\n" + json.dumps(facts, ensure_ascii=False)
    )
    _run(prompt, "rekap", facts, related=["/", "/artikel"])


def gen_analisis(db: D1Client, trend_id: str) -> None:
    facts = trend_facts(db, trend_id)
    if not facts.get("meta"):
        print(f"Tren {trend_id} tidak ditemukan.")
        sys.exit(1)
    platform, slug = trend_id.split(":", 1)
    prompt = (
        "Tulis ANALISIS mengapa tren ini sedang viral di Indonesia, berbasis lembar "
        "fakta (kapan pertama muncul di arsip Lagi Tren, peringkat terbaik, berapa "
        "hari bertahan, apakah menyeberang platform). " + SCHEMA_HINT +
        "\n\nLEMBAR FAKTA:\n" + json.dumps(facts, ensure_ascii=False)
    )
    _run(prompt, "analisis", facts, related=[f"/{platform}/{slug}", "/artikel"])


def _run(prompt: str, category: str, facts: dict, related: list[str]) -> None:
    if not config.ANTHROPIC_API_KEY:
        print("ANTHROPIC_API_KEY kosong.")
        sys.exit(1)
    doc = _parse(_claude(prompt))
    if not doc:
        print("Gagal parse keluaran model.")
        sys.exit(1)
    problems = _qc(doc)
    if problems:
        print("QC GAGAL:", "; ".join(problems))
        sys.exit(1)
    path = _save_draft(doc, category, facts, related)
    print(f"Draf tersimpan: {path}")
    print("Review lalu terbitkan dengan: python publish_articles.py", doc["slug"])


def main() -> None:
    db = D1Client()
    if not db._configured():
        print("D1 tidak dikonfigurasi.")
        sys.exit(1)
    mode = sys.argv[1] if len(sys.argv) > 1 else "rekap"
    if mode == "analisis" and len(sys.argv) > 2:
        gen_analisis(db, sys.argv[2])
    else:
        gen_rekap(db)


if __name__ == "__main__":
    main()
