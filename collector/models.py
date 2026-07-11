"""Model data bersama untuk collector Lagi Tren."""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Optional


def now_iso() -> str:
    """Waktu sekarang dalam ISO 8601 UTC."""
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Trend:
    """Satu item tren. Dipetakan langsung ke tabel `trends` di D1.

    `id` harus stabil per item (mis. 'google:<slug>') agar UPSERT
    menimpa baris lama alih-alih membuat duplikat.
    """

    id: str
    platform: str
    rank: int
    title: str
    url: str
    subtitle: Optional[str] = None
    metric: Optional[int] = None
    metric_label: Optional[str] = None
    ai_summary: Optional[str] = None
    thumbnail: Optional[str] = None
    source: Optional[str] = None
    hashtags: list[str] = field(default_factory=list)
    affiliate_url: Optional[str] = None
    price: Optional[str] = None
    # Deret minat pencarian (khusus Google) untuk grafik volume.
    interest: list[int] = field(default_factory=list)
    # Konteks kaya per-platform (google: berita; youtube: komentar terbaik).
    extra: dict = field(default_factory=dict)
    collected_at: str = field(default_factory=now_iso)

    def to_row(self) -> dict:
        """Bentuk siap-simpan (list -> JSON string)."""
        d = asdict(self)
        d["hashtags"] = json.dumps(self.hashtags, ensure_ascii=False)
        d["interest"] = json.dumps(self.interest) if self.interest else None
        d["extra"] = json.dumps(self.extra, ensure_ascii=False) if self.extra else None
        return d
