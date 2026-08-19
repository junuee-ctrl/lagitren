/** Identitas penerbit — satu sumber untuk E-E-A-T (P1-2). */

export const SITE_URL =
  process.env.NEXT_PUBLIC_SITE_URL ?? "https://lagitren.id";

export const SITE_NAME = "Lagi Tren";
export const CONTACT_EMAIL = "keyframe.jakarta@gmail.com";
export const SITE_LOCATION = "Jakarta, Indonesia";

/** Penerbit konten — tim redaksi (bukan persona fiktif; transparan soal AI). */
export const AUTHOR_NAME = "Tim Redaksi Lagitren";
export const AUTHOR_ROLE = "Redaksi & Kurasi Data Tren";
export const AUTHOR_URL = `${SITE_URL}/redaksi`;

/** JSON-LD Organization — dipasang di seluruh situs (layout). */
export function organizationJsonLd() {
  return {
    "@context": "https://schema.org",
    "@type": "Organization",
    "@id": `${SITE_URL}/#organization`,
    name: SITE_NAME,
    url: SITE_URL,
    logo: {
      "@type": "ImageObject",
      url: `${SITE_URL}/icon.png`,
      width: 512,
      height: 512
    },
    email: CONTACT_EMAIL,
    address: {
      "@type": "PostalAddress",
      addressLocality: "Jakarta",
      addressCountry: "ID"
    }
  };
}

/** Ref publisher/author untuk NewsArticle. */
export function publisherRef() {
  return {
    "@type": "Organization",
    name: SITE_NAME,
    url: SITE_URL,
    logo: {
      "@type": "ImageObject",
      url: `${SITE_URL}/icon.png`,
      width: 512,
      height: 512
    }
  };
}

export function authorRef() {
  return { "@type": "Organization", name: AUTHOR_NAME, url: AUTHOR_URL };
}

/** ISO 8601 dari nilai collected_at D1 ("YYYY-MM-DD HH:MM:SS" UTC). */
export function toIso(value?: string): string | undefined {
  if (!value) return undefined;
  const d = new Date(value.includes("T") ? value : value.replace(" ", "T") + "Z");
  return Number.isNaN(d.getTime()) ? undefined : d.toISOString();
}
