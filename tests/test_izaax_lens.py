from market_phase_detector.lenses.izaax import build_izaax_history_row, build_izaax_lens


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


def test_izaax_history_row_stays_in_growth_without_true_boom_support():
    row = build_izaax_history_row(
        "2024-05",
        {
            "as_of": "2024-05",
            "leading_index_change": 0.57,
            "industrial_production_trend": "improving",
            "overtime_trend": "stable",
            "unemployment_trend": "stable",
            "exports_yoy": 9.1,
            "pmi": 55.4,
            "cci_total": 50.0,
            "inventory_sales_ratio": "stable",
        },
        previous_phase="Growth",
    )

    assert row.phase == "Growth"
    assert row.support_current_phase_signals
    assert not row.support_next_phase_signals
    assert "Growth" in row.decision_summary or "成長" in row.decision_summary
