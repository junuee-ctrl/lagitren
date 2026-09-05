import { getSitemapTrends } from "@/lib/db";
import { platformHref } from "@/lib/platforms";
import { slugFromId } from "@/lib/embed";
import { SITE_NAME, SITE_URL, toIso } from "@/lib/site";

/**
 * Google News sitemap (P1-2): hanya item ≤48 jam terakhir.
 * Syarat pendaftaran Publisher Center / peluang Discover.
 */

export const revalidate = 1800;

export async function GET() {
  const trends = await getSitemapTrends(2000);
  const cutoff = Date.now() - 48 * 3600 * 1000;

  const entries = trends
    .filter((t) => {
      const iso = toIso(t.collectedAt);
      return iso ? new Date(iso).getTime() >= cutoff : false;
    })
    .slice(0, 1000)
    .map((t) => {
      const url = `${SITE_URL}${platformHref(t.platform)}/${slugFromId(t.id)}`;
      return `  <url>
    <loc>${url}</loc>
    <news:news>
      <news:publication>
        <news:name>${SITE_NAME}</news:name>
        <news:language>id</news:language>
      </news:publication>
      <news:publication_date>${toIso(t.collectedAt)}</news:publication_date>
      <news:title><![CDATA[${t.title}]]></news:title>
    </news:news>
  </url>`;
    })
    .join("\n");

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">
${entries}
</urlset>`;

  return new Response(xml, {
    headers: {
      "Content-Type": "application/xml; charset=utf-8",
      "Cache-Control": "public, max-age=600"
    }
  });
}
