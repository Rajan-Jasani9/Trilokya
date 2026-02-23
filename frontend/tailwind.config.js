/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f6f6',
          100: '#d9eaea',
          200: '#b3d4d4',
          300: '#8cbfbf',
          400: '#4f9797',
          500: '#1f8a8a', // Accent Muted Teal
          600: '#146c6c', // Primary Teal
          700: '#0f4c4c', // Primary Dark Teal
          800: '#0b3b3b',
          900: '#072626',
        },
        shell: {
          background: '#F4F6F7',
          border: '#D9E2E2',
        },
        trl: {
          low: '#C44536',     // 1–3 high risk
          mid: '#D4A017',     // 4–6 moderate
          high: '#2E7D32',    // 7–9 mature
          neutral: '#9E9E9E', // not assessed
          track: '#E5ECEC',
        },
      },
      screens: {
        'sm': '640px',
        'md': '768px',
        'lg': '1024px',
        'xl': '1280px',
        '2xl': '1536px',
      },
    },
  },
  plugins: [],
}
