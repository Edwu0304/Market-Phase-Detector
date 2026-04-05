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
        reasons.append("就業與信用壓力已升高到足以確認衰退風險。")
        return CandidateDecision(phase="Recession", reasons=reasons)

    if leading_index_change > 0 and yield_curve < 0:
        reasons.append("殖利率曲線倒掛屬於景氣晚期警訊。")
        if hy_spread >= 4.0:
            reasons.append("信用利差正在從低風險區往上擴大。")
        return CandidateDecision(phase="Boom", reasons=reasons)

    if leading_index_change >= 0 and claims_trend in {"stable", "falling"} and hy_spread < 4.0:
        reasons.append("領先活動維持穩定，尚未出現廣泛壓力確認。")
        return CandidateDecision(phase="Growth", reasons=reasons)

    reasons.append("領先活動正從偏弱環境往上修復。")
    return CandidateDecision(phase="Recovery", reasons=reasons)
