"use client";

/* eslint-disable @next/next/no-img-element */
import { useEffect, useRef } from "react";
import type { Trend } from "@/lib/types";
import { youtubeId, canEmbed } from "@/lib/embed";

declare global {
  interface Window {
    instgrm?: { Embeds: { process: () => void } };
    twttr?: { widgets: { load: (el?: HTMLElement) => void } };
  }
}

/**
 * Muat script embed pihak ketiga sekali, lalu proses embed di dalam `ref`.
 * Dipakai untuk Instagram / TikTok / X yang butuh script mereka.
 */
function useEmbedScript(
  src: string,
  onReady?: () => void,
  ref?: React.RefObject<HTMLElement>
) {
  useEffect(() => {
    const existing = document.querySelector<HTMLScriptElement>(
      `script[src="${src}"]`
    );
    const run = () => onReady?.();
    if (existing) {
      run();
      return;
    }
    const s = document.createElement("script");
    s.src = src;
    s.async = true;
    s.onload = run;
    document.body.appendChild(s);
    // ref sengaja tidak di-cleanup: script embed global dibiarkan.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [src]);
}

function YouTubeEmbed({ id, title }: { id: string; title: string }) {
  return (
    <div className="aspect-video w-full overflow-hidden rounded-xl bg-black">
      <iframe
        className="h-full w-full"
        src={`https://www.youtube-nocookie.com/embed/${id}`}
        title={title}
        loading="lazy"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
        referrerPolicy="strict-origin-when-cross-origin"
        allowFullScreen
      />
    </div>
  );
}

function InstagramEmbed({ url }: { url: string }) {
  const ref = useRef<HTMLDivElement>(null);
  useEmbedScript("https://www.instagram.com/embed.js", () =>
    window.instgrm?.Embeds.process()
  );
  return (
    <div ref={ref}>
      <blockquote
        className="instagram-media"
        data-instgrm-permalink={url}
        data-instgrm-version="14"
        style={{ margin: "0 auto", maxWidth: 540, width: "100%" }}
      />
    </div>
  );
}

function TikTokEmbed({ url }: { url: string }) {
  const videoId = url.match(/\/video\/(\d+)/)?.[1] ?? "";
  useEmbedScript("https://www.tiktok.com/embed.js");
  return (
    <blockquote
      className="tiktok-embed"
      cite={url}
      data-video-id={videoId}
      style={{ maxWidth: 605, minWidth: 280, margin: "0 auto" }}
    >
      <section />
    </blockquote>
  );
}

function TwitterEmbed({ url }: { url: string }) {
  const ref = useRef<HTMLDivElement>(null);
  useEmbedScript(
    "https://platform.twitter.com/widgets.js",
    () => window.twttr?.widgets.load(ref.current ?? undefined),
    ref
  );
  return (
    <div ref={ref} className="flex justify-center">
      <blockquote className="twitter-tweet" data-lang="id">
        <a href={url}>Memuat postingan dari X…</a>
      </blockquote>
    </div>
  );
}

/**
 * Media utama halaman detail. Menampilkan konten platform LANGSUNG di situs kita
 * (embed) bila memungkinkan; kalau tidak, tampilkan thumbnail sebagai fallback.
 * Untuk Google (kata kunci) tidak ada media — halaman detail fokus ke penjelasan.
 */
export default function TrendMedia({ trend }: { trend: Trend }) {
  if (trend.platform === "youtube") {
    const id = youtubeId(trend);
    if (id) return <YouTubeEmbed id={id} title={trend.title} />;
  }
  if (trend.platform === "instagram" && canEmbed(trend)) {
    return <InstagramEmbed url={trend.url} />;
  }
  if (trend.platform === "tiktok" && canEmbed(trend)) {
    return <TikTokEmbed url={trend.url} />;
  }
  if (trend.platform === "twitter" && canEmbed(trend)) {
    return <TwitterEmbed url={trend.url} />;
  }
  if (trend.thumbnail) {
    return (
      <img
        src={trend.thumbnail}
        alt={trend.title}
        className="w-full rounded-xl object-cover"
      />
    );
  }
  return null;
}
