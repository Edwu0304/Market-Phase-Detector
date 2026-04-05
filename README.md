# Market Phase Detector

Monthly Taiwan and US strategy-map site with one site phase plus three independent author lenses.

## Current Scope

- Taiwan and US monthly phase detection
- Three master lenses with independent monthly sliders
- Real metric values for each lens history row
- Static multi-page dashboard output
- Cloudflare Pages deployment

## Local Development

```bash
pip install -e .
pytest -v
python -m market_phase_detector.cli
```

The CLI regenerates `data/latest.json`, `data/history`, `data/site-content.json`, and a deployable static site in `dist/`.

## Deployment Direction

- Generate the latest snapshot locally or in CI
- Publish the `dist/` directory to Cloudflare Pages
- The deployed site serves `/`, `/tw/`, and `/us/` with three-lens panels and independent history sliders
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
- Every country payload includes `lenses.izaax`, `lenses.urakami`, and `lenses.marks`
- Each lens bundle includes a current snapshot, real metric values, and its own monthly history series

## Static Pages

- `/` is the strategy-map landing page
- `/tw/` is the Taiwan three-lens map
- `/us/` is the United States three-lens map
