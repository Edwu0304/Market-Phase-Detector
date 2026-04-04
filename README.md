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
- Publish the frontend as a static site on GitHub Pages
- The site is hosted by GitHub, so it remains reachable from your phone and does not depend on your local machine being on

## GitHub Pages Setup

1. In the repository settings, open `Pages`.
2. Set the build source to `GitHub Actions`.
3. Trigger the `Monthly Market Update` workflow manually once, or push a new commit.
4. After the workflow finishes, GitHub Pages will expose a public HTTPS URL for the `dist/` site.

The workflow already:

- runs tests
- generates the latest live snapshot
- builds `dist/`
- deploys `dist/` to GitHub Pages
