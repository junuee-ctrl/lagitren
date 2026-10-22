/**
 * Banner promosi situs saudara: Rasi (zodiak.lagitren.id).
 * - Mobile: 320×100, layar ≥ 768px: 728×90 (gambar di public/promo/; nama sengaja tanpa "banner"/"728x90" agar tidak diblokir ad-blocker).
 * - Tinggi dipesan lewat atribut width/height + aspect-ratio supaya tata letak
 *   tidak bergeser saat gambar dimuat (CLS).
 */
export default function RasiBanner({ className = "" }: { className?: string }) {
  return (
    <div className={`my-8 flex justify-center ${className}`}>
      <a
        href="https://zodiak.lagitren.id/?utm_source=lagitren&utm_medium=promo&utm_campaign=rasi"
        aria-label="Rasi — Ramalanmu hari ini: tarot, zodiak & shio dari tanggal lahirmu"
        className="block w-full max-w-[320px] md:max-w-[728px]"
      >
        <picture>
          <source media="(min-width: 768px)" srcSet="/promo/rasi-wide.png" width={728} height={90} />
          <img
            src="/promo/rasi-mobile.png"
            width={320}
            height={100}
            alt="Rasi — Ramalanmu hari ini. Tarot, zodiak & shio dari tanggal lahirmu."
            loading="lazy"
            decoding="async"
            className="h-auto w-full rounded-xl"
          />
        </picture>
      </a>
    </div>
  );
}
