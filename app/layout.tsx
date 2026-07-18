import type { Metadata } from "next";
import "./globals.css";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import { ADSENSE_CLIENT } from "@/lib/adsense";

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL ?? "https://lagitren.id";

// Token beacon Cloudflare Web Analytics (publik; bukan rahasia).
// Diambil dari dashboard Cloudflare → Web Analytics. Kosong → nonaktif.
const CF_ANALYTICS_TOKEN = process.env.NEXT_PUBLIC_CF_ANALYTICS_TOKEN;
// ID Pengukuran Google Analytics 4. Default ke properti lagitren.id;
// bisa ditimpa lewat env NEXT_PUBLIC_GA_ID bila perlu.
const GA_ID = process.env.NEXT_PUBLIC_GA_ID || "G-CZCFHY3VWY";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    default: "Lagi Tren — Apa yang Lagi Tren di Indonesia Hari Ini",
    template: "%s · Lagi Tren"
  },
  description:
    "Lagi Tren mengumpulkan tren real-time dari Google, YouTube, TikTok, Instagram, Shopee, dan X (Twitter) di Indonesia, lengkap dengan ringkasan AI kenapa sesuatu sedang viral.",
  keywords: [
    "trending di Indonesia hari ini",
    "yang lagi viral di TikTok",
    "produk paling dicari di Shopee",
    "YouTube trending Indonesia",
    "apa yang lagi tren"
  ],
  openGraph: {
    type: "website",
    locale: "id_ID",
    url: SITE_URL,
    siteName: "Lagi Tren",
    title: "Lagi Tren — Apa yang Lagi Tren di Indonesia",
    description:
      "Tren real-time dari berbagai platform Indonesia dalam satu halaman, dengan ringkasan AI."
  },
  twitter: {
    card: "summary_large_image",
    title: "Lagi Tren — Apa yang Lagi Tren di Indonesia",
    description:
      "Tren real-time dari Google, YouTube, TikTok, Instagram, Shopee, dan X."
  },
  robots: { index: true, follow: true },
  alternates: { canonical: SITE_URL },
  verification: {
    google: "IOCf3HyY_9-5tLsVfZyMmgfgjVHqDKG2Kw1tKWSP_kw"
  }
};

export default function RootLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="id" suppressHydrationWarning>
      <head>
        {/* Set tema sebelum paint agar tidak berkedip (FOUC). */}
        <script
          dangerouslySetInnerHTML={{
            __html:
              "(function(){try{var t=localStorage.getItem('theme');if(t==='dark'||(!t&&window.matchMedia('(prefers-color-scheme:dark)').matches)){document.documentElement.classList.add('dark')}}catch(e){}})()"
          }}
        />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />
        {/* Century Gothic itu font berbayar → tak bisa di-embed. Muat Jost
            (geometrik, mirip) sebagai fallback untuk yang tak punya CG. */}
        <link
          href="https://fonts.googleapis.com/css2?family=Jost:wght@400;500;600;700;800&display=swap"
          rel="stylesheet"
        />
        {ADSENSE_CLIENT && (
          <script
            async
            src={`https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=${ADSENSE_CLIENT}`}
            crossOrigin="anonymous"
          />
        )}
        {CF_ANALYTICS_TOKEN && (
          <script
            defer
            src="https://static.cloudflareinsights.com/beacon.min.js"
            data-cf-beacon={`{"token": "${CF_ANALYTICS_TOKEN}"}`}
          />
        )}
        {GA_ID && (
          <>
            <script
              async
              src={`https://www.googletagmanager.com/gtag/js?id=${GA_ID}`}
            />
            <script
              dangerouslySetInnerHTML={{
                __html: `window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments)}gtag('js',new Date());gtag('config','${GA_ID}');`
              }}
            />
          </>
        )}
      </head>
      <body className="min-h-screen font-sans">
        <Header />
        <main className="container-page py-6">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
