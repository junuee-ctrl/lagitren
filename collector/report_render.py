"""Render Laporan Intelijen Tren (HTML → PDF) dari content/intel/latest.json.

Semua grafik digambar dari riwayat peringkat nyata di arsip. Naskah naratif
disusun redaksi; struktur tiap temuan WAJIB: Fakta → Interpretasi → Rekomendasi,
supaya pembaca (dan klien mereka) bisa memisahkan data dari penilaian.

Pemakaian:
  python report_render.py > ../laporan.html                 # edisi terkunci
  python report_render.py ../content/intel/latest.json > x  # data terbaru
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Naskah naratif (FINDINGS / AGENCY / ALERT) ditulis untuk satu edisi tertentu,
# jadi berkas datanya ikut dikunci. Lewatkan path lain sbg argumen untuk edisi baru.
_SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "content/intel/edisi-2026-09-14.json"
INTEL = json.loads(_SRC.read_text(encoding="utf-8"))

BRAND, GRAPE, ACCENT, AMBER = "#E6007A", "#8B3DD6", "#00C9B1", "#F59E0B"
INK, MUTED, LINE = "#14121A", "#6B6878", "#E6E4EC"

PLAT = {
    "google": "Google", "youtube": "YouTube", "tiktok": "TikTok",
    "instagram": "Instagram", "twitter": "X", "netflix": "Netflix",
    "shopee": "TikTok Shop",
}
STAGE_ID = {"naik": "Naik", "puncak": "Puncak", "turun": "Turun",
            "stabil": "Stabil", "baru": "Baru"}


def spark(daily, w=132, h=30, color=BRAND):
    """Sparkline peringkat. Sumbu y dibalik: peringkat #1 di ATAS."""
    ranks = [d["best_rank"] for d in daily] or [1]
    if len(ranks) == 1:
        ranks = ranks * 2
    mn, mx = min(ranks), max(ranks)
    span = max(1, mx - mn)
    n = len(ranks)
    pts = []
    for i, r in enumerate(ranks):
        x = 16 + i * (w - 34) / (n - 1)
        y = 7 + (r - mn) / span * (h - 16)
        pts.append((round(x, 1), round(y, 1)))
    poly = " ".join(f"{x},{y}" for x, y in pts)
    x0, y0 = pts[0]
    x1, y1 = pts[-1]
    return (
        f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" aria-label="riwayat peringkat">'
        f'<polyline points="{poly}" fill="none" stroke="{color}" '
        f'stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>'
        f'<circle cx="{x0}" cy="{y0}" r="2.6" fill="#fff" stroke="{color}" stroke-width="1.6"/>'
        f'<circle cx="{x1}" cy="{y1}" r="4" fill="{color}" stroke="#fff" stroke-width="1.6"/>'
        f'<text x="{x0-4}" y="{y0+3.5}" text-anchor="end" font-size="8" fill="{MUTED}">#{ranks[0]}</text>'
        f'<text x="{x1+6}" y="{y1+3.5}" font-size="8.5" font-weight="700" fill="{INK}">#{ranks[-1]}</text>'
        f"</svg>"
    )


def lifecycle(t, w=228, h=96):
    """Kurva daur hidup satu tren, dengan label hari."""
    daily = t["daily"]
    ranks = [d["best_rank"] for d in daily]
    if len(ranks) == 1:
        ranks = ranks * 2
        daily = daily * 2
    mn, mx = min(ranks), max(ranks)
    span = max(1, mx - mn)
    n = len(ranks)
    pad_l, pad_r, pad_t, pad_b = 26, 14, 14, 20
    pts = []
    for i, r in enumerate(ranks):
        x = pad_l + i * (w - pad_l - pad_r) / max(1, n - 1)
        y = pad_t + (r - mn) / span * (h - pad_t - pad_b)
        pts.append((round(x, 1), round(y, 1)))
    poly = " ".join(f"{x},{y}" for x, y in pts)
    area = f"{pts[0][0]},{h-pad_b} " + poly + f" {pts[-1][0]},{h-pad_b}"
    best_i = ranks.index(mn)
    dots = "".join(
        f'<circle cx="{x}" cy="{y}" r="{4 if i==best_i else 2.4}" '
        f'fill="{BRAND if i==best_i else "#fff"}" stroke="{BRAND}" stroke-width="1.6"/>'
        for i, (x, y) in enumerate(pts)
    )
    days = "".join(
        f'<text x="{pts[i][0]}" y="{h-6}" text-anchor="middle" font-size="7" '
        f'fill="{MUTED}">{daily[i]["day"][-2:]}</text>'
        for i in range(n) if n <= 8 or i % 2 == 0
    )
    return (
        f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
        f'<line x1="{pad_l-6}" y1="{pad_t}" x2="{w-pad_r}" y2="{pad_t}" stroke="{LINE}" stroke-width="1"/>'
        f'<line x1="{pad_l-6}" y1="{h-pad_b}" x2="{w-pad_r}" y2="{h-pad_b}" stroke="{LINE}" stroke-width="1"/>'
        f'<text x="{pad_l-9}" y="{pad_t+3}" text-anchor="end" font-size="7.5" fill="{MUTED}">#{mn}</text>'
        + (f'<text x="{pad_l-9}" y="{h-pad_b+3}" text-anchor="end" font-size="7.5" '
           f'fill="{MUTED}">#{mx}</text>' if mx != mn else "")
        + f'<polygon points="{area}" fill="{BRAND}" opacity="0.07"/>'
        f'<polyline points="{poly}" fill="none" stroke="{BRAND}" stroke-width="2" '
        f'stroke-linejoin="round" stroke-linecap="round"/>{dots}{days}</svg>'
    )


