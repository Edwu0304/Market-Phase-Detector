from pathlib import Path


def test_each_lens_panel_has_independent_slider_state():
    script = Path("frontend/src/pages/renderCountry.js").read_text(encoding="utf-8")
    assert "independentSliderState" in script
    assert "lens-history-slider" in script
    assert "updateLensRow" in script


def test_country_page_keeps_current_header_separate_from_lens_history():
    page_script = Path("frontend/src/pages/renderCountry.js").read_text(encoding="utf-8")
    country_components = Path("frontend/src/domain/country.js").read_text(encoding="utf-8")
    assert "current-site-summary" in country_components
    assert "renderCountryPage" in page_script
    assert "history-table" in page_script


def test_izaax_month_switch_preserves_table_scroll_position():
    page_script = Path("frontend/src/pages/renderCountry.js").read_text(encoding="utf-8")
    assert "scrollLeft" in page_script
    assert "scrollTop" in page_script
    assert "izaax-table-scroll-wrapper" in page_script


def test_standard_lens_month_switch_preserves_table_scroll_position():
    page_script = Path("frontend/src/pages/renderCountry.js").read_text(encoding="utf-8")
    country_components = Path("frontend/src/domain/country.js").read_text(encoding="utf-8")
    assert "history-table-wrap" in country_components
    assert "preservedTableScrollLeft" in page_script
    assert "preservedTableScrollTop" in page_script
