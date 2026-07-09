import type { Platform, Trend } from "./types";
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
    collectedAt: row.collected_at
  };
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
  WHERE platform = ?
  ORDER BY rank ASC
  LIMIT ?
`;

const LATEST_ALL = `
  SELECT * FROM trends
  ORDER BY platform ASC, rank ASC
`;

/** Ambil tren teratas untuk satu platform. */
export async function getTrendsByPlatform(
  platform: Platform,
  limit = 20
): Promise<Trend[]> {
  const db = await getDB();
  if (!db) return mockTrendsByPlatform(platform).slice(0, limit);
  try {
    const { results } = await db
      .prepare(LATEST_BY_PLATFORM)
      .bind(platform, limit)
      .all<TrendRow>();
    if (!results || results.length === 0) {
      return mockTrendsByPlatform(platform).slice(0, limit);
    }
    return results.map(rowToTrend);
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
