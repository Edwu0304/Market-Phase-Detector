from market_phase_detector.models.phases import CandidateDecision


def derive_us_candidate(
    leading_index_change: float,
    claims_trend: str,
    sahm_rule: float,
    yield_curve: float,
    hy_spread: float,
) -> CandidateDecision:
    reasons: list[str] = []

    if sahm_rule >= 0.5 or (claims_trend == "rising" and hy_spread >= 4.5 and leading_index_change < 0):
        reasons.append("Labor and credit stress are strong enough to confirm recession risk")
        return CandidateDecision(phase="Recession", reasons=reasons)

    if leading_index_change > 0 and yield_curve < 0:
        reasons.append("Yield curve inversion is a late-cycle warning")
        if hy_spread >= 4.0:
            reasons.append("Credit spreads are widening from benign levels")
        return CandidateDecision(phase="Boom", reasons=reasons)

    if leading_index_change >= 0 and claims_trend in {"stable", "falling"} and hy_spread < 4.0:
        reasons.append("Leading activity remains stable without broad stress confirmation")
        return CandidateDecision(phase="Growth", reasons=reasons)

    reasons.append("Leading activity is improving from softer conditions")
    return CandidateDecision(phase="Recovery", reasons=reasons)
