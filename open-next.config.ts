import { defineCloudflareConfig } from "@opennextjs/cloudflare";

// Konfigurasi OpenNext untuk menjalankan Next.js di Cloudflare.
// Default sudah cukup untuk situs ISR/SSR dengan binding D1.
export default defineCloudflareConfig({
  // incrementalCache, tagCache, dll. bisa ditambahkan di sini bila perlu.
});
