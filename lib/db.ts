import type { Platform, Trend, TrendExtra } from "./types";
import { MOCK_TRENDS, mockTrendsByPlatform } from "./mock";

/**
 * Lapisan akses data.
 *
 * Di produksi (Cloudflare Pages/Workers via OpenNext) kita membaca dari
 * binding D1 `env.DB`. Bila binding tidak tersedia (mis. `next dev` tanpa
 * wrangler, atau tabel masih kosong), kita jatuh ke data mock supaya UI
 * tetap tampil. Dengan begitu situs bisa dikembangkan & dideploy sebelum
 * collector Python mengisi data nyata.
 */

// Bentuk baris tabel `trends` di D1 (snake_case).
interface TrendRow {
  id: string;
  platform: string;
  rank: number;
  title: string;
  subtitle: string | null;
  metric: number | null;
  metric_label: string | null;
  ai_summary: string | null;
  url: string;
  thumbnail: string | null;
  source: string | null;
  hashtags: string | null; // JSON array string
  affiliate_url: string | null;
  price: string | null;
  interest: string | null; // JSON array string, mis. "[10,20,100]"
  extra: string | null; // JSON konteks kaya per-platform
  is_current: number | null; // 1 = sedang tren, 0 = arsip
  collected_at: string;
}

function rowToTrend(row: TrendRow): Trend {
  let hashtags: string[] | undefined;
  if (row.hashtags) {
    try {
      const parsed = JSON.parse(row.hashtags);
      if (Array.isArray(parsed)) hashtags = parsed.map(String);
    } catch {
      hashtags = row.hashtags
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);
    }
  }
  return {
    id: row.id,
    platform: row.platform as Platform,
    rank: row.rank,
    title: row.title,
    subtitle: row.subtitle ?? undefined,
    metric: row.metric ?? undefined,
    metricLabel: row.metric_label ?? undefined,
    aiSummary: row.ai_summary ?? undefined,
    url: row.url,
    thumbnail: row.thumbnail ?? undefined,
    source: row.source ?? undefined,
    hashtags,
    affiliateUrl: row.affiliate_url ?? undefined,
    price: row.price ?? undefined,
    interest: parseInterest(row.interest),
    extra: parseExtra(row.extra),
    isCurrent: row.is_current == null ? true : row.is_current === 1,
    collectedAt: row.collected_at
  };
}

function parseExtra(raw: string | null): TrendExtra | undefined {
  if (!raw) return undefined;
  try {
    const obj = JSON.parse(raw);
    if (obj && typeof obj === "object" && !Array.isArray(obj)) {
      const extra: TrendExtra = {};
      if (Array.isArray(obj.news) && obj.news.length > 0) {
        extra.news = obj.news
          .filter((n: unknown) => n && typeof n === "object")
          .map((n: Record<string, unknown>) => ({
            title: String(n.title ?? ""),
            url: String(n.url ?? ""),
            source: n.source ? String(n.source) : undefined
          }))
          .filter((n: { title: string; url: string }) => n.title && n.url);
      }
      if (Array.isArray(obj.comments) && obj.comments.length > 0) {
        extra.comments = obj.comments
          .filter((c: unknown) => c && typeof c === "object")
          .map((c: Record<string, unknown>) => ({
            author: c.author ? String(c.author) : undefined,
            text: String(c.text ?? ""),
            likes: typeof c.likes === "number" ? c.likes : undefined
          }))
          .filter((c: { text: string }) => c.text);
      }
      if (obj.ott && typeof obj.ott === "object") {
        const o = obj.ott as Record<string, unknown>;
        extra.ott = {
          kind: o.kind ? String(o.kind) : undefined,
          rating: typeof o.rating === "number" ? o.rating : undefined,
          synopsis: o.synopsis ? String(o.synopsis) : undefined,
          weeks: (o.weeks as string | number) ?? undefined,
          rank: (o.rank as string | number) ?? undefined
        };
      }
      if (
        (extra.news && extra.news.length) ||
        (extra.comments && extra.comments.length) ||
        extra.ott
      ) {
        return extra;
      }
    }
  } catch {
    /* abaikan */
  }
  return undefined;
}

