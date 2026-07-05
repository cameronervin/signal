# Run Evals

Use `.agents/loops/eval-calibration.loop.md`.

```bash
cd backend
uv run pytest tests/test_lead_pipeline.py -v
```

Add broader eval commands here when the eval suite grows beyond fixture-backed
pipeline checks.
