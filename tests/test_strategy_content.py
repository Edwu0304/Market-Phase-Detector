from market_phase_detector.strategy_content import (
    COUNTRY_LABELS,
    PHASE_LABELS,
    build_country_handbook,
    build_landing_content,
)


def test_build_country_handbook_returns_three_lenses():
    handbook = build_country_handbook("TW", "Recovery")

    assert handbook["country"] == "TW"
    assert handbook["phase"] == "Recovery"
    assert len(handbook["lenses"]) == 3


def test_build_landing_content_exposes_unified_framework_notice():
    landing = build_landing_content()

    assert COUNTRY_LABELS["TW"] == "Taiwan 台灣"
    assert PHASE_LABELS["Growth"] == "Growth 成長"
    assert "not a claim" in landing["method_notice"]["en"]
