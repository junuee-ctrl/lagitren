// Lapisan cache edge di depan worker OpenNext (hemat "Workers CPU ms").
//
// Latar (Nov 2026): OpenNext dipakai tanpa incrementalCache, jadi `revalidate`
// di halaman TIDAK disimpan — setiap request merender ulang halaman (CPU).
// Di sini halaman publik disimpan di Cache API Cloudflare per data center
// (gratis, tanpa resource baru) selama beberapa menit. Data sendiri baru
// berubah tiap ~3 jam (collector), jadi 5 menit tidak terasa.
//
// Aman: hanya GET tanpa header RSC (navigasi klien Next memakai payload lain
// di URL yang sama), hanya status 200, dan jalur dinamis dikecualikan.

import handler from "./.open-next/worker.js";

export * from "./.open-next/worker.js";

const NO_CACHE_PREFIX = ["/api/", "/admin", "/go/", "/_next/"];

function ttlFor(pathname) {
  if (pathname.startsWith("/og/")) return 86400;
  if (pathname.endsWith(".xml") || pathname.startsWith("/feed")) return 1800;
  if (pathname === "/robots.txt" || pathname === "/ads.txt") return 3600;
  return 300;
}

function cacheable(request, url) {
  if (request.method !== "GET") return false;
  if (request.headers.get("rsc") || request.headers.get("next-router-prefetch")) return false;
  if (url.searchParams.has("_rsc")) return false;
  if (url.searchParams.has("key")) return false; // halaman admin ber-kunci
  return !NO_CACHE_PREFIX.some((p) => url.pathname.startsWith(p));
}

export default {
  ...handler,
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    if (!cacheable(request, url)) return handler.fetch(request, env, ctx);

    const cache = caches.default;
    const key = new Request(url.toString(), { method: "GET" });
    try {
      const hit = await cache.match(key);
      if (hit) {
        const res = new Response(hit.body, hit);
        res.headers.set("x-lagitren-cache", "HIT");
        return res;
      }
    } catch {
      // Cache API gagal → lanjut render biasa.
    }

    const res = await handler.fetch(request, env, ctx);
    if (res.status !== 200 || res.headers.has("set-cookie")) return res;
    const type = res.headers.get("content-type") || "";
    if (!/text\/html|xml|rss|image\/|text\/plain/.test(type)) return res;

    try {
      const copy = new Response(res.clone().body, res);
      copy.headers.set("cache-control", `public, max-age=${ttlFor(url.pathname)}`);
      ctx.waitUntil(cache.put(key, copy));
    } catch {
      // abaikan
    }
    const out = new Response(res.body, res);
    out.headers.set("x-lagitren-cache", "MISS");
    return out;
  },
};
