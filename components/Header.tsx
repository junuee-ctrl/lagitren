import Link from "next/link";
import { PLATFORM_ORDER, PLATFORMS, platformHref } from "@/lib/platforms";
import ThemeToggle from "./ThemeToggle";
import PlatformIcon from "./PlatformIcon";
import Logo from "./Logo";

export default function Header() {
  return (
    <header className="sticky top-0 z-40 border-b border-gray-200/80 bg-white/80 backdrop-blur-md dark:border-white/10 dark:bg-night/80">
      <div className="container-page flex h-16 items-center justify-between gap-3">
        <Link href="/" className="shrink-0" aria-label="Lagi Tren — beranda">
          <Logo textClass="text-lg sm:text-xl" />
        </Link>

        <nav
          aria-label="Platform"
          className="hidden items-center gap-0.5 lg:flex"
        >
          {PLATFORM_ORDER.map((key) => {
            const p = PLATFORMS[key];
            return (
              <Link
                key={key}
                href={platformHref(key)}
                className="inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-sm font-medium text-gray-600 transition hover:bg-gray-100 hover:text-ink dark:text-gray-300 dark:hover:bg-white/10 dark:hover:text-white"
              >
                <PlatformIcon platform={key} className="h-4 w-4" />
                {p.name.split(" ")[0]}
              </Link>
            );
          })}
        </nav>

        <div className="flex items-center gap-2">
          <ThemeToggle />
          <Link href="/#google" className="btn-brand lg:hidden">
            Lihat Tren
          </Link>
        </div>
      </div>
    </header>
  );
}
