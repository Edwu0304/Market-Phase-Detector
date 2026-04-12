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
            "m2_yoy": 5.38,
            "yield_curve_spread": 0.38,
            "pe_ratio": 23.22,
            "margin_amount": 368046780,
            "margin_trend": "moderate",
        }
    )

    assert decision.phase == "Boom"
    metric_ids = {metric.metric_id for metric in decision.metrics}
    assert "bank_lending_rate" in metric_ids
    assert "credit_change" in metric_ids
    assert "m1b_change" in metric_ids
    assert "m2_yoy" in metric_ids
    assert "yield_curve" in metric_ids
    assert "margin_balance" in metric_ids
    assert decision.reasons
