from market_phase_detector.lenses.marks import build_marks_lens


def test_marks_lens_uses_credit_and_risk_inputs():
    decision = build_marks_lens(
        {
            "as_of": "2026-03-31",
            "hy_spread": 5.8,
            "leading_index_change": -0.2,
            "yield_curve": -0.3,
            "claims_trend": "rising",
        }
    )

    assert decision.phase == "Recession"
    assert {metric.metric_id for metric in decision.metrics} == {
        "hy_spread",
        "valuation_proxy",
        "fear_proxy",
    }
    assert decision.reasons
