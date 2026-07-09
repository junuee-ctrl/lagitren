/**
 * Slot iklan Google AdSense.
 *
 * Placeholder sampai AdSense disetujui. Setelah punya client & slot ID,
 * set NEXT_PUBLIC_ADSENSE_CLIENT dan isi `slot`, lalu render <ins className="adsbygoogle" .../>.
 * Untuk sekarang menampilkan area netral agar layout final terlihat.
 */

const ADSENSE_CLIENT = process.env.NEXT_PUBLIC_ADSENSE_CLIENT;

export default function AdSlot({
  slot,
  label = "Iklan"
}: {
  slot?: string;
  label?: string;
}) {
  const active = Boolean(ADSENSE_CLIENT && slot);

  return (
    <div
      className="my-2 flex min-h-[90px] items-center justify-center rounded-xl border border-dashed border-gray-300 bg-white/60 text-xs uppercase tracking-widest text-gray-400"
      aria-label={label}
      data-ad-slot={slot ?? ""}
    >
      {active ? (
        // Setelah AdSense aktif, ganti blok ini dengan <ins className="adsbygoogle" />.
        <span>Iklan</span>
      ) : (
        <span>Ruang Iklan</span>
      )}
    </div>
  );
}
