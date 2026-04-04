from market_phase_detector.engine.state_machine import resolve_transition


def test_upgrade_requires_two_confirming_months():
    result = resolve_transition(
        previous_phase="Recovery",
        candidate_phase="Growth",
        previous_candidate_phase="Growth",
        stress_override=False,
    )

    assert result.final_phase == "Growth"
