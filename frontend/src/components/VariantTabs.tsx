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
      <div className="variant-tabs" role="group" aria-label="Variant selection">
        {KINDS.map((k) => (
          <button
            key={k}
            type="button"
            onClick={() => setTab(k)}
            aria-pressed={tab === k}
            className={'tab' + (tab === k ? ' active' : '')}
          >
            {k}
          </button>
        ))}
      </div>
      {active ? (
        <div className="variant-body">
          <pre className="variant-code">{active.code}</pre>
          <p className="variant-meta">
            complexity {active.complexity} · readability {active.readability}/10
          </p>
          <p className="variant-explanation">{active.explanation}</p>
        </div>
      ) : (
        <p className="warn-text">No variants for this bottleneck.</p>
      )}
    </div>
  );
}