function parseInterest(raw: string | null): number[] | undefined {
  if (!raw) return undefined;
  try {
    const arr = JSON.parse(raw);
    if (Array.isArray(arr) && arr.length > 0) return arr.map(Number);
  } catch {
    /* abaikan */
  }
  return undefined;
}

// D1Database bertipe longgar agar tidak wajib bergantung pada @cloudflare/workers-types.
interface D1Like {
  prepare: (query: string) => {
    bind: (...values: unknown[]) => {
      all: <T = unknown>() => Promise<{ results: T[] }>;
    };
    all: <T = unknown>() => Promise<{ results: T[] }>;
  };
}

async function getDB(): Promise<D1Like | null> {
  try {
    const mod = await import("@opennextjs/cloudflare");
    const ctx = await mod.getCloudflareContext();
    const db = (ctx?.env as Record<string, unknown> | undefined)?.DB;
    if (db && typeof (db as D1Like).prepare === "function") {
      return db as D1Like;
    }
  } catch {
    // binding/paket tidak tersedia → pakai mock
  }
  return null;
}

const LATEST_BY_PLATFORM = `
  SELECT * FROM trends
  WHERE platform = ? AND is_current = 1
  ORDER BY rank ASC
  LIMIT ?
`;

const LATEST_ALL = `
  SELECT * FROM trends
  WHERE is_current = 1
  ORDER BY platform ASC, rank ASC
`;

// Untuk sitemap: semua halaman (termasuk arsip) yang terbaru diperbarui.
const SITEMAP_TRENDS = `
  SELECT id, platform, collected_at, updated_at
  FROM trends
  ORDER BY updated_at DESC
  LIMIT ?
`;

const COUNT_ALL = `SELECT COUNT(*) AS c FROM trends`;

/**
 * Jumlah total baris di D1. Dipakai untuk memutuskan apakah situs sudah
 * punya data nyata. Bila > 0, kita TIDAK memakai data mock lagi (agar tidak
 * mencampur data nyata dengan contoh).
 */
async function totalCount(db: D1Like): Promise<number> {
  try {
    const { results } = await db.prepare(COUNT_ALL).all<{ c: number }>();
    return Number(results?.[0]?.c ?? 0);
  } catch {
    return 0;
  }
}

/** Ambil tren teratas untuk satu platform. */
export async function getTrendsByPlatform(
  platform: Platform,
  limit = 20
): Promise<Trend[]> {
  const db = await getDB();
  // Tanpa D1 (dev lokal) → pakai contoh.
  if (!db) return mockTrendsByPlatform(platform).slice(0, limit);
  try {
    const { results } = await db
      .prepare(LATEST_BY_PLATFORM)
      .bind(platform, limit)
      .all<TrendRow>();
    if (results && results.length > 0) return results.map(rowToTrend);
    // Kosong: bila DB sudah punya data nyata (platform lain), jangan palsukan.
    const total = await totalCount(db);
    if (total > 0) return [];
    // DB benar-benar kosong (baru deploy) → contoh sebagai bootstrap.
    return mockTrendsByPlatform(platform).slice(0, limit);
  } catch {
    return mockTrendsByPlatform(platform).slice(0, limit);
  }
}

/** Ambil semua tren, dikelompokkan per platform, untuk homepage. */
export async function getAllTrends(): Promise<Trend[]> {
  const db = await getDB();
  if (!db) return MOCK_TRENDS;
  try {
    const { results } = await db.prepare(LATEST_ALL).all<TrendRow>();
    if (!results || results.length === 0) return MOCK_TRENDS;
    return results.map(rowToTrend);
  } catch {
    return MOCK_TRENDS;
  }
}

const BY_ID = `SELECT * FROM trends WHERE id = ? LIMIT 1`;

