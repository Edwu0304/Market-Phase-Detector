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
            "decision_summary": f"初始月份以 {PHASE_LABELS[final_phase]} 的支持訊號最多，作為當期階段。",
            "support_current_phase_signals": list(phase_signals.get(final_phase, [])),
            "support_next_phase_signals": list(phase_signals.get(next_phase_value, [])),
            "conflict_signals": conflict_signals,
        }

    candidate_next_phase = next_phase(previous_phase_value)
    next_of_next_phase = next_phase(candidate_next_phase)
    current_support = list(phase_signals.get(previous_phase_value, []))
    next_support = list(phase_signals.get(candidate_next_phase, []))

    if len(next_support) >= min_next_support:
        final_phase = candidate_next_phase
        decision_mode = "advance"
        decision_summary = (
            f"因為 {'、'.join(next_support)}，所以由 {PHASE_LABELS[previous_phase_value]} "
            f"轉為 {PHASE_LABELS[final_phase]}。"
        )
    else:
        final_phase = previous_phase_value
        decision_mode = "hold"
        if next_support:
            decision_summary = (
                f"雖然出現 {'、'.join(next_support)}，但還不足以由 {PHASE_LABELS[previous_phase_value]} "
                f"轉為 {PHASE_LABELS[candidate_next_phase]}。"
            )
        else:
            decision_summary = (
                f"目前沒有足夠訊號由 {PHASE_LABELS[previous_phase_value]} 轉為 "
                f"{PHASE_LABELS[candidate_next_phase]}。"
            )

    conflict_targets = {final_phase, next_phase(final_phase)}
    if previous_phase_value == final_phase:
        conflict_targets.add(candidate_next_phase)
    else:
        conflict_targets.add(next_of_next_phase)

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
