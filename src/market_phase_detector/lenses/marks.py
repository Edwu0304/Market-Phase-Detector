from market_phase_detector.lenses.metric_sets import LENS_TITLES
from market_phase_detector.models.lenses import LensDecision, LensHistoryRow, LensMetric
from market_phase_detector.strategy_content import PHASE_LABELS


def _phase_from_risk(hy_spread: float, valuation_proxy: float, fear_proxy: float) -> str:
    if hy_spread >= 5.5 or fear_proxy >= 1.0:
        return "Recession"
    if hy_spread <= 3.5 and valuation_proxy > 0.5 and fear_proxy <= -0.5:
        return "Boom"
    if hy_spread <= 4.5:
        return "Growth"
    return "Recovery"


def build_marks_lens(observations: dict) -> LensDecision:
    hy_spread = observations.get("hy_spread", 4.5)
    valuation_proxy = observations.get("leading_index_change", 0.0) - (0.5 if observations.get("yield_curve", 0.0) < 0 else 0.0)
    fear_proxy = 1.0 if observations.get("claims_trend") == "rising" or observations.get("unemployment_trend") == "rising" else -0.5 if hy_spread < 4.0 else 0.0
    phase = _phase_from_risk(hy_spread, valuation_proxy, fear_proxy)
    reasons = [
        f"高收益債利差代理值為 {hy_spread:.2f}。",
        "估值與風險偏好代理偏熱。" if valuation_proxy > 0.5 else "估值與風險偏好尚未過熱。",
        "恐慌代理升高。" if fear_proxy > 0 else "恐慌代理偏低，市場較平靜或自滿。",
    ]
    metrics = [
        LensMetric("hy_spread", "高收益債利差", hy_spread, "spread", "negative" if hy_spread >= 5.5 else "positive", proxy_label="信用壓力代理"),
        LensMetric("valuation_proxy", "估值／風險偏好代理", valuation_proxy, "decimal", "negative" if valuation_proxy > 0.5 else "positive"),
        LensMetric("fear_proxy", "恐慌／自滿代理", fear_proxy, "decimal", "positive" if fear_proxy > 0 else "negative", proxy_label="情緒代理"),
    ]
    return LensDecision(
        lens_id="marks",
        title=LENS_TITLES["marks"],
        phase=phase,
        phase_label=PHASE_LABELS[phase],
        reasons=reasons,
        metrics=metrics,
    )


def build_marks_history_row(month: str, observations: dict) -> LensHistoryRow:
    current = build_marks_lens(observations)
    return LensHistoryRow(
        month=month,
        as_of=observations["as_of"],
        phase=current.phase,
        phase_label=current.phase_label,
        reasons=current.reasons,
        metrics=current.metrics,
    )
