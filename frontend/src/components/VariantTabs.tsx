import { useState } from 'react';

export interface Variant {
  id: number;
  bottleneck_id?: number | null;
  kind: string;
  code: string;
  complexity: string;
  readability: number;
  explanation: string;
}

const KINDS = ['speed', 'memory', 'balanced'] as const;

export default function VariantTabs({ variants }: { variants: Variant[] }) {
  const [tab, setTab] = useState<string>('balanced');
  const byKind = new Map(variants.map((v) => [v.kind, v]));
  const active = byKind.get(tab) ?? variants[0];

  return (
    <div className="mt-2">
      <div className="flex gap-2">
        {KINDS.map((k) => (
          <button
            key={k}
            type="button"
            onClick={() => setTab(k)}
            className={
              'border px-3 py-0.5 text-xs ' +
              (tab === k
                ? 'border-optgreen bg-optgreen/10 text-optgreen'
                : 'border-editoredge text-zinc-400')
            }
          >
            {k}
          </button>
        ))}
      </div>
      {active ? (
        <div className="mt-2 border border-editoredge bg-editordark p-3">
          <pre className="overflow-x-auto whitespace-pre-wrap font-mono text-xs text-zinc-100">{active.code}</pre>
          <p className="mt-2 text-xs text-inksoft">
            complexity {active.complexity} · readability {active.readability}/10
          </p>
          <p className="mt-1 text-xs text-zinc-300">{active.explanation}</p>
        </div>
      ) : (
        <p className="mt-2 text-xs text-optamber">No variants for this bottleneck.</p>
      )}
    </div>
  );
}
