"""Jalankan collector lokal (TikTok, Instagram, X) sekali — untuk penjadwalan.

Alur:
  1. Cek lock file — bila run lain masih hidup & belum kedaluwarsa, keluar.
  2. Bila Chrome debug (port 9222) belum jalan, buka Chrome dgn profil
     'chrome-lagitren' (yang sudah login) di posisi layar tersembunyi.
  3. Jalankan tiap sumber di PROSES TERPISAH dgn batas waktu keras (F2).
     Satu sumber macet → dibunuh paksa, sumber lain tetap jalan.
  4. Tutup Chrome yang tadi dibuka + hapus lock.

Pasca-insiden 2026-08-18 (Playwright menggantung 13j40m):
  - F2: isolasi proses per sumber + terminate/kill saat lewat batas.
  - F4: lock file PID (anti-tumpuk) + batas waktu global 28 menit
        (Task Scheduler juga memutus di 30 menit — lapis kedua).

Cocok untuk Windows Task Scheduler (lihat LOCAL_COLLECTOR.md).
Login TikTok & Instagram harus sudah tersimpan di profil (jalankan
`python login_browser.py` / `python start_chrome.py` sekali sebelumnya).
"""
import multiprocessing as mp
import os
import socket
import subprocess
import sys
import threading
import time
from datetime import datetime

# Pastikan collector memakai mode CDP.
os.environ.setdefault("BROWSER_CDP", "http://localhost:9222")
# Di lokal (browser login tersedia) → aktifkan pengambilan tweet teratas X.
os.environ.setdefault("TWITTER_WITH_TWEETS", "1")

PORT = 9222
LOCK_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "run_local.lock")
STALE_LOCK_MIN = 40          # lock lebih tua dari ini = run lama macet → ambil alih
GLOBAL_LIMIT_SEC = 28 * 60   # batas hidup total proses ini (F4)

# Batas waktu keras per sumber, detik (F2). TikTok paling lama karena
# membuka halaman tag untuk video per hashtag.
SOURCE_TIMEOUTS = {
    "tiktok": 600,
    "instagram": 420,
    "twitter": 420,
}
DEFAULT_SOURCE_TIMEOUT = 300


def _find_chrome():
    from start_chrome import CANDIDATES
    return next((c for c in CANDIDATES if os.path.exists(c)), None)


def _port_open(host: str, port: int) -> bool:
    with socket.socket() as s:
        s.settimeout(1)
        try:
            s.connect((host, port))
            return True
        except OSError:
            return False


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except PermissionError:
        return True
    except OSError:
        return False


def _kill_tree(pid: int) -> None:
    """Bunuh proses beserta anak-anaknya (node playwright, dsb.)."""
    try:
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/PID", str(pid), "/T", "/F"],
                capture_output=True, timeout=15,
            )
        else:
            os.kill(pid, 9)
    except Exception:
        pass


def _acquire_lock() -> bool:
    """F4: satu instance saja. True = boleh lanjut."""
    if os.path.exists(LOCK_FILE):
        try:
            with open(LOCK_FILE, encoding="utf-8") as f:
                pid_s, ts_s = f.read().strip().split("|", 1)
            old_pid = int(pid_s)
            age_min = (time.time() - float(ts_s)) / 60
        except Exception:
            old_pid, age_min = 0, STALE_LOCK_MIN + 1
        if old_pid and _pid_alive(old_pid) and age_min < STALE_LOCK_MIN:
            print(f"[lock] Run lain masih jalan (pid={old_pid}, {age_min:.0f} mnt) — keluar.")
            return False
        # Lock basi: run lama macet → bunuh sisa prosesnya, ambil alih.
        if old_pid and _pid_alive(old_pid):
            print(f"[lock] Lock basi ({age_min:.0f} mnt) — bunuh pid lama {old_pid}.")
            _kill_tree(old_pid)
        try:
            os.remove(LOCK_FILE)
        except OSError:
            pass
    with open(LOCK_FILE, "w", encoding="utf-8") as f:
        f.write(f"{os.getpid()}|{time.time()}")
    return True


