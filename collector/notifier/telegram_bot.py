"""Notifikasi status ke Telegram.

Aman dipanggil meski token belum diisi (akan mencetak ke log saja).
"""
from __future__ import annotations

import logging

import requests

import config

log = logging.getLogger("telegram")


def send(text: str, silent: bool = False) -> bool:
    if not (config.TELEGRAM_BOT_TOKEN and config.TELEGRAM_CHAT_ID):
        log.info("[telegram tidak dikonfigurasi] %s", text)
        return False
    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        resp = requests.post(
            url,
            json={
                "chat_id": config.TELEGRAM_CHAT_ID,
                "text": text,
                "parse_mode": "HTML",
                "disable_notification": silent,
                "disable_web_page_preview": True,
            },
            timeout=20,
        )
        resp.raise_for_status()
        return True
    except Exception as exc:
        log.warning("Gagal kirim Telegram: %s", exc)
        return False


def notify_success(summary: dict[str, int]) -> None:
    parts = [f"{k.capitalize()} {v}" for k, v in summary.items()]
    send("✅ Pengumpulan selesai: " + ", ".join(parts) + " item.")


def notify_error(platform: str, message: str) -> None:
    send(f"❌ Gagal mengumpulkan <b>{platform}</b>: {message}")
