"use client";

import Script from "next/script";

/**
 * Google Analytics 4 via next/script (cara resmi & andal di App Router).
 * Ditaruh di <body>; strategy afterInteractive memuat setelah halaman siap.
 */
export default function GoogleAnalytics({ gaId }: { gaId?: string }) {
  if (!gaId) return null;
  return (
    <>
      <Script
        src={`https://www.googletagmanager.com/gtag/js?id=${gaId}`}
        strategy="afterInteractive"
      />
      <Script id="ga-init" strategy="afterInteractive">
        {`window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments)}gtag('js',new Date());gtag('config','${gaId}');`}
      </Script>
    </>
  );
}
