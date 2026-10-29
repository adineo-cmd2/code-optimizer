import { useEffect, useRef, useState } from 'react';
import { apiPost } from '../lib/apiClient';
const BASE = (import.meta.env.BASE_URL ?? '/').replace(/\/$/, '');

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
      window.location.href = `${BASE}/analysis?sid=${res.session_id}`;
    } catch (e2) {
      setErr(e2 instanceof Error ? e2.message : 'Submit failed.');
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={submit} className="run-form">
      <div ref={cmHost} className={cmUpgraded.current ? '' : 'hidden'} />
      {!cmUpgraded.current && (
        <textarea
          value={code}
          onChange={(e) => setCode(e.target.value)}
          rows={14}
          spellCheck={false}
          placeholder="Paste code to profile…"
          aria-label="Code to profile"
          className="code-input w-full"
        />
      )}
      {cmUpgraded.current && (
        <textarea
          value={code}
          onChange={(e) => setCode(e.target.value)}
          rows={4}
          spellCheck={false}
          aria-label="Code fallback"
          className="code-fallback w-full"
        />
      )}
      <div className="grid">
        <label>Language
          <select value={language} onChange={(e) => setLanguage(e.target.value)}
            className="input mt-1">
            <option value="python">python</option>
            <option value="javascript">javascript</option>
          </select>
        </label>
        <label>Traffic (e.g. 1000 concurrent)
          <input value={traffic} onChange={(e) => setTraffic(e.target.value)}
            placeholder="1000 concurrent"
            className="input mt-1" />
        </label>
        <label>Data volume (e.g. 1M rows)
          <input value={dataVolume} onChange={(e) => setDataVolume(e.target.value)}
            placeholder="1M rows"
            className="input mt-1" />
        </label>
        <label>Input size (e.g. n=10000)
          <input value={inputSize} onChange={(e) => setInputSize(e.target.value)}
            placeholder="n=10000"
            className="input mt-1" />
        </label>
      </div>
      {err && <p className="error-text" role="alert">{err}</p>}
      <button type="submit" disabled={busy} className="btn btn-accent run-submit">
        {busy ? 'Profiling…' : 'Profile & optimize'}
      </button>
    </form>
  );
}
