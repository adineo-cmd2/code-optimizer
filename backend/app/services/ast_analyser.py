"""Static code analysis. NEVER executes submitted code (ast + regex only)."""

import ast
import re

IO_NAMES = {"query", "execute", "fetch", "fetchall", "fetchone", "request",
            "get", "post", "put", "open", "read", "write", "save", "delete",
            "axios", "find", "findOne", "save"}

JS_LOOP_RE = re.compile(r"\b(for|while)\s*\(|\.forEach\s*\(|\.map\s*\(")
JS_FUNC_RE = re.compile(r"function\s+([A-Za-z_$][\w$]*)\s*\([^)]*\)\s*\{")
JS_IO_RE = re.compile(r"\b(fetch|axios|query|execute|\bfs\.|document\.|localStorage)\b")


class _PyVisitor(ast.NodeVisitor):
    def __init__(self):
        self.functions = []
        self.imports = []
        self._stack = []

    def visit_FunctionDef(self, node):
        self._stack.append(node)
        info = {"node": node, "name": node.name, "lineno": node.lineno,
                "complexity": 1, "loop_depth": 0, "max_depth": 0,
                "signals": set(), "has_self_call": False}
        self.functions.append(info)
        self.generic_visit(node)
        self._stack.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    def _depth(self):
        return sum(1 for _ in self._walk_loops())

    def _walk_loops(self):
        return []

    def _current(self):
        return self.functions[-1] if self.functions else None

    def _loop_enter(self, node):
        # recompute max depth by walking from enclosing function
        fn = self._stack[-1] if self._stack else None
        if fn is None:
            return
        info = next(f for f in self.functions if f["node"] is fn)
        depth = self._nesting(fn, node)
        info["max_depth"] = max(info["max_depth"], depth)
        if depth >= 2:
            info["signals"].add("nested_loop")

    def _nesting(self, fn, target):
        best = 1

        def walk(node, depth):
            nonlocal best
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.For, ast.AsyncFor, ast.While)):
                    if child is target or self._contains(child, target):
                        best = max(best, depth + 1)
                    walk(child, depth + 1)
                else:
                    walk(child, depth)

        walk(fn, 0)
        return best

    def _contains(self, node, target):
        return any(child is target or self._contains(child, target)
                   for child in ast.iter_child_nodes(node))

    def visit_For(self, node):
        self._loop_enter(node)
        self.generic_visit(node)

    def visit_AsyncFor(self, node):
        self._loop_enter(node)
        self.generic_visit(node)

    def visit_While(self, node):
        self._loop_enter(node)
        self.generic_visit(node)

    def visit_If(self, node):
        cur = self._current()
        if cur is not None and self._stack and cur["node"] is self._stack[-1]:
            cur["complexity"] += 1
        self.generic_visit(node)

    def visit_ExceptHandler(self, node):
        cur = self._current()
        if cur is not None and self._stack and cur["node"] is self._stack[-1]:
            cur["complexity"] += 1
            if node.type is None or (isinstance(node.type, ast.Name) and node.type.id in ("Exception", "BaseException")):
                cur["signals"].add("broad_except")
        self.generic_visit(node)

    def visit_BoolOp(self, node):
        cur = self._current()
        if cur is not None and self._stack and cur["node"] is self._stack[-1]:
            cur["complexity"] += 1
        self.generic_visit(node)

    def visit_Call(self, node):
        cur = self._current()
        name = ""
        if isinstance(node.func, ast.Name):
            name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            name = node.func.attr
        if cur is not None and self._stack and cur["node"] is self._stack[-1]:
            if name in ("sort", "sorted"):
                cur["signals"].add("sort_call")
            if self._stack and name == self._stack[-1].name:
                cur["signals"].add("recursion")
        self.generic_visit(node)

    def visit_Import(self, node):
        for a in node.names:
            self.imports.append(a.name.split(".")[0])

    def visit_ImportFrom(self, node):
        if node.module:
            self.imports.append(node.module.split(".")[0])


def _in_loop(tree, node):
    """Check whether node sits inside a loop (for IO-in-loop detection)."""
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            if isinstance(parent, (ast.For, ast.AsyncFor, ast.While)) and (
                    child is node or any(c is node for c in ast.walk(child))):
                return True
    return False


