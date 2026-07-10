"use client";

import { useEffect, useRef } from "react";
import { ADSENSE_CLIENT } from "@/lib/adsense";

/**
 * Slot iklan Google AdSense.
 *
 * - Bila NEXT_PUBLIC_ADSENSE_CLIENT di-set (mis. "ca-pub-123..."),
 *   merender unit iklan nyata <ins class="adsbygoogle">.
 * - Bila belum di-set (atau belum ada slot id), menampilkan placeholder
 *   netral agar tata letak final tetap terlihat.
 *
 * Slot id per-unit bisa diberikan lewat prop `adSlot` (angka dari AdSense).
 * Tanpa slot id, Auto Ads AdSense tetap dapat menempatkan iklan sendiri.
 */

declare global {
  interface Window {
    adsbygoogle?: unknown[];
  }
}

export default function AdSlot({
  slot,
  adSlot,
  label = "Iklan"
}: {
  /** Nama internal slot (untuk debugging/analytics). */
  slot?: string;
  /** data-ad-slot dari AdSense (angka). Kosongkan bila pakai Auto Ads. */
  adSlot?: string;
  label?: string;
}) {
  const ref = useRef<HTMLModElement>(null);

  useEffect(() => {
    if (!ADSENSE_CLIENT || !adSlot) return;
    try {
      (window.adsbygoogle = window.adsbygoogle || []).push({});
    } catch {
      /* abaikan (script belum siap / diblokir) */
    }
  }, [adSlot]);

  if (ADSENSE_CLIENT && adSlot) {
    return (
      <ins
        ref={ref}
        className="adsbygoogle my-2 block"
        style={{ display: "block" }}
        data-ad-client={ADSENSE_CLIENT}
        data-ad-slot={adSlot}
        data-ad-format="auto"
        data-full-width-responsive="true"
        data-ad-region={slot}
        aria-label={label}
      />
    );
  }

  return (
    <div
      className="my-2 flex min-h-[90px] items-center justify-center rounded-xl border border-dashed border-gray-300 bg-white/60 text-xs uppercase tracking-widest text-gray-400"
      aria-label={label}
      data-ad-slot={slot ?? ""}
    >
      <span>Ruang Iklan</span>
    </div>
  );
}
