"""틱톡샵 어필리에이트 패널에서 상품 목록을 가져온다 (로그인된 Chrome 사용).

운영자 PC에서 실행되며, TikTok/Instagram/X 수집기와 동일하게 CDP로 실제
Chrome에 붙는다. 결과는 `collector/products.csv`에 기록되고, 같은 실행 안에서
`shopping_products` 수집기가 그 파일을 읽어 D1로 보낸다.

주: 이 파일은 운영자(한국어)만 읽는 도구라 메시지를 한국어로 쓴다.
사이트에 노출되는 문구는 기존대로 인도네시아어를 유지한다.

두 가지 모드:

  python affiliate_panel.py --discover "<패널 URL>"
      패널을 열고 오가는 JSON 응답을 전부 녹화한 뒤
      logs/panel_discovery.json + logs/panel_dump/*.json 에 저장한다.
      한 번만 실행해서 보고서를 넘기면, 셀렉터를 추측하지 않고
      상품 목록 엔드포인트를 확정할 수 있다.

  python affiliate_panel.py [--limit 20] [--dry-run]
      일반 모드 (아래 PANEL_URL + PANEL_ENDPOINT가 채워져 있어야 함).

사전 조건 (다른 로컬 수집기와 동일):
  .env 에 BROWSER_CDP=http://127.0.0.1:9222
  그리고 Chrome이 --remote-debugging-port=9222 로 실행 중일 것
  (start_chrome_cdp.bat 실행하면 자동 처리)
"""
from __future__ import annotations

import argparse
import csv
import os
import json
import logging
import re
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

import config
from collectors import _browser

logging.basicConfig(level=logging.INFO, format="%(levelname)s [%(name)s] %(message)s")
log = logging.getLogger("panel")

ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / "products.csv"
LOG_DIR = ROOT / "logs"

# Diisi setelah mode --discover memastikan endpointnya.
PANEL_URL = ("https://partner.tiktokshop.com/affiliate-product-management/"
             "affiliate-product-pool/ranking?tab=0&market=4&prePage=product_ranking")
# discover(2026-09-16)로 확인된 엔드포인트
PANEL_ENDPOINT = "/affiliate/partner/product/ranking/list"
MAX_PRODUCTS = 20

FIELDS = ["rank", "title", "image", "price", "sales", "category",
          "shop", "commission", "commission_rate", "affiliate_url"]

# Kata kunci yang menandai sebuah respons JSON kemungkinan berisi daftar produk.
HINTS = ("product", "item", "commission", "sold", "sale", "gmv", "title")


def _rupiah(v) -> str:
    try:
        return "Rp" + f"{int(round(float(v))):,}".replace(",", ".")
    except Exception:
        return str(v or "")


# ---------------------------------------------------------------- discovery

