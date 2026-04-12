from market_phase_detector.lenses.izaax import build_izaax_lens


def test_izaax_lens_builds_phase_metrics_and_reasons():
    decision = build_izaax_lens(
        {
            "as_of": "2026-03-31",
            "leading_index_change": 0.3,
            "coincident_trend": "improving",
            "unemployment_trend": "stable",
            "exports_yoy": 4.5,
            "unemployment_claims": 82000,
            "unemployment_claims_trend": "falling",
            "pmi": 55.4,
            "cci_total": 71.2,
        }
    )

    assert decision.phase in {"Growth", "Boom"}
    metric_ids = {metric.metric_id for metric in decision.metrics}
    assert "leading_index_change" in metric_ids
    assert "unemployment_claims" in metric_ids
    assert "pmi" in metric_ids
    assert decision.reasons