def _analyse_python(code: str) -> dict:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return {"functions": [], "imports": [], "call_edges": [],
                "parse_error": True}
    vis = _PyVisitor()
    vis.visit(tree)
    functions = []
    for f in vis.functions:
        node = f["node"]
        signals = set(f["signals"])
        # IO / membership / concat inside loops; recursion already flagged
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                fname = ""
                if isinstance(child.func, ast.Name):
                    fname = child.func.id
                elif isinstance(child.func, ast.Attribute):
                    fname = child.func.attr
                if fname in IO_NAMES and _in_loop(node, child):
                    signals.add("io_in_loop")
            if isinstance(child, ast.Compare) and any(
                    isinstance(op, ast.In) for op in child.ops):
                if _in_loop(node, child):
                    signals.add("membership_in_loop")
            if isinstance(child, ast.AugAssign) and isinstance(child.op, ast.Add):
                if _in_loop(node, child):
                    signals.add("string_concat")
        depth = f["max_depth"]
        if "sort_call" in signals and depth == 0:
            big_o = "O(n log n)"
        elif depth == 0:
            big_o = "O(1)"
        elif depth == 1:
            big_o = "O(n)"
        else:
            big_o = f"O(n^{depth})"
        try:
            snippet = ast.get_source_segment(code, node) or ""
        except Exception:
            snippet = ""
        functions.append({"name": f["name"], "lineno": f["lineno"],
                          "complexity": f["complexity"], "loop_depth": depth,
                          "big_o": big_o, "signals": sorted(signals),
                          "snippet": snippet[:800]})
    edges = []
    names = {f["name"] for f in functions}
    for f in functions:
        node = next(x["node"] for x in vis.functions if x["name"] == f["name"])
        for child in ast.walk(node):
            if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                if child.func.id in names and child.func.id != f["name"]:
                    edges.append({"from": f["name"], "to": child.func.id})
    return {"functions": functions, "imports": sorted(set(vis.imports)),
            "call_edges": edges}


def _analyse_javascript(code: str) -> dict:
    functions = []
    for m in JS_FUNC_RE.finditer(code):
        name, start = m.group(1), m.start()
        depth = 0
        end = len(code)
        for i in range(m.end() - 1, len(code)):
            if code[i] == "{":
                depth += 1
            elif code[i] == "}":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        body = code[start:end]
        # Nesting depth: brace depth at each loop keyword (1 = function
        # body level, so one loop -> 1, nested loop -> 2+).
        loop_depth = 0
        for m in re.finditer(r"\b(for|while)\s*\(|\.forEach\s*\(|\.map\s*\(", body):
            depth = 0
            for ch in body[:m.start()]:
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
            loop_depth = max(loop_depth, depth)
        signals = []
        if loop_depth >= 2:
            signals.append("nested_loop")
        if JS_IO_RE.search(body) and loop_depth >= 1:
            signals.append("io_in_loop")
        if re.search(r"\.push\s*\(", body) and loop_depth >= 1:
            signals.append("append_loop")
        if re.search(r"\.indexOf\s*\(", body) and loop_depth >= 1:
            signals.append("membership_in_loop")
        big_o = "O(1)" if loop_depth == 0 else ("O(n)" if loop_depth == 1 else f"O(n^{loop_depth})")
        functions.append({"name": name, "lineno": code[:start].count("\n") + 1,
                          "complexity": 1 + body.count("if(") + body.count("if ("),
                          "loop_depth": loop_depth, "big_o": big_o,
                          "signals": signals, "snippet": body[:800]})
    return {"functions": functions, "imports": [], "call_edges": []}


def _analyse_generic(code: str) -> dict:
    loops = len(re.findall(r"\b(for|while|loop)\b", code))
    signals = ["nested_loop"] if loops >= 2 else (["loop"] if loops else [])
    return {"functions": [{"name": "main", "lineno": 1,
                           "complexity": 1 + loops, "loop_depth": min(loops, 2),
                           "big_o": "O(n)" if loops else "O(1)",
                           "signals": signals, "snippet": code[:800]}],
            "imports": [], "call_edges": []}


def analyse(code: str, language: str) -> dict:
    lang = (language or "").lower()
    if lang in ("python", "py"):
        return _analyse_python(code or "")
    if lang in ("javascript", "js", "jsx", "ts", "typescript"):
        return _analyse_javascript(code or "")
    return _analyse_generic(code or "")
