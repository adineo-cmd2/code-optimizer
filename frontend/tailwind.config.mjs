/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        editordark: '#0d1117',
        editorpanel: '#161b22',
        editoredge: '#30363d',
        optgreen: '#3fb950',
        optamber: '#d29922',
        optred: '#f85149',
        inksoft: '#8b949e',
      },
      fontFamily: {
        mono: ['ui-monospace', 'SFMono-Regular', 'Menlo', 'Consolas', 'monospace'],
      },
    },
  },
  plugins: [],
};
