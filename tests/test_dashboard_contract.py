import json
from pathlib import Path


def test_latest_payload_exposes_meta_source():
    payload = json.loads(Path("data/latest.json").read_text(encoding="utf-8"))

    assert "meta" in payload
    assert "source" in payload["meta"]


def test_frontend_script_references_meta_and_observations():
    script = Path("frontend/src/app.js").read_text(encoding="utf-8")

    assert "payload.meta" in script
    assert "country.observations" in script


def test_readme_mentions_github_pages_hosting():
    readme = Path("README.md").read_text(encoding="utf-8")

    assert "GitHub Pages" in readme


def test_frontend_script_references_history_timeline():
    script = Path("frontend/src/app.js").read_text(encoding="utf-8")

    assert "history/index.json" in script
    assert "timeline" in script
