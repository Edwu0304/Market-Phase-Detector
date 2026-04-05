from pathlib import Path


def test_visual_system_defines_phase_classes_and_three_column_grid():
    styles = Path("frontend/src/styles.css").read_text(encoding="utf-8")
    assert ".phase-recovery" in styles
    assert ".phase-growth" in styles
    assert ".phase-boom" in styles
    assert ".phase-recession" in styles
    assert ".lens-row-body" in styles


def test_visual_system_mentions_current_and_historical_grouping():
    script = Path("frontend/src/app.js").read_text(encoding="utf-8")
    assert "current-site-summary" in script
    assert "history-state" in script
    assert "history-table" in script
    assert "網站總相位" in script