def score_bar(parts, w=150, h=13):
    """Bar bertumpuk 4 komponen skor, dengan jarak 2px antar-segmen."""
    order = [("velocity", BRAND, 35), ("cross_platform", GRAPE, 25),
             ("persistence", ACCENT, 25), ("peak", AMBER, 15)]
    total_max = 100
    x = 0
    segs = []
    for key, col, _mx in order:
        v = parts.get(key, 0)
        if v <= 0:
            continue
        sw = v / total_max * w
        segs.append(f'<rect x="{round(x,1)}" y="0" width="{max(0,round(sw-2,1))}" '
                    f'height="{h}" rx="3" fill="{col}"/>')
        x += sw
    return (f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'<rect x="0" y="0" width="{w}" height="{h}" rx="3" fill="#F2F1F6"/>'
            + "".join(segs) + "</svg>")


def cat_bar(n, nmax, w=118, h=11):
    sw = max(3, n / max(1, nmax) * w)
    return (f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'<rect x="0" y="0" width="{w}" height="{h}" rx="3" fill="#F2F1F6"/>'
            f'<rect x="0" y="0" width="{round(sw,1)}" height="{h}" rx="3" fill="{GRAPE}"/></svg>')


def pick(title_part: str):
    for t in INTEL["radar"]:
        if title_part.lower() in t["title"].lower():
            return t
    return None


# ── naskah edisi (disusun redaksi; struktur Fakta → Interpretasi → Rekomendasi)
FINDINGS = [
    dict(
        tag="WATCH", t="Papan tren Google pekan ini didominasi jadwal sepak bola",
        f="130 dari tren yang kami rekam pekan ini masuk kategori sepak bola — "
          "122 di antaranya muncul di Google, 8 di YouTube.",
        i="Pada jendela ini papan Google berfungsi sebagian besar sebagai papan "
          "jadwal pertandingan. Lonjakannya terikat jam tayang, bukan minat pada "
          "kategori produk.",
        r="Jangan membaca “tren Google Indonesia” mentah-mentah sebagai sinyal "
          "minat konsumen. Saring kategori olahraga lebih dulu sebelum memakai "
          "daftar ini untuk perencanaan kata kunci.",
    ),
    dict(
        tag="DO", t="Netflix berganti takhta tanpa melepas juara lama",
        f="Di daftar Top 10 mingguan Netflix Indonesia yang berlaku, “Dilan ITB 1997” "
          "di #1; “Ghost in the Cell”, juara minggu sebelumnya, turun ke #2.",
        i="Juara lama tidak keluar dari papan atas — keduanya menyerap perhatian pada "
          "minggu yang sama. Daftar ini berlaku seminggu penuh, bukan diukur harian.",
        r="Jendela menumpang percakapan film masih terbuka untuk KEDUA judul, bukan "
          "hanya yang di puncak. Untuk brand hiburan/FMCG, ini pekan dengan dua "
          "kaitan sekaligus.",
    ),
    dict(
        tag="DO", t="Lagu lama melompat ke puncak dalam satu hari",
        f="R. City “Locked Away” (rilis 2015) bergerak dari #10 ke #1 dalam satu "
          "hari; komponen velocity-nya penuh (35 dari 35).",
        i="Di arsip kami, lompatan sebesar ini dalam kurang dari 24 jam lebih sering "
          "muncul pada audio yang dipakai ulang daripada pada rilisan baru.",
        r="Untuk konten bersuara, periksa katalog lama sebelum melisensikan rilisan "
          "baru — biaya lisensinya umumnya lebih rendah dengan daya tarik setara.",
    ),
    dict(
        tag="DON'T", t="“Bertahan N hari” tidak bisa dibandingkan antar platform",
        f="Tren Google paling tahan di jendela ini hanya 3 hari (“olahraga”, #9 → #2); "
          "tiap judul Netflix tampil di semua potret harian. Google menyegarkan data "
          "±10 menit; Netflix terbit mingguan.",
        i="Tiga hari di Google sudah luar biasa; tujuh hari di Netflix adalah nilai minimum.",
        r="Bandingkan ketahanan hanya di dalam satu platform, dan sesuaikan jendela aksi: "
          "jam untuk Google, minggu untuk Netflix.",
    ),
    dict(
        tag="WATCH", t="Tidak ada sinyal lintas platform yang lolos ambang bukti",
        f="Kriteria kami (minimal dua token distingtif yang sama, muncul di minimal "
          "dua platform) tidak meloloskan satu pun klaster pekan ini.",
        i="Ini bukan berarti tidak ada topik yang menyeberang platform — melainkan "
          "tidak ada yang memenuhi ambang bukti kami. Kami memilih melaporkan "
          "ketiadaan daripada menautkan topik yang kebetulan berbagi satu kata.",
        r="Perlakukan sebagai netral, bukan negatif. Bila Anda memantau satu topik "
          "spesifik, kirimkan kata kuncinya dan kami pantau langsung di edisi berikut.",
    ),
]

