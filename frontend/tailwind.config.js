/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        eoc: {
          darkest: '#070b12',
          panel: '#0d131f',
          surface: '#131b2c',
          border: '#1f2b40',
          accent: '#00f0ff',
          danger: '#ef4444',
          warning: '#f59e0b',
          success: '#10b981',
          info: '#3b82f6',
        },
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'glow-cyan': '0 0 15px -3px rgba(0, 240, 255, 0.3)',
        'glow-danger': '0 0 15px -3px rgba(239, 68, 68, 0.4)',
        'glow-success': '0 0 15px -3px rgba(16, 185, 129, 0.4)',
      },
    },
  },
  plugins: [],
}
