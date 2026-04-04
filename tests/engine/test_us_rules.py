from market_phase_detector.engine.us_rules import derive_us_candidate


def test_us_boom_candidate_when_activity_is_firm_but_risk_builds():
    candidate = derive_us_candidate(
        leading_index_change=0.45,
        claims_trend="stable",
        sahm_rule=0.28,
        yield_curve=-0.35,
        hy_spread=3.8,
    )

    assert candidate.phase == "Boom"
    assert "Yield curve inversion is a late-cycle warning" in candidate.reasons