AGENCY = {
    "know": [
        ("Dominasi sepak bola di papan Google", "122 tren · kategori terbesar pekan ini"),
        ("Dilan ITB 1997 memuncaki Netflix", "#1 di daftar mingguan yang berlaku"),
        ("Ghost in the Cell turun ke #2", "juara minggu lalu, turun satu tingkat"),
        ("Lagu katalog lama naik cepat di YouTube", "#10 → #1 dalam satu hari"),
        ("Durasi tren beda satuan per platform", "Google ±10 menit · Netflix mingguan"),
    ],
    "safe": [
        ("Dua judul Netflix teratas", "keduanya masih di papan atas — kaitan ganda"),
        ("Audio katalog lama", "biaya lisensi umumnya lebih rendah"),
        ("Penempatan media di jam pertandingan", "perhatian terkumpul — bukan untuk materi skor"),
    ],
    "saturated": [
        ("Konten jadwal/skor sepak bola", "papan Google sudah penuh; sulit menonjol"),
        ("Menumpang kata kunci bencana", "umurnya < 1 hari; sudah lewat saat materi siap"),
    ],
    "watch": [
        ("Daftar mingguan Netflix berikutnya", "terbit sekali seminggu — satu-satunya titik perubahan"),
    ],
}

ALERT = dict(
    topic="Sepak bola menguasai papan pencarian",
    why="122 dari 130 tren kategori sepak bola pekan ini muncul di Google",
    platforms="Google (122) · YouTube (8)",
    momentum="Tinggi, terikat jadwal pertandingan",
    window="Berulang tiap akhir pekan pertandingan",
    fit="Otomotif · FMCG · Telekomunikasi · Keuangan",
    do="Siapkan konten & bidding di sekitar jam tayang pertandingan besar.",
    dont="Jangan memakai daftar tren Google mentah sebagai proksi minat produk.",
    watch="Apakah dominasi ini menurun di pekan tanpa laga besar.",
)

ALERT2 = dict(
    topic="Lagu katalog lama melompat ke puncak YouTube dalam sehari",
    why="R. City \u201cLocked Away\u201d (rilis 2015) naik dari #10 ke #1 dalam kurang dari 24 jam",
    platforms="YouTube",
    momentum="Sangat tinggi \u2014 komponen kecepatan penuh (35 dari 35)",
    window="Pendek: papan YouTube kami ambil tiap jam dan bergerak setiap hari",
    fit="Minuman \u00b7 FMCG \u00b7 Fesyen \u2014 untuk konten pendek bersuara",
    do="Periksa hak pakai audio katalog lama sebelum melisensikan rilisan baru.",
    dont="Jangan anggap populer di papan berarti bebas dipakai \u2014 lisensi tetap wajib.",
    watch="Apakah lagu lama lain ikut naik \u2014 itu menandai pola, bukan kebetulan.",
    evidence="R. City - Locked Away",
)