def discover(url: str, wait_s: int = 25) -> None:
    """Rekam semua respons JSON saat panel dibuka, lalu tulis laporannya."""
    LOG_DIR.mkdir(exist_ok=True)
    dump_dir = LOG_DIR / "panel_dump"
    dump_dir.mkdir(exist_ok=True)
    for old in dump_dir.glob("*.json"):
        old.unlink()

    seen: list[dict] = []

    with sync_playwright() as p:
        ctx = _browser.get_context(p)
        page = ctx.new_page()

        def on_response(resp):
            try:
                ct = (resp.headers or {}).get("content-type", "")
                if "json" not in ct.lower():
                    return
                body = resp.text()
            except Exception:
                return
            if len(body) < 200:
                return
            low = body.lower()
            score = sum(1 for h in HINTS if h in low)
            if score < 3:
                return
            idx = len(seen)
            name = f"{idx:02d}_{re.sub(r'[^a-z0-9]+', '-', resp.url.split('?')[0].lower())[-70:]}.json"
            try:
                (dump_dir / name).write_text(body[:400_000], encoding="utf-8")
            except Exception:
                pass
            seen.append({
                "url": resp.url.split("?")[0],
                "status": resp.status,
                "bytes": len(body),
                "hint_score": score,
                "file": name,
                "sample_keys": _top_keys(body),
            })

        page.on("response", on_response)
        log.info("패널 여는 중: %s", url)
        page.goto(url, wait_until="load", timeout=60_000)
        # Panel memuat daftar lewat XHR & lazy-scroll — gulirkan beberapa kali.
        for _ in range(6):
            page.mouse.wheel(0, 1800)
            page.wait_for_timeout(1500)
        page.wait_for_timeout(wait_s * 1000 // 6)
        try:
            page.remove_listener("response", on_response)
        except Exception:
            pass
        log.info("최종 URL: %s", page.url)
        _browser.close_context(ctx)

    seen.sort(key=lambda r: (-r["hint_score"], -r["bytes"]))
    report = {"opened": url, "captured": len(seen), "responses": seen[:40]}
    out = LOG_DIR / "panel_discovery.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    log.info("완료. JSON 응답 %d건 저장됨.", len(seen))
    log.info("보고서  : %s  ← 이 파일을 보내주세요", out)
    log.info("원본 덤프: %s  ← 계정 정보가 섞일 수 있으니 보내지도, 커밋하지도 마세요", dump_dir)
    for r in seen[:8]:
        log.info("  점수 %d  %7d B  %s", r["hint_score"], r["bytes"], r["url"])


def _top_keys(body: str, limit: int = 14) -> list[str]:
    try:
        data = json.loads(body)
    except Exception:
        return []
    keys: list[str] = []

    def walk(o, depth=0):
        if len(keys) >= limit or depth > 4:
            return
        if isinstance(o, dict):
            for k, v in o.items():
                if k not in keys:
                    keys.append(k)
                walk(v, depth + 1)
        elif isinstance(o, list) and o:
            walk(o[0], depth + 1)

    walk(data)
    return keys[:limit]


# ------------------------------------------------------------------ scrape

def scrape(limit: int = MAX_PRODUCTS) -> list[dict]:
    if not PANEL_URL or not PANEL_ENDPOINT:
        log.error("PANEL_URL/PANEL_ENDPOINT가 비어 있음 — 먼저 --discover 를 실행하세요.")
        sys.exit(2)

    payloads: list[dict] = []
    with sync_playwright() as p:
        ctx = _browser.get_context(p)
        page = ctx.new_page()

        def on_response(resp):
            if PANEL_ENDPOINT not in resp.url:
                return
            try:
                payloads.append(resp.json())
            except Exception:
                pass

        page.on("response", on_response)
        page.goto(PANEL_URL, wait_until="load", timeout=60_000)
        deadline = time.time() + 45
        while time.time() < deadline and _count(payloads) < limit:
            page.mouse.wheel(0, 1800)
            page.wait_for_timeout(1500)
        try:
            page.remove_listener("response", on_response)
        except Exception:
            pass
        _browser.close_context(ctx)

    rows = _parse(payloads, limit)
    if not rows:
        log.error("상품을 0개 읽음 — 패널 구조가 바뀌었을 수 있음. --discover 를 다시 실행하세요.")
        sys.exit(3)
    return rows


def _count(payloads) -> int:
    return sum(len(_items(p)) for p in payloads)


def _items(payload) -> list[dict]:
    """응답에서 상품 배열을 찾는다 (data.products 등 위치가 바뀌어도 동작)."""
    best: list[dict] = []

    def walk(o, depth=0):
        nonlocal best
        if depth > 7:
            return
        if isinstance(o, list) and o and isinstance(o[0], dict):
            if "product_id" in o[0] or "title" in o[0]:
                if len(o) > len(best):
                    best = o
        if isinstance(o, dict):
            for v in o.values():
                walk(v, depth + 1)
        elif isinstance(o, list):
            for v in o[:50]:
                walk(v, depth + 1)

    walk(payload)
    return best


def _price(v) -> str:
    """price 는 {"format_price": "Rp10.999"} 또는 문자열로 온다."""
    if isinstance(v, dict):
        for k in ("format_price", "formatPrice", "price", "min_price"):
            if v.get(k):
                return str(v[k])
        return ""
    return str(v or "")


def _rate(v) -> str:
    """commission_rate 는 베이시스 단위 정수(600 = 6%)."""
    try:
        return f"{round(float(v) / 100)}%"
    except Exception:
        return str(v or "")


# 패널이 카테고리를 주지 않으므로 제목 키워드로 추정한다.
# 카테고리는 카드의 이모지 타일을 결정할 뿐, 수치가 아니다.
CAT_RULES = [
    ("health", r"\bteh\b|herbal|collagen drink|minuman|vitamin|suplemen|madu"),
    ("home", r"gantungan|hook|tempel tembok|rak\b|wall|dapur|toples|keranjang"),
    ("fashion", r"hijab|bergo|khimar|jilbab|kerudung|gamis|baju|kaos|tas\b|sepatu|pouch"),
    ("mom_baby", r"\bbayi\b|baby|anak\b|mainan|popok"),
    ("gadget", r"charger|kabel data|earphone|headset|powerbank|lampu led"),
    ("food", r"keripik|snack|kopi\b|mie\b|sambal"),
]


def _category(title: str, fallback: str = "beauty") -> str:
    low = title.lower()
    for cat, pat in CAT_RULES:
        if re.search(pat, low):
            return cat
    return fallback


# 판매 홍보용 접두 라벨 제거 (단, 실제 정보인 것은 남긴다).
_HYPE = re.compile(r"^\s*(?:\[[^\]]*\]|\u3010[^\u3011]*\u3011)\s*")
_KEEP = re.compile(r"BPOM|BUY 1|GET \d|FREE\b", re.I)


def _clean_title(t: str, limit: int = 92) -> str:
    t = str(t or "").strip()
    while True:
        m = _HYPE.match(t)
        if not m or _KEEP.search(m.group(0)):
            break
        t = t[m.end():]
    t = re.sub(r"\s+", " ", t).strip(" -|")
    # 패널 원문에 붙어버린 낱말 분리 (대문자 연속 뒤 대문자+소문자).
    t = re.sub(r"([A-Z]{2,})([A-Z][a-z])", r"\1 \2", t)
    if len(t) > limit:
        t = t[:limit].rsplit(" ", 1)[0].rstrip(" ,-|")
    return t


def _affiliate_url(product_id: str) -> str:
    """패널의 'Copy link' 와 동일한 형식으로 조립한다."""
    return (f"https://shop-id.tokopedia.com/view/product/{product_id}"
            "?region=ID&locale=en&source=agency")


def _previous_categories() -> dict[str, str]:
    """이전 CSV에서 product_id -> category 를 읽어 수동 분류를 보존한다."""
    out: dict[str, str] = {}
    if not CSV_PATH.exists():
        return out
    try:
        with CSV_PATH.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                m = re.search(r"/product/(\d+)", row.get("affiliate_url", ""))
                if m and row.get("category"):
                    out[m.group(1)] = row["category"]
    except Exception:
        pass
    return out


def _dedup_key(title: str, n: int = 34) -> str:
    """같은 상품의 다른 캠페인을 묶기 위한 키.

    패널에는 동일 상품이 캠페인별로 따로 올라오며 product_id 도 다르다
    (예: [BEST SELLER] / [SPECIAL MEGA LIVE] 같은 JJ Glow 비누).
    영숫자만 남긴 앞부분이 같으면 같은 상품으로 본다.
    """
    return re.sub(r"[^a-z0-9]", "", title.lower())[:n]


def _parse(payloads: list[dict], limit: int) -> list[dict]:
    prev = _previous_categories()
    rows: list[dict] = []
    seen: set[str] = set()
    seen_key: dict[str, int] = {}
    for payload in payloads:
        for it in _items(payload):
            pid = str(it.get("product_id") or "").strip()
            title = _clean_title(it.get("title"))
            if not pid or not title or pid in seen:
                continue
            key = _dedup_key(title)
            if key in seen_key:
                log.info("중복 제외: %s (이미 %d번으로 등록)", title[:46], seen_key[key])
                continue
            seen_key[key] = len(rows) + 1
            seen.add(pid)
            shop = it.get("shop_info") or {}
            rows.append({
                "rank": len(rows) + 1,
                "title": title,
                "image": str(it.get("cover_url") or ""),
                "price": _price(it.get("price")),
                "sales": str(it.get("metrics") or ""),
                "category": prev.get(pid) or _category(title),
                "shop": str(shop.get("shop_name") or "") if isinstance(shop, dict) else "",
                "commission": str(it.get("earn_amount") or ""),
                "commission_rate": _rate(it.get("commission_rate")),
                "affiliate_url": _affiliate_url(pid),
            })
            if len(rows) >= limit:
                return rows
    return rows


def write_csv(rows: list[dict]) -> None:
    with CSV_PATH.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    log.info("상품 %d개를 %s 에 기록함", len(rows), CSV_PATH)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--discover", metavar="URL", help="패널 JSON 응답을 녹화하고 종료")
    ap.add_argument("--limit", type=int, default=MAX_PRODUCTS)
    ap.add_argument("--dry-run", action="store_true", help="결과만 출력하고 CSV는 쓰지 않음")
    a = ap.parse_args()

    # 패널 전용 브라우저를 별도 포트로 띄운 경우 PANEL_CDP 가 우선한다.
    panel_cdp = os.environ.get("PANEL_CDP", "").strip()
    if panel_cdp:
        config.BROWSER_CDP = panel_cdp
        log.info("PANEL_CDP 사용: %s", panel_cdp)

    if not config.BROWSER_CDP:
        log.error("BROWSER_CDP가 .env에 없음 — 패널은 로그인된 Chrome이 필요합니다.")
        log.error("다음 줄을 추가하세요:  BROWSER_CDP=http://127.0.0.1:9222")
        sys.exit(2)

    if not _browser.cdp_alive():
        log.error("=" * 66)
        log.error("Chrome이 디버깅 포트(%s)로 실행되어 있지 않습니다.", _browser.cdp_url())
        log.error("collector 폴더의 start_chrome_cdp.bat 를 먼저 실행하고,")
        log.error("Chrome 창이 열리면 partner.tiktokshop.com 로그인 상태를 확인한 뒤")
        log.error("이 명령을 다시 실행하세요. Chrome은 계속 열어두어야 합니다.")
        log.error("=" * 66)
        sys.exit(4)

    if a.discover:
        discover(a.discover)
        return

    rows = scrape(a.limit)
    for r in rows:
        log.info("%2d %-9s %8s %4s | %s", r["rank"], r["category"][:9],
                 r["commission"], r["commission_rate"], r["title"][:50])
    missing = [r["rank"] for r in rows if not r["affiliate_url"]]
    if missing:
        log.warning("어필리에이트 링크가 비어 있는 행: %s", missing)
    if a.dry_run:
        log.info("--dry-run: CSV를 쓰지 않았습니다.")
        return
    write_csv(rows)


if __name__ == "__main__":
    main()
