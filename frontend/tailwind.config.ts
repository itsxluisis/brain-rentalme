import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        surface: {
          DEFAULT: "rgba(255, 255, 255, 0.05)",
          hover: "rgba(255, 255, 255, 0.08)",
          border: "rgba(255, 255, 255, 0.07)",
        },
        accent: {
          DEFAULT: "#3B82F6",
          hover: "#2563EB",
          soft: "#60A5FA",
        },
        background: {
          start: "#080c14",
          end: "#0f1521",
        },
        region: {
          asturias: "#14B8A6",
          madrid: "#F59E0B",
          malaga: "#F97316",
          "costa-brava": "#06B6D4",
          ibiza: "#EC4899",
          "la-manga": "#10B981",
        },
      },
      borderRadius: {
        card: "16px",
        input: "12px",
        sm: "8px",
      },
      backdropBlur: {
        glass: "16px",
      },
      boxShadow: {
        glow: "0 0 20px rgba(59, 130, 246, 0.12)",
      },
      fontFamily: {
        mono: ["JetBrains Mono", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
