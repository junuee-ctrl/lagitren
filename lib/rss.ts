import { getPlatform, platformHref } from "@/lib/platforms";
import { slugFromId } from "@/lib/embed";
import { SITE_NAME, SITE_URL, toIso } from "@/lib/site";

function esc(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

/** Bangun respons RSS 2.0 dari daftar tren (P1-2). */
export function rssFor(
  items: {
    id: string;
    platform: string;
    title: string;
    aiSummary?: string;
    collectedAt?: string;
  }[],
  title: string,
  path: string
): Response {
  const entries = items
    .slice(0, 50)
    .map((t) => {
      const meta = getPlatform(t.platform);
      const url = `${SITE_URL}${platformHref(t.platform as never)}/${slugFromId(t.id)}`;
      const date = toIso(t.collectedAt);
      return `  <item>
    <title>${esc(t.title)}</title>
    <link>${url}</link>
    <guid isPermaLink="true">${url}</guid>
    ${date ? `<pubDate>${new Date(date).toUTCString()}</pubDate>` : ""}
    ${t.aiSummary ? `<description>${esc(t.aiSummary)}</description>` : ""}
    ${meta ? `<category>${esc(meta.name)}</category>` : ""}
  </item>`;
    })
    .join("\n");

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
  <title>${esc(title)}</title>
  <link>${SITE_URL}</link>
  <atom:link href="${SITE_URL}${path}" rel="self" type="application/rss+xml"/>
  <description>Tren real-time Indonesia — ${esc(SITE_NAME)}</description>
  <language>id-ID</language>
${entries}
</channel>
</rss>`;

  return new Response(xml, {
    headers: {
      "Content-Type": "application/rss+xml; charset=utf-8",
      "Cache-Control": "public, max-age=600"
    }
  });
}
