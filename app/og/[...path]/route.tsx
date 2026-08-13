import { ImageResponse } from "next/og";
import { getTrendById } from "@/lib/db";
import { getPlatform } from "@/lib/platforms";
import type { Platform, Trend } from "@/lib/types";

/**
 * Kartu OG 1200×630 dinamis (P1-1) — syarat Google Discover & CTR sosial.
 *
 *   /og/site                → kartu default situs (home)
 *   /og/google              → kartu halaman platform
 *   /og/google/jadwal-persib → kartu tren spesifik (judul besar + rank)
 *
 * Font di-fetch dari Google Fonts DIsubset per-teks (param `text=`) sehingga
 * tetap kecil, termasuk fallback Korea/Jepang/Arab/Thai bila judul memakainya.
 */

export const dynamic = "force-dynamic";

const W = 1200;
const H = 630;
const BRAND = "#E6007A";
const ACCENT = "#00C9B1";
const GRAPE = "#8B3DD6";

// ── util ─────────────────────────────────────────────────────────────

function stripUnrenderable(s: string): string {
  // Emoji/simbol di luar cakupan font → buang agar tidak jadi kotak.
  return s
    .replace(/[\u{1F000}-\u{1FAFF}\u{2600}-\u{27BF}\u{FE0F}\u{200D}]/gu, "")
    .replace(/\s+/g, " ")
    .trim();
}

function truncate(s: string, max: number): string {
  return s.length > max ? s.slice(0, max - 1).trimEnd() + "…" : s;
}

async function loadGoogleFont(
  family: string,
  text: string,
  weight: number
): Promise<ArrayBuffer | null> {
  try {
    const css = await (
      await fetch(
        `https://fonts.googleapis.com/css2?family=${encodeURIComponent(
          family
        )}:wght@${weight}&text=${encodeURIComponent(text || "lagitren")}`,
        {
          headers: {
            // UA lawas → Google mengirim TTF (bukan woff2 yang tak didukung satori)
            "User-Agent":
              "Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/110.0"
          }
        }
      )
    ).text();
    const m = css.match(/src: url\((.+?)\) format\('(?:truetype|opentype)'\)/);
    if (!m) return null;
    return await (await fetch(m[1])).arrayBuffer();
  } catch {
    return null;
  }
}

// Skrip non-Latin → font Noto yang menanggungnya (disubset per judul).
const SCRIPT_FONTS: Array<[RegExp, string]> = [
  [/[가-힣]/, "Noto Sans KR"],
  [/[぀-ヿ一-鿿]/, "Noto Sans JP"],
  [/[؀-ۿ]/, "Noto Sans Arabic"],
  [/[฀-๿]/, "Noto Sans Thai"]
];

function b64(buf: ArrayBuffer): string {
  const b = new Uint8Array(buf);
  let s = "";
  for (let i = 0; i < b.length; i += 8192)
    s += String.fromCharCode(...b.subarray(i, i + 8192));
  return btoa(s);
}

/** Coba unduh thumbnail asli (YouTube/Netflix/produk) → data URI. */
async function fetchThumb(url?: string): Promise<string | null> {
  if (!url || !url.startsWith("http")) return null;
  try {
    const r = await fetch(url, { signal: AbortSignal.timeout(3500) });
    const ct = r.headers.get("content-type") ?? "";
    if (!r.ok || !ct.startsWith("image/") || ct.includes("svg")) return null;
    const buf = await r.arrayBuffer();
    if (buf.byteLength < 1000 || buf.byteLength > 2_500_000) return null;
    return `data:${ct};base64,${b64(buf)}`;
  } catch {
    return null;
  }
}

// ── kartu ────────────────────────────────────────────────────────────