def _release_lock() -> None:
    try:
        os.remove(LOCK_FILE)
    except OSError:
        pass


def _worker(platform: str, q) -> None:
    """Jalan di PROSES ANAK: kumpulkan satu platform."""
    try:
        from main import run
        res = run([platform])
        q.put((platform, "ok", res.get(platform) if isinstance(res, dict) else res))
    except Exception as exc:  # noqa: BLE001
        q.put((platform, "error", f"{type(exc).__name__}: {exc}"[:200]))


def _run_isolated(platforms: list[str]) -> dict:
    """F2: tiap sumber proses sendiri + join(timeout) + kill tree."""
    summary: dict = {}
    q = mp.Queue()
    for pf in platforms:
        limit = SOURCE_TIMEOUTS.get(pf, DEFAULT_SOURCE_TIMEOUT)
        t0 = time.time()
        proc = mp.Process(target=_worker, args=(pf, q), name=f"collect-{pf}")
        proc.start()
        proc.join(timeout=limit)
        dur = time.time() - t0
        if proc.is_alive():
            print(f"[{pf}] LEWAT BATAS {limit}s — proses dibunuh paksa.")
            _kill_tree(proc.pid)
            proc.join(timeout=10)
            if proc.is_alive():
                proc.kill()
            summary[pf] = f"TIMEOUT>{limit}s"
        else:
            summary[pf] = f"exit={proc.exitcode}"
        # Ambil hasil dari queue (tanpa menunggu).
        while True:
            try:
                ppf, status, val = q.get_nowait()
            except Exception:
                break
            summary[ppf] = val if status == "ok" else f"ERR {val}"
        print(f"[{pf}] selesai {dur:.0f}s → {summary.get(pf)}")
    return summary


def main() -> None:
    print(f"=== run_local mulai {datetime.now():%Y-%m-%d %H:%M:%S} (pid={os.getpid()}) ===")
    if not _acquire_lock():
        return

    # F4: sabuk pengaman terakhir — proses bunuh diri setelah GLOBAL_LIMIT_SEC.
    def _suicide():
        print(f"[watchdog] Lewat {GLOBAL_LIMIT_SEC//60} menit — keluar paksa.")
        _release_lock()
        os._exit(3)

    timer = threading.Timer(GLOBAL_LIMIT_SEC, _suicide)
    timer.daemon = True
    timer.start()

    profile = os.path.expandvars(r"%USERPROFILE%\chrome-lagitren")
    if os.name != "nt":
        profile = os.path.expanduser("~/chrome-lagitren")

    proc = None
    try:
        if not _port_open("127.0.0.1", PORT):
            chrome = _find_chrome()
            if not chrome:
                print("Chrome tidak ditemukan.")
                sys.exit(1)
            proc = subprocess.Popen(
                [
                    chrome,
                    f"--remote-debugging-port={PORT}",
                    f"--user-data-dir={profile}",
                    "--window-position=-32000,-32000",  # sembunyikan jendela
                    "--window-size=1280,900",
                    "--no-first-run",
                    "--no-default-browser-check",
                ]
            )
            for _ in range(30):
                if _port_open("127.0.0.1", PORT):
                    break
                time.sleep(1)
            time.sleep(2)

        # SELALU jalankan ketiganya. (Rotasi per-jam sebelumnya membuat
        # Instagram bisa terlewat berhari-hari.)
        cli = [a for a in sys.argv[1:] if not a.startswith("-")]
        platforms = cli if cli else ["tiktok", "instagram", "twitter"]
        results = _run_isolated(platforms)
        print("Ringkasan:", results)
    finally:
        timer.cancel()
        if proc:
            try:
                proc.terminate()
            except Exception:
                pass
        _release_lock()
        print(f"=== run_local selesai {datetime.now():%Y-%m-%d %H:%M:%S} ===")


if __name__ == "__main__":
    mp.freeze_support()
    main()
