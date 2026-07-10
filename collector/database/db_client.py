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
   url, thumbnail, source, hashtags, affiliate_url, price, interest, collected_at, updated_at)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
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
  collected_at=excluded.collected_at,
  updated_at=datetime('now');
"""

LOG_RUN_SQL = """
INSERT INTO collection_runs (platform, status, item_count, message, started_at)
VALUES (?, ?, ?, ?, ?);
"""

# Hapus item lama satu platform yang TIDAK ada di kumpulan id terbaru.
# (dipanggil setelah upsert agar tabel hanya berisi snapshot terkini)
PRUNE_SQL_TMPL = "DELETE FROM trends WHERE platform = ? AND id NOT IN ({placeholders});"


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
                r["price"], r["interest"], r["collected_at"],
            ],
        )

    def save_trends(self, platform: str, trends: list[Trend], prune: bool = True) -> int:
        """Upsert semua tren satu platform, lalu (opsional) buang yang usang."""
        count = 0
        for t in trends:
            self.upsert_trend(t)
            count += 1
        if prune and trends and not (self.dry_run or not self._configured()):
            ids = [t.id for t in trends]
            placeholders = ",".join(["?"] * len(ids))
            self.query(
                PRUNE_SQL_TMPL.format(placeholders=placeholders),
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
