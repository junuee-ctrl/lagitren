/**
 * Logo Lagi Tren — mark "#" bergaya glitch (magenta + teal) + wordmark.
 * SVG mandiri: tajam di ukuran apa pun & beradaptasi tema (kata "lagi").
 *
 * Catatan: bila punya berkas logo asli, taruh di /public dan ganti mark ini.
 */
function HashMark({ className = "h-8 w-8" }: { className?: string }) {
  const bars = (
    <>
      <rect x="15" y="5" width="7" height="38" rx="2.5" />
      <rect x="30" y="5" width="7" height="38" rx="2.5" />
      <rect x="7" y="15" width="38" height="7" rx="2.5" />
      <rect x="7" y="27" width="38" height="7" rx="2.5" />
    </>
  );
  return (
    <svg
      viewBox="0 0 52 48"
      className={className}
      role="img"
      aria-label="Lagi Tren"
    >
      <g transform="skewX(-9) translate(2 0)">
        {/* fringe teal (efek glitch) */}
        <g fill="#00C9B1" opacity="0.9" transform="translate(-2 -1.5)">
          {bars}
        </g>
        {/* utama magenta */}
        <g fill="#E6007A">{bars}</g>
      </g>
    </svg>
  );
}

export default function Logo({
  className = "",
  textClass = "text-xl"
}: {
  className?: string;
  textClass?: string;
}) {
  return (
    <span className={`inline-flex items-center gap-2 ${className}`}>
      <HashMark className="h-8 w-8 shrink-0" />
      <span
        className={`font-extrabold lowercase leading-none tracking-tight ${textClass}`}
      >
        <span className="text-ink dark:text-white">lagi </span>
        <span className="text-brand">tren</span>
        <span className="text-ink dark:text-white">.</span>
        <span className="text-brand">id</span>
      </span>
    </span>
  );
}
