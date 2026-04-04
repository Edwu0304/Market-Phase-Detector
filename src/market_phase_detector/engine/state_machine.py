from market_phase_detector.models.phases import TransitionDecision


PHASE_ORDER = {
    "Recovery": 0,
    "Growth": 1,
    "Boom": 2,
    "Recession": 3,
}


def resolve_transition(
    previous_phase: str,
    candidate_phase: str,
    previous_candidate_phase: str | None,
    stress_override: bool,
) -> TransitionDecision:
    if candidate_phase == previous_phase:
        return TransitionDecision(final_phase=previous_phase)

    previous_rank = PHASE_ORDER[previous_phase]
    candidate_rank = PHASE_ORDER[candidate_phase]

    is_upgrade = candidate_rank < 3 and candidate_rank > previous_rank
    is_downgrade = candidate_rank > previous_rank

    if is_upgrade and previous_candidate_phase == candidate_phase:
        return TransitionDecision(final_phase=candidate_phase)

    if is_downgrade and (stress_override or previous_candidate_phase == candidate_phase):
        return TransitionDecision(final_phase=candidate_phase)

    return TransitionDecision(
        final_phase=previous_phase,
        watch="insufficient_confirmation",
    )
