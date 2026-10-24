from app.services.bottleneck_predictor import parse_scale, predict


def _hotspot(signals, loop_depth=2):
    return {
        "function": "process",
        "signals": signals,
        "complexity": 5,
        "big_o": "O(n^2)",
        "loop_depth": loop_depth,
        "snippet": "for x in items:\n    for y in x:\n        out.append(y)",
    }


def test_big_scale_is_critical():
    scale = parse_scale({"traffic": "1000 concurrent", "input_size": "1M rows"})
    assert scale == 1000 * 1_000_000
    hotspots = [_hotspot(["io_in_loop", "nested_loop"], loop_depth=3)]
    preds = predict(hotspots, 1_000_000)
    assert len(preds) == 1
    assert preds[0]["priority"] == "critical"
    assert preds[0]["predicted_ms"] >= 500


def test_tiny_scale_is_low():
    preds = predict([_hotspot(["broad_except"], loop_depth=0)], 1)
    assert len(preds) == 1
    assert preds[0]["priority"] == "low"


def test_empty_hotspots_give_empty_predictions():
    assert predict([], 1_000_000) == []
