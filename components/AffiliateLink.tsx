"use client";

import type { ReactNode } from "react";

/**
 * Tautan afiliasi yang mengirim event GA4 "affiliate_click" saat diklik,
 * lalu membuka tujuan (TikTok Shop / Tokopedia) di tab baru.
 * Dipakai supaya kita tahu produk mana yang diklik menuju TikTok.
 */
export default function AffiliateLink({
  href,
  name,
  id,
  category,
  className,
  children
}: {
  href: string;
  name?: string;
  id?: string;
  category?: string;
  className?: string;
  children: ReactNode;
}) {
  function handleClick() {
    try {
      const w = window as unknown as {
        gtag?: (...args: unknown[]) => void;
      };
      w.gtag?.("event", "affiliate_click", {
        item_id: id,
        item_name: name,
        item_category: category,
        item_list_name: "TikTok Shop",
        link_url: href
      });
    } catch {
      /* analitik tak boleh menghambat navigasi */
    }
  }

  return (
    <a
      href={href}
      target="_blank"
      rel="nofollow sponsored noopener noreferrer"
      onClick={handleClick}
      className={className}
    >
      {children}
    </a>
  );
}
