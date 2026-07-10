import { getRecentRuns } from "@/lib/db";

// Endpoint debug sementara: menampilkan riwayat pengumpulan terbaru dari D1.
// Berguna untuk memantau collector (mis. respons TikTok/Instagram) tanpa akses
// ke log GitHub Actions. Aman dihapus setelah semua collector stabil.

export const dynamic = "force-dynamic";

export async function GET() {
  const runs = await getRecentRuns(25);
  return new Response(JSON.stringify({ runs }, null, 2), {
    headers: { "content-type": "application/json; charset=utf-8" }
  });
}
