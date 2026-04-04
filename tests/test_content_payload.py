import json
from pathlib import Path

from market_phase_detector.content import build_site_content


def test_build_site_content_contains_home_and_country_pages():
    payload = build_site_content()

    assert "home" in payload
    assert "countries" in payload
    assert "TW" in payload["countries"]
    assert "US" in payload["countries"]


def test_generated_site_content_file_exists():
    path = Path("data/site-content.json")
    if path.exists():
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert "home" in payload
