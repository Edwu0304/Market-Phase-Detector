from pathlib import Path


def test_wrangler_config_supports_pages_assets():
    config = Path("wrangler.toml").read_text(encoding="utf-8")

    assert 'name = "market-phase-detector"' in config
    assert "pages_build_output_dir" in config
