from market_phase_detector.lenses.metric_sets import LENS_TITLES
from market_phase_detector.models.lenses import (
    IzaaxTransposedBundle,
    LensDecision,
    LensHistoryRow,
    LensMetric,
    TransposedMetricRow,
)
from market_phase_detector.strategy_content import PHASE_LABELS

# 愛榭克景氣循環四階段（不可跳過，循環順序）
PHASE_SEQUENCE = ["Recovery", "Growth", "Boom", "Recession"]

# 進入下一階段的關鍵指標
TRANSITION_METRICS = {
    "Recovery": {  # Recovery → Growth 需要這些改善
        "next": ["leading_index_change", "industrial_production_trend", "exports_yoy"],
        "prev": ["unemployment_claims", "labor_stress"],
    },
    "Growth": {  # Growth → Boom 需要這些過熱
        "next": ["cci_level", "inventory_sales_ratio", "export_or_production"],
        "prev": ["leading_index_change", "exports_yoy"],
    },
    "Boom": {  # Boom → Recession 需要這些惡化
        "next": ["sahm_rule", "unemployment_claims", "inventory_sales_ratio"],
        "prev": ["cci_level", "leading_index_change"],
    },
    "Recession": {  # Recession → Recovery 需要這些好轉
        "next": ["leading_index_change", "unemployment_claims", "sahm_rule"],
        "prev": ["inventory_sales_ratio", "labor_stress"],
    },
}


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
    # 使用真實指標
    leading_score = observations.get("leading_index_change", 0.0)
    industrial_trend = observations.get("industrial_production_trend", "stable")
    industrial_score = _direction_score(industrial_trend)
    labor_stress = 1.0 if observations.get("unemployment_trend") == "rising" else 0.0
    overtime_trend = observations.get("overtime_trend", "stable")
    overtime_score = _direction_score(overtime_trend)
    export_score = 0.5 if observations.get("exports_yoy", 0) > 0 else (-0.5 if observations.get("exports_yoy", 0) < 0 else 0.0)

    # 新增：初領失業救濟金趨勢
    claims_trend = observations.get("unemployment_claims_trend", "stable")
    claims_score = _direction_score(claims_trend)

    # 新增：消費者信心指數
    cci_level = observations.get("cci_total", 50.0)
    cci_signal = "euphoria" if cci_level > 80 else ("caution" if cci_level > 70 else "neutral")

    # 新增：薩姆規則
    sahm_value = observations.get("sahm_rule", None)
    sahm_signal = sahm_value is not None and sahm_value >= 0.5

    # 新增：庫存/銷售比
    inv_sales = observations.get("inventory_sales_ratio", {})
    inv_trend = inv_sales.get("trend", "stable") if inv_sales else "stable"
    inv_score = -1.0 if inv_trend == "accumulating" else (1.0 if inv_trend == "clearing" else 0.0)

    score = leading_score + industrial_score + overtime_score + export_score - labor_stress + claims_score * 0.5 + inv_score * 0.3
    phase = _phase_from_score(score, labor_stress)

    reasons = [
        f"領先動能分數為 {leading_score:.2f}。",
        f"工業生產趨勢 {_direction_label(industrial_trend)}。",
        "勞動壓力正在升高。" if labor_stress else "勞動壓力仍受控制。",
        f"加班工時趨勢 {_direction_label(overtime_trend)}。",
    ]

    # 新增原因說明
    if claims_trend != "stable":
        reasons.append(f"初領失業救濟金人數 {_direction_label(claims_trend)}。")
    if sahm_signal:
        reasons.append("薩姆規則已觸發衰退訊號！")
    if cci_signal == "euphoria":
        reasons.append("消費者信心過熱，留意反轉訊號。")

    metrics = [
        LensMetric("leading_index_change", "領先指標變動", leading_score, "decimal", "positive" if leading_score > 0 else "negative" if leading_score < 0 else "neutral"),
        LensMetric("industrial_production_trend", "工業生產趨勢", industrial_score, "decimal", "positive" if industrial_score > 0 else "negative" if industrial_score < 0 else "neutral"),
        LensMetric("labor_stress", "勞動壓力", labor_stress, "decimal", "negative" if labor_stress else "positive"),
        LensMetric("overtime_trend", "加班工時趨勢", overtime_score, "decimal", "positive" if overtime_score > 0 else "negative" if overtime_score < 0 else "neutral"),
        LensMetric("exports_yoy", "出口年增率", observations.get("exports_yoy", 0.0), "percent", "positive" if observations.get("exports_yoy", 0) > 0 else "negative"),
        # 新增指標
        LensMetric("unemployment_claims", "初領失業救濟金", claims_score, "decimal", "positive" if claims_score > 0 else "negative" if claims_score < 0 else "neutral"),
        LensMetric("cci_level", "消費者信心指數", cci_level, "decimal", "negative" if cci_signal == "euphoria" else "positive"),
        LensMetric("sahm_rule", "薩姆規則", sahm_value if sahm_value is not None else 0.0, "decimal", "negative" if sahm_signal else "positive"),
        LensMetric("inventory_sales_ratio", "庫存/銷售比", inv_score, "decimal", "negative" if inv_score < 0 else "positive" if inv_score > 0 else "neutral"),
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


def _phase_index(phase: str) -> int:
    """Get index of phase in the fixed sequence."""
    try:
        return PHASE_SEQUENCE.index(phase)
    except ValueError:
        return 0


def _next_phase(phase: str) -> str:
    """Get next phase in sequence (circular)."""
    idx = _phase_index(phase)
    return PHASE_SEQUENCE[(idx + 1) % len(PHASE_SEQUENCE)]


def _prev_phase(phase: str) -> str:
    """Get previous phase in sequence (circular)."""
    idx = _phase_index(phase)
    return PHASE_SEQUENCE[(idx - 1) % len(PHASE_SEQUENCE)]


def _format_display_value(value, display_format: str) -> str:
    """Format value for display."""
    if value is None:
        return "—"
    if isinstance(value, str):
        return value
    if display_format == "percent":
        return f"{value:.1f}%"
    if display_format == "spread":
        return f"{value:.2f}"
    if display_format == "decimal":
        return f"{value:.2f}"
    return f"{value}"


def _get_metric_value_for_phase(metric_id: str, observations: dict) -> float | str | None:
    """Extract or compute the value for a specific metric_id from observations."""
    if metric_id == "leading_index_change":
        return observations.get("leading_index_change")
    elif metric_id == "industrial_production_trend":
        # Compute from industrial_production_change
        change = observations.get("industrial_production_change")
        if change is None:
            return "stable"
        if change > 0.5:
            return "improving"
        elif change < -0.5:
            return "deteriorating"
        return "stable"
    elif metric_id == "labor_stress":
        # Compute from unemployment_trend
        return 1.0 if observations.get("unemployment_trend") == "rising" else 0.0
    elif metric_id == "overtime_trend":
        # Compute from overtime_hours_change
        change = observations.get("overtime_hours_change")
        if change is None:
            return "stable"
        if change > 0.5:
            return "rising"
        elif change < -0.5:
            return "falling"
        return "stable"
    elif metric_id == "exports_yoy":
        return observations.get("exports_yoy")
    elif metric_id == "unemployment_claims":
        return observations.get("unemployment_claims")
    elif metric_id == "cci_level":
        return observations.get("cci_total")
    elif metric_id == "sahm_rule":
        return observations.get("sahm_rule")
    elif metric_id == "inventory_sales_ratio":
        inv_sales = observations.get("inventory_sales_ratio", {})
        return inv_sales.get("trend", "stable") if isinstance(inv_sales, dict) else "stable"
    return None


def _get_display_format_for_metric(metric_id: str) -> str:
    """Get display format for a metric."""
    formats = {
        "leading_index_change": "decimal",
        "industrial_production_trend": "decimal",
        "labor_stress": "decimal",
        "overtime_trend": "decimal",
        "exports_yoy": "percent",
        "unemployment_claims": "decimal",
        "cci_level": "decimal",
        "sahm_rule": "decimal",
        "inventory_sales_ratio": "decimal",
    }
    return formats.get(metric_id, "decimal")


def _get_metric_label(metric_id: str) -> str:
    """Get Chinese label for metric."""
    labels = {
        "leading_index_change": "領先指標變動",
        "industrial_production_trend": "工業生產趨勢",
        "labor_stress": "勞動壓力",
        "overtime_trend": "加班工時趨勢",
        "exports_yoy": "出口年增率",
        "unemployment_claims": "初領失業救濟金",
        "cci_level": "消費者信心指數",
        "sahm_rule": "薩姆規則",
        "inventory_sales_ratio": "庫存/銷售比",
    }
    return labels.get(metric_id, metric_id)


def build_izaax_transposed_bundle(
    current_observations: dict,
    history_observations: list[dict],
    max_months: int = 24,
) -> IzaaxTransposedBundle:
    """Build transposed Izaax bundle: metrics as rows, months as columns.

    This is the primary UI for Izaax lens, showing:
    1. Current phase prominently at top
    2. Transposed table with metrics as rows, months as columns
    3. Highlighted metrics critical for next phase transition
    """
    # Determine current phase from lens
    current_decision = build_izaax_lens(current_observations)
    current_phase = current_decision.phase
    current_phase_label = current_decision.phase_label

    # Phase sequence info
    next_ph = _next_phase(current_phase)
    prev_ph = _prev_phase(current_phase)
    transition_info = TRANSITION_METRICS.get(current_phase, {"next": [], "prev": []})
    next_key_metrics = transition_info.get("next", [])

    # Collect all months (current + history), deduplicate
    all_obs = history_observations[-max_months:] + [current_observations]
    seen_months = set()
    deduped_obs = []
    for obs in all_obs:
        m = obs.get("month", obs.get("as_of", ""))
        if m not in seen_months:
            seen_months.add(m)
            deduped_obs.append(obs)
    all_obs = deduped_obs
    months = [obs.get("month", obs.get("as_of", "")) for obs in all_obs]

    # All unique metric IDs used in Izaax
    all_metric_ids = [
        "leading_index_change",
        "industrial_production_trend",
        "labor_stress",
        "overtime_trend",
        "exports_yoy",
        "unemployment_claims",
        "cci_level",
        "sahm_rule",
        "inventory_sales_ratio",
    ]

    # Build transposed metric rows
    metric_rows = []
    for metric_id in all_metric_ids:
        display_format = _get_display_format_for_metric(metric_id)
        label = _get_metric_label(metric_id)
        is_key = metric_id in next_key_metrics

        # Determine transition direction relevance
        if is_key:
            transition_direction = "next"
        elif metric_id in transition_info.get("prev", []):
            transition_direction = "prev"
        else:
            transition_direction = ""

        # Collect values across all months
        values = []
        for obs in all_obs:
            raw_value = _get_metric_value_for_phase(metric_id, obs)
            dv = _format_display_value(raw_value, display_format)
            # Determine status based on value direction
            if isinstance(raw_value, (int, float)):
                status = "positive" if raw_value > 0 else ("negative" if raw_value < 0 else "neutral")
            elif isinstance(raw_value, str):
                status = "positive" if raw_value in ("improving", "falling", "clearing") else ("negative" if raw_value in ("deteriorating", "rising", "accumulating") else "neutral")
            else:
                status = "neutral"

            values.append({
                "month": obs.get("month", obs.get("as_of", "")),
                "display_value": dv,
                "status": status,
            })

        metric_rows.append(TransposedMetricRow(
            metric_id=metric_id,
            label=label,
            display_format=display_format,
            is_transition_key=is_key,
            transition_direction=transition_direction,
            values=values,
        ))

    return IzaaxTransposedBundle(
        current_phase=current_phase,
        current_phase_label=current_phase_label,
        next_phase=next_ph,
        prev_phase=prev_ph,
        phase_sequence=PHASE_SEQUENCE,
        transition_keys=next_key_metrics,
        metric_rows=metric_rows,
        months=months,
        reasons=current_decision.reasons,
    )
