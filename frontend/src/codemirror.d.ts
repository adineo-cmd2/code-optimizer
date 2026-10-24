// Shorthand ambient declarations for the OPTIONAL CodeMirror 6 packages.
// The registry install was attempted; on failure the editor stays a plain
// textarea (see CodeEditor.tsx). These keep `astro check` green either way.
declare module '@codemirror/view';
declare module '@codemirror/state';
declare module '@codemirror/lang-python';
declare module '@codemirror/lang-javascript';
