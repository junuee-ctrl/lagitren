import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

/**
 * Redirect afiliasi: lagitren.id/go/shopee/[slug]
 *
 * Untuk saat ini kami mengarahkan ke pencarian Shopee berdasarkan slug.
 * Nanti, saat Shopee Affiliate aktif, ganti target dengan deep link
 * afiliasi nyata (mis. diambil dari tabel D1 `affiliate_links`).
 */
export function GET(
  _req: NextRequest,
  { params }: { params: { slug: string } }
) {
  const keyword = decodeURIComponent(params.slug).replace(/-/g, " ").trim();
  const target = keyword
    ? `https://shopee.co.id/search?keyword=${encodeURIComponent(keyword)}`
    : "https://shopee.co.id/";

  // 302 agar mudah diubah ke deep link afiliasi tanpa cache permanen.
  return NextResponse.redirect(target, 302);
}
