# Market Phase Detector

Monthly Taiwan and US market-cycle dashboard built with a conservative, explainable phase engine.

## Current Scope

- Taiwan and US monthly phase detection
- Conservative state transitions
- Static dashboard output
- Cloudflare Pages deployment

## Local Development

```bash
pip install -e .
pytest -v
python -m market_phase_detector.cli
```

The sample CLI writes `data/latest.json` and builds a deployable static site into `dist/`.

## Deployment Direction

- Generate the latest snapshot locally or in CI
- Publish the `dist/` directory to Cloudflare Pages
- The site remains reachable from your phone and does not depend on your local machine being on once deployed

## Cloudflare Pages Setup

1. Log in with Wrangler:

```bash
npx wrangler login
```

2. Build the latest static output:

```bash
python -m market_phase_detector.cli
```

3. Deploy the site:

```bash
npx wrangler pages deploy dist --project-name market-phase-detector
```

## GitHub Actions Secrets

If you want the monthly workflow to deploy to Cloudflare automatically, add these GitHub repository secrets:

- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_ACCOUNT_ID`

## Cloudflare Config

- `wrangler.toml` declares `pages_build_output_dir = "dist"`
- `dist/` includes the landing page, Taiwan page, United States page, and `data/history`

## Static Pages

- `/` is the unified cycle-map landing page
- `/tw/` is the Taiwan strategy manual
- `/us/` is the United States strategy manual
