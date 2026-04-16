import json
from pathlib import Path


def test_latest_payload_exposes_meta_source():
    payload = json.loads(Path("data/latest.json").read_text(encoding="utf-8"))

    assert "meta" in payload
    assert "source" in payload["meta"]


def test_frontend_modules_reference_meta_and_observations():
    app_script = Path("frontend/src/app.js").read_text(encoding="utf-8")
    shared_script = Path("frontend/src/pages/shared.js").read_text(encoding="utf-8")
    country_script = Path("frontend/src/pages/renderCountry.js").read_text(encoding="utf-8")

    assert "site-content.json" in app_script
    assert "payload.meta" in shared_script
    assert "country.observations" in country_script


def test_readme_mentions_github_pages_hosting():
    readme = Path("README.md").read_text(encoding="utf-8")

    assert "Cloudflare Pages" in readme


def test_frontend_modules_reference_history_timeline():
    country_script = Path("frontend/src/pages/renderCountry.js").read_text(encoding="utf-8")

    assert "lens-history-slider" in country_script
    assert "history-table" in country_script


def test_frontend_modules_mentions_interpretive_lenses():
    app_script = Path("frontend/src/app.js").read_text(encoding="utf-8")
    landing_script = Path("frontend/src/pages/renderLanding.js").read_text(encoding="utf-8")
    country_script = Path("frontend/src/pages/renderCountry.js").read_text(encoding="utf-8")
    lens_components = Path("frontend/src/domain/lens.js").read_text(encoding="utf-8")

    assert "buildLanding" in landing_script
    assert "renderCountryPage" in app_script
    assert "buildLensRow" in country_script
    assert "renderTransposedMetricTable" in lens_components
    assert "transition-driver" in lens_components
    assert "decision_summary" in lens_components
