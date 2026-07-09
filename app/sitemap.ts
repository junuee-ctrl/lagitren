import type { MetadataRoute } from "next";
import { PLATFORM_ORDER } from "@/lib/platforms";

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL ?? "https://lagitren.id";

export default function sitemap(): MetadataRoute.Sitemap {
  const now = new Date();

  const staticPages = [
    "",
    "/about",
    "/contact",
    "/privacy",
    "/disclaimer",
    "/affiliate"
  ].map((path) => ({
    url: `${SITE_URL}${path}`,
    lastModified: now,
    changeFrequency: "weekly" as const,
    priority: path === "" ? 1 : 0.5
  }));

  const platformPages = PLATFORM_ORDER.map((p) => ({
    url: `${SITE_URL}/${p}`,
    lastModified: now,
    changeFrequency: "hourly" as const,
    priority: 0.8
  }));

  return [...staticPages, ...platformPages];
}
