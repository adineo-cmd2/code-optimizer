import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient

from app.db.session import Base, engine
from app.main import app

SLOW_CODE = (
    "def process(items):\n"
    "    result = []\n"
    "    for i in items:\n"
    "        for j in items:\n"
    "            result.append(i * j)\n"
    "    return result\n"
)


def test_api_smoke():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    c = TestClient(app)
    assert c.get("/healthz").json() == {"ok": True}

    r = c.post(
        "/api/optimize/submit",
        json={
            "code": SLOW_CODE,
            "language": "python",
            "traffic": "1000 concurrent",
            "data_volume": "",
            "input_size": "1M rows",
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    sid = body["session_id"]
    assert len(body["bottlenecks"]) >= 1

    r = c.get(f"/api/optimize/{sid}")
    assert r.status_code == 200, r.text
    detail = r.json()
    first_bn = detail["bottlenecks"][0]
    first_variants = [v for v in detail["variants"] if v.get("bottleneck_id") == first_bn["id"]]
    assert len(first_variants) == 3

    r = c.post(f"/api/optimize/{sid}/apply", json={"speed": 10})
    assert r.status_code == 200, r.text
    selections = r.json()["selections"]
    assert selections
    assert all(kind in ("speed", "memory", "balanced") for kind in selections.values())

    r = c.get(f"/api/optimize/{sid}/diff", params={"variant": "balanced"})
    assert r.status_code == 200, r.text
    diff = r.json()["diff"]
    assert "\n+" in diff and "\n-" in diff
