"use client";

import { useEffect, useRef } from "react";

/**
 * Sematkan beberapa tweet (X) di dalam situs kita menggunakan widgets.js resmi.
 * Dipakai halaman detail X untuk menampilkan "tweet teratas" yang memimpin tren.
 */
export default function TweetEmbeds({ urls }: { urls: string[] }) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const src = "https://platform.twitter.com/widgets.js";
    const load = () => {
      (window as unknown as { twttr?: { widgets: { load: (el?: HTMLElement) => void } } })
        .twttr?.widgets.load(ref.current ?? undefined);
    };
    const existing = document.querySelector<HTMLScriptElement>(
      `script[src="${src}"]`
    );
    if (existing) {
      load();
      return;
    }
    const s = document.createElement("script");
    s.src = src;
    s.async = true;
    s.onload = load;
    document.body.appendChild(s);
  }, [urls.join(",")]);

  return (
    <div ref={ref} className="space-y-3">
      {urls.map((u) => (
        <blockquote key={u} className="twitter-tweet" data-lang="id" data-dnt="true">
          <a href={u}>Memuat tweet…</a>
        </blockquote>
      ))}
    </div>
  );
}
