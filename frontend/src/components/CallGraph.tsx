export interface GraphNode {
  function: string;
  predicted_ms?: number;
  priority?: string;
}

function color(priority?: string): string {
  switch ((priority ?? '').toLowerCase()) {
    case 'critical': return '#f85149';
    case 'high': return '#d29922';
    case 'medium': return '#3fb950';
    default: return '#8b949e';
  }
}

// Dependency-free SVG call graph: one node per hotspot/bottleneck function,
// sized by predicted_ms, coloured by priority. Purely presentational.
export default function CallGraph({ nodes }: { nodes: GraphNode[] }) {
  if (!nodes.length) return <p className="text-sm text-inksoft">No hotspots to graph.</p>;
  const W = Math.max(320, nodes.length * 140);
  const H = 160;
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full border border-editoredge bg-editorpanel" role="img" aria-label="Call graph">
      {nodes.slice(1).map((_, i) => {
        const x1 = 70 + i * 140 + 30;
        const x2 = 70 + (i + 1) * 140 - 30;
        return <line key={`e${i}`} x1={x1} y1={H / 2} x2={x2} y2={H / 2} stroke="#30363d" strokeWidth={2} />;
      })}
      {nodes.map((n, i) => {
        const cx = 70 + i * 140;
        const cy = H / 2;
        const r = 22 + Math.min(26, Math.log10((n.predicted_ms ?? 1) + 10) * 10);
        return (
          <g key={i}>
            <circle cx={cx} cy={cy} r={r} fill="#0d1117" stroke={color(n.priority)} strokeWidth={2} />
            <text x={cx} y={cy + 4} textAnchor="middle" fill="#e6edf3" fontSize={11} fontFamily="monospace">
              {n.function.slice(0, 12)}
            </text>
            <text x={cx} y={cy + r + 16} textAnchor="middle" fill="#8b949e" fontSize={10} fontFamily="monospace">
              {n.predicted_ms != null ? `${Math.round(n.predicted_ms)}ms` : n.priority ?? ''}
            </text>
          </g>
        );
      })}
    </svg>
  );
}
