import Link from "next/link";
import { PLATFORM_ORDER, PLATFORMS } from "@/lib/platforms";
import ThemeToggle from "./ThemeToggle";

export default function Header() {
  return (
    <header className="sticky top-0 z-40 border-b border-gray-200/80 bg-white/80 backdrop-blur-md dark:border-white/10 dark:bg-night/80">
      <div className="container-page flex h-16 items-center justify-between gap-3">
        <Link href="/" className="flex shrink-0 items-center gap-2">
          <span
            className="grid h-9 w-9 place-items-center rounded-xl bg-gradient-to-br from-brand to-accent text-lg shadow-sm shadow-brand/30"
            aria-hidden
          >
            🔥
          </span>
          <span className="text-xl font-extrabold tracking-tight">
            Lagi{" "}
            <span className="bg-gradient-to-r from-brand to-accent bg-clip-text text-transparent">
              Tren
            </span>
          </span>
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
                href={`/${key}`}
                className="rounded-full px-3 py-1.5 text-sm font-medium text-gray-600 transition hover:bg-gray-100 hover:text-ink dark:text-gray-300 dark:hover:bg-white/10 dark:hover:text-white"
              >
                <span className="mr-1" aria-hidden>
                  {p.icon}
                </span>
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
