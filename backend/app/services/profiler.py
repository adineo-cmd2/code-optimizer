"""Rank analysed functions into hotspots (most expensive first)."""


def profile(analysis: dict) -> list:
    fns = (analysis or {}).get("functions", [])
    hot = [f for f in fns if f.get("signals")]
    hot.sort(key=lambda f: (-f.get("complexity", 0), f.get("name", "")))
    return [{"function": f["name"], "signals": list(f.get("signals", [])),
             "complexity": f.get("complexity", 1), "big_o": f.get("big_o", "O(1)"),
             "loop_depth": f.get("loop_depth", 0),
             "snippet": f.get("snippet", "")} for f in hot]
