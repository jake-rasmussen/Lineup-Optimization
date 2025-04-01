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
    animation: {
      scroll: 'scroll var(--animation-duration, 40s) var(--animation-direction, forwards) linear infinite',
    },
    keyframes: {
      scroll: {
        to: {
          transform: 'translate(calc(-50% - 0.5rem))',
        },
      },
    },
  },
  plugins: [heroui()],
} satisfies Config;