import { getTrendsByPlatform } from "@/lib/db";
import { getPlatform } from "@/lib/platforms";
import { rssFor } from "@/lib/rss";
import { SITE_NAME } from "@/lib/site";
import type { Platform } from "@/lib/types";

/** RSS per platform: /feed/google, /feed/netflix, /feed/produk, dst. */

export const revalidate = 600;

export async function GET(
  _req: Request,
  { params }: { params: { platform: string } }
) {
  const meta = getPlatform(params.platform);
  if (!meta) return new Response("Not found", { status: 404 });
  const trends = await getTrendsByPlatform(meta.key as Platform, 30);
  return rssFor(
    trends,
    `${SITE_NAME} — ${meta.name}`,
    `/feed/${params.platform}`
  );
}
