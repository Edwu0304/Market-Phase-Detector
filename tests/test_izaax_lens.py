from market_phase_detector.lenses.izaax import build_izaax_lens


def test_izaax_lens_builds_phase_metrics_and_reasons():
    decision = build_izaax_lens(
        {
            "as_of": "2026-03-31",
            "leading_index_change": 0.3,
            "coincident_trend": "improving",
            "unemployment_trend": "stable",
            "exports_yoy": 4.5,
        }
    )

    assert decision.phase in {"Growth", "Boom"}
    assert decision.metrics[0].metric_id == "leading_index_change"
    assert decision.reasons
