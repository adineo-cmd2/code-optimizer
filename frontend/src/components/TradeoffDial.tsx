import { useState } from 'react';
import { apiPost } from '../lib/apiClient';

const BASE = (import.meta.env.BASE_URL ?? '/').replace(/\/$/, '');

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
      <label className="slider-row">{label}: {v}
        <input type="range" min={0} max={10} value={v}
          onChange={(e) => set(Number(e.target.value))}
          className="w-full" />
      </label>
    );
  }

  return (
    <div className="dial-panel">
      <h3 className="panel-title">Tradeoff dial</h3>
      <div className="slider-stack">
        {slider('speed', speed, setSpeed)}
        {slider('memory', memory, setMemory)}
        {slider('readability', readability, setReadability)}
      </div>
      {err && <p className="error-text mt-2">{err}</p>}
      <button onClick={apply} disabled={busy} className="btn btn-accent btn-sm mt-3">
        {busy ? 'Selecting…' : 'Apply tradeoff'}
      </button>
      {kind && (
        <p className="dial-result">
          Selection: <strong>{kind}</strong>{' '}
          <a href={`${BASE}/diff?sid=${sessionId}&variant=${kind}`}>
            View diff ({kind})
          </a>
        </p>
      )}
    </div>
  );
}