export async function GET(
  _req: Request,
  { params }: { params: { path: string[] } }
) {
  const [platformSlug, slug] = params.path ?? [];
  const meta = platformSlug === "site" ? null : getPlatform(platformSlug ?? "");
  const platform = meta?.key as Platform | undefined;

  let trend: Trend | null = null;
  if (platform && slug) {
    try {
      trend = await getTrendById(platform, slug);
    } catch {
      trend = null;
    }
  }

  const rawTitle = trend
    ? trend.title
    : meta
      ? `${meta.name} Indonesia Hari Ini`
      : "Apa yang lagi tren di Indonesia hari ini?";
  const title = truncate(stripUnrenderable(rawTitle) || "Lagi Tren", 95);
  const kicker = trend
    ? meta
      ? `Lagi tren di ${meta.name} Indonesia`
      : "Lagi tren di Indonesia"
    : "Tren real-time · diperbarui otomatis";
  const rank = trend?.rank && trend.rank <= 50 ? trend.rank : null;
  const accentColor = meta?.color ?? BRAND;

  const thumb = await fetchThumb(trend?.thumbnail);

  // Font: subset persis karakter yang dipakai (kecil & cepat).
  const allText = `${title} ${kicker} lagi tren.id #№0123456789`;
  const fonts: Array<{
    name: string;
    data: ArrayBuffer;
    weight: 400 | 700;
    style: "normal";
  }> = [];
  const jostBold = await loadGoogleFont("Jost", allText, 700);
  if (jostBold)
    fonts.push({ name: "Jost", data: jostBold, weight: 700, style: "normal" });
  const jostReg = await loadGoogleFont("Jost", allText, 400);
  if (jostReg)
    fonts.push({ name: "Jost", data: jostReg, weight: 400, style: "normal" });
  for (const [re, fam] of SCRIPT_FONTS) {
    if (re.test(title)) {
      const data = await loadGoogleFont(fam, title, 700);
      if (data) fonts.push({ name: "Jost", data, weight: 700, style: "normal" });
      break;
    }
  }

  const titleSize = title.length > 60 ? 52 : title.length > 34 ? 62 : 76;

  const card = (
    <div
      style={{
        width: "100%",
        height: "100%",
        display: "flex",
        fontFamily: "Jost",
        backgroundImage: `linear-gradient(135deg, ${BRAND} 0%, ${GRAPE} 52%, ${ACCENT} 100%)`
      }}
    >
      {/* panel kiri: teks */}
      <div
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          padding: "56px 60px"
        }}
      >
        {/* header: mark # glitch + wordmark */}
        <div style={{ display: "flex", alignItems: "center" }}>
          <div style={{ display: "flex", position: "relative", width: 74, height: 74 }}>
            <div
              style={{
                position: "absolute",
                top: 4,
                left: 0,
                fontSize: 72,
                fontWeight: 700,
                color: "rgba(0,201,177,0.95)",
                transform: "skewX(-9deg)"
              }}
            >
              #
            </div>
            <div
              style={{
                position: "absolute",
                top: 0,
                left: 4,
                fontSize: 72,
                fontWeight: 700,
                color: "#ffffff",
                transform: "skewX(-9deg)"
              }}
            >
              #
            </div>
          </div>
          <div style={{ display: "flex", fontSize: 40, fontWeight: 700, color: "#fff" }}>
            lagi tren
            <span style={{ color: "rgba(255,255,255,0.75)" }}>.id</span>
          </div>
        </div>

        {/* judul */}
        <div style={{ display: "flex", flexDirection: "column" }}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              marginBottom: 18
            }}
          >
            {rank && (
              <div
                style={{
                  display: "flex",
                  backgroundColor: "#ffffff",
                  color: accentColor,
                  fontWeight: 700,
                  fontSize: 30,
                  padding: "6px 22px",
                  borderRadius: 999,
                  marginRight: 18
                }}
              >
                #{rank} Trending
              </div>
            )}
            <div
              style={{
                display: "flex",
                fontSize: 30,
                fontWeight: 400,
                color: "rgba(255,255,255,0.92)"
              }}
            >
              {kicker}
            </div>
          </div>
          <div
            style={{
              display: "flex",
              fontSize: titleSize,
              fontWeight: 700,
              color: "#ffffff",
              lineHeight: 1.12,
              textShadow: "0 3px 14px rgba(0,0,0,0.25)"
            }}
          >
            {title}
          </div>
        </div>

        {/* footer */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between"
          }}
        >
          <div
            style={{
              display: "flex",
              fontSize: 28,
              color: "rgba(255,255,255,0.9)",
              fontWeight: 400
            }}
          >
            Kenapa ini lagi tren? Baca ringkasannya →
          </div>
          <div
            style={{
              display: "flex",
              backgroundColor: "rgba(255,255,255,0.18)",
              borderRadius: 999,
              padding: "8px 24px",
              fontSize: 26,
              fontWeight: 700,
              color: "#fff"
            }}
          >
            lagitren.id
          </div>
        </div>
      </div>

      {/* panel kanan: thumbnail asli bila ada */}
      {thumb && (
        <div
          style={{
            display: "flex",
            width: 430,
            height: "100%",
            position: "relative"
          }}
        >
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={thumb}
            alt=""
            width={430}
            height={H}
            style={{ objectFit: "cover", width: 430, height: H }}
          />
          <div
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              width: 60,
              height: H,
              backgroundImage:
                "linear-gradient(90deg, rgba(139,61,214,0.9), rgba(139,61,214,0))"
            }}
          />
        </div>
      )}
    </div>
  );

  return new ImageResponse(card, {
    width: W,
    height: H,
    fonts: fonts.length > 0 ? fonts : undefined,
    headers: {
      "Cache-Control": "public, max-age=3600, s-maxage=86400",
      "Content-Type": "image/png"
    }
  });
}
