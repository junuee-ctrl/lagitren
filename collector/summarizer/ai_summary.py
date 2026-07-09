"""Ringkasan AI: Ollama lokal (utama) dengan fallback Claude Haiku (opsional).

Selalu mengembalikan string. Bila semua backend gagal, kembalikan string
kosong agar collector tetap jalan (kartu tampil tanpa ringkasan).
"""
from __future__ import annotations

import logging
import re

import requests

import config
from .prompts import SYSTEM_PROMPT, build_user_prompt

log = logging.getLogger("ai")

_BANNED = ["100% terbukti", "pasti berhasil", "dijamin aman"]


def _clean(text: str) -> str:
    text = (text or "").strip()
    # Hilangkan awalan umum & tanda kutip pembungkus.
    text = re.sub(r"^(ringkasan|jawaban|summary)\s*[:\-]\s*", "", text, flags=re.I)
    text = text.strip().strip('"').strip()
    # Buang frasa terlarang bila lolos.
    for phrase in _BANNED:
        text = re.sub(re.escape(phrase), "", text, flags=re.I)
    # Rapikan spasi berlebih.
    return re.sub(r"\s+", " ", text).strip()


def _summarize_ollama(platform: str, title: str, context: str) -> str:
    url = f"{config.OLLAMA_HOST.rstrip('/')}/api/chat"
    payload = {
        "model": config.OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(platform, title, context)},
        ],
        "stream": False,
        "options": {"temperature": 0.4, "num_predict": 200},
    }
    resp = requests.post(url, json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    return _clean(data.get("message", {}).get("content", ""))


def _summarize_claude(platform: str, title: str, context: str) -> str:
    if not config.ANTHROPIC_API_KEY:
        return ""
    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": config.ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": config.ANTHROPIC_MODEL,
            "max_tokens": 200,
            "system": SYSTEM_PROMPT,
            "messages": [
                {
                    "role": "user",
                    "content": build_user_prompt(platform, title, context),
                }
            ],
        },
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()
    parts = data.get("content", [])
    text = "".join(p.get("text", "") for p in parts if p.get("type") == "text")
    return _clean(text)


def summarize(platform: str, title: str, context: str = "") -> str:
    """Coba Ollama dulu, lalu Claude, lalu kembalikan '' bila gagal."""
    try:
        out = _summarize_ollama(platform, title, context)
        if out:
            return out
        log.warning("Ollama mengembalikan kosong untuk: %s", title)
    except Exception as exc:
        log.warning("Ollama gagal (%s), coba fallback Claude...", exc)

    try:
        out = _summarize_claude(platform, title, context)
        if out:
            return out
    except Exception as exc:
        log.warning("Claude fallback gagal: %s", exc)

    return ""
