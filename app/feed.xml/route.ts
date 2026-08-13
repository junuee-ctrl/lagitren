import { getAllTrends } from "@/lib/db";
import { rssFor } from "@/lib/rss";
import { SITE_NAME } from "@/lib/site";

/** RSS 2.0 seluruh platform (P1-2). Per-platform: /feed/[platform]. */

export const revalidate = 600;

export async function GET() {
  const trends = await getAllTrends();
  const sorted = [...trends].sort((a, b) =>
    (b.collectedAt ?? "").localeCompare(a.collectedAt ?? "")
  );
  return rssFor(sorted, `${SITE_NAME} — Semua Tren`, "/feed.xml");
}
