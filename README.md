# Market Phase Detector

Monthly Taiwan and US market-cycle dashboard built with a conservative, explainable phase engine.

## Current Scope

- Taiwan and US monthly phase detection
- Conservative state transitions
- Static dashboard output
- GitHub Actions monthly automation

## Local Development

```bash
pip install -e .
pytest -v
python -m market_phase_detector.cli
```

The sample CLI writes `data/latest.json` and builds a deployable static site into `dist/`.

## Deployment Direction

- Run the monthly pipeline in GitHub Actions
- Publish the frontend as a static site on Cloudflare Pages
- Replace the sample CLI payload with live collectors as the next step
