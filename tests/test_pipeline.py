from market_phase_detector.pipeline import build_country_snapshot


def test_pipeline_returns_country_snapshot_with_decision():
    snapshot = build_country_snapshot(
        country="US",
        as_of="2026-03-31",
        observations={"ism": 51.1},
        derived_signals={"macro_direction": "stable"},
        candidate_phase="Growth",
        final_phase="Growth",
        reasons=["ISM stable above 50"],
        watch=None,
    )

    assert snapshot["decision"]["final_phase"] == "Growth"
    assert snapshot["observations"]["ism"] == 51.1


def test_pipeline_can_include_lens_bundles():
    snapshot = build_country_snapshot(
        country="TW",
        as_of="2026-03-31",
        observations={"business_signal_score": 40},
        derived_signals={"macro_direction": "improving"},
        candidate_phase="Recovery",
        final_phase="Recovery",
        reasons=["Leading indicators are improving"],
        watch=None,
        lenses={
            "izaax": {
                "phase": "Recovery",
                "metrics": [{"id": "leading_index_change", "value": 0.2}],
                "history": [{"month": "2026-03", "phase": "Recovery"}],
            }
        },
    )

    assert snapshot["lenses"]["izaax"]["phase"] == "Recovery"
    assert snapshot["lenses"]["izaax"]["history"][0]["month"] == "2026-03"
