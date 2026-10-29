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
    case 'critical': return 'badge-critical';
    case 'high': return 'badge-high';
    case 'medium': return 'badge-medium';
    default: return 'badge-low';
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

  if (err) return <p className="error-text">{err}</p>;
  if (sid == null) return <p className="muted">Loading…</p>;

  const hotspotRows: Hotspot[] =
    hotspots.length > 0
      ? hotspots
      : bottlenecks.map((b) => ({ function: b.function, priority: b.priority, predicted_ms: b.predicted_ms }));

  return (
    <div className="space-y-6">
      <div>
        <p className="report-id">
          Session #{sid}{language ? ` · ${language}` : ''}
        </p>
        <h3 className="report-label">Hotspots</h3>
        {hotspotRows.length === 0 && <p className="muted">No hotspots detected.</p>}
        <ul className="hotspot-list">
          {hotspotRows.map((h, i) => {
            return (
              <li key={i} className="hotspot-row">
                <span className="hotspot-name">{h.function ?? `hotspot ${i + 1}`}</span>
                <span className={`badge ${badge(h.priority ?? h.severity ?? '')}`}>
                  {h.priority ?? h.severity ?? 'low'}
                </span>
                {h.predicted_ms != null && (
                  <span className="hotspot-ms">~{Math.round(h.predicted_ms)}ms est.</span>
                )}
                {(h.signals ?? []).length > 0 && (
                  <span className="hotspot-signals">{(h.signals ?? []).join('; ')}</span>
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
        <h3 className="report-label">Bottlenecks ({bottlenecks.length})</h3>
        {bottlenecks.length === 0 && <p className="muted">No bottlenecks — code looks clean.</p>}
        <div>
          {bottlenecks.map((b) => (
            <div key={b.id} className="bottleneck">
              <div className="bottleneck-head">
                <span className="bottleneck-name">{b.function}</span>
                <span className={`badge ${badge(b.priority)}`}>{b.priority}</span>
                <span className="hotspot-ms">~{Math.round(b.predicted_ms)}ms est.</span>
              </div>
              <p className="bottleneck-cause">{b.root_cause}</p>
              {b.snippet && (
                <pre className="code-inset">{b.snippet}</pre>
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
