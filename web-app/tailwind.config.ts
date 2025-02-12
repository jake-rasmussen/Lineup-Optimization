import { type Config } from "tailwindcss";
import { fontFamily } from "tailwindcss/defaultTheme";
import { heroui } from "@heroui/react";

export default {
  content: [
    "./src/**/*.tsx",
    "./node_modules/@heroui/theme/dist/**/*.{js,ts,jsx,tsx}"
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["var(--font-poppins)", ...fontFamily.sans],
      },
    },
  },
  plugins: [heroui()],
} satisfies Config;