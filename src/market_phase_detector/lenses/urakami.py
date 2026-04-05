from market_phase_detector.lenses.metric_sets import LENS_TITLES
from market_phase_detector.models.lenses import LensDecision, LensHistoryRow, LensMetric
from market_phase_detector.strategy_content import PHASE_LABELS


def _phase_from_inputs(yield_curve: float, rates_regime: float, leadership: float) -> str:
    if yield_curve < 0 and rates_regime < 0:
        return "Recession"
    if yield_curve > 0.4 and rates_regime > 0 and leadership > 0:
        return "Boom"
    if yield_curve >= 0 and leadership >= 0:
        return "Growth"
    return "Recovery"


def build_urakami_lens(observations: dict) -> LensDecision:
    yield_curve = observations.get("yield_curve", 0.0)
    rates_regime = observations.get("leading_index_change", observations.get("business_signal_score", 0.0) / 10.0)
    leadership = observations.get("coincident_direction_score", 0.0)
    if leadership == 0.0:
        leadership = 1.0 if observations.get("coincident_trend") == "improving" else -1.0 if observations.get("coincident_trend") == "deteriorating" else 0.0
    phase = _phase_from_inputs(yield_curve, rates_regime, leadership)

    reasons = [
        f"殖利率曲線代理值為 {yield_curve:.2f}。",
        "利率環境正在轉鬆。" if rates_regime > 0 else "利率環境仍偏緊。",
        "市場主流正在擴散。" if leadership > 0 else "市場主流仍偏狹窄或中性。",
    ]
    metrics = [
        LensMetric("yield_curve", "殖利率曲線", yield_curve, "spread", "positive" if yield_curve > 0 else "negative", proxy_label="利率曲線代理"),
        LensMetric("rates_regime", "利率環境", rates_regime, "decimal", "positive" if rates_regime > 0 else "negative"),
        LensMetric("market_leadership_proxy", "市場領導廣度代理", leadership, "decimal", "positive" if leadership > 0 else "negative" if leadership < 0 else "neutral", proxy_label="市場廣度代理"),
    ]
    return LensDecision(
        lens_id="urakami",
        title=LENS_TITLES["urakami"],
        phase=phase,
        phase_label=PHASE_LABELS[phase],
        reasons=reasons,
        metrics=metrics,
    )


def build_urakami_history_row(month: str, observations: dict) -> LensHistoryRow:
    current = build_urakami_lens(observations)
    return LensHistoryRow(
        month=month,
        as_of=observations["as_of"],
        phase=current.phase,
        phase_label=current.phase_label,
        reasons=current.reasons,
        metrics=current.metrics,
    )
