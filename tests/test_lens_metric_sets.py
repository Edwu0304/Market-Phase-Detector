from market_phase_detector.lenses.metric_sets import LENS_METRIC_SETS


def test_lens_metric_sets_cover_three_author_styles():
    assert {metric["id"] for metric in LENS_METRIC_SETS["izaax"]} >= {
        "leading_index_change",
        "coincident_trend_score",
        "labor_stress",
        "export_or_production",
    }
    assert {metric["id"] for metric in LENS_METRIC_SETS["urakami"]} >= {
        "yield_curve",
        "rates_regime",
        "market_leadership_proxy",
    }
    assert {metric["id"] for metric in LENS_METRIC_SETS["marks"]} >= {
        "hy_spread",
        "valuation_proxy",
        "fear_proxy",
    }
