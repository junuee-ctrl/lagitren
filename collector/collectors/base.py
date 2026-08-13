"""Utilitas bersama untuk semua collector."""
from __future__ import annotations

import hashlib
import re
import unicodedata


def slugify(text: str, max_len: int = 60) -> str:
    """Ubah teks jadi slug aman untuk ID (huruf-kecil, tanda hubung).

    Non-Latin (Korea/Jepang/Arab/Thai...) → transliterasi via unidecode
    (mis. "사랑" → "salang"). Bila hasil < 3 huruf → slug hash stabil
    ("t-a1b2c3d4") supaya URL tetap konsisten & tidak jadi sampah SEO.
    """
    src = text
    norm = unicodedata.normalize("NFKD", text)
    ascii_txt = norm.encode("ascii", "ignore").decode("ascii")
    # Mayoritas karakter hilang saat di-ASCII-kan? → coba transliterasi.
    if len(ascii_txt.strip()) < max(3, len(src.strip()) // 2):
        try:
            from unidecode import unidecode  # type: ignore

            ascii_txt = unidecode(src)
        except Exception:
            pass
    s = re.sub(r"[^a-z0-9]+", "-", ascii_txt.lower()).strip("-")
    if len(s) < 3:
        s = "t-" + hashlib.sha256(src.encode("utf-8")).hexdigest()[:8]
    return s[:max_len]


def make_id(platform: str, key: str) -> str:
    """ID stabil per item, mis. 'google:iphone-16-harga'."""
    return f"{platform}:{slugify(key)}"


# ── Penyaringan kualitas & bahasa (dipakai IG/konten sosial) ──────────

# Aksara non-Latin asing → hampir pasti bukan konten Indonesia.
_FOREIGN_SCRIPT_RE = re.compile(
    "["
    "가-힣"  # Hangul (Korea)
    "぀-ヿ"  # Hiragana/Katakana (Jepang)
    "一-鿿"  # Han (Mandarin/Kanji)
    "ऀ-ॿ"  # Devanagari (Hindi)
    "฀-๿"  # Thai
    "؀-ۿ"  # Arab
    "Ѐ-ӿ"  # Sirilik
    "֐-׿"  # Ibrani
    "]"
)
# Karakter khas Vietnam (đ/ơ/ư + blok Latin Extended Additional).
_VIET_RE = re.compile("[đĐơƠưƯ]|[Ạ-ỹ]")

# Kata fungsi khas Indonesia (sinyal kuat konten ID).
_ID_HINTS = {
    "yang", "dan", "di", "ini", "itu", "dengan", "untuk", "tidak", "ada",
    "aku", "kamu", "banget", "nih", "aja", "gak", "ga", "bgt", "kalo",
    "kita", "buat", "lagi", "udah", "sudah", "juga", "karena", "bisa",
    "mau", "dari", "ke", "nya", "biar", "dong", "sih", "yg", "gue", "lu",
}
# Kata fungsi khas Spanyol/Portugis (spam akun bola luar: Garnacho, dll.).
_ES_PT_HINTS = {
    "que", "los", "las", "con", "para", "una", "por", "del", "não", "voce",
    "vo0ê", "está", "como", "mas", "pero", "muy", "este", "esta", "sao",
    "também", "com", "uma", "meu", "seu", "nós",
}


def clean_caption(caption: str, max_len: int = 90) -> str:
    """Ambil baris judul yang rapi dari caption.

    - Pilih baris pertama yang bermakna (≥3 huruf/angka).
    - Buang awalan hashtag/mention.
    - Potong di batas KATA (tidak memotong di tengah kata).
    """
    text = (caption or "").replace("\r", " ")
    chosen = ""
    for line in text.split("\n"):
        line = line.strip()
        stripped = re.sub(r"^(?:[#@][\w.]+\s*)+", "", line).strip()
        cand = stripped or line
        if len(re.sub(r"[^\w]", "", cand, flags=re.UNICODE)) >= 3:
            chosen = cand
            break
    if not chosen:
        return ""
    chosen = re.sub(r"\s+", " ", chosen).strip()
    if len(chosen) > max_len:
        cut = chosen[:max_len].rsplit(" ", 1)[0].strip()
        chosen = (cut or chosen[:max_len]).rstrip(" ,.;:!-–—") + "…"
    return chosen


def acceptable_language(text: str) -> bool:
    """True bila teks kemungkinan Indonesia/Inggris (bukan bahasa asing lain)."""
    if not text:
        return True  # tanpa caption → jangan tolak (post viral bisa tanpa teks)
    if _FOREIGN_SCRIPT_RE.search(text):
        return False
    if _VIET_RE.search(text):
        return False
    words = set(re.findall(r"[a-zA-Z]+", text.lower()))
    # Spanyol/Portugis tanpa satu pun kata Indonesia → tolak.
    if (words & _ES_PT_HINTS) and not (words & _ID_HINTS):
        return False
    return True
