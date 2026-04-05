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
        reasons.append("領先與同時指標同步轉弱。")
        return CandidateDecision(phase="Recession", reasons=reasons)

    if business_signal_score >= 32 and leading_trend != "improving":
        reasons.append("景氣燈號已在高檔，但領先資料不再改善。")
        return CandidateDecision(phase="Boom", reasons=reasons)

    if (
        leading_trend == "improving"
        and coincident_trend == "improving"
        and unemployment_trend != "rising"
        and exports_yoy >= 0
    ):
        reasons.append("領先與同時指標同步改善。")
        return CandidateDecision(phase="Growth", reasons=reasons)

    reasons.append("領先指標正從低檔往上修復。")
    if exports_trend == "improving":
        reasons.append("外需正在止穩。")
    return CandidateDecision(phase="Recovery", reasons=reasons)
