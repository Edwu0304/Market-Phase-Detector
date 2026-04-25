from market_phase_detector.lenses.izaax import (
    build_izaax_history_row,
    build_izaax_lens,
    build_izaax_transposed_bundle,
)


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
    assert row.decision_mode == "hold"


def test_izaax_history_row_can_override_growth_when_recession_signals_dominate():
    row = build_izaax_history_row(
        "2026-02",
        {
            "as_of": "2026-02",
            "leading_index_change": 0.38,
            "industrial_production_trend": "deteriorating",
            "overtime_trend": "stable",
            "unemployment_trend": "rising",
            "exports_yoy": -4.1,
            "pmi": 58.5,
            "cci_total": 50.0,
            "inventory_sales_ratio": "stable",
        },
        previous_phase="Growth",
    )

    assert row.phase == "Growth"
    assert row.decision_mode == "hold"
    assert row.warning_state == "recession_warning"
    assert row.warning_reasons


def test_izaax_transposed_bundle_uses_latest_overridden_phase():
    history = [
        {
            "month": "2026-01",
            "as_of": "2026-01",
            "leading_index_change": 0.59,
            "industrial_production_trend": "deteriorating",
            "overtime_trend": "stable",
            "unemployment_trend": "stable",
            "exports_yoy": -4.4,
            "pmi": 57.2,
            "cci_total": 50.0,
            "inventory_sales_ratio": "stable",
        }
    ]
    current = {
        "as_of": "2026-02",
        "leading_index_change": 0.38,
        "industrial_production_trend": "deteriorating",
        "overtime_trend": "stable",
        "unemployment_trend": "rising",
        "exports_yoy": -4.1,
        "pmi": 58.5,
        "cci_total": 50.0,
        "inventory_sales_ratio": "stable",
    }

    bundle = build_izaax_transposed_bundle(current, history)

    assert bundle.current_phase == "Growth"
    assert bundle.month_columns[-1]["phase"] == "Growth"
    assert bundle.month_columns[-1]["warning_state"] == "recession_warning"
