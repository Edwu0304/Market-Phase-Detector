from market_phase_detector.models.phases import CandidateDecision


def derive_tw_candidate(
    business_signal_score: int,
    leading_trend: str,
    coincident_trend: str,
    unemployment_trend: str,
    exports_yoy: float,
    exports_trend: str,
) -> CandidateDecision:
    reasons: list[str] = []

    if (
        leading_trend == "deteriorating"
        and coincident_trend == "deteriorating"
        and unemployment_trend == "rising"
    ):
        reasons.append("Leading and coincident indicators are weakening together")
        return CandidateDecision(phase="Recession", reasons=reasons)

    if business_signal_score >= 32 and leading_trend != "improving":
        reasons.append("Business signal is elevated while leading data is no longer improving")
        return CandidateDecision(phase="Boom", reasons=reasons)

    if (
        leading_trend == "improving"
        and coincident_trend == "improving"
        and unemployment_trend != "rising"
        and exports_yoy >= 0
    ):
        reasons.append("Leading and coincident indicators are improving together")
        return CandidateDecision(phase="Growth", reasons=reasons)

    reasons.append("Leading indicators are improving from weak levels")
    if exports_trend == "improving":
        reasons.append("External demand is stabilizing")
    return CandidateDecision(phase="Recovery", reasons=reasons)