CSS = """
@page { size: A4; margin: 0; }
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: Carlito, "DejaVu Sans", sans-serif; color: #14121A; font-size: 10pt; line-height: 1.45; }
.page { width:210mm; height:297mm; padding:15mm 14mm 13mm; position:relative; page-break-after:always; overflow:hidden; }
.page:last-child { page-break-after:auto; }
.cover { background:linear-gradient(135deg,#E6007A 0%,#8B3DD6 52%,#00C9B1 100%); color:#fff; padding:24mm 17mm; }
.mark{position:relative;height:24mm}.mark .h{position:absolute;font-size:58pt;font-weight:800;transform:skewX(-9deg);line-height:1}
.mark .h.b{color:rgba(0,201,177,.95);top:3mm;left:0}.mark .h.f{color:#fff;top:2mm;left:2.4mm}
.wm{font-size:16pt;font-weight:800;margin-top:1mm}.wm span{opacity:.75;font-weight:600}
.kick{margin-top:14mm;font-size:9pt;letter-spacing:2.4px;text-transform:uppercase;opacity:.9;font-weight:800}
.cover h1{font-size:30pt;line-height:1.1;font-weight:800;margin-top:4mm;letter-spacing:-.5px}
.per{margin-top:6mm;font-size:13pt;font-weight:700}
.badge{display:inline-block;margin-top:5mm;background:#fff;color:#E6007A;font-weight:800;padding:2.2mm 5.5mm;border-radius:99px;font-size:9.5pt}
.cq{margin-top:9mm;font-size:11.5pt;line-height:1.5;max-width:140mm;opacity:.97}
.toc{margin-top:9mm;border-top:1px solid rgba(255,255,255,.35);padding-top:5mm;max-width:150mm}
.toc .l{font-size:8pt;letter-spacing:2px;text-transform:uppercase;opacity:.85;font-weight:800;margin-bottom:3mm}
.toc .r{display:flex;gap:5mm;font-size:10pt;padding:1.3mm 0;border-bottom:1px solid rgba(255,255,255,.18)}
.toc .r b{flex:0 0 8mm;opacity:.8}
.cover .ft{position:absolute;left:17mm;right:17mm;bottom:15mm;font-size:9pt;opacity:.92;border-top:1px solid rgba(255,255,255,.35);padding-top:3.5mm;display:flex;justify-content:space-between}
.ph{display:flex;align-items:baseline;gap:4mm;border-bottom:2.5px solid #E6007A;padding-bottom:2.5mm;margin-bottom:6mm}
.ph .n{font-size:8.5pt;font-weight:800;color:#E6007A;letter-spacing:1.6px}
.ph h2{font-size:18pt;font-weight:800;letter-spacing:-.3px}
h3{font-size:11.5pt;font-weight:800;margin:5mm 0 2mm}
p{margin-bottom:2.4mm}.small{font-size:8.8pt}.muted{color:#6B6878}
.stats{display:flex;gap:2.5mm;margin-bottom:5mm}
.stat{flex:1;background:#F7F6FA;border-radius:3mm;padding:3mm;border-left:3px solid #E6007A}
.stat .v{font-size:15pt;font-weight:800;line-height:1.1}.stat .l{font-size:8pt;color:#6B6878;margin-top:.5mm}
.fnd{border:1px solid #E6E4EC;border-radius:3mm;padding:3.5mm 4mm;margin-bottom:3.2mm}
.fnd .hd{display:flex;align-items:center;gap:3mm;margin-bottom:2mm}
.fnd .hd .t{font-weight:800;font-size:10.5pt;flex:1}
.tag{font-size:7.5pt;font-weight:800;padding:.8mm 2.5mm;border-radius:99px;color:#fff;letter-spacing:.5px}
.tag.DO{background:#00A38F}.tag.WATCH{background:#F59E0B}.tag[class*="DON"]{background:#E6007A}
.fir{display:grid;grid-template-columns:20mm 1fr;gap:1.5mm 3mm;font-size:8.8pt}
.fir .k{font-weight:800;color:#6B6878;font-size:7.5pt;letter-spacing:.8px;padding-top:.3mm}
table{width:100%;border-collapse:collapse;font-size:8.8pt}
th{text-align:left;background:#F7F6FA;padding:2mm 2.5mm;font-weight:800;font-size:7.8pt;text-transform:uppercase;letter-spacing:.5px;color:#6B6878;border-bottom:1px solid #E6E4EC}
td{padding:1.8mm 2.5mm;border-bottom:1px solid #E6E4EC;vertical-align:middle}
.sc{font-weight:800;font-size:11pt;color:#E6007A}
.stg{font-size:7.5pt;font-weight:800;padding:.6mm 2mm;border-radius:99px;background:#F2F1F6;color:#6B6878}
.lg{display:flex;gap:4mm;font-size:7.8pt;color:#6B6878;margin-top:2mm;flex-wrap:wrap}
.lg i{display:inline-block;width:2.6mm;height:2.6mm;border-radius:1mm;margin-right:1.2mm;vertical-align:-.3mm}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:4mm}
.card{border:1px solid #E6E4EC;border-radius:3mm;padding:3.5mm}
.card .ct{font-weight:800;font-size:9.5pt;margin-bottom:.5mm}
.card .cs{font-size:8pt;color:#6B6878;margin-bottom:2mm}
.box{border:1px solid #E6E4EC;border-radius:3mm;padding:4mm;margin-top:4mm}
.box.tip{background:#F2FCFA;border-color:#B8EDE5}
.box h4{font-size:10pt;font-weight:800;margin-bottom:2mm}
ul{margin:0 0 0 4.5mm}li{margin-bottom:1.4mm}
.pf{position:absolute;left:14mm;right:14mm;bottom:7mm;display:flex;justify-content:space-between;font-size:7.5pt;color:#6B6878;border-top:1px solid #E6E4EC;padding-top:2mm}
.agy{border-left:3px solid #E6007A;padding-left:3.5mm;margin-bottom:4mm}
.agy .h{font-weight:800;font-size:10pt;margin-bottom:1.5mm}
.agy .it{display:flex;justify-content:space-between;gap:4mm;font-size:8.8pt;padding:1.2mm 0;border-bottom:1px dotted #E6E4EC}
.agy .it span:last-child{color:#6B6878;font-size:8pt;text-align:right;flex:0 0 62mm}
.alert{border:2px solid #E6007A;border-radius:4mm;overflow:hidden}
.alert .top{background:#E6007A;color:#fff;padding:4mm 5mm;display:flex;justify-content:space-between;align-items:center}
.alert .top .lbl{font-size:8pt;font-weight:800;letter-spacing:2px}
.alert .top h3{font-size:15pt;font-weight:800;margin:1mm 0 0}
.alert .logo{border:1px dashed rgba(255,255,255,.7);border-radius:2mm;padding:2mm 4mm;font-size:7.5pt;opacity:.85;text-align:center}
.steps{display:grid;gap:2.5mm;margin-top:3mm}\n.st{display:flex;gap:3.5mm;align-items:flex-start;font-size:9pt;line-height:1.45}\n.st .no{flex:none;width:6.5mm;height:6.5mm;border-radius:50%;background:#E6007A;color:#fff;font-size:8.5pt;font-weight:800;display:flex;align-items:center;justify-content:center}\n.alert .bd{padding:5mm}
.alert .ev{display:flex;gap:5mm;align-items:center;margin-top:3.5mm;padding-top:3.5mm;border-top:1px solid #E6E4EC}
.alert .ev .k{width:28mm;flex:none;font-size:8pt;font-weight:700;color:#6B6878;text-transform:uppercase;letter-spacing:.4px}
.kv{display:grid;grid-template-columns:30mm 1fr;gap:2mm 4mm;font-size:9pt}
.kv .k{font-weight:800;color:#6B6878;font-size:8pt}
.act{display:grid;grid-template-columns:1fr 1fr 1fr;gap:3mm;margin-top:4mm}
.act div{border-radius:3mm;padding:3mm;font-size:8.3pt}
.act .d{background:#E9FAF7;border:1px solid #B8EDE5}.act .n{background:#FFF0F7;border:1px solid #F9C8DF}
.act .w{background:#FFF8EC;border:1px solid #FBE0B0}
.act b{display:block;font-size:8pt;letter-spacing:.8px;margin-bottom:1mm}
.tiers{display:flex;gap:2.5mm;margin-top:3mm}
.tier{flex:1;border:1px solid #E6E4EC;border-radius:3mm;padding:3.5mm}
.tier.hi{border:2px solid #E6007A;background:#FFF9FC}
.tier .nm{font-weight:800;font-size:10pt}
.tier .pr{font-size:12pt;font-weight:800;color:#E6007A;margin:1.5mm 0 1mm}
.tier .pr small{font-size:8pt;color:#6B6878;font-weight:600}
.tier ul{margin-left:3.5mm;font-size:8.2pt}.tier li{margin-bottom:1mm}
.cta{margin-top:5mm;background:linear-gradient(135deg,#E6007A,#8B3DD6);color:#fff;border-radius:3mm;padding:5mm}
.cta h4{font-size:12pt;font-weight:800;margin-bottom:1.5mm}
"""


