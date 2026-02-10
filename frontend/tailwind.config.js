/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class', // Enable class-based dark mode
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#007AFF',
        danger: '#FF3B30',
        warning: '#FF9500',
        success: '#34C759',
        background: {
          light: '#F5F5F7',
          dark: '#000000',
        },
      },
    },
  },
  plugins: [],
}
