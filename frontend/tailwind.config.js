/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#ebf5fb',
          100: '#d4ebf8',
          200: '#a9d7f1',
          300: '#7ec3ea',
          400: '#53afe3',
          500: '#3498db',
          600: '#2980b9',
          700: '#1e6a97',
          800: '#145375',
          900: '#093d54',
        },
        secondary: {
          50: '#e8f8f0',
          100: '#d1f1e1',
          200: '#a3e4c3',
          300: '#75d6a5',
          400: '#47c987',
          500: '#2ecc71',
          600: '#27ae60',
          700: '#1e8e4f',
          800: '#166e3e',
          900: '#0e4f2d',
        },
        slate: {
          750: '#3b4a5c',
          850: '#1e2a38',
        },
      },
      fontFamily: {
        system: ['-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'sans-serif'],
        serif: ['Georgia', 'Cambria', 'Times New Roman', 'serif'],
        rounded: ['Nunito', 'Quicksand', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