def fnd_html(f):
    return f"""<div class="fnd">
  <div class="hd"><span class="t">{f['t']}</span><span class="tag {f['tag'].replace("'","")}">{f['tag']}</span></div>
  <div class="fir">
    <div class="k">FAKTA</div><div>{f['f']}</div>
    <div class="k">INTERPRETASI</div><div>{f['i']}</div>
    <div class="k">REKOMENDASI</div><div>{f['r']}</div>
  </div></div>"""


def radar_rows(n=11):
    out = []
    for t in INTEL["radar"][:n]:
        sp = t["score_parts"]
        out.append(
            f"<tr><td class='sc'>{t['score']}</td>"
            f"<td>{t['title'][:44]}</td>"
            f"<td class='muted small'>{PLAT.get(t['platform'], t['platform'])}</td>"
            f"<td>{spark(t['daily'])}</td>"
            f"<td><span class='stg'>{STAGE_ID.get(t['stage'], t['stage'])}</span></td>"
            f"<td>{score_bar(sp)}</td></tr>")
    return "".join(out)


# Kurva daur hidup hanya bermakna bila sumbernya berubah lebih sering daripada
# kami memotretnya. Netflix terbit mingguan dan daftar produk edisi ini
# diperbarui manual — garis datarnya adalah jejak jadwal sumber, bukan perilaku
# pasar, jadi keduanya dikecualikan dari kartu kurva.
CADENCE_ARTIFACT = {"netflix", "shopee"}


def by_stage(stage):
    for t in INTEL["radar"]:
        if t["platform"] in CADENCE_ARTIFACT:
            continue
        if t["stage"] == stage and len(t["daily"]) >= 2:
            return t
    return None


def find_radar(fragment):
    for t in INTEL["radar"]:
        if fragment.lower() in t["title"].lower():
            return t
    return None


def alert_card(a, logo=True):
    ev = find_radar(a["evidence"]) if a.get("evidence") else None
    chart = ""
    if ev:
        chart = (f"<div class='ev'><div class='k'>Bukti peringkat</div>"
                 f"<div>{lifecycle(ev, w=250, h=64)}"
                 f"<div class='small muted' style='margin-top:1mm'>{ev['title'][:44]} · "
                 f"7 hari terakhir</div></div></div>")
    logo_html = ("<div class='logo'>logo agensi<br>(paket Agency)</div>" if logo else "")
    return f"""<div class="alert">
    <div class="top">
      <div><div class="lbl">TREND ALERT</div><h3>{a['topic']}</h3></div>
      {logo_html}
    </div>
    <div class="bd">
      <div class="kv">
        <div class="k">Kenapa sekarang</div><div>{a['why']}</div>
        <div class="k">Platform</div><div>{a['platforms']}</div>
        <div class="k">Momentum</div><div>{a['momentum']}</div>
        <div class="k">Jendela waktu</div><div>{a['window']}</div>
        <div class="k">Kategori brand</div><div>{a['fit']}</div>
      </div>
      {chart}
      <div class="act">
        <div class="d"><b>DO</b>{a['do']}</div>
        <div class="n"><b>DON'T</b>{a['dont']}</div>
        <div class="w"><b>WATCH</b>{a['watch']}</div>
      </div>
    </div>
  </div>"""


