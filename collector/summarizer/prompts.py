"""Prompt Bahasa Indonesia untuk ringkasan 'kenapa lagi tren'."""
from __future__ import annotations

SYSTEM_PROMPT = (
    "Anda editor tren berbahasa Indonesia untuk situs Lagi Tren. "
    "Jelaskan SECARA SINGKAT kenapa sebuah topik sedang tren DI INDONESIA.\n"
    "ATURAN WAJIB:\n"
    "- Bahasa Indonesia natural, santai. Maksimal 3 kalimat, fokus 'kenapa ramai'.\n"
    "- SEMUA data ini dari INDONESIA (volume pencarian, tren, unggahan Indonesia). "
    "Tafsirkan dalam konteks Indonesia. JANGAN mengaitkan dengan peristiwa luar "
    "negeri (mis. Amerika Serikat) KECUALI Konteks secara eksplisit menyebutnya.\n"
    "- JANGAN MENGARANG. Jangan menyebut peristiwa, nama orang, tempat, atau angka "
    "spesifik yang TIDAK ADA di Konteks. Bila Konteks kosong atau tipis, beri "
    "penjelasan UMUM dan jujur (mis. 'lonjakan pencarian biasanya dipicu berita "
    "atau rilis terbaru') TANPA menyebut kejadian tertentu. Lebih baik umum "
    "daripada salah.\n"
    "- Untuk VIDEO/FOTO (TikTok, Instagram, YouTube): Anda TIDAK menonton video "
    "atau melihat foto. JANGAN mendeskripsikan adegan, visual, atau isi yang tidak "
    "tertulis. Ringkas HANYA dari caption, nama hashtag, dan angka interaksi. "
    "Topik boleh disimpulkan dari nama hashtag/caption bila jelas.\n"
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
        "pemicunya belum pasti — JANGAN menebak peristiwa spesifik (apalagi "
        "kejadian luar negeri)."
    ),
    "youtube": (
        "Ini video yang sedang trending di Indonesia. Jelaskan daya tariknya dari "
        "deskripsi/komentar di Konteks. Jangan mendeskripsikan isi video yang "
        "tidak ada di Konteks."
    ),
    "tiktok": (
        "Ini HASHTAG yang viral di TikTok Indonesia (bukan satu video tertentu). "
        "Simpulkan topiknya dari NAMA hashtag bila jelas (mis. nama pertandingan, "
        "acara, atau tokoh). Sebutkan bahwa hashtag ini ramai berdasarkan jumlah "
        "video/penayangan. JANGAN mengarang isi/adegan video."
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
        "Ini film/serial di Top 10 Netflix Indonesia. Berdasarkan sinopsis di "
        "Konteks, jelaskan kira-kira kenapa banyak ditonton (genre, premis, daya "
        "tarik). Jangan spoiler dan jangan mengarang plot yang tidak ada."
    ),
}


def build_user_prompt(platform: str, title: str, context: str = "") -> str:
    hint = _PLATFORM_HINT.get(platform, "")
    hint_line = f"\nPetunjuk: {hint}" if hint else ""
    if context and context.strip():
        ctx = f"\nKonteks (bukti nyata dari platform, dari Indonesia):\n{context.strip()}"
    else:
        ctx = (
            "\nKonteks: (TIDAK tersedia). Jangan mengarang peristiwa/nama spesifik. "
            "Beri penjelasan umum dan jujur bahwa topik ini sedang naik di Indonesia."
        )
    return (
        f"Platform: {platform}\n"
        f'Topik/judul yang sedang tren DI INDONESIA: "{title}"{hint_line}{ctx}\n\n'
        "Jelaskan dalam maksimal 3 kalimat kenapa ini sedang tren di Indonesia, "
        "sesuai aturan (tanpa mengarang, tanpa mendeskripsikan visual yang tak terlihat)."
    )
