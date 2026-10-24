"""Rule-based variant generation. Honest no-transform fallback, LLM hook."""

import os
import re


def _no_transform(snippet: str) -> dict:
    return {
        "speed": {"code": snippet, "time_complexity": "same",
                  "space_complexity": "same", "readability": 5,
                  "explanation": "No safe rule transform matched this pattern; "
                                 "review manually before changing."},
        "memory": {"code": snippet, "time_complexity": "same",
                   "space_complexity": "same", "readability": 5,
                   "explanation": "No safe rule transform matched this pattern; "
                                  "review manually before changing."},
        "balanced": {"code": snippet, "time_complexity": "same",
                     "space_complexity": "same", "readability": 5,
                     "explanation": "No safe rule transform matched this pattern; "
                                    "review manually before changing."},
    }


_APPEND_LOOP_RE = re.compile(
    r"for\s+(\w+)\s+in\s+([^:]+):\s*\n((?:[ \t]+.*\n?)+)")
_IN_LIST_RE = re.compile(r"if\s+(.+?)\s+in\s+(\w+)\s*:")
_CONCAT_LOOP_RE = re.compile(r"for\s+(\w+)\s+in\s+([^:]+):\s*\n((?:[ \t]+.*\n?)+)")
_JS_PUSH_RE = re.compile(r"for\s*\([^;]*;[^;]*;[^)]*\)\s*\{\s*(\w+)\.push\(([^)]+)\)", re.DOTALL)


def _append_chain(snippet: str) -> tuple | None:
    """Find TARGET.append(EXPR) with enclosing for-chain outermost-first.

    Returns (target, expr, [(var, iterable), ...]) or None.
    """
    lines = (snippet or "").splitlines()
    for i, line in enumerate(lines):
        m = re.match(r"(\s+)(\w+)\.append\((.+)\)\s*$", line)
        if not m:
            continue
        indent, target, expr = len(m.group(1)), m.group(2), m.group(3).strip()
        chain: list = []
        level = indent
        for j in range(i - 1, -1, -1):
            fm = re.match(r"(\s*)for\s+(\w+)\s+in\s+([^:]+):\s*$", lines[j])
            if fm and len(fm.group(1)) < level:
                chain.append((fm.group(2), fm.group(3).strip()))
                level = len(fm.group(1))
        if chain:
            chain.reverse()
            return target, expr, chain
    return None