def lifecycle_cards():
    want = [("puncak", "Naik lalu memuncak"), ("stabil", "Bertahan di posisi sama"),
            ("naik", "Sedang menanjak"), ("turun", "Mulai menurun")]
    cards = []
    for stage, label in want:
        t = by_stage(stage)
        if not t:
            continue
        cards.append(
            f"<div class='card'><div class='ct'>{label}</div>"
            f"<div class='cs'>{t['title'][:40]} · {PLAT.get(t['platform'],t['platform'])} · skor {t['score']}</div>"
            f"{lifecycle(t)}</div>")
    return "".join(cards)


NUM_ID = {1: "Satu", 2: "Dua", 3: "Tiga", 4: "Empat"}


def lifecycle_title():
    n = sum(1 for st in ("puncak", "stabil", "naik", "turun") if by_stage(st))
    return f"{NUM_ID.get(n, n)} bentuk kurva yang muncul pekan ini"


def category_rows():
    cats = INTEL.get("categories", [])[:8]
    nmax = max((c["n_trends"] for c in cats), default=1)
    out = []
    for c in cats:
        plats = " · ".join(f"{PLAT.get(k,k)} {v}" for k, v in list(c["platforms"].items())[:3])
        out.append(f"<tr><td><b>{c['label']}</b></td><td>{cat_bar(c['n_trends'], nmax)}</td>"
                   f"<td class='sc' style='font-size:10pt'>{c['n_trends']}</td>"
                   f"<td class='muted small'>{plats}</td></tr>")
    return "".join(out)


def agy_block(title, items, color="#E6007A"):
    rows = "".join(f"<div class='it'><span>{a}</span><span>{b}</span></div>" for a, b in items)
    return f"<div class='agy' style='border-color:{color}'><div class='h'>{title}</div>{rows}</div>"


