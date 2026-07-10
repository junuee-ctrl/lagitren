/**
 * Grafik minat pencarian resmi Google Trends (embed iframe).
 *
 * Dimuat langsung dari Google di browser pengunjung — data asli & real-time,
 * gratis, tanpa API/rate-limit di sisi server kita. Alternatif andal untuk
 * pytrends yang sering diblokir dari IP datacenter (GitHub Actions).
 */
export default function GoogleTrendsWidget({
  keyword,
  geo = "ID",
  time = "now 7-d"
}: {
  keyword: string;
  geo?: string;
  time?: string;
}) {
  const req = {
    comparisonItem: [{ keyword, geo, time }],
    category: 0,
    property: ""
  };
  // tz -420 = UTC+7 (WIB, Jakarta), dalam menit negatif sesuai format Google.
  const src =
    "https://trends.google.com/trends/embed/explore/TIMESERIES?req=" +
    encodeURIComponent(JSON.stringify(req)) +
    "&tz=-420";

  return (
    <iframe
      src={src}
      title={`Tren pencarian "${keyword}" di Google (Indonesia)`}
      loading="lazy"
      className="w-full rounded-lg"
      style={{ height: 420, border: 0 }}
      referrerPolicy="no-referrer-when-downgrade"
    />
  );
}
