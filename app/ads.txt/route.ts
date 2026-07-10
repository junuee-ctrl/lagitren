// Menyajikan /ads.txt untuk Google AdSense.
// Dibuat otomatis dari NEXT_PUBLIC_ADSENSE_CLIENT (mis. "ca-pub-123..").
// AdSense butuh baris ini agar iklan bisa tayang & pendapatan terverifikasi.

import { ADSENSE_CLIENT } from "@/lib/adsense";

export const dynamic = "force-static";

export function GET() {
  const client = ADSENSE_CLIENT ?? "";
  // "ca-pub-XXX" -> "pub-XXX"
  const pub = client.replace(/^ca-/, "");
  const body = pub
    ? `google.com, ${pub}, DIRECT, f08c47fec0942fa0\n`
    : "# ads.txt: set NEXT_PUBLIC_ADSENSE_CLIENT untuk mengaktifkan.\n";
  return new Response(body, {
    headers: { "content-type": "text/plain; charset=utf-8" }
  });
}
