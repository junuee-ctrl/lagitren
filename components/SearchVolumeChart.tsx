/**
 * Grafik minat pencarian (Google Trends style) — SVG murni, tanpa library.
 * `data`: deret nilai relatif 0–100. Menampilkan area + garis + titik terakhir.
 */
export default function SearchVolumeChart({
  data,
  color = "#4285F4",
  labels
}: {
  data: number[];
  color?: string;
  labels?: string[];
}) {
  if (!data || data.length < 2) return null;

  const W = 640;
  const H = 160;
  const pad = { top: 12, right: 12, bottom: 22, left: 12 };
  const innerW = W - pad.left - pad.right;
  const innerH = H - pad.top - pad.bottom;

  const max = Math.max(...data, 1);
  const min = Math.min(...data, 0);
  const range = Math.max(max - min, 1);

  const x = (i: number) => pad.left + (i / (data.length - 1)) * innerW;
  const y = (v: number) => pad.top + innerH - ((v - min) / range) * innerH;

  const linePath = data
    .map((v, i) => `${i === 0 ? "M" : "L"} ${x(i).toFixed(1)} ${y(v).toFixed(1)}`)
    .join(" ");
  const areaPath =
    `${linePath} L ${x(data.length - 1).toFixed(1)} ${pad.top + innerH} ` +
    `L ${x(0).toFixed(1)} ${pad.top + innerH} Z`;

  const lastI = data.length - 1;
  const gid = `grad-${color.replace("#", "")}`;

  return (
    <figure className="w-full">
      <svg
        viewBox={`0 0 ${W} ${H}`}
        className="h-auto w-full"
        role="img"
        aria-label="Grafik minat pencarian dari waktu ke waktu"
        preserveAspectRatio="none"
      >
        <defs>
          <linearGradient id={gid} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity="0.28" />
            <stop offset="100%" stopColor={color} stopOpacity="0.02" />
          </linearGradient>
        </defs>

        {/* garis dasar */}
        <line
          x1={pad.left}
          y1={pad.top + innerH}
          x2={W - pad.right}
          y2={pad.top + innerH}
          stroke="#e5e7eb"
          strokeWidth="1"
        />

        <path d={areaPath} fill={`url(#${gid})`} />
        <path
          d={linePath}
          fill="none"
          stroke={color}
          strokeWidth="2.5"
          strokeLinejoin="round"
          strokeLinecap="round"
        />

        {/* titik terakhir */}
        <circle cx={x(lastI)} cy={y(data[lastI])} r="4" fill={color} />
        <circle cx={x(lastI)} cy={y(data[lastI])} r="8" fill={color} fillOpacity="0.18" />

        {/* label sumbu-x (opsional) */}
        {labels &&
          labels.length === data.length &&
          labels.map((lab, i) =>
            i % Math.ceil(data.length / 4) === 0 || i === lastI ? (
              <text
                key={i}
                x={x(i)}
                y={H - 6}
                fontSize="11"
                fill="#9ca3af"
                textAnchor={i === 0 ? "start" : i === lastI ? "end" : "middle"}
              >
                {lab}
              </text>
            ) : null
          )}
      </svg>
    </figure>
  );
}
