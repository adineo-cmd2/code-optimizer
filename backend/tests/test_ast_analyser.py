from app.services.ast_analyser import analyse
from app.services.profiler import profile


SLOW_CODE = (
    "def process(items):\n"
    "    out = []\n"
    "    for x in items:\n"
    "        for y in x:\n"
    "            out.append(y)\n"
    "    return out\n"
)

CLEAN_CODE = "def add(a, b):\n    return a + b\n"


def test_nested_append_loop_detected():
    analysis = analyse(SLOW_CODE, "python")
    fns = {f["name"]: f for f in analysis["functions"]}
    assert "process" in fns
    fn = fns["process"]
    assert fn["loop_depth"] == 2
    assert "nested_loop" in fn["signals"]
    assert fn["big_o"] == "O(n^2)"

    hotspots = profile(analysis)
    assert len(hotspots) >= 1
    assert hotspots[0]["function"] == "process"
    assert "nested_loop" in hotspots[0]["signals"]


def test_clean_function_has_no_signals():
    analysis = analyse(CLEAN_CODE, "python")
    fns = {f["name"]: f for f in analysis["functions"]}
    assert "add" in fns
    assert fns["add"]["signals"] == []

    assert profile(analysis) == []
