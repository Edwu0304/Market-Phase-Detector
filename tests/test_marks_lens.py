from market_phase_detector.lenses.marks import build_marks_history_row, build_marks_lens


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
            "credit_spread": 2.8,
            "cci_total": 82.0,
            "margin_amount": 520000000,
        }
    )

    assert decision.phase == "Recession"
    metric_ids = {metric.metric_id for metric in decision.metrics}
    assert "stock_index_yoy" in metric_ids
    assert "credit_change" in metric_ids
    assert "inventory_change" in metric_ids
    assert "credit_spread" in metric_ids
    assert "cci_level" in metric_ids
    assert "margin_balance" in metric_ids
    assert decision.semantic_rows
    assert decision.reasons


def test_marks_history_row_exposes_support_buckets():
    row = build_marks_history_row(
        "2026-03",
        {
            "as_of": "2026-03-31",
            "stock_trend": "deteriorating",
            "credit_trend": "deteriorating",
            "inventory_trend": "deteriorating",
            "stock_index_yoy": -10.0,
            "credit_change": -50.0,
            "inventory_change": 100.0,
            "credit_spread": 2.8,
            "cci_total": 82.0,
            "margin_amount": 520000000,
        },
        previous_phase="Boom",
    )

    assert row.support_current_phase_signals
    assert hasattr(row, "support_next_phase_signals")
    assert hasattr(row, "conflict_signals")
    assert row.semantic_rows
