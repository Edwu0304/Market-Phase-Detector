from market_phase_detector.lenses.metric_sets import LENS_TITLES
from market_phase_detector.models.lenses import LensDecision, LensHistoryRow, LensMetric
from market_phase_detector.strategy_content import PHASE_LABELS


def _direction_score(value: str) -> float:
    mapping = {"improving": 1.0, "stable": 0.0, "deteriorating": -1.0, "falling": 1.0, "rising": -1.0}
    return mapping.get(value, 0.0)


def _direction_label(value: str) -> str:
    mapping = {
        "improving": "改善",
        "stable": "持平",
        "deteriorating": "惡化",
        "falling": "下降",
        "rising": "上升",
    }
    return mapping.get(value, value)


def _phase_from_score(score: float, labor_stress: float) -> str:
    if labor_stress >= 1.0 and score <= -1.0:
        return "Recession"
    if score >= 2.0:
        return "Boom"
    if score >= 0.5:
        return "Growth"
    return "Recovery"


def build_izaax_lens(observations: dict) -> LensDecision:
    leading_score = observations.get("leading_index_change", 0.0)
    coincident_score = _direction_score(observations.get("coincident_trend", "stable"))
    labor_stress = 1.0 if observations.get("unemployment_trend") == "rising" or observations.get("claims_trend") == "rising" else 0.0
    export_or_production = observations.get("exports_yoy", observations.get("leading_index_change", 0.0))
    score = leading_score + coincident_score + (0.5 if export_or_production > 0 else -0.5 if export_or_production < 0 else 0.0) - labor_stress
    phase = _phase_from_score(score, labor_stress)

    coincident_direction = observations.get("coincident_trend", observations.get("claims_trend", "stable"))
    reasons = [
        f"領先動能分數為 {leading_score:.2f}。",
        f"同時面方向目前是 {_direction_label(coincident_direction)}。",
        "勞動壓力正在升高。" if labor_stress else "勞動壓力仍受控制。",
    ]

    metrics = [
        LensMetric("leading_index_change", "領先指標變動", leading_score, "decimal", "positive" if leading_score > 0 else "negative" if leading_score < 0 else "neutral"),
        LensMetric("coincident_trend_score", "同時指標方向", coincident_score, "decimal", "positive" if coincident_score > 0 else "negative" if coincident_score < 0 else "neutral"),
        LensMetric("labor_stress", "勞動壓力", labor_stress, "decimal", "negative" if labor_stress else "positive"),
        LensMetric("export_or_production", "出口／生產", export_or_production, "percent", "positive" if export_or_production > 0 else "negative" if export_or_production < 0 else "neutral"),
    ]

    return LensDecision(
        lens_id="izaax",
        title=LENS_TITLES["izaax"],
        phase=phase,
        phase_label=PHASE_LABELS[phase],
        reasons=reasons,
        metrics=metrics,
    )


def build_izaax_history_row(month: str, observations: dict) -> LensHistoryRow:
    current = build_izaax_lens(observations)
    return LensHistoryRow(
        month=month,
        as_of=observations["as_of"],
        phase=current.phase,
        phase_label=current.phase_label,
        reasons=current.reasons,
        metrics=current.metrics,
    )
