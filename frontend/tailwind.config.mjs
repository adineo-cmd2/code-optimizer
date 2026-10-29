/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        // Measurement-lab mapping for the existing utility names.
        // editordark is used as a code-surface tint; text-editordark sits on
        // cobalt buttons. Both resolve to a warm paper value on this light UI.
        editordark: '#e9e6dc',
        editorpanel: '#fbfaf6',
        editoredge: '#d6d3ca',
        optgreen: '#1d4ed8',
        optamber: '#8a5a00',
        optred: '#b93c0a',
        inksoft: '#5f6368',
        zinc: {
          100: '#17181a',
          300: '#3b3d40',
          400: '#5f6368',
        },
      },
      fontFamily: {
        display: ["'Bricolage Grotesque'", 'system-ui', 'sans-serif'],
        body: ["'IBM Plex Sans'", 'system-ui', 'sans-serif'],
        mono: ["'IBM Plex Mono'", 'ui-monospace', 'monospace'],
      },
    },
  },
  plugins: [],
};
