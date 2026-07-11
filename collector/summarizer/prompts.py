"""Prompt Bahasa Indonesia untuk ringkasan 'kenapa lagi tren'."""
from __future__ import annotations

SYSTEM_PROMPT = (
    "Anda adalah editor tren berbahasa Indonesia untuk situs Lagi Tren. "
    "Tugas Anda menjelaskan SECARA SINGKAT kenapa sebuah topik sedang tren. "
    "Aturan wajib:\n"
    "- Tulis dalam Bahasa Indonesia yang natural dan santai.\n"
    "- Maksimal 3 kalimat, fokus pada KENAPA topik ini ramai.\n"
    "- DASARKAN penjelasan pada 'Konteks' yang diberikan (judul berita, "
    "deskripsi, atau komentar penonton). Bila konteks ada, gunakan sebagai "
    "bukti utama alih-alih menebak.\n"
    "- Jangan mengarang fakta spesifik (angka pasti, nama orang) yang tidak "
    "ada dalam konteks; bila konteks minim, tetap wajar dan tidak mengklaim.\n"
    "- DILARANG memakai frasa: '100% terbukti', 'pasti berhasil', 'dijamin aman'.\n"
    "- Bila menyebut produk/harga, sertakan 'harga dapat berubah sewaktu-waktu'.\n"
    "- Jangan menyalin judul atau konteks mentah; rangkai jadi penjelasan.\n"
    "- Keluarkan HANYA teks ringkasan, tanpa awalan seperti 'Ringkasan:'."
)

# Petunjuk fokus per platform agar ringkasan terasa relevan.
_PLATFORM_HINT = {
    "google": (
        "Ini kata kunci yang lonjakan pencariannya tinggi. Jelaskan peristiwa "
        "atau berita di baliknya berdasarkan judul berita pada konteks."
    ),
    "youtube": (
        "Ini video yang sedang trending. Jelaskan daya tariknya; bila ada "
        "cuplikan komentar penonton, manfaatkan untuk menangkap reaksi mereka."
    ),
    "tiktok": (
        "Ini hashtag/konten yang viral di TikTok. Jelaskan jenis konten atau "
        "tantangan/tren di baliknya."
    ),
    "instagram": (
        "Ini unggahan/topik yang ramai di Instagram. Jelaskan kenapa menarik "
        "perhatian."
    ),
    "twitter": (
        "Ini topik yang jadi perbincangan di X (Twitter). Jelaskan pemicu "
        "perbincangannya."
    ),
    "shopee": (
        "Ini produk yang banyak dicari. Jelaskan kenapa diminati; ingatkan "
        "bahwa harga dapat berubah sewaktu-waktu."
    ),
}


def build_user_prompt(platform: str, title: str, context: str = "") -> str:
    hint = _PLATFORM_HINT.get(platform, "")
    hint_line = f"\nPetunjuk: {hint}" if hint else ""
    ctx = (
        f"\nKonteks (bukti nyata dari platform):\n{context.strip()}"
        if context and context.strip()
        else "\nKonteks: (tidak tersedia — jelaskan seperlunya tanpa mengarang)"
    )
    return (
        f"Platform: {platform}\n"
        f'Topik/judul yang sedang tren: "{title}"{hint_line}{ctx}\n\n'
        "Jelaskan dalam maksimal 3 kalimat kenapa ini sedang tren di Indonesia."
    )
