from pathlib import Path


def test_visual_system_defines_phase_classes_and_three_column_grid():
    styles = Path("frontend/src/styles.css").read_text(encoding="utf-8")
    assert ".phase-recovery" in styles
    assert ".phase-growth" in styles
    assert ".phase-boom" in styles
    assert ".phase-recession" in styles
    assert ".lens-row-body" in styles


def test_visual_system_mentions_current_and_historical_grouping():
    page_script = Path("frontend/src/pages/renderCountry.js").read_text(encoding="utf-8")
    country_components = Path("frontend/src/domain/country.js").read_text(encoding="utf-8")
    assert "current-site-summary" in country_components
    assert "history-state" in page_script
    assert "history-table" in page_script
    assert "lens-row-stack" in page_script


def test_visual_system_is_grouped_by_design_system_sections():
    styles = Path("frontend/src/styles.css").read_text(encoding="utf-8")
    assert "/* ===== Foundation Tokens ===== */" in styles
    assert "/* ===== Base Elements ===== */" in styles
    assert "/* ===== Layout Shell ===== */" in styles
    assert "/* ===== Landing Domain ===== */" in styles
    assert "/* ===== Country Domain ===== */" in styles
    assert "/* ===== Lens Domain ===== */" in styles
    assert "/* ===== Izaax Domain ===== */" in styles
    assert "/* ===== Responsive Rules ===== */" in styles


def test_visual_system_mentions_terminal_ui_regions():
    styles = Path("frontend/src/styles.css").read_text(encoding="utf-8")
    assert ".terminal-hero" in styles
    assert ".market-overview-strip" in styles
    assert ".country-status-band" in styles
    assert ".country-command-header" in styles
    assert ".lens-workspace" in styles
