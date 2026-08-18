import { NextRequest, NextResponse } from "next/server";

/**
 * GET /admin/status?key=<ADMIN_KEY>
 *
 * Status kesehatan pipeline (P0-8/F6): per platform — kapan terakhir sukses,
 * berapa item, run terakhir (termasuk error), dan umur data di tabel trends.
 * Dibaca dari D1 `collection_runs` + `trends`. JSON ringkas, enak dibaca
 * dari browser ponsel.
 *
 * Auth: query `key` harus sama dengan env ADMIN_KEY (set di dashboard
 * Cloudflare → Workers → Settings → Variables). Tanpa ADMIN_KEY endpoint
 * nonaktif (503). Selalu noindex + robots.txt sudah men-disallow /admin/.
 */

export const dynamic = "force-dynamic";

interface D1Like {
  prepare: (q: string) => {
    bind: (...v: unknown[]) => { all: <T = unknown>() => Promise<{ results: T[] }> };
    all: <T = unknown>() => Promise<{ results: T[] }>;
  };
}

const PLATFORMS = [
  "google",
  "youtube",
  "instagram",
  "tiktok",
  "twitter",
  "netflix",
  "shopee",
  "watchdog"
];

function wib(iso: string | null | undefined): string | null {
  if (!iso) return null;
  const d = new Date(String(iso).endsWith("Z") ? String(iso) : `${iso}Z`);
  if (isNaN(d.getTime())) return String(iso);
  return (
    d.toLocaleString("id-ID", {
      timeZone: "Asia/Jakarta",
      day: "2-digit",
      month: "short",
      hour: "2-digit",
      minute: "2-digit"
    }) + " WIB"
  );
}

function hoursAgo(iso: string | null | undefined): number | null {
  if (!iso) return null;
  const d = new Date(String(iso).endsWith("Z") ? String(iso) : `${iso}Z`);
  if (isNaN(d.getTime())) return null;
  return Math.round(((Date.now() - d.getTime()) / 36e5) * 10) / 10;
}

export async function GET(req: NextRequest) {
  const headers = { "X-Robots-Tag": "noindex, nofollow" };

  let env: Record<string, unknown> | undefined;
  try {
    const mod = await import("@opennextjs/cloudflare");
    env = (await mod.getCloudflareContext())?.env as Record<string, unknown>;
  } catch {
    /* dev tanpa binding */
  }

  const adminKey = (env?.ADMIN_KEY as string) || process.env.ADMIN_KEY || "";
  if (!adminKey) {
    return NextResponse.json(
      { error: "ADMIN_KEY belum diset di environment Cloudflare." },
      { status: 503, headers }
    );
  }
  if (req.nextUrl.searchParams.get("key") !== adminKey) {
    return NextResponse.json({ error: "kunci salah" }, { status: 401, headers });
  }

  const db = env?.DB as D1Like | undefined;
  if (!db || typeof db.prepare !== "function") {
    return NextResponse.json({ error: "D1 tidak tersedia" }, { status: 503, headers });
  }

  type RunRow = {
    platform: string;
    status: string;
    item_count: number;
    message: string | null;
    started_at: string;
  };

  // Run terakhir + sukses terakhir per platform (2 query saja).
  const lastRuns = await db
    .prepare(
      `SELECT r.platform, r.status, r.item_count, r.message, r.started_at
       FROM collection_runs r
       JOIN (SELECT platform, MAX(started_at) m FROM collection_runs GROUP BY platform) t
         ON t.platform = r.platform AND t.m = r.started_at`
    )
    .all<RunRow>();
  const lastOk = await db
    .prepare(
      `SELECT platform, MAX(started_at) AS started_at, item_count
       FROM collection_runs WHERE status = 'ok' AND item_count > 0
       GROUP BY platform`
    )
    .all<RunRow>();
  const fresh = await db
    .prepare(
      `SELECT platform, MAX(collected_at) AS collected_at, COUNT(*) AS n
       FROM trends WHERE is_current = 1 GROUP BY platform`
    )
    .all<{ platform: string; collected_at: string; n: number }>();

  const byLast = new Map(lastRuns.results.map((r) => [r.platform, r]));
  const byOk = new Map(lastOk.results.map((r) => [r.platform, r]));
  const byFresh = new Map(fresh.results.map((r) => [r.platform, r]));

  const sources = PLATFORMS.map((p) => {
    const ok = byOk.get(p);
    const last = byLast.get(p);
    const fr = byFresh.get(p);
    return {
      platform: p,
      last_success: wib(ok?.started_at),
      last_success_hours_ago: hoursAgo(ok?.started_at),
      last_run_status: last?.status ?? null,
      last_run_at: wib(last?.started_at),
      last_run_message: last?.message?.slice(0, 300) ?? null,
      items_current: fr?.n ?? 0,
      data_updated: wib(fr?.collected_at)
    };
  });

  return NextResponse.json(
    { generated_at: wib(new Date().toISOString().replace("Z", "")), sources },
    { headers }
  );
}
