# Latency-Aware AI Code Optimizer — backend

Run from `backend/`:

```bash
pip install -r requirements.txt
cp .env.example .env   # optional; works with no keys (rule-based engine)
python3 -m uvicorn app.main:app --port 8008
```

Static analysis only — submitted code is never executed.
Tests: `python3 -m pytest tests/ -v` (7 tests).
