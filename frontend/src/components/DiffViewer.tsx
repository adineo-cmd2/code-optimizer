import { useEffect, useState } from 'react';
import { apiGet } from '../lib/apiClient';

function lineClass(line: string): string {
  if (line.startsWith('+') && !line.startsWith('+++')) return 'bg-optgreen/10 text-optgreen';
  if (line.startsWith('-') && !line.startsWith('---')) return 'bg-optred/10 text-optred';
  if (line.startsWith('@@')) return 'text-optamber';
  return 'text-zinc-300';
}

export default function DiffViewer({ sessionId, variant }: { sessionId: number; variant: string }) {
  const [diff, setDiff] = useState<string | null>(null);
  const [err, setErr] = useState('');

  useEffect(() => {
    let live = true;
    (async () => {
      try {
        const allowed = ['speed', 'memory', 'balanced'];
        const v = allowed.includes(variant) ? variant : 'balanced';
        const res = await apiGet(`/api/optimize/${sessionId}/diff?variant=${v}`);
        if (live) setDiff(res.diff ?? '');
      } catch (e) {
        if (live) setErr(e instanceof Error ? e.message : 'Diff load failed.');
      }
    })();
    return () => { live = false; };
  }, [sessionId, variant]);

  if (err) return <p className="text-sm text-optred">{err}</p>;
  if (diff == null) return <p className="text-sm text-inksoft">Loading diff…</p>;
  if (!diff.trim()) return <p className="text-sm text-inksoft">No differences — variant matches the original.</p>;
  return (
    <pre className="overflow-x-auto border border-editoredge bg-editorpanel p-3 font-mono text-xs leading-5">
      {diff.split('\n').map((line, i) => (
        <div key={i} className={lineClass(line)}>{line || ' '}</div>
      ))}
    </pre>
  );
}
