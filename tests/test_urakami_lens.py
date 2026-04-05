from market_phase_detector.lenses.urakami import build_urakami_lens


def test_urakami_lens_uses_rates_and_market_proxies():
    decision = build_urakami_lens(
        {
            "as_of": "2026-03-31",
            "yield_curve": 0.25,
            "leading_index_change": 0.2,
            "coincident_trend": "improving",
        }
    )

    assert decision.phase in {"Growth", "Boom"}
    assert {metric.metric_id for metric in decision.metrics} == {
        "yield_curve",
        "rates_regime",
        "market_leadership_proxy",
    }
    assert decision.reasons