def _python_variants(snippet: str, signal: str) -> dict | None:
    if "append_loop" in signal or "nested_loop" in signal:
        found = _append_chain(snippet)
        if found:
            target, expr, chain = found
            clauses = " ".join(f"for {v} in {it}" for v, it in chain)
            speed = f"{target} = [{expr} {clauses}]"
            memory = (f"{target} = ({expr} {clauses})"
                      f"  # generator: constant memory, iterate once")
            balanced = (f"# Flattened with a comprehension (was a nested loop)\n"
                        f"{target} = [{expr} {clauses}]")
            return {
                "speed": {"code": speed, "time_complexity": "O(n)",
                          "space_complexity": "O(n)", "readability": 4,
                          "explanation": "List comprehension removes append "
                                         "overhead and runs in C."},
                "memory": {"code": memory, "time_complexity": "O(n)",
                           "space_complexity": "O(1)", "readability": 3,
                           "explanation": "Generator avoids materialising "
                                          "the list; use if consumed once."},
                "balanced": {"code": balanced, "time_complexity": "O(n)",
                             "space_complexity": "O(n)", "readability": 5,
                             "explanation": "Comprehension with a comment "
                                            "explaining the change."},
            }
    if "membership" in signal:
        m = _IN_LIST_RE.search(snippet)
        if m:
            val, lst = m.group(1).strip(), m.group(2).strip()
            conv = f"{lst}_set = set({lst})  # build once, outside the loop"
            return {
                "speed": {"code": f"{conv}\nif {val} in {lst}_set:",
                          "time_complexity": "O(1) lookup",
                          "space_complexity": "O(n) set", "readability": 4,
                          "explanation": "Set membership is O(1) vs O(n) scan."},
                "memory": {"code": f"{conv}\nif {val} in {lst}_set:",
                           "time_complexity": "O(1) lookup",
                           "space_complexity": "O(n) set", "readability": 4,
                           "explanation": "Same set approach; frees the list "
                                          "if no longer needed."},
                "balanced": {"code": f"# O(1) membership via a precomputed set\n{conv}\nif {val} in {lst}_set:",
                             "time_complexity": "O(1) lookup",
                             "space_complexity": "O(n) set", "readability": 5,
                             "explanation": "Commented set conversion."},
            }
    if "concat" in signal or "string_concat" in signal:
        m = _CONCAT_LOOP_RE.search(snippet)
        if m:
            var, iterable = m.group(1), m.group(2).strip()
            return {
                "speed": {"code": f"result = ''.join(str({var}) for {var} in {iterable})",
                          "time_complexity": "O(n)", "space_complexity": "O(n)",
                          "readability": 4,
                          "explanation": "join avoids quadratic reallocation of +=."},
                "memory": {"code": "import io\nbuf = io.StringIO()\n"
                                   f"for {var} in {iterable}:\n    buf.write(str({var}))\nresult = buf.getvalue()",
                           "time_complexity": "O(n)", "space_complexity": "O(n)",
                           "readability": 3,
                           "explanation": "StringIO streams chunks without copies."},
                "balanced": {"code": f"# join() instead of += in a loop\nresult = ''.join(str({var}) for {var} in {iterable})",
                             "time_complexity": "O(n)", "space_complexity": "O(n)",
                             "readability": 5,
                             "explanation": "Idiomatic join with a comment."},
            }
    return None


def _js_variants(snippet: str, signal: str) -> dict | None:
    m = _JS_PUSH_RE.search(snippet)
    if m:
        arr, expr = m.group(1), m.group(2).strip()
        return {
            "speed": {"code": f"const {arr} = source.map(x => {expr});",
                      "time_complexity": "O(n)", "space_complexity": "O(n)",
                      "readability": 4,
                      "explanation": "map replaces manual push loop."},
            "memory": {"code": f"function* gen() {{ for (const x of source) yield {expr}; }}",
                       "time_complexity": "O(n)", "space_complexity": "O(1)",
                       "readability": 3,
                       "explanation": "Generator streams values lazily."},
            "balanced": {"code": f"// map() instead of a push loop\nconst {arr} = source.map(x => {expr});",
                         "time_complexity": "O(n)", "space_complexity": "O(n)",
                         "readability": 5,
                         "explanation": "Commented map version."},
        }
    if "membership" in signal and ".indexOf(" in snippet:
        return {
            "speed": {"code": snippet.replace(".indexOf(", ".indexOf(") + "\n// → precompute: const seen = new Set(list); seen.has(x)",
                      "time_complexity": "O(1) lookup", "space_complexity": "O(n)",
                      "readability": 4,
                      "explanation": "Set.has is O(1) vs indexOf O(n) scan."},
            "memory": {"code": snippet, "time_complexity": "same",
                       "space_complexity": "same", "readability": 5,
                       "explanation": "No safe automatic rewrite; use a Set manually."},
            "balanced": {"code": snippet, "time_complexity": "same",
                         "space_complexity": "same", "readability": 5,
                         "explanation": "No safe automatic rewrite; use a Set manually."},
        }
    return None


def variants(snippet: str, signal: str, language: str) -> dict:
    """Return {speed, memory, balanced} variant dicts."""
    lang = (language or "").lower()
    out = None
    if lang in ("python", "py"):
        out = _python_variants(snippet or "", signal or "")
    elif lang in ("javascript", "js", "jsx", "ts", "typescript"):
        out = _js_variants(snippet or "", signal or "")
    if out is None:
        out = _no_transform(snippet or "")
    if os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY"):
        # LLM rewrite hook: v1 keeps rule output for determinism.
        pass
    return out
