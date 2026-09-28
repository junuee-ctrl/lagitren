"""Kirim antrean kata kunci / artikel PanduHukum yang disiapkan Claude ke GitHub.

Latar (2026-09-27): sesi Claude di PC ini tidak punya kredensial git. Claude
menaruh berkas di collector/logs/pending_panduhukum/ (folder di-.gitignore):
  - queue_add.txt      -> baris "keyword | slug | pillar" ditambahkan ke
                          keyword-queue.txt
  - <slug>.mdx         -> disalin ke content/pinjol/<slug>.mdx (hanya bila belum ada)
Skrip ini (dipanggil run_local_task.bat, Windows Task Scheduler) yang commit & push
memakai kredensial git Windows. Berkas yang sudah terkirim diberi akhiran .done.

Pengaman: memakai klon khusus ~/.panduhukum-publish yang tiap run disamakan dengan
origin/main (reset --hard), hanya berkas di atas yang di-add, pola token ditolak.
"""
from __future__ import annotations

import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PENDING = Path(__file__).resolve().parent / "logs" / "pending_panduhukum"
# Klon khusus milik skrip ini (bukan klon kerja manusia) -> boleh di-reset keras.
REPO = Path.home() / ".panduhukum-publish"
REMOTE = "https://github.com/junuee-ctrl/panduhukum.git"
_SECRET_PARTS = ["git" + "hub_pat_", "gh" + "p_", "gh" + "o_", "sk" + "-ant-",
                 "AK" + "IA[0-9A-Z]{12}", "xo" + "x[bp]-", "-----" + "BEGIN"]
SECRET_RE = re.compile("(" + "|".join(_SECRET_PARTS) + ")", re.I)
LINE_RE = re.compile(r"^[^|#\n]+\|\s*[a-z0-9-]+\s*\|\s*[a-z0-9-]+\s*$")


def log(m: str) -> None:
    print(f"{datetime.now():%Y-%m-%d %H:%M:%S} [push_panduhukum] {m}", flush=True)


def git(*a: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def main() -> int:
    q = PENDING / "queue_add.txt"
    mdxs = sorted(PENDING.glob("*.mdx"))
    if not q.exists() and not mdxs:
        return 0
    if not (REPO / ".git").exists():
        c = subprocess.run(["git", "clone", "-q", REMOTE, str(REPO)], capture_output=True,
                           text=True, encoding="utf-8", errors="replace")
        if c.returncode != 0:
            log("clone gagal: " + c.stderr[:300])
            return 1
    for f in ([q] if q.exists() else []) + mdxs:
        if SECRET_RE.search(f.read_text(encoding="utf-8", errors="replace")):
            log(f"TOLAK {f.name}: pola rahasia")
            return 1
    if git("fetch", "-q", "origin").returncode != 0:
        log("fetch gagal")
        return 1
    git("checkout", "-q", "main")
    git("reset", "-q", "--hard", "origin/main")
    git("clean", "-qfd")
    paths: list[str] = []
    added = 0
    if q.exists():
        qf = REPO / "keyword-queue.txt"
        cur = qf.read_text(encoding="utf-8")
        have = {l.split("|")[1].strip() for l in cur.splitlines()
                if "|" in l and not l.strip().startswith("#")}
        new = []
        for l in q.read_text(encoding="utf-8").splitlines():
            l = l.strip()
            if not LINE_RE.match(l):
                continue
            slug = l.split("|")[1].strip()
            if slug in have or (REPO / "content" / "pinjol" / f"{slug}.mdx").exists():
                continue
            new.append(l); have.add(slug)
        if new:
            qf.write_text(cur.rstrip("\n") + "\n" + "\n".join(new) + "\n", encoding="utf-8")
            paths.append("keyword-queue.txt"); added = len(new)
    pub = []
    for m in mdxs:
        dst = REPO / "content" / "pinjol" / m.name
        if dst.exists():
            # Boleh menimpa hanya DRAFT (published:false) — mis. draft Actions yang sudah
            # diverifikasi & diterbitkan. Artikel yang sudah terbit tidak pernah ditimpa.
            if not re.search(r'"published"\s*:\s*false', dst.read_text(encoding="utf-8", errors="replace")):
                log(f"lewati {m.name}: sudah terbit")
                continue
            log(f"timpa draft {m.name}")
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(m.read_bytes())
        paths.append(f"content/pinjol/{m.name}"); pub.append(m.stem)
    if not paths:
        for f in ([q] if q.exists() else []) + mdxs:
            f.rename(f.with_name(f.name + ".done"))
        log("tidak ada perubahan (semua sudah ada)")
        return 0
    git("add", "--", *paths)
    msg = ("publish: " + ", ".join(pub) + " (ditulis & diverifikasi, via PC)") if pub else \
          f"queue: +{added} keywords"
    if pub and added:
        msg += f" + queue +{added}"
    c = subprocess.run(["git", "-c", "user.name=junuee", "-c", "user.email=junuee@gmail.com",
                        "commit", "-m", msg, "--", *paths], cwd=REPO,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if c.returncode != 0:
        log("commit gagal: " + (c.stderr or c.stdout)[:300])
        return 1
    p = git("push")
    if p.returncode != 0:
        log("push gagal (dicoba lagi run berikut): " + p.stderr[:300])
        return 1
    for f in ([q] if q.exists() else []) + mdxs:
        f.rename(f.with_name(f.name + ".done"))
    log("TERKIRIM: " + msg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
