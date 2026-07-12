"""Klien Cloudflare D1 via REST API.

Collector berjalan di PC lokal (Jakarta) dan menulis langsung ke D1
produksi lewat REST API Cloudflare, tanpa perlu wrangler.

Endpoint:
  POST /accounts/{account_id}/d1/database/{database_id}/query
  body: {"sql": "...", "params": [...]}
"""
from __future__ import annotations

import logging
from typing import Any, Sequence

import requests

import config
from models import Trend

log = logging.getLogger("db")

_API_BASE = "https://api.cloudflare.com/client/v4"

UPSERT_SQL = """
INSERT INTO trends
  (id, platform, rank, title, subtitle, metric, metric_label, ai_summary,
   url, thumbnail, source, hashtags, affiliate_url, price, interest, extra, is_current, collected_at, updated_at)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, datetime('now'))
ON CONFLICT(id) DO UPDATE SET
  platform=excluded.platform,
  rank=excluded.rank,
  title=excluded.title,
  subtitle=excluded.subtitle,
  metric=excluded.metric,
  metric_label=excluded.metric_label,
  ai_summary=excluded.ai_summary,
  url=excluded.url,
  thumbnail=excluded.thumbnail,
  source=excluded.source,
  hashtags=excluded.hashtags,
  affiliate_url=excluded.affiliate_url,
  price=excluded.price,
  interest=excluded.interest,
  extra=excluded.extra,
  is_current=1,
  collected_at=excluded.collected_at,
  updated_at=datetime('now');
"""

LOG_RUN_SQL = """
INSERT INTO collection_runs (platform, status, item_count, message, started_at)
VALUES (?, ?, ?, ?, ?);
"""

# ARSIP (bukan hapus) item lama satu platform yang tidak ada di kumpulan terbaru:
# is_current=0. Halaman detailnya TETAP ada (penting untuk akumulasi SEO);
# hanya tidak muncul di daftar "sedang tren".
ARCHIVE_SQL_TMPL = (
    "UPDATE trends SET is_current = 0 "
    "WHERE platform = ? AND is_current = 1 AND id NOT IN ({placeholders});"
)


class D1Client:
    def __init__(self) -> None:
        self.account_id = config.CF_ACCOUNT_ID
        self.database_id = config.CF_D1_DATABASE_ID
        self.token = config.CF_API_TOKEN
        self.dry_run = config.DRY_RUN
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            }
        )

    @property
    def _url(self) -> str:
        return (
            f"{_API_BASE}/accounts/{self.account_id}"
            f"/d1/database/{self.database_id}/query"
        )

    def _resolve_db_id(self) -> None:
        """Cari database_id 'lagitren-db' otomatis via API (bila belum diisi)."""
        if self.database_id or not (self.account_id and self.token):
            return
        try:
            resp = self._session.get(
                f"{_API_BASE}/accounts/{self.account_id}/d1/database",
                timeout=20,
            )
            data = resp.json()
            for db in data.get("result", []) or []:
                if db.get("name") == "lagitren-db":
                    self.database_id = db.get("uuid") or db.get("id") or ""
                    if self.database_id:
                        log.info("D1 database_id ditemukan otomatis.")
                    return
            log.warning("Database 'lagitren-db' tidak ditemukan via API.")
        except Exception as exc:
            log.warning("Gagal resolve database_id: %s", exc)

    def _configured(self) -> bool:
        if not self.database_id:
            self._resolve_db_id()
        return bool(self.account_id and self.database_id and self.token)

    def query(self, sql: str, params: Sequence[Any] | None = None) -> dict:
        """Jalankan satu statement SQL berparameter."""
        if self.dry_run or not self._configured():
            log.info("[DRY_RUN] %s | params=%s", sql.split("\n")[0][:60], params)
            return {"dry_run": True}
        resp = self._session.post(
            self._url,
            json={"sql": sql, "params": list(params or [])},
            timeout=30,
        )
        if resp.status_code != 200:
            raise RuntimeError(f"D1 error {resp.status_code}: {resp.text[:300]}")
        data = resp.json()
        if not data.get("success", False):
            raise RuntimeError(f"D1 gagal: {data.get('errors')}")
        return data

    def upsert_trend(self, t: Trend) -> None:
        r = t.to_row()
        self.query(
            UPSERT_SQL,
            [
                r["id"], r["platform"], r["rank"], r["title"], r["subtitle"],
                r["metric"], r["metric_label"], r["ai_summary"], r["url"],
                r["thumbnail"], r["source"], r["hashtags"], r["affiliate_url"],
                r["price"], r["interest"], r["extra"], r["collected_at"],
            ],
        )

    def fetch_existing_summaries(self, ids: list[str]) -> dict[str, dict]:
        """Ambil (title, ai_summary) yang SUDAH ada untuk daftar id.

        Dipakai sebagai cache: agar tren yang tidak berubah tidak diringkas
        ulang setiap jam (menghemat biaya & waktu LLM).
        """
        if not ids or self.dry_run or not self._configured():
            return {}
        out: dict[str, dict] = {}
        chunk = 50
        for i in range(0, len(ids), chunk):
            part = ids[i : i + chunk]
            placeholders = ",".join(["?"] * len(part))
            sql = (
                "SELECT id, title, ai_summary FROM trends "
                f"WHERE id IN ({placeholders})"
            )
            try:
                data = self.query(sql, part)
                res = data.get("result")
                rows = res[0].get("results") if isinstance(res, list) and res else []
                for r in rows or []:
                    out[r["id"]] = {
                        "title": r.get("title"),
                        "ai_summary": r.get("ai_summary"),
                    }
            except Exception as exc:
                log.warning("Gagal ambil cache ringkasan: %s", exc)
        return out

    def _ensure_schema(self) -> None:
        """Pastikan kolom baru ada (aman dijalankan berkali-kali)."""
        if getattr(self, "_schema_ready", False):
            return
        for stmt in (
            "ALTER TABLE trends ADD COLUMN interest TEXT",
            "ALTER TABLE trends ADD COLUMN extra TEXT",
            "ALTER TABLE trends ADD COLUMN is_current INTEGER NOT NULL DEFAULT 1",
        ):
            try:
                self.query(stmt)
            except Exception:
                pass  # kolom sudah ada
        self._schema_ready = True

    def save_trends(self, platform: str, trends: list[Trend], prune: bool = True) -> int:
        """Upsert tren satu platform, lalu ARSIPKAN (bukan hapus) yang usang."""
        live = not (self.dry_run or not self._configured())
        if live:
            self._ensure_schema()
        count = 0
        for t in trends:
            self.upsert_trend(t)
            count += 1
        # Tandai item yang tidak lagi tren sebagai arsip (is_current=0).
        if prune and trends and live:
            ids = [t.id for t in trends]
            placeholders = ",".join(["?"] * len(ids))
            self.query(
                ARCHIVE_SQL_TMPL.format(placeholders=placeholders),
                [platform, *ids],
            )
        return count

    def log_run(
        self, platform: str, status: str, item_count: int, message: str, started_at: str
    ) -> None:
        try:
            self.query(LOG_RUN_SQL, [platform, status, item_count, message, started_at])
        except Exception as exc:  # logging tidak boleh menggagalkan collector
            log.warning("Gagal mencatat run: %s", exc)
