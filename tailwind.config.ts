import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}"
  ],
  theme: {
    extend: {
      colors: {
        // Warna brand mengikuti logo: magenta + teal.
        brand: {
          DEFAULT: "#E6007A",
          dark: "#C60068",
          light: "#FF3DA6"
        },
        accent: {
          DEFAULT: "#00C9B1", // teal dari logo
          grape: "#8B3DD6" // ungu jembatan untuk gradasi
        },
        ink: "#111827",
        surface: "#F7F7FB",
        // permukaan gelap
        night: {
          DEFAULT: "#0E0F13",
          card: "#191A20",
          soft: "#22242C"
        },
        google: "#4285F4",
        youtube: "#FF0000",
        tiktok: "#010101",
        instagram: "#E4405F",
        shopee: "#EE4D2D",
        twitter: "#000000",
        netflix: "#E50914"
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"]
      },
      maxWidth: {
        content: "1120px"
      },
      keyframes: {
        "float-slow": {
          "0%,100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-10px)" }
        },
        "pop-in": {
          "0%": { opacity: "0", transform: "translateY(8px) scale(.98)" },
          "100%": { opacity: "1", transform: "translateY(0) scale(1)" }
        }
      },
      animation: {
        "float-slow": "float-slow 6s ease-in-out infinite",
        "pop-in": "pop-in .4s ease-out both"
      }
    }
  },
  plugins: []
};

export default config;
