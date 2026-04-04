from market_phase_detector.models.phases import DecisionRecord


def build_country_snapshot(
    country: str,
    as_of: str,
    observations: dict,
    derived_signals: dict,
    candidate_phase: str,
    final_phase: str,
    reasons: list[str],
    watch: str | None,
    handbook: dict | None = None,
) -> dict:
    decision = DecisionRecord(
        country=country,
        as_of=as_of,
        candidate_phase=candidate_phase,
        final_phase=final_phase,
        watch=watch,
        reasons=reasons,
    )

    snapshot = {
        "country": country,
        "as_of": as_of,
        "observations": observations,
        "derived_signals": derived_signals,
        "decision": {
            "candidate_phase": decision.candidate_phase,
            "final_phase": decision.final_phase,
            "watch": decision.watch,
            "reasons": decision.reasons,
        },
    }

    if handbook is not None:
        snapshot["handbook"] = handbook

    return snapshot
