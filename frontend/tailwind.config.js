/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        deal: {
          great: "#10b981",
          good: "#3b82f6",
          fair: "#f59e0b",
          overpriced: "#ef4444",
        },
      },
    },
  },
  plugins: [],
};
