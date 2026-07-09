import Link from "next/link";
import { PLATFORM_ORDER, PLATFORMS } from "@/lib/platforms";

export default function Header() {
  return (
    <header className="sticky top-0 z-40 border-b border-gray-200 bg-white/90 backdrop-blur">
      <div className="container-page flex h-16 items-center justify-between gap-4">
        <Link href="/" className="flex items-center gap-2">
          <span className="text-2xl" aria-hidden>
            🔥
          </span>
          <span className="text-xl font-extrabold tracking-tight">
            Lagi <span className="text-brand">Tren</span>
          </span>
        </Link>

        <nav
          aria-label="Platform"
          className="hidden items-center gap-1 md:flex"
        >
          {PLATFORM_ORDER.map((key) => {
            const p = PLATFORMS[key];
            return (
              <Link
                key={key}
                href={`/${key}`}
                className="rounded-full px-3 py-1.5 text-sm font-medium text-gray-600 transition hover:bg-surface hover:text-ink"
              >
                <span className="mr-1" aria-hidden>
                  {p.icon}
                </span>
                {p.name.split(" ")[0]}
              </Link>
            );
          })}
        </nav>

        <Link href="/#google" className="btn-brand md:hidden">
          Lihat Tren
        </Link>
      </div>
    </header>
  );
}
