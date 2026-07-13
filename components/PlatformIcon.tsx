import {
  SiGoogle,
  SiYoutube,
  SiTiktok,
  SiInstagram,
  SiNetflix,
  SiShopee,
  SiX
} from "react-icons/si";
import type { IconType } from "react-icons";
import type { Platform } from "@/lib/types";
import { PLATFORMS } from "@/lib/platforms";

const ICONS: Record<Platform, IconType> = {
  google: SiGoogle,
  youtube: SiYoutube,
  tiktok: SiTiktok,
  instagram: SiInstagram,
  netflix: SiNetflix,
  shopee: SiShopee,
  twitter: SiX
};

// Brand yang (nyaris) hitam → pakai warna adaptif tema agar tetap terlihat.
const DARKISH = new Set<Platform>(["tiktok", "twitter"]);

/**
 * Logo brand resmi tiap platform (SVG).
 * - `mono`: render dengan currentColor (mis. putih di atas hero berwarna).
 * - default: warna brand; tiktok/X pakai warna teks adaptif (light/dark).
 */
export default function PlatformIcon({
  platform,
  className = "h-4 w-4",
  mono = false
}: {
  platform: Platform;
  className?: string;
  mono?: boolean;
}) {
  const Icon = ICONS[platform];
  if (!Icon) return null;
  if (mono) return <Icon className={className} aria-hidden />;
  if (DARKISH.has(platform)) {
    return (
      <Icon
        className={`text-gray-800 dark:text-gray-100 ${className}`}
        aria-hidden
      />
    );
  }
  return (
    <Icon
      className={className}
      style={{ color: PLATFORMS[platform].color }}
      aria-hidden
    />
  );
}
