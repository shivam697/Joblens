/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      // Custom color palette — dark premium design system
      colors: {
        app: '#0F172A',       // Main dark background (slate-950)
        card: '#1E293B',      // Card backgrounds (slate-900)
        'input-bg': '#0F172A', // Input field backgrounds
        primary: {
          DEFAULT: '#6366F1',  // Indigo-500 — buttons, active links
          hover: '#4F46E5',    // Indigo-600 — button hover
          light: '#818CF8',    // Indigo-400 — subtle highlights
        },
        accent: '#8B5CF6',    // Violet-500 — score ring, highlights
        success: '#10B981',   // Emerald-500 — offered, matched
        warning: '#F59E0B',   // Amber-500 — screening, missing keywords
        danger: '#F43F5E',    // Rose-500 — rejected, errors
      },
      // Typography — Sora for headings, DM Sans for body
      fontFamily: {
        display: ['Sora', 'sans-serif'],
        body: ['DM Sans', 'sans-serif'],
      },
      // Smooth border radius for cards and inputs
      borderRadius: {
        '2xl': '1rem',
        '3xl': '1.5rem',
      },
    },
  },
  plugins: [],
}
