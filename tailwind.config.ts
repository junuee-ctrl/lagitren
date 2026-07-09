import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}"
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: "#FF6B00",
          dark: "#E85D00"
        },
        ink: "#111827",
        surface: "#F9FAFB",
        google: "#4285F4",
        youtube: "#FF0000",
        tiktok: "#010101",
        instagram: "#E4405F",
        shopee: "#EE4D2D",
        twitter: "#000000"
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"]
      },
      maxWidth: {
        content: "1120px"
      }
    }
  },
  plugins: []
};

export default config;
