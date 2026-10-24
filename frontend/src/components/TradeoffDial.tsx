import { useState } from 'react';
import { apiPost } from '../lib/apiClient';

// Stateless tradeoff dial. The backend apply endpoint is stateless: it maps
// the three 0-10 weights to a single kind (speed|memory|balanced). The diff
// page selects ONLY via ?variant=, so we surface an explicit link carrying
// the winning kind — never anything else.
export default function TradeoffDial({ sessionId }: { sessionId: number }) {
  const [speed, setSpeed] = useState(5);
  const [memory, setMemory] = useState(5);
  const [readability, setReadability] = useState(5);
  const [kind, setKind] = useState<string | null>(null);
  const [err, setErr] = useState('');
  const [busy, setBusy] = useState(false);

  async function apply() {
    setErr('');
    setBusy(true);
    try {
      const res = await apiPost(`/api/optimize/${sessionId}/apply`, {
        speed, memory, readability,
      });
      const vals: string[] = Object.values(res.selections ?? {});
      const allowed = ['speed', 'memory', 'balanced'];
      const win = allowed.includes(vals[0]) ? vals[0] : 'balanced';
      setKind(win);
    } catch (e) {
      setErr(e instanceof Error ? e.message : 'Apply failed.');
    } finally {
      setBusy(false);
    }
  }

  function slider(label: string, v: number, set: (n: number) => void) {
    return (
      <label className="block text-xs">{label}: {v}
        <input type="range" min={0} max={10} value={v}
          onChange={(e) => set(Number(e.target.value))}
          className="w-full" />
      </label>
    );
  }

  return (
    <div className="border border-editoredge bg-editorpanel p-4">
      <h3 className="text-sm font-bold text-optgreen">Tradeoff dial</h3>
      <div className="mt-2 space-y-2">
        {slider('speed', speed, setSpeed)}
        {slider('memory', memory, setMemory)}
        {slider('readability', readability, setReadability)}
      </div>
      {err && <p className="mt-2 text-xs text-optred">{err}</p>}
      <button onClick={apply} disabled={busy}
        className="mt-3 bg-optgreen px-4 py-1 text-sm font-bold text-editordark disabled:opacity-50">
        {busy ? 'Selecting…' : 'Apply tradeoff'}
      </button>
      {kind && (
        <p className="mt-3 text-sm">
          Selection: <span className="font-bold text-optgreen">{kind}</span>{' '}
          <a className="underline" href={`/diff?sid=${sessionId}&variant=${kind}`}>
            View diff ({kind})
          </a>
        </p>
      )}
    </div>
  );
}
