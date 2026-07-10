import type { Metadata } from "next";
import "./globals.css";
import Header from "@/components/Header";
import Footer from "@/components/Footer";

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL ?? "https://lagitren.id";
const ADSENSE_CLIENT = process.env.NEXT_PUBLIC_ADSENSE_CLIENT;

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
  alternates: { canonical: SITE_URL }
};

export default function RootLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="id">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap"
          rel="stylesheet"
        />
        {ADSENSE_CLIENT && (
          <script
            async
            src={`https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=${ADSENSE_CLIENT}`}
            crossOrigin="anonymous"
          />
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
