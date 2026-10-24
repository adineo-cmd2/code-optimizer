import { useEffect, useState } from 'react';
import { apiGet } from '../lib/apiClient';
import VariantTabs, { type Variant } from './VariantTabs';
import TradeoffDial from './TradeoffDial';
import CallGraph from './CallGraph';

interface Bottleneck {
  id: number;
  function: string;
  root_cause: string;
  predicted_ms: number;
  priority: string;
  snippet: string;
}

interface Hotspot {
  function?: string;
  signals?: string[];
  severity?: string;
  priority?: string;
  predicted_ms?: number;
}

function badge(priority: string): string {
  switch ((priority ?? '').toLowerCase()) {
    case 'critical': return 'border-optred bg-optred/10 text-optred';
    case 'high': return 'border-optamber bg-optamber/10 text-optamber';
    case 'medium': return 'border-optgreen bg-optgreen/10 text-optgreen';
    default: return 'border-editoredge text-inksoft';
  }
}

export default function AnalysisView() {
  const [sid, setSid] = useState<number | null>(null);
  const [language, setLanguage] = useState('');
  const [bottlenecks, setBottlenecks] = useState<Bottleneck[]>([]);
  const [variants, setVariants] = useState<Variant[]>([]);
  const [hotspots, setHotspots] = useState<Hotspot[]>([]);
  const [err, setErr] = useState('');

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const id = Number(params.get('sid'));
    if (!id) { setErr('Missing ?sid=. Submit code first.'); return; }
    setSid(id);
    try {
      const raw = window.sessionStorage.getItem(`opt-hotspots-${id}`);
      if (raw) setHotspots(JSON.parse(raw));
    } catch { /* optional */ }
    (async () => {
      try {
        const res = await apiGet(`/api/optimize/${id}`);
        setLanguage(res.language ?? '');
        setBottlenecks(res.bottlenecks ?? []);
        setVariants(res.variants ?? []);
      } catch (e) {
        setErr(e instanceof Error ? e.message : 'Load failed. Sign in via Settings first.');
      }
    })();
  }, []);

  if (err) return <p className="text-sm text-optred">{err}</p>;
  if (sid == null) return <p className="text-sm text-inksoft">Loading…</p>;

  const hotspotRows: Hotspot[] =
    hotspots.length > 0
      ? hotspots
      : bottlenecks.map((b) => ({ function: b.function, priority: b.priority, predicted_ms: b.predicted_ms }));

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-sm font-bold text-optgreen">
          Session #{sid}{language ? ` · ${language}` : ''}
        </h2>
        <h3 className="mt-3 text-sm font-bold">Hotspots</h3>
        {hotspotRows.length === 0 && <p className="text-sm text-inksoft">No hotspots detected.</p>}
        <ul className="mt-2 space-y-2">
          {hotspotRows.map((h, i) => {
            return (
              <li key={i} className="flex flex-wrap items-center gap-2 border border-editoredge bg-editorpanel px-3 py-2 text-sm">
                <span className="font-bold">{h.function ?? `hotspot ${i + 1}`}</span>
                <span className={`border px-2 py-0.5 text-xs ${badge(h.priority ?? h.severity ?? '')}`}>
                  {h.priority ?? h.severity ?? 'low'}
                </span>
                {h.predicted_ms != null && (
                  <span className="text-xs text-inksoft">~{Math.round(h.predicted_ms)}ms est.</span>
                )}
                {(h.signals ?? []).length > 0 && (
                  <span className="w-full text-xs text-inksoft">{(h.signals ?? []).join('; ')}</span>
                )}
              </li>
            );
          })}
        </ul>
        <div className="mt-3">
          <CallGraph nodes={hotspotRows.map((h) => ({
            function: h.function ?? '?',
            predicted_ms: h.predicted_ms,
            priority: h.priority ?? h.severity,
          }))} />
        </div>
      </div>

      <div>
        <h3 className="text-sm font-bold">Bottlenecks ({bottlenecks.length})</h3>
        {bottlenecks.length === 0 && <p className="mt-2 text-sm text-inksoft">No bottlenecks — code looks clean.</p>}
        <div className="mt-2 space-y-4">
          {bottlenecks.map((b) => (
            <div key={b.id} className="border border-editoredge bg-editorpanel p-4">
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-bold">{b.function}</span>
                <span className={`border px-2 py-0.5 text-xs ${badge(b.priority)}`}>{b.priority}</span>
                <span className="text-xs text-inksoft">~{Math.round(b.predicted_ms)}ms est.</span>
              </div>
              <p className="mt-2 text-xs text-zinc-300">{b.root_cause}</p>
              {b.snippet && (
                <pre className="mt-2 overflow-x-auto whitespace-pre-wrap border border-editoredge bg-editordark p-2 font-mono text-xs text-zinc-400">{b.snippet}</pre>
              )}
              <VariantTabs variants={variants.filter((v) => v.bottleneck_id === b.id)} />
            </div>
          ))}
        </div>
      </div>

      <TradeoffDial sessionId={sid} />
    </div>
  );
}