def build() -> str:
    cov = INTEL
    n_total = cov["total_trends"]
    win = cov["window_days"]
    a = ALERT
    return f"""<!doctype html><html lang="id"><head><meta charset="utf-8">
<title>Indonesia Weekly Trend Intelligence</title><style>{CSS}</style></head><body>

<section class="page cover">
  <div class="mark"><div class="h b">#</div><div class="h f">#</div></div>
  <div class="wm">lagi tren<span>.id</span> · intelligence</div>
  <div class="kick">Indonesia Weekly Trend Intelligence</div>
  <h1>Apa yang naik,<br>berapa lama bertahan,<br>dan apa yang harus dilakukan.</h1>
  <div class="per">Edisi 8 – 14 September 2026</div>
  <div class="badge">CONTOH GRATIS</div>
  <p class="cq">Platform hanya menampilkan daftar hari ini. Kami merekam peringkatnya
  setiap pengumpulan, lalu menghitung kecepatan, ketahanan, dan puncak tiap topik —
  sehingga setiap temuan datang dengan angka, bukan kesan.</p>
  <div class="toc"><div class="l">Isi edisi ini</div>
    <div class="r"><b>01</b><span>Ringkasan eksekutif — Fakta / Interpretasi / Rekomendasi</span></div>
    <div class="r"><b>02</b><span>Trend Radar — skor & riwayat peringkat</span></div>
    <div class="r"><b>03</b><span>Kurva daur hidup & bobot kategori</span></div>
    <div class="r"><b>04</b><span>Untuk agensi — apa yang aman diaktifkan pekan ini</span></div>
    <div class="r"><b>05</b><span>Trend Alert — halaman siap kirim ke klien</span></div>
    <div class="r"><b>06</b><span>Metodologi, batasan & paket</span></div>
  </div>
  <div class="ft"><div>Tim Redaksi Lagitren · lagitren.id</div><div>{n_total} tren terukur · 7 platform</div></div>
</section>

<section class="page">
  <div class="ph"><span class="n">01</span><h2>Ringkasan Eksekutif</h2></div>
  <div class="stats">
    <div class="stat"><div class="v">{n_total}</div><div class="l">tren terukur ({win} hari)</div></div>
    <div class="stat"><div class="v">7</div><div class="l">platform dipantau</div></div>
    <div class="stat"><div class="v">5</div><div class="l">temuan pekan ini</div></div>
    <div class="stat"><div class="v">0</div><div class="l">klaster lintas platform lolos ambang</div></div>
  </div>
  {"".join(fnd_html(f) for f in FINDINGS)}
  <div class="pf"><div>Indonesia Weekly Trend Intelligence · Edisi contoh</div><div>lagitren.id · 1</div></div>
</section>

<section class="page">
  <div class="ph"><span class="n">02</span><h2>Trend Radar</h2></div>
  <p class="small muted">Skor 0–100 dihitung dari empat komponen terukur. Kolom riwayat
  menunjukkan pergerakan peringkat harian di jendela {win} hari — angka kecil berarti posisi lebih baik.</p>
  <table style="margin-top:4mm">
    <tr><th>Skor</th><th>Topik</th><th>Platform</th><th>Riwayat peringkat</th><th>Tahap</th><th>Komponen</th></tr>
    {radar_rows()}
  </table>
  <div class="lg">
    <span><i style="background:{BRAND}"></i>Velocity (0–35)</span>
    <span><i style="background:{GRAPE}"></i>Lintas platform (0–25)</span>
    <span><i style="background:{ACCENT}"></i>Ketahanan (0–25)</span>
    <span><i style="background:{AMBER}"></i>Puncak (0–15)</span>
  </div>
  <div class="box tip"><h4>Cara membaca skor</h4>
  <p class="small" style="margin:0"><b>Velocity</b> mengukur perbaikan peringkat di jendela ini —
  skor tinggi berarti topik sedang bergerak cepat, bukan sekadar besar. <b>Ketahanan</b> menghitung
  jumlah hari berbeda topik itu muncul. <b>Puncak</b> mencatat posisi terbaik yang pernah dicapai.
  <b>Lintas platform</b> hanya terisi bila topik yang sama terdeteksi di lebih dari satu platform
  menurut ambang bukti kami — pekan ini kosong untuk semua baris, dan kami membiarkannya nol
  alih-alih melonggarkan ambang.</p>
  <p class="small" style="margin:2mm 0 0"><b>Penting:</b> ketahanan hanya sebanding di dalam
  satu platform. Netflix menerbitkan daftar per minggu, dan daftar produk TikTok Shop pada edisi
  ini diperbarui manual — sehingga skor ketahanan keduanya penuh karena jadwal sumbernya, bukan
  karena perhatian pasar yang bertahan. Baca tabel ini per platform, bukan lintas platform.</p></div>
  <div class="pf"><div>Indonesia Weekly Trend Intelligence · Edisi contoh</div><div>lagitren.id · 2</div></div>
</section>

<section class="page">
  <div class="ph"><span class="n">03</span><h2>Daur Hidup &amp; Kategori</h2></div>
  <h3>{lifecycle_title()}</h3>
  <p class="small muted">Titik penuh menandai peringkat terbaik. Sumbu kiri menunjukkan rentang
  peringkat topik tersebut; angka bawah adalah tanggal.</p>
  <div class="grid2" style="margin-top:3mm">{lifecycle_cards()}</div>
  <h3>Bobot kategori pekan ini</h3>
  <table><tr><th>Kategori</th><th>Proporsi</th><th>Tren</th><th>Sebaran platform</th></tr>{category_rows()}</table>
  <p class="small muted" style="margin-top:2.5mm">Kategori ditentukan kamus kata kunci yang kami kelola
  dan dapat diaudit. Kategori <b>bukan</b> sinyal lintas platform: ia menunjukkan bobot tema, bukan
  satu topik yang menyeberang.</p>
  <div class="pf"><div>Indonesia Weekly Trend Intelligence · Edisi contoh</div><div>lagitren.id · 3</div></div>
</section>

<section class="page">
  <div class="ph"><span class="n">04</span><h2>Untuk Agensi</h2></div>
  <p class="small muted">Disusun untuk dibaca lima menit sebelum rapat klien.</p>
  <div style="margin-top:4mm">
  {agy_block("5 tren yang perlu diketahui klien Anda", AGENCY["know"], "#E6007A")}
  {agy_block("3 tren yang aman diaktifkan pekan ini", AGENCY["safe"], "#00A38F")}
  {agy_block("2 tren yang sudah jenuh", AGENCY["saturated"], "#F59E0B")}
  {agy_block("1 tren yang layak dipantau pekan depan", AGENCY["watch"], "#8B3DD6")}
  </div>
  <div class="box"><h4>Catatan pemisahan</h4>
  <p class="small" style="margin:0">Daftar “aman / jenuh / dipantau” adalah <b>penilaian redaksi</b>
  berdasarkan angka di halaman 2–3, bukan hasil perhitungan otomatis. Angka pendukungnya tercantum
  di kolom kanan tiap baris supaya Anda bisa menilai ulang sendiri.</p></div>

  <h3 style="margin-top:6mm">Cara memakai halaman ini di rapat klien</h3>
  <div class="steps">
    <div class="st"><div class="no">1</div><div><b>Buka dengan angka, bukan opini.</b>
    Sebut satu fakta dari halaman 2 (mis. “130 dari tren pekan ini sepak bola”) sebelum
    masuk ke rekomendasi — klien menilai sumbernya dulu.</div></div>
    <div class="st"><div class="no">2</div><div><b>Pilih satu baris “aman”, tolak satu baris “jenuh”.</b>
    Menolak satu ide secara eksplisit membuat rekomendasi terdengar sebagai seleksi,
    bukan daftar keinginan.</div></div>
    <div class="st"><div class="no">3</div><div><b>Kirim halaman 5 apa adanya.</b>
    Halaman Trend Alert dirancang berdiri sendiri; pelanggan Agency menggantinya
    dengan logo dan warna sendiri sebelum diteruskan.</div></div>
  </div>
  <div class="pf"><div>Indonesia Weekly Trend Intelligence · Edisi contoh</div><div>lagitren.id · 4</div></div>
</section>

<section class="page">
  <div class="ph"><span class="n">05</span><h2>Trend Alert — siap kirim ke klien</h2></div>
  <p class="small muted">Halaman ini dirancang untuk dicetak atau diteruskan apa adanya.
  Pelanggan paket Agency dapat mengganti logo dan warna dengan identitas agensinya.</p>
  <div style="margin-top:4mm">{alert_card(ALERT)}</div>
  <div style="margin-top:5mm">{alert_card(ALERT2, logo=False)}</div>
  <p class="small muted" style="margin-top:3.5mm">Sumber angka: arsip peringkat Lagi Tren,
  jendela {win} hari hingga 14 September 2026. “Kategori brand” adalah saran redaksi, bukan hasil
  pengukuran audiens — kami tidak mengumpulkan data demografi.</p>
  <div class="pf"><div>Indonesia Weekly Trend Intelligence · Edisi contoh</div><div>lagitren.id · 5</div></div>
</section>

<section class="page">
  <div class="ph"><span class="n">06</span><h2>Metodologi &amp; Paket</h2></div>
  <h3>Bagaimana angka ini dibuat</h3>
  <p class="small">Empat tahap, setiap pekan sama: <b>pengumpulan</b> terjadwal dari sumber publik
  resmi tiap platform (Google Trends ±10 menit, YouTube Data API ±1 jam, TikTok Creative Center ±3 jam,
  tagar Instagram terpilih ±3 jam, daftar tren X ±3 jam, Top 10 Netflix harian, kurasi produk TikTok
  Shop harian) → <b>normalisasi</b> menjadi potret peringkat bertanda waktu → <b>penskoran</b> otomatis
  (velocity, lintas platform, ketahanan, puncak) → <b>pemeriksaan redaksi</b> atas interpretasi dan
  rekomendasi sebelum terbit. Seluruh angka dihasilkan pipeline dari basis data kami; tim redaksi
  bertanggung jawab atas bagian interpretasi dan rekomendasi, yang dibantu perangkat AI dalam
  penyusunan draf.</p>
  <div class="box"><h4>Yang tidak kami klaim</h4>
  <p class="small" style="margin:0">Kami <b>tidak</b> mengumpulkan data demografi audiens maupun
  analisis format kreatif, jadi laporan ini tidak memuat angka usia, gender, atau pola kreatif.
  Data kami adalah potret berkala, bukan siaran langsung — pergerakan di antara dua pengambilan
  bisa terlewat. Daftar Instagram bergantung pada tagar yang kami pantau. Arsip berjalan sejak
  19 Agustus 2026; analisis pola jangka panjang akan tersedia seiring arsip memanjang.</p></div>

  <h3>Berapa waktu yang dihemat</h3>
  <p class="small">Mengumpulkan tujuh papan tren secara manual, mencatat peringkatnya, dan
  merapikannya menjadi materi rapat memakan waktu beberapa jam kerja strategist setiap pekan —
  dan hasilnya tetap tanpa riwayat, karena platform tidak menyimpannya. Paket Pro menggantikan
  pekerjaan itu dengan satu berkas yang sudah berisi angka, grafik, dan rekomendasi.</p>

  <h3>Paket berlangganan</h3>
  <div class="tiers">
    <div class="tier"><div class="nm">Gratis</div><div class="pr">Rp0</div>
      <ul><li>Ringkasan mingguan via email</li><li>3 temuan utama</li><li>Tanpa akses arsip</li></ul></div>
    <div class="tier hi"><div class="nm">Pro</div><div class="pr">Rp299.000<small> /bulan</small></div>
      <ul><li>Laporan lengkap tiap pekan</li><li>Trend Radar + kurva daur hidup</li>
      <li>Akses arsip peringkat 7 platform</li><li>1 permintaan kata kunci / bulan</li>
      <li>Tahunan Rp2.990.000 (hemat 2 bulan)</li></ul></div>
    <div class="tier"><div class="nm">Agency</div><div class="pr">Rp1.490.000<small> /bulan</small></div>
      <ul><li><b>White-label:</b> logo &amp; warna agensi</li><li><b>Halaman Trend Alert siap kirim klien</b></li>
      <li>Semua fitur Pro, hingga 5 pengguna</li><li>Pantauan 10 kata kunci / brand</li>
      <li>Rekap bulanan + sesi tanya-jawab</li></ul></div>
    <div class="tier"><div class="nm">Data</div><div class="pr">mulai Rp4,9 jt<small> /bulan</small></div>
      <ul><li>Ekspor data mentah (CSV)</li><li>Akses API arsip</li><li>Cakupan sesuai kebutuhan</li></ul></div>
  </div>
  <div class="cta"><h4>Coba dua edisi tanpa biaya</h4>
  <p class="small" style="margin:0">Kirim nama brand/agensi dan paket yang diminati ke
  <b>keyframe.jakarta@gmail.com</b>. Untuk paket Agency kami sertakan satu edisi ber-logo agensi Anda
  sebagai contoh.</p></div>
  <div class="pf"><div>Indonesia Weekly Trend Intelligence · Edisi contoh · Data per 14 September 2026</div><div>lagitren.id · 6</div></div>
</section>
</body></html>"""


if __name__ == "__main__":
    sys.stdout.write(build())
