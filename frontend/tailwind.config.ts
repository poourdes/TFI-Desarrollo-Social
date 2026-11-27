import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        muni: {
          navy: "#0B2D52",
          celeste: "#00A6D6",
          "celeste-claro": "#E6F6FC",
          sol: "#F2B705",
        },
        brand: {
          50: "#E6F6FC",
          100: "#CDEEF9",
          200: "#9BDDF2",
          600: "#0095C0",
          700: "#00A6D6",
          800: "#0B2D52",
          900: "#08223D",
        },
        sand: {
          50: "#F7FBFD",
          100: "#F1F5F9",
          200: "#E2E8F0",
        },
      },
      boxShadow: {
        soft: "0 8px 30px rgba(11, 45, 82, 0.08)",
      },
    },
  },
  plugins: [],
} satisfies Config;
