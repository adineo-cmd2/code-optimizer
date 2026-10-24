/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        "editordark": "#0d1117",
        "editorpanel": "#161b22",
        "editoredge": "#2b323b",
        "optgreen": "#3fb950",
        "optamber": "#d29922",
        "optred": "#f85149",
        "inksoft": "#93a1ad"
},
      fontFamily: {
        "display": [
                "'Space Grotesk'",
                "system-ui",
                "sans-serif"
        ],
        "body": [
                "'JetBrains Mono'",
                "ui-monospace",
                "monospace"
        ],
        "mono": [
                "'JetBrains Mono'",
                "ui-monospace",
                "monospace"
        ]
},
    },
  },
  plugins: [],
};
