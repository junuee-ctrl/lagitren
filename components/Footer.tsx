import Link from "next/link";
import { PLATFORM_ORDER, PLATFORMS, platformHref } from "@/lib/platforms";
import PlatformIcon from "./PlatformIcon";
import Logo from "./Logo";

const LEGAL = [
  { href: "/arsip", label: "Arsip Tren" },
  { href: "/about", label: "Tentang Kami" },
  { href: "/contact", label: "Kontak" },
  { href: "/privacy", label: "Kebijakan Privasi" },
  { href: "/disclaimer", label: "Disclaimer" },
  { href: "/affiliate", label: "Afiliasi" }
];

export default function Footer() {
  return (
    <footer className="mt-14 border-t border-gray-200 bg-white dark:border-white/10 dark:bg-night-card">
      <div className="container-page grid gap-8 py-10 sm:grid-cols-3">
        <div>
          <Logo textClass="text-lg" />
          <p className="mt-3 max-w-xs text-sm text-gray-500 dark:text-gray-400">
            Rekomendasi, review, dan info terbaru yang lagi tren di Indonesia —
            dari berbagai platform, dalam satu halaman.
          </p>
        </div>

        <div>
          <h3 className="text-sm font-semibold text-ink dark:text-white">
            Platform
          </h3>
          <ul className="mt-3 space-y-2 text-sm">
            {PLATFORM_ORDER.map((key) => (
              <li key={key}>
                <Link
                  href={platformHref(key)}
                  className="link-quiet inline-flex items-center gap-2"
                >
                  <PlatformIcon platform={key} className="h-3.5 w-3.5" />
                  {PLATFORMS[key].name}
                </Link>
              </li>
            ))}
          </ul>
        </div>

        <div>
          <h3 className="text-sm font-semibold text-ink dark:text-white">
            Informasi
          </h3>
          <ul className="mt-3 space-y-2 text-sm">
            {LEGAL.map((l) => (
              <li key={l.href}>
                <Link href={l.href} className="link-quiet">
                  {l.label}
                </Link>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="border-t border-gray-100 dark:border-white/10">
        <div className="container-page flex flex-col items-center justify-between gap-2 py-4 text-xs text-gray-400 dark:text-gray-500 sm:flex-row">
          <p>© 2026 Lagi Tren. Semua tren milik platform masing-masing.</p>
          <p>lagitren.id</p>
        </div>
      </div>
    </footer>
  );
}
