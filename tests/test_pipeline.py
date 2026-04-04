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


def test_pipeline_can_include_additional_sections():
    snapshot = build_country_snapshot(
        country="TW",
        as_of="2026-03-31",
        observations={"business_signal_score": 40},
        derived_signals={"macro_direction": "improving"},
        candidate_phase="Recovery",
        final_phase="Recovery",
        reasons=["Leading indicators are improving"],
        watch=None,
        handbook={"phase_label": "Recovery 復甦"},
    )

    assert snapshot["handbook"]["phase_label"] == "Recovery 復甦"
