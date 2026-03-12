/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './**/templates/**/*.html',
  ],
  theme: {
    extend: {
      fontFamily: {
        typewriter: ['"Courier Prime"', 'monospace'],
      },
    }
  },
  plugins: [],
}
