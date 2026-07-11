import type { MetadataRoute } from "next";
import { PLATFORM_ORDER } from "@/lib/platforms";
import { getSitemapTrends } from "@/lib/db";
import { slugFromId } from "@/lib/embed";

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL ?? "https://lagitren.id";

// Segarkan sitemap berkala agar halaman tren baru cepat ditemukan Google.
export const revalidate = 600; // 10 menit

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const now = new Date();

  const staticPages: MetadataRoute.Sitemap = [
    "",
    "/arsip",
    "/about",
    "/contact",
    "/privacy",
    "/disclaimer",
    "/affiliate"
  ].map((path) => ({
    url: `${SITE_URL}${path}`,
    lastModified: now,
    changeFrequency: path === "/arsip" ? "daily" : "weekly",
    priority: path === "" ? 1 : path === "/arsip" ? 0.6 : 0.5
  }));

  const platformPages: MetadataRoute.Sitemap = PLATFORM_ORDER.map((p) => ({
    url: `${SITE_URL}/${p}`,
    lastModified: now,
    changeFrequency: "hourly",
    priority: 0.8
  }));

  // Halaman detail per tren — INI yang menarik trafik pencarian.
  let detailPages: MetadataRoute.Sitemap = [];
  try {
    const trends = await getSitemapTrends(5000);
    const seen = new Set<string>();
    detailPages = trends
      .map((t) => {
        const url = `${SITE_URL}/${t.platform}/${slugFromId(t.id)}`;
        if (seen.has(url)) return null;
        seen.add(url);
        const lm = new Date(t.collectedAt);
        return {
          url,
          lastModified: Number.isNaN(lm.getTime()) ? now : lm,
          changeFrequency: "hourly" as const,
          priority: 0.7
        };
      })
      .filter((x): x is NonNullable<typeof x> => x !== null);
  } catch {
    /* abaikan bila DB tak tersedia */
  }

  return [...staticPages, ...platformPages, ...detailPages];
}
