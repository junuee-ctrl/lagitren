"""Isi kolom image products.csv dari GOOGLE IMAGES — pilih gambar ORIGINAL besar.
Buka Chrome login (hidden, CDP 9222), cari tiap judul produk, ambil URL gambar
resolusi tinggi dari data hasil (bukan thumbnail gstatic). Selalu menimpa."""
import csv, os, re, socket, subprocess, sys, time
from urllib.parse import quote
os.environ.setdefault("BROWSER_CDP", "http://localhost:9222")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from start_chrome import CANDIDATES
PORT = 9222
CSV_PATH = os.path.join(HERE, "products.csv")

# ["https://....jpg",H,W]  (format data hasil Google Images)
TRIP = re.compile(r'\["(https?://[^"]+?\.(?:jpg|jpeg|png|webp)(?:\?[^"]*)?)",(\d+),(\d+)\]')

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

BAD = ("gstatic.com", "google.com", "googleusercontent.com/a/", "sprite", "logo")

def best_image(page, query):
    page.goto(f"https://www.google.com/search?q={quote(query)}&tbm=isch&hl=id&gl=ID",
              wait_until="domcontentloaded", timeout=45000)
    page.wait_for_timeout(1800)
    accept_consent(page)
    page.wait_for_timeout(1200)
    html = page.content()
    fallback = None
    for url, h, w in TRIP.findall(html):
        lo = url.lower()
        if any(b in lo for b in BAD):
            continue
        w, h = int(w), int(h)
        if w >= 300 and h >= 300:
            return url                      # gambar original besar pertama
        if fallback is None and w >= 150:
            fallback = url
    if fallback:
        return fallback
    # cadangan terakhir: thumbnail gstatic
    for el in page.query_selector_all("img"):
        src = el.get_attribute("src") or ""
        if src.startswith("https://") and "encrypted-tbn" in src:
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
                title = (r.get("title") or "").strip()
                if not title:
                    continue
                try:
                    img = best_image(page, title)
                    if img:
                        r["image"] = img; filled += 1
                        big = "BIG" if "gstatic" not in img else "thumb"
                        print(f"{big:5} {title[:30]:30} -> {img[:60]}")
                    else:
                        print(f"--    {title[:30]:30} (tak ada)")
                except Exception as exc:
                    print(f"ERR   {title[:30]:30} {type(exc).__name__}")
            try: page.close()
            except Exception: pass
            _browser.close_context(ctx)
    finally:
        if proc:
            try: proc.terminate()
            except Exception: pass
    with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
    print(f"\nSelesai: {filled} gambar diisi.")

if __name__ == "__main__":
    main()
