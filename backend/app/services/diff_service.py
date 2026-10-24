"""Unified diffs (stdlib difflib)."""

import difflib


def unified(original: str, new: str, name: str = "code") -> str:
    a = (original or "").splitlines(keepends=True)
    b = (new or "").splitlines(keepends=True)
    return "".join(difflib.unified_diff(a, b, fromfile=f"a/{name}", tofile=f"b/{name}"))
