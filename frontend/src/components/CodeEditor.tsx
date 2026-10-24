import { useEffect, useRef, useState } from 'react';
import { apiPost } from '../lib/apiClient';

// Textarea-first editor. CodeMirror 6 is attempted only as a progressive
// enhancement: if @codemirror/* packages are installed cleanly the editor
// upgrades in place, otherwise the plain textarea remains fully functional.
export default function CodeEditor() {
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('python');
  const [traffic, setTraffic] = useState('');
  const [dataVolume, setDataVolume] = useState('');
  const [inputSize, setInputSize] = useState('');
  const [err, setErr] = useState('');
  const [busy, setBusy] = useState(false);
  const cmHost = useRef<HTMLDivElement | null>(null);
  const cmUpgraded = useRef(false);

  // Optional CodeMirror upgrade — safe no-op when packages are absent.
  useEffect(() => {
    let cancelled = false;
    let view: { destroy(): void } | null = null;
    (async () => {
      if (cmUpgraded.current || !cmHost.current) return;
      try {
        // Optional packages (@codemirror/*). The registry install was
        // attempted and failed, so these resolve only if a user adds them
        // later. Non-literal specifiers + @vite-ignore keep Rollup from
        // resolving at build time; the try/catch keeps the textarea.
        const mod = (p: string) => import(/* @vite-ignore */ p);
        const [cmView, cmState, langPy, langJs] = await Promise.all([
          mod('@codemirror/' + 'view'),
          mod('@codemirror/' + 'state'),
          mod('@codemirror/' + 'lang-python'),
          mod('@codemirror/' + 'lang-javascript'),
        ]);
        if (cancelled || !cmHost.current) return;
        const lang = language === 'javascript' ? langJs.javascript() : langPy.python();
        const state = cmState.EditorState.create({
          doc: code,
          extensions: [
            lang,
            cmView.EditorView.updateListener.of((u: { docChanged: boolean; state: { doc: { toString(): string } } }) => {
              if (u.docChanged) setCode(u.state.doc.toString());
            }),
          ],
        });
        view = new cmView.EditorView({ state, parent: cmHost.current });
        cmUpgraded.current = true;
      } catch {
        // Packages not installed — keep the textarea.
      }
    })();
    return () => {
      cancelled = true;
      try { view?.destroy(); } catch { /* noop */ }
    };
    // Only attempt upgrade once on mount.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setErr('');
    if (!code.trim()) { setErr('Code required.'); return; }
    setBusy(true);
    try {
      const res = await apiPost('/api/optimize/submit', {
        code, language, traffic, data_volume: dataVolume, input_size: inputSize,
      });
      try {
        window.sessionStorage.setItem(
          `opt-hotspots-${res.session_id}`,
          JSON.stringify(res.hotspots ?? []),
        );
      } catch { /* storage optional */ }
      window.location.href = `/analysis?sid=${res.session_id}`;
    } catch (e2) {
      setErr(e2 instanceof Error ? e2.message : 'Submit failed.');
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={submit} className="space-y-3">
      <div ref={cmHost} className={cmUpgraded.current ? '' : 'hidden'} />
      {!cmUpgraded.current && (
        <textarea
          value={code}
          onChange={(e) => setCode(e.target.value)}
          rows={14}
          spellCheck={false}
          placeholder="Paste code to profile…"
          className="w-full border border-editoredge bg-editorpanel p-3 font-mono text-sm text-zinc-100"
        />
      )}
      {cmUpgraded.current && (
        <textarea
          value={code}
          onChange={(e) => setCode(e.target.value)}
          rows={4}
          spellCheck={false}
          aria-label="Code fallback"
          className="w-full border border-editoredge bg-editorpanel p-3 font-mono text-sm text-zinc-100"
        />
      )}
      <div className="grid grid-cols-2 gap-3">
        <label className="text-sm">Language
          <select value={language} onChange={(e) => setLanguage(e.target.value)}
            className="mt-1 w-full border border-editoredge bg-editorpanel p-2 text-sm">
            <option value="python">python</option>
            <option value="javascript">javascript</option>
          </select>
        </label>
        <label className="text-sm">Traffic (e.g. 1000 concurrent)
          <input value={traffic} onChange={(e) => setTraffic(e.target.value)}
            placeholder="1000 concurrent"
            className="mt-1 w-full border border-editoredge bg-editorpanel p-2 text-sm" />
        </label>
        <label className="text-sm">Data volume (e.g. 1M rows)
          <input value={dataVolume} onChange={(e) => setDataVolume(e.target.value)}
            placeholder="1M rows"
            className="mt-1 w-full border border-editoredge bg-editorpanel p-2 text-sm" />
        </label>
        <label className="text-sm">Input size (e.g. n=10000)
          <input value={inputSize} onChange={(e) => setInputSize(e.target.value)}
            placeholder="n=10000"
            className="mt-1 w-full border border-editoredge bg-editorpanel p-2 text-sm" />
        </label>
      </div>
      {err && <p className="text-sm text-optred">{err}</p>}
      <button disabled={busy} className="bg-optgreen px-4 py-1 text-sm font-bold text-editordark disabled:opacity-50">
        {busy ? 'Profiling…' : 'Profile & optimize'}
      </button>
    </form>
  );
}
