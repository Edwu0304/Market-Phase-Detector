from market_phase_detector.engine.tw_rules import derive_tw_candidate


def test_tw_recovery_candidate_when_leading_data_turns_up():
    candidate = derive_tw_candidate(
        business_signal_score=18,
        leading_trend="improving",
        coincident_trend="stable",
        unemployment_trend="stable",
        exports_yoy=-2.5,
        exports_trend="improving",
    )

    assert candidate.phase == "Recovery"
    assert "Leading indicators are improving from weak levels" in candidate.reasons
