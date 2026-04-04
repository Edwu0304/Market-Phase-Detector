from pathlib import Path


def test_wrangler_toml_has_pages_output_dir():
    config = Path("wrangler.toml").read_text(encoding="utf-8")

    assert 'pages_build_output_dir = "dist"' in config


def test_readme_mentions_cloudflare_pages():
    readme = Path("README.md").read_text(encoding="utf-8")

    assert "Cloudflare Pages" in readme
    assert "npx wrangler pages deploy dist --project-name market-phase-detector" in readme
