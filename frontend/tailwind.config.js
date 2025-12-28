/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        glass: {
          border: 'rgba(255, 255, 255, 0.6)',
          bg: 'rgba(255, 255, 255, 0.4)',
          light: 'rgba(255, 255, 255, 0.6)',
        },
      },
      backdropBlur: {
        xs: '2px',
      },
      animation: {
        'blob': 'blob 20s infinite',
        'blob-slow': 'blob 25s infinite',
        'slide-up': 'slideUp 0.3s ease-out',
        'dots': 'dots 1.4s infinite',
      },
      keyframes: {
        blob: {
          '0%, 100%': { 
            transform: 'translate(0px, 0px) scale(1)',
          },
          '33%': { 
            transform: 'translate(30px, -50px) scale(1.05)',
          },
          '66%': { 
            transform: 'translate(-20px, 20px) scale(0.95)',
          },
        },
        slideUp: {
          '0%': { 
            opacity: '0',
            transform: 'translateY(10px)',
          },
          '100%': { 
            opacity: '1',
            transform: 'translateY(0)',
          },
        },
        dots: {
          '0%, 20%': { content: '"."' },
          '40%': { content: '".."' },
          '60%, 100%': { content: '"..."' },
        },
      },
    },
  },
  plugins: [],
}
