"""discover 덤프에서 상품 목록의 '구조만' 안전하게 출력한다.

logs/panel_dump/*.json 중 ranking/list 응답을 찾아, 상품 배열의 키 이름과
값의 형태만 보여준다. 계정·토큰·서명처럼 민감할 수 있는 값은 가린다.
출력 결과는 그대로 복사해서 공유해도 안전하다.

사용법:
  cd C:\\lagitren\\collector
  python panel_schema.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

DUMP = Path(__file__).resolve().parent / "logs" / "panel_dump"

# 값이 가려져야 하는 키 (부분 일치, 대소문자 무시)
SECRET = re.compile(
    r"token|uid|user_?id|seller|shop_?id|creator_?id|auth|cookie|session|sign|"
    r"secret|access|account|email|phone|region_?code|open_?id|sec_",
    re.I,
)
# 상품 배열임을 알려주는 키
TITLE_KEYS = ("title", "product_name", "productName", "name", "product_title")


def mask(key: str, val):
    if SECRET.search(key):
        return "<가림>"
    if isinstance(val, str):
        if len(val) > 70:
            return val[:70] + f"...({len(val)}자)"
        # 19자리 이상 숫자 문자열 = 내부 ID → 길이만
        if val.isdigit() and len(val) >= 15:
            return f"<숫자ID {len(val)}자리>"
        return val
    if isinstance(val, (int, float, bool)) or val is None:
        return val
    if isinstance(val, list):
        return f"[리스트 {len(val)}개]" + (
            f" 첫 항목 키: {list(val[0])[:10]}" if val and isinstance(val[0], dict) else ""
        )
    if isinstance(val, dict):
        return "{" + ", ".join(list(val)[:10]) + "}"
    return type(val).__name__


def find_items(obj, depth=0):
    """상품처럼 보이는 dict 리스트 중 가장 긴 것을 찾는다."""
    best = []

    def walk(o, d=0):
        nonlocal best
        if d > 7:
            return
        if isinstance(o, list) and o and isinstance(o[0], dict):
            if any(k in o[0] for k in TITLE_KEYS) and len(o) > len(best):
                best = o
        if isinstance(o, dict):
            for v in o.values():
                walk(v, d + 1)
        elif isinstance(o, list):
            for v in o[:30]:
                walk(v, d + 1)

    walk(obj)
    return best


def report(path: Path) -> bool:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"  (읽기 실패: {exc})")
        return False
    items = find_items(data)
    if not items:
        print("  상품 배열을 찾지 못함.")
        return False

    print(f"  상품 개수: {len(items)}")
    print(f"  최상위 응답 키: {list(data)[:12] if isinstance(data, dict) else type(data).__name__}")
    print("  --- 첫 번째 상품의 필드 ---")
    for k, v in items[0].items():
        print(f"    {k:<28} = {mask(k, v)}")

    if len(items) > 1:
        diff = [k for k in items[0] if str(items[0].get(k)) != str(items[1].get(k))]
        print(f"  --- 상품마다 달라지는 필드({len(diff)}개) ---")
        print("    " + ", ".join(diff[:25]))
    return True


def main() -> None:
    if not DUMP.exists():
        print(f"덤프 폴더가 없습니다: {DUMP}")
        print("먼저 affiliate_panel.py --discover 를 실행하세요.")
        return

    files = sorted(DUMP.glob("*.json"))
    targets = [f for f in files if "ranking" in f.name or "product" in f.name]
    if not targets:
        targets = files

    print(f"덤프 파일 {len(files)}개 중 {len(targets)}개 검사\n")
    for f in targets:
        print(f"■ {f.name}  ({f.stat().st_size:,} B)")
        report(f)
        print()


if __name__ == "__main__":
    main()
