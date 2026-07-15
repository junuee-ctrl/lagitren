"""Isi kolom image products.csv dari GOOGLE IMAGES (thumbnail gstatic).
Buka Chrome login (hidden, CDP 9222), cari tiap judul produk di Google Images,
ambil URL gambar pertama, tulis balik ke products.csv."""
import csv, os, socket, subprocess, sys, time
from urllib.parse import quote
os.environ.setdefault("BROWSER_CDP", "http://localhost:9222")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from start_chrome import CANDIDATES
PORT = 9222
CSV_PATH = os.path.join(HERE, "products.csv")

def port_open():
    with socket.socket() as s:
        s.settimeout(1)
        try:
            s.connect(("127.0.0.1", PORT)); return True
        except OSError:
            return False

def launch_chrome():
    profile = os.path.expandvars(r"%USERPROFILE%\chrome-lagitren")
    chrome = next((c for c in CANDIDATES if os.path.exists(c)), None)
    if not chrome:
        print("Chrome tidak ditemukan."); sys.exit(1)
    proc = subprocess.Popen([
        chrome, f"--remote-debugging-port={PORT}", f"--user-data-dir={profile}",
        "--window-position=-32000,-32000", "--window-size=1280,900",
        "--no-first-run", "--no-default-browser-check",
    ])
    for _ in range(30):
        if port_open(): break
        time.sleep(1)
    time.sleep(2)
    return proc

def accept_consent(page):
    for txt in ("Terima semua", "Accept all", "Setuju semua", "Saya setuju", "I agree"):
        try:
            b = page.get_by_text(txt, exact=False).first
            if b and b.is_visible():
                b.click(timeout=1500); page.wait_for_timeout(1200); return
        except Exception:
            continue

def first_image(page, query):
    q = quote(f"{query}")
    page.goto(f"https://www.google.com/search?q={q}&tbm=isch&hl=id&gl=ID",
              wait_until="domcontentloaded", timeout=45000)
    page.wait_for_timeout(2000)
    accept_consent(page)
    page.wait_for_timeout(1800)
    for el in page.query_selector_all("img"):
        src = el.get_attribute("src") or ""
        if src.startswith("https://") and ("encrypted-tbn" in src or "gstatic.com/images" in src):
            return src
    return None

def main():
    from playwright.sync_api import sync_playwright  # noqa
    from collectors import _browser
    with open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f); fields = reader.fieldnames or []; rows = list(reader)
    if "image" not in fields:
        fields = list(fields) + ["image"]
    proc = None if port_open() else launch_chrome()
    filled = 0
    try:
        with sync_playwright() as p:
            ctx = _browser.get_context(p); page = ctx.new_page()
            for r in rows:
                if (r.get("image") or "").strip():
                    continue
                title = (r.get("title") or "").strip()
                if not title:
                    continue
                try:
                    img = first_image(page, title)
                    if img:
                        r["image"] = img; filled += 1
                        print(f"OK  {title[:32]:32} -> {img[:55]}")
                    else:
                        print(f"--  {title[:32]:32} (tak ada)")
                except Exception as exc:
                    print(f"ERR {title[:32]:32} {type(exc).__name__}")
            try: page.close()
            except Exception: pass
            _browser.close_context(ctx)
    finally:
        if proc:
            try: proc.terminate()
            except Exception: pass
    with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
    print(f"\nSelesai: {filled} gambar diisi ke products.csv")

if __name__ == "__main__":
    main()
