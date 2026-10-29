import { useEffect, useState } from 'react';
import { apiGet } from '../lib/apiClient';

function lineClass(line: string): string {
  if (line.startsWith('+') && !line.startsWith('+++')) return 'diff-add';
  if (line.startsWith('-') && !line.startsWith('---')) return 'diff-del';
  if (line.startsWith('@@')) return 'diff-hunk';
  return 'diff-ctx';
}

export default function DiffViewer({ sessionId, variant }: { sessionId: number; variant: string }) {
  const [diff, setDiff] = useState<string | null>(null);
  const [err, setErr] = useState('');

  useEffect(() => {
    let live = true;
    (async () => {
      try {
        const allowed = ['speed', 'memory', 'balanced'];
        // The route is statically built, so query values are resolved again on
        // the client. Server-provided props win when a real session id exists.
        const params = new URLSearchParams(window.location.search);
        const querySid = Number(params.get('sid'));
        const effectiveId = sessionId > 0 ? sessionId : querySid;
        const rawVariant = sessionId > 0 ? variant : (params.get('variant') ?? variant);
        const v = allowed.includes(rawVariant) ? rawVariant : 'balanced';
        if (!Number.isFinite(effectiveId) || effectiveId <= 0) {
          if (live) setErr('Missing ?sid=. Open an analysis first, then follow its diff link.');
          return;
        }
        const res = await apiGet(`/api/optimize/${effectiveId}/diff?variant=${v}`);
        if (live) setDiff(res.diff ?? '');
      } catch (e) {
        if (live) setErr(e instanceof Error ? e.message : 'Diff load failed.');
      }
    })();
    return () => { live = false; };
  }, [sessionId, variant]);

  if (err) return <p className="error-text">{err}</p>;
  if (diff == null) return <p className="muted">Loading diff…</p>;
  if (!diff.trim()) return <p className="muted">No differences — variant matches the original.</p>;
  return (
    <pre className="diff-view" aria-label="Unified diff">
      {diff.split('\n').map((line, i) => (
        <span key={i} className={`diff-line ${lineClass(line)}`}>{line || ' '}</span>
      ))}
    </pre>
  );
}
