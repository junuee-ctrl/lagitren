"""Prompt Bahasa Indonesia untuk ringkasan 'kenapa lagi tren'."""
from __future__ import annotations

SYSTEM_PROMPT = (
    "Anda editor tren berbahasa Indonesia untuk situs Lagi Tren. "
    "Jelaskan SECARA SINGKAT kenapa sebuah topik sedang tren/populer DI INDONESIA.\n"
    "ATURAN WAJIB:\n"
    "- Bahasa Indonesia natural, santai. Maksimal 3 kalimat, fokus 'kenapa ramai'.\n"
    "- Data ini mencerminkan apa yang sedang populer/dicari DI INDONESIA. "
    "Untuk KATA KUNCI/BERITA/TOPIK (Google, X): tafsirkan sebagai peristiwa di "
    "Indonesia; JANGAN mengaitkan dengan peristiwa luar negeri (mis. Amerika) "
    "kecuali Konteks menyebutnya.\n"
    "- Untuk FILM/SERIAL/LAGU/PRODUK: kontennya BISA berasal dari negara mana pun "
    "(Korea, Thailand, AS, Jepang, dll). JANGAN berasumsi buatan Indonesia atau "
    "menyebutnya 'budaya lokal'. Sebutkan asal/genre SESUAI FAKTA di Konteks; "
    "cukup katakan ini sedang POPULER DI INDONESIA.\n"
    "- JANGAN MENGARANG. Jangan menyebut peristiwa, nama, tempat, atau angka "
    "spesifik yang TIDAK ADA di Konteks. Bila Konteks kosong/tipis, beri "
    "penjelasan UMUM dan jujur tanpa menyebut kejadian tertentu. Lebih baik umum "
    "daripada salah.\n"
    "- Untuk VIDEO/FOTO (TikTok, Instagram, YouTube): Anda TIDAK menonton video "
    "atau melihat foto. JANGAN mendeskripsikan adegan/visual yang tidak tertulis. "
    "Ringkas HANYA dari caption, nama hashtag, dan angka interaksi.\n"
    "- Hindari basa-basi kosong seperti 'produksi berkualitas', 'cerita menarik', "
    "'relatable' tanpa dasar. Gunakan isi SINOPSIS/Konteks yang nyata.\n"
    "- DILARANG frasa: '100% terbukti', 'pasti berhasil', 'dijamin aman'.\n"
    "- Bila menyebut produk/harga, tambahkan 'harga dapat berubah sewaktu-waktu'.\n"
    "- Jangan menyalin judul/konteks mentah; rangkai jadi penjelasan.\n"
    "- Keluarkan HANYA teks ringkasan, tanpa awalan seperti 'Ringkasan:'."
)

# Petunjuk fokus per platform agar ringkasan terasa relevan.
_PLATFORM_HINT = {
    "google": (
        "Ini kata kunci dengan lonjakan pencarian tinggi DI INDONESIA. Jelaskan "
        "kemungkinan pemicunya HANYA berdasarkan judul berita di Konteks. Bila "
        "tidak ada berita di Konteks, katakan kata kunci ini sedang naik dan "
        "pemicunya belum pasti — JANGAN menebak peristiwa spesifik (apalagi luar "
        "negeri)."
    ),
    "youtube": (
        "Ini video yang sedang trending di Indonesia. Jelaskan daya tariknya dari "
        "deskripsi/komentar di Konteks. Jangan mendeskripsikan isi video yang "
        "tidak ada di Konteks."
    ),
    "tiktok": (
        "Ini HASHTAG yang viral di TikTok Indonesia (bukan satu video tertentu). "
        "Simpulkan topiknya dari NAMA hashtag bila jelas (mis. nama pertandingan, "
        "acara, atau tokoh). Sebutkan ramai berdasarkan jumlah video/penayangan. "
        "JANGAN mengarang isi/adegan video."
    ),
    "instagram": (
        "Ini unggahan yang ramai di Instagram. Ringkas HANYA dari caption dan "
        "hashtag. JANGAN mendeskripsikan isi foto/video yang tidak disebut di "
        "caption."
    ),
    "twitter": (
        "Ini topik yang jadi perbincangan di X (Twitter) Indonesia. Jelaskan "
        "pemicunya dari Konteks; bila tidak ada, sebut sedang ramai tanpa menebak."
    ),
    "shopee": (
        "Ini produk yang banyak dicari di Indonesia. Jelaskan kenapa diminati dari "
        "nama/kategori; ingatkan bahwa harga dapat berubah sewaktu-waktu."
    ),
    "netflix": (
        "Ini film/serial yang masuk Top 10 Netflix INDONESIA (populer DI "
        "Indonesia, tapi filmnya bisa dari negara mana pun). Berdasarkan SINOPSIS "
        "dan ASAL film di Konteks, sebutkan genre/premisnya secara ringkas dan "
        "asal negaranya bila diketahui (mis. 'film horor Thailand', 'drama "
        "Korea'). JANGAN berasumsi buatan Indonesia, jangan spoiler, jangan "
        "mengarang plot yang tidak ada di sinopsis."
    ),
}


def build_user_prompt(platform: str, title: str, context: str = "") -> str:
    hint = _PLATFORM_HINT.get(platform, "")
    hint_line = f"\nPetunjuk: {hint}" if hint else ""
    if context and context.strip():
        ctx = f"\nKonteks (bukti nyata dari platform):\n{context.strip()}"
    else:
        ctx = (
            "\nKonteks: (TIDAK tersedia). Jangan mengarang peristiwa/nama spesifik. "
            "Beri penjelasan umum dan jujur bahwa topik ini sedang populer di Indonesia."
        )
    return (
        f"Platform: {platform}\n"
        f'Topik/judul yang sedang tren/populer DI INDONESIA: "{title}"{hint_line}{ctx}\n\n'
        "Jelaskan dalam maksimal 3 kalimat, sesuai aturan (tanpa mengarang, tanpa "
        "menganggap konten luar negeri sebagai buatan Indonesia)."
    )
