from market_phase_detector.lenses.urakami import build_urakami_lens


def test_urakami_lens_uses_rates_and_market_proxies():
    decision = build_urakami_lens(
        {
            "as_of": "2026-03-31",
            "rate_trend": "falling",
            "credit_trend": "improving",
            "money_supply_trend": "improving",
            "bank_lending_rate": 2.0,
            "credit_change": 100.0,
            "m1b_change": 50.0,
        }
    )

    assert decision.phase == "Boom"
    # Check that core metrics are present (new metrics may also be included)
    metric_ids = {metric.metric_id for metric in decision.metrics}
    assert "bank_lending_rate" in metric_ids
    assert "credit_change" in metric_ids
    assert "m1b_change" in metric_ids
    assert decision.reasons