/** Ambil satu trend berdasarkan platform + slug (untuk halaman detail). */
export async function getTrendById(
  platform: Platform,
  slug: string
): Promise<Trend | null> {
  const id = `${platform}:${slug}`;
  const db = await getDB();
  if (!db) {
    return (
      MOCK_TRENDS.find((t) => t.id === id && t.platform === platform) ?? null
    );
  }
  try {
    const { results } = await db.prepare(BY_ID).bind(id).all<TrendRow>();
    if (results && results.length > 0) return rowToTrend(results[0]);
  } catch {
    /* fallthrough ke mock */
  }
  return MOCK_TRENDS.find((t) => t.id === id) ?? null;
}

/** Trend lain dari platform yang sama (untuk navigasi internal). */
export async function getRelatedTrends(
  platform: Platform,
  excludeId: string,
  limit = 6
): Promise<Trend[]> {
  const all = await getTrendsByPlatform(platform, 20);
  return all.filter((t) => t.id !== excludeId).slice(0, limit);
}

interface SitemapRow {
  id: string;
  platform: string;
  collected_at: string;
  updated_at: string;
}

/** Semua halaman tren (termasuk arsip) untuk sitemap SEO. */
export async function getSitemapTrends(
  limit = 5000
): Promise<{ id: string; platform: Platform; collectedAt: string }[]> {
  const db = await getDB();
  if (!db) {
    return MOCK_TRENDS.map((t) => ({
      id: t.id,
      platform: t.platform,
      collectedAt: t.collectedAt
    }));
  }
  try {
    const { results } = await db
      .prepare(SITEMAP_TRENDS)
      .bind(limit)
      .all<SitemapRow>();
    if (results && results.length > 0) {
      return results.map((r) => ({
        id: r.id,
        platform: r.platform as Platform,
        collectedAt: r.updated_at || r.collected_at
      }));
    }
  } catch {
    /* fallthrough */
  }
  return MOCK_TRENDS.map((t) => ({
    id: t.id,
    platform: t.platform,
    collectedAt: t.collectedAt
  }));
}

// Arsip: tren yang sudah TIDAK aktif (is_current=0), terbaru dulu.
// Dipakai halaman /arsip untuk memberi jalur internal ke halaman lama
// (menghindari "halaman yatim" & bagus untuk SEO).
const ARCHIVED_TRENDS = `
  SELECT * FROM trends
  WHERE is_current = 0
  ORDER BY collected_at DESC
  LIMIT ?
`;

/** Ambil tren arsip (sudah tidak tren) untuk halaman /arsip. */
export async function getArchivedTrends(limit = 300): Promise<Trend[]> {
  const db = await getDB();
  if (!db) return [];
  try {
    const { results } = await db
      .prepare(ARCHIVED_TRENDS)
      .bind(limit)
      .all<TrendRow>();
    if (results && results.length > 0) return results.map(rowToTrend);
  } catch {
    /* abaikan */
  }
  return [];
}

/** Riwayat pengumpulan terbaru (untuk debug/monitoring). */
export async function getRecentRuns(limit = 20): Promise<unknown[]> {
  const db = await getDB();
  if (!db) return [];
  try {
    const { results } = await db
      .prepare(
        "SELECT platform, status, item_count, message, started_at, finished_at FROM collection_runs ORDER BY finished_at DESC LIMIT ?"
      )
      .bind(limit)
      .all();
    return results ?? [];
  } catch (e) {
    return [{ error: String(e) }];
  }
}

/** Preview homepage: N teratas per platform. */
export async function getHomepageTrends(perPlatform = 4): Promise<Trend[]> {
  const all = await getAllTrends();
  const counts = new Map<string, number>();
  const out: Trend[] = [];
  for (const t of [...all].sort((a, b) => a.rank - b.rank)) {
    const c = counts.get(t.platform) ?? 0;
    if (c < perPlatform) {
      out.push(t);
      counts.set(t.platform, c + 1);
    }
  }
  return out;
}
