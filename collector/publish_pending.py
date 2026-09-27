"""Terbitkan artikel BARU yang ditaruh di content/artikel/ tapi belum di-commit.

Latar (2026-09-27): rutinitas artikel harian ditulis oleh Claude di PC ini,
tetapi sesi Claude tidak memegang kredensial git (dan push dari cloud diblokir).
Maka Claude hanya MENULIS file JSON; skrip ini — dijalankan Windows Task
Scheduler lewat run_local_task.bat (tiap 3 jam) — yang commit & push.

Aturan keamanan (repo PUBLIC):
  - Hanya file content/artikel/*.json yang BELUM dilacak git (artikel baru).
    Tidak pernah `git add -A`, tidak menyentuh file lain.
  - Setiap file wajib lolos QC yang sama dengan publish_articles.py + cek skema.
    Gagal QC → dilewati & dicatat, tidak di-commit.
  - Pola rahasia (token/kunci) di isi file → tolak.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ART_DIR = ROOT / "content" / "artikel"
CATEGORIES = {"panduan", "analisis", "rekap", "kurasi", "bulanan"}
MIN_CHARS, MIN_SECTIONS = 1200, 3
# Berkas infrastruktur penerbit ini sendiri: bila berubah/baru, ikut di-commit
# (daftar tetap, bukan pola) supaya perubahan skrip tidak membuat pull --rebase macet.
INFRA = ["collector/publish_pending.py", "collector/run_local_task.bat"]
# Pola dirakit dari potongan supaya berkas ini sendiri tidak cocok dengan polanya.
_SECRET_PARTS = ["git" + "hub_pat_", "gh" + "p_", "gh" + "o_", "sk" + "-ant-",
                 "AK" + "IA[0-9A-Z]{12}", "xo" + "x[bp]-", "-----" + "BEGIN"]
SECRET_RE = re.compile("(" + "|".join(_SECRET_PARTS) + ")", re.I)


def log(msg: str) -> None:
    print(f"{datetime.now():%Y-%m-%d %H:%M:%S} [publish_pending] {msg}", flush=True)


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                          text=True, encoding="utf-8", errors="replace", check=check)


def qc(path: Path) -> list[str]:
    raw = path.read_text(encoding="utf-8-sig")
    if SECRET_RE.search(raw):
        return ["berisi pola rahasia/token"]
    try:
        d = json.loads(raw)
    except json.JSONDecodeError as e:
        return [f"JSON rusak: {e}"]
    p: list[str] = []
    for k in ("slug", "title", "category", "lead", "published_at"):
        if not d.get(k):
            p.append(f"field '{k}' kosong")
    if d.get("slug") and d["slug"] != path.stem:
        p.append(f"slug '{d['slug']}' ≠ nama file '{path.stem}'")
    if d.get("category") and d["category"] not in CATEGORIES:
        p.append(f"kategori tak dikenal: {d['category']}")
    if d.get("published_at") and not re.fullmatch(r"\d{4}-\d\d-\d\d \d\d:\d\d:\d\d", d["published_at"]):
        p.append("published_at harus 'YYYY-MM-DD HH:MM:SS'")
    secs = d.get("sections") or []
    if not isinstance(secs, list) or any(
        not isinstance(s, dict) or not s.get("heading") or not isinstance(s.get("paragraphs"), list)
        for s in secs
    ):
        p.append("sections harus [{heading, paragraphs[]}]")
        secs = []
    total = len(d.get("lead") or "") + sum(len(x) for s in secs for x in s["paragraphs"])
    if total < MIN_CHARS:
        p.append(f"terlalu pendek ({total} < {MIN_CHARS})")
    if len(secs) < MIN_SECTIONS:
        p.append(f"subjudul kurang ({len(secs)} < {MIN_SECTIONS})")
    for key in ("sources", "related"):
        if key in d and not isinstance(d[key], list):
            p.append(f"'{key}' harus list")
    if "dataCard" in d and not isinstance(d["dataCard"], dict):
        p.append("'dataCard' harus objek")
    return p


def push_if_ahead() -> int:
    """Push commit lokal yang belum terkirim (mis. push run sebelumnya gagal)."""
    git("fetch", "-q", check=False)
    ahead = git("rev-list", "--count", "@{u}..HEAD", check=False).stdout.strip()
    if not (ahead.isdigit() and int(ahead) > 0):
        return 0
    if git("pull", "--rebase", "--autostash", check=False).returncode != 0:
        git("rebase", "--abort", check=False)
        log("pull --rebase gagal sebelum push ulang")
        return 1
    push = git("push", check=False)
    if push.returncode != 0:
        log("push gagal (commit lokal tetap ada, dicoba lagi run berikut): "
            + push.stderr.strip()[:300])
        return 1
    log(f"push berhasil ({ahead} commit)")
    return 0


def commit_pending() -> tuple[int, str]:
    new = [ROOT / f for f in git("ls-files", "--others", "--exclude-standard",
                                   "--", "content/artikel/*.json").stdout.split()]
    new = [f for f in new if f.suffix == ".json" and f.parent == ART_DIR]
    infra = [x for x in INFRA if git("status", "--porcelain", "--", x).stdout.strip()]
    ok: list[Path] = []
    for f in new:
        probs = qc(f)
        if probs:
            log(f"LEWATI {f.name}: " + "; ".join(probs))
        else:
            ok.append(f)
    for x in list(infra):
        if SECRET_RE.search((ROOT / x).read_text(encoding="utf-8", errors="replace")):
            log(f"TOLAK {x}: berisi pola rahasia")
            infra.remove(x)
    bad = len(new) - len(ok)
    if not ok and not infra:
        return (1 if bad else 0), ""
    pull = git("pull", "--rebase", "--autostash", check=False)
    if pull.returncode != 0:
        log("git pull --rebase gagal: " + (pull.stderr or pull.stdout).strip()[:300])
        git("rebase", "--abort", check=False)
        return 1, ""
    rel = [str(f.relative_to(ROOT)).replace("\\", "/") for f in ok]
    git("add", "--", *(rel + infra))
    slugs = ", ".join(f.stem for f in ok)
    msg = f"artikel: {slugs} (otomatis)" if ok else "collector: penerbit artikel otomatis"
    c = git("-c", "user.name=junuee", "-c", "user.email=junuee@gmail.com",
            "commit", "-m", msg, "--", *(rel + infra), check=False)
    if c.returncode != 0:
        log("commit gagal: " + (c.stderr or c.stdout).strip()[:300])
        return 1, ""
    return (1 if bad else 0), (slugs or "-") + (f" (+infra {', '.join(infra)})" if infra else "")


def main() -> int:
    code, done = commit_pending()
    pcode = push_if_ahead()
    if done and pcode == 0:
        log(f"TERBIT: {done}")
    return max(code, pcode)


if __name__ == "__main__":
    sys.exit(main())
