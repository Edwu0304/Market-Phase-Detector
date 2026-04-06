from market_phase_detector.lenses.marks import build_marks_lens


def test_marks_lens_uses_credit_and_risk_inputs():
    decision = build_marks_lens(
        {
            "as_of": "2026-03-31",
            "stock_trend": "deteriorating",
            "credit_trend": "deteriorating",
            "inventory_trend": "deteriorating",
            "stock_index_yoy": -10.0,
            "credit_change": -50.0,
            "inventory_change": 100.0,
        }
    )

    assert decision.phase == "Recession"
    # Check that core metrics are present (new metrics may also be included)
    metric_ids = {metric.metric_id for metric in decision.metrics}
    assert "stock_index_yoy" in metric_ids
    assert "credit_change" in metric_ids
    assert "inventory_change" in metric_ids
    assert decision.reasons
