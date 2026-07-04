/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/**/*.{js,ts,jsx,tsx}", "./components/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        void: "#0A0E12",
        panel: "#12181F",
        panel2: "#161D26",
        hairline: "#232C36",
        ink: "#E7EDF2",
        muted: "#8A98A6",
        cyan: "#35D0C4",
        bleeding: "#E5484D",
        ischemia: "#F5A340",
        normal: "#3FB950",
      },
      fontFamily: {
        display: ["var(--font-display)"],
        body: ["var(--font-body)"],
        mono: ["var(--font-mono)"],
      },
    },
  },
  plugins: [],
};
