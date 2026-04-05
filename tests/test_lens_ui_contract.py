from pathlib import Path


def test_each_lens_panel_has_independent_slider_state():
    script = Path("frontend/src/app.js").read_text(encoding="utf-8")
    assert "independentSliderState" in script
    assert "lens-history-slider" in script
    assert "updateLensRow" in script


def test_country_page_keeps_current_header_separate_from_lens_history():
    script = Path("frontend/src/app.js").read_text(encoding="utf-8")
    assert "current-site-summary" in script
    assert "renderCountryPage" in script
    assert "history-table" in script
