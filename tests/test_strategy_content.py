from market_phase_detector.strategy_content import AUTHOR_META, COUNTRY_LABELS, PHASE_LABELS, build_country_handbook, build_landing_content, build_strategy_block


def test_build_country_handbook_returns_three_authors():
    handbook = build_country_handbook("TW", "Recovery")
    assert handbook["country"] == "TW"
    assert handbook["phase"] == "Recovery"
    assert len(handbook["authors"]) == 3


def test_build_landing_content_exposes_unified_framework_notice():
    landing = build_landing_content()
    assert COUNTRY_LABELS["TW"] == "台灣"
    assert PHASE_LABELS["Growth"] == "成長"
    assert "網站總相位" in landing["method_notice"]["zh"]


def test_strategy_blocks_resolve_by_author_and_phase():
    assert AUTHOR_META["marks"]["title"] == "霍華．馬克斯"
    assert "高收益利差" in build_strategy_block("marks", "Recovery", "indicators")
