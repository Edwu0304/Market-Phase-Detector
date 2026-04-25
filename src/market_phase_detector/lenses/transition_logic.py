from market_phase_detector.strategy_content import PHASE_LABELS


PHASE_SEQUENCE = ["Recovery", "Growth", "Boom", "Recession"]


def next_phase(phase: str) -> str:
    idx = PHASE_SEQUENCE.index(phase)
    return PHASE_SEQUENCE[(idx + 1) % len(PHASE_SEQUENCE)]


def previous_phase(phase: str) -> str:
    idx = PHASE_SEQUENCE.index(phase)
    return PHASE_SEQUENCE[(idx - 1) % len(PHASE_SEQUENCE)]


def pick_phase_from_support(phase_signals: dict[str, list[str]]) -> str:
    ranked = sorted(
        PHASE_SEQUENCE,
        key=lambda phase: (len(phase_signals.get(phase, [])), -PHASE_SEQUENCE.index(phase)),
        reverse=True,
    )
    return ranked[0] if ranked and phase_signals.get(ranked[0]) else "Recovery"


def resolve_phase_transition(
    phase_signals: dict[str, list[str]],
    previous_phase_value: str | None,
    min_next_support: int = 2,
) -> dict[str, object]:
    if previous_phase_value is None:
        final_phase = pick_phase_from_support(phase_signals)
        next_phase_value = next_phase(final_phase)
        conflict_signals = [
            signal
            for phase, signals in phase_signals.items()
            if phase not in {final_phase, next_phase_value}
            for signal in signals
        ]
        return {
            "phase": final_phase,
            "decision_mode": "initial",
            "decision_summary": f"Initial month resolves to {PHASE_LABELS[final_phase]} based on the strongest support.",
            "support_current_phase_signals": list(phase_signals.get(final_phase, [])),
            "support_next_phase_signals": list(phase_signals.get(next_phase_value, [])),
            "conflict_signals": conflict_signals,
        }

    candidate_next_phase = next_phase(previous_phase_value)
    strongest_phase = pick_phase_from_support(phase_signals)
    current_support = list(phase_signals.get(previous_phase_value, []))
    next_support = list(phase_signals.get(candidate_next_phase, []))
    strongest_support = list(phase_signals.get(strongest_phase, []))

    if (
        strongest_phase not in {previous_phase_value, candidate_next_phase}
        and len(strongest_support) >= min_next_support
        and len(strongest_support) > max(len(current_support), len(next_support))
    ):
        final_phase = strongest_phase
        decision_mode = "override"
        decision_summary = (
            f"Override {PHASE_LABELS[previous_phase_value]} and resolve to {PHASE_LABELS[final_phase]} "
            f"because {'; '.join(strongest_support)}."
        )
    elif len(next_support) >= min_next_support:
        final_phase = candidate_next_phase
        decision_mode = "advance"
        decision_summary = (
            f"Advance from {PHASE_LABELS[previous_phase_value]} to {PHASE_LABELS[final_phase]} "
            f"because {'; '.join(next_support)}."
        )
    else:
        final_phase = previous_phase_value
        decision_mode = "hold"
        if next_support:
            decision_summary = (
                f"Hold {PHASE_LABELS[previous_phase_value]}; "
                f"{'; '.join(next_support)} is not enough to move to {PHASE_LABELS[candidate_next_phase]}."
            )
        else:
            decision_summary = (
                f"Hold {PHASE_LABELS[previous_phase_value]}; "
                f"there is not enough evidence to move to {PHASE_LABELS[candidate_next_phase]}."
            )

    conflict_targets = {final_phase, next_phase(final_phase)}
    if previous_phase_value == final_phase:
        conflict_targets.add(candidate_next_phase)

    conflict_signals = [
        signal
        for phase, signals in phase_signals.items()
        if phase not in conflict_targets
        for signal in signals
    ]

    return {
        "phase": final_phase,
        "decision_mode": decision_mode,
        "decision_summary": decision_summary,
        "support_current_phase_signals": current_support if final_phase == previous_phase_value else list(phase_signals.get(final_phase, [])),
        "support_next_phase_signals": list(phase_signals.get(next_phase(final_phase), [])),
        "conflict_signals": conflict_signals,
    }
