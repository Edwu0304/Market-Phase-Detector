from market_phase_detector.lenses.metric_sets import LENS_TITLES
from market_phase_detector.lenses.transition_logic import (
    PHASE_SEQUENCE,
    next_phase,
    pick_phase_from_support,
    previous_phase,
    resolve_phase_transition,
)
from market_phase_detector.models.lenses import (
    IzaaxTransposedBundle,
    LensDecision,
    LensHistoryRow,
    LensMetric,
    TransposedMetricRow,
)
from market_phase_detector.strategy_content import PHASE_LABELS


TRANSITION_METRICS = {
    "Recovery": {"next": ["leading_index_change", "industrial_production_trend", "pmi"], "prev": ["labor_stress", "unemployment_claims"]},
    "Growth": {"next": ["cci_level", "inventory_sales_ratio", "overtime_trend"], "prev": ["leading_index_change", "pmi"]},
    "Boom": {"next": ["sahm_rule", "unemployment_claims", "inventory_sales_ratio"], "prev": ["cci_level", "leading_index_change"]},
    "Recession": {"next": ["leading_index_change", "pmi", "sahm_rule"], "prev": ["inventory_sales_ratio", "labor_stress"]},
}


def _direction_score(value: str) -> float:
    mapping = {"improving": 1.0, "stable": 0.0, "deteriorating": -1.0, "falling": 1.0, "rising": -1.0}
    return mapping.get(value, 0.0)


def _inventory_score(value) -> float:
    if isinstance(value, dict):
        trend = value.get("trend", "stable")
    else:
        trend = value or "stable"
    if trend in {"clearing", "improving"}:
        return 1.0
    if trend in {"accumulating", "deteriorating"}:
        return -1.0
    return 0.0


def _metric_status(value: float | None, positive_threshold: float = 0.0) -> str:
    if value is None:
        return "neutral"
    if value > positive_threshold:
        return "positive"
    if value < positive_threshold:
        return "negative"
    return "neutral"


def _build_narrative(phase: str, previous_phase_value: str | None) -> str:
    if previous_phase_value and previous_phase_value != phase:
        return f"Transitioned from {PHASE_LABELS[previous_phase_value]} to {PHASE_LABELS[phase]} based on explicit next-phase evidence."
    return {
        "Recovery": "Leading data is stabilizing after weakness, but conviction is not broad yet.",
        "Growth": "Leading, production, and demand data are improving together.",
        "Boom": "Growth remains strong and overheating evidence is now visible.",
        "Recession": "Labor and demand pressure are strong enough to dominate the cycle signal.",
    }[phase]


def _transition_keys_for_phase(phase: str, previous_phase_value: str | None) -> list[str]:
    if previous_phase_value and previous_phase_value != phase:
        return TRANSITION_METRICS.get(previous_phase_value, {}).get("next", [])
    return TRANSITION_METRICS.get(phase, {}).get("next", [])


def _phase_signals(observations: dict) -> dict[str, list[str]]:
    signals = {phase: [] for phase in PHASE_SEQUENCE}

    leading = observations.get("leading_index_change", 0.0) or 0.0
    industrial = observations.get("industrial_production_trend", observations.get("coincident_trend", "stable"))
    overtime = observations.get("overtime_trend", "stable")
    labor = observations.get("unemployment_trend", "stable")
    exports_yoy = observations.get("exports_yoy")
    pmi = observations.get("pmi")
    cci = observations.get("cci_total")
    sahm = observations.get("sahm_rule")
    inventory = observations.get("inventory_sales_ratio")

    if leading > 0:
        signals["Recovery"].append(f"領先指標維持改善 ({leading:.2f})")
    if labor != "rising":
        signals["Recovery"].append("就業壓力仍受控")
    if exports_yoy is not None and exports_yoy > 0:
        signals["Recovery"].append(f"出口重新回到正成長 ({exports_yoy:.1f}%)")
    if pmi is not None and pmi >= 50:
        signals["Recovery"].append(f"PMI 回到 50 以上 ({pmi:.1f})")

    if leading >= 0.2:
        signals["Growth"].append(f"領先指標動能轉強 ({leading:.2f})")
    if industrial == "improving":
        signals["Growth"].append("工業生產趨勢改善")
    if exports_yoy is not None and exports_yoy >= 5:
        signals["Growth"].append(f"出口成長明顯轉強 ({exports_yoy:.1f}%)")
    if pmi is not None and pmi >= 54:
        signals["Growth"].append(f"PMI 維持強勢擴張 ({pmi:.1f})")

    if cci is not None and cci >= 80:
        signals["Boom"].append(f"景氣熱度逼近過熱 ({cci:.1f})")
    if overtime == "rising":
        signals["Boom"].append("加班工時顯示需求進一步升溫")
    if _inventory_score(inventory) < 0:
        signals["Boom"].append("庫存壓力升高，接近高峰末段")

    if leading <= -0.2:
        signals["Recession"].append(f"領先指標轉弱 ({leading:.2f})")
    if industrial == "deteriorating":
        signals["Recession"].append("工業生產趨勢轉差")
    if labor == "rising":
        signals["Recession"].append("就業壓力升高")
    if exports_yoy is not None and exports_yoy < 0:
        signals["Recession"].append(f"出口轉為衰退 ({exports_yoy:.1f}%)")
    if pmi is not None and pmi < 50:
        signals["Recession"].append(f"PMI 跌破 50 ({pmi:.1f})")
    if sahm is not None and sahm >= 0.5:
        signals["Recession"].append(f"Sahm Rule 觸發 ({sahm:.2f})")

    return signals


def build_izaax_lens(observations: dict) -> LensDecision:
    phase_signals = _phase_signals(observations)
    phase = pick_phase_from_support(phase_signals)
    if len(phase_signals.get("Growth", [])) >= 2 and phase == "Recovery":
        phase = "Growth"

    leading_score = observations.get("leading_index_change", 0.0) or 0.0
    industrial_trend = observations.get("industrial_production_trend", observations.get("coincident_trend", "stable"))
    overtime_trend = observations.get("overtime_trend", "stable")
    labor_stress = 1.0 if observations.get("unemployment_trend") == "rising" else 0.0
    claims_trend = observations.get("unemployment_claims_trend", "stable")
    exports_yoy = observations.get("exports_yoy", 0.0) or 0.0
    pmi = observations.get("pmi")
    cci_level = observations.get("cci_total")
    cci_signal = "euphoria" if cci_level is not None and cci_level > 80 else ("warm" if cci_level is not None and cci_level > 70 else "neutral")
    sahm_value = observations.get("sahm_rule")
    inventory_score = _inventory_score(observations.get("inventory_sales_ratio"))

    reasons = list(phase_signals.get(phase, [])) or [f"Phase resolved to {phase} with limited explicit evidence."]

    metrics = [
        LensMetric("leading_index_change", "Leading Index Change", leading_score, "decimal", _metric_status(leading_score)),
        LensMetric("industrial_production_trend", "Industrial Production Trend", _direction_score(industrial_trend), "decimal", _metric_status(_direction_score(industrial_trend))),
        LensMetric("labor_stress", "Labor Stress", labor_stress, "decimal", "negative" if labor_stress else "positive"),
        LensMetric("overtime_trend", "Overtime Trend", _direction_score(overtime_trend), "decimal", _metric_status(_direction_score(overtime_trend))),
        LensMetric("exports_yoy", "Exports YoY", exports_yoy, "percent", _metric_status(exports_yoy)),
        LensMetric("unemployment_claims", "Unemployment Claims", observations.get("unemployment_claims") or 0.0, "decimal", "positive" if claims_trend == "falling" else "negative" if claims_trend == "rising" else "neutral", proxy_label="Proxy"),
        LensMetric("cci_level", "CCI", cci_level if cci_level is not None else 50.0, "decimal", "negative" if cci_signal == "euphoria" else "positive", proxy_label="Proxy"),
        LensMetric("pmi", "PMI", pmi if pmi is not None else 50.0, "decimal", "positive" if pmi is not None and pmi >= 50 else "negative" if pmi is not None else "neutral", proxy_label="Proxy"),
        LensMetric("sahm_rule", "Sahm Rule", sahm_value if sahm_value is not None else 0.0, "decimal", "negative" if sahm_value is not None and sahm_value >= 0.5 else "positive"),
        LensMetric("inventory_sales_ratio", "Inventory/Sales", inventory_score, "decimal", _metric_status(inventory_score)),
    ]

    return LensDecision(
        lens_id="izaax",
        title=LENS_TITLES["izaax"],
        phase=phase,
        phase_label=PHASE_LABELS[phase],
        reasons=reasons,
        metrics=metrics,
        transition_keys=_transition_keys_for_phase(phase, None),
        narrative=_build_narrative(phase, None),
        stance={
            "Recovery": "start building risk",
            "Growth": "hold trend exposure",
            "Boom": "trim risk",
            "Recession": "defend capital",
        }[phase],
    )


def build_izaax_history_row(month: str, observations: dict, previous_phase: str | None = None) -> LensHistoryRow:
    current = build_izaax_lens(observations)
    phase_signals = _phase_signals(observations)
    resolved = resolve_phase_transition(phase_signals, previous_phase, min_next_support=2)
    resolved_phase = resolved["phase"]
    return LensHistoryRow(
        month=month,
        as_of=observations["as_of"],
        phase=resolved_phase,
        phase_label=PHASE_LABELS[resolved_phase],
        reasons=list(phase_signals.get(resolved_phase, [])),
        metrics=current.metrics,
        previous_phase=previous_phase,
        previous_phase_label=PHASE_LABELS[previous_phase] if previous_phase else None,
        transition_keys=_transition_keys_for_phase(resolved_phase, previous_phase),
        narrative=_build_narrative(resolved_phase, previous_phase),
        stance={
            "Recovery": "start building risk",
            "Growth": "hold trend exposure",
            "Boom": "trim risk",
            "Recession": "defend capital",
        }[resolved_phase],
        decision_mode=resolved["decision_mode"],
        decision_summary=resolved["decision_summary"],
        support_current_phase_signals=list(resolved["support_current_phase_signals"]),
        support_next_phase_signals=list(resolved["support_next_phase_signals"]),
        conflict_signals=list(resolved["conflict_signals"]),
        supporting_signals=list(resolved["support_current_phase_signals"]),
        conflicting_signals=list(resolved["conflict_signals"]),
    )


def _format_display_value(value, display_format: str) -> str:
    if value is None:
        return "--"
    if isinstance(value, str):
        return value
    if display_format == "percent":
        return f"{value:.1f}%"
    return f"{value:.2f}"


def _get_metric_value_for_phase(metric_id: str, observations: dict):
    mapping = {
        "leading_index_change": observations.get("leading_index_change"),
        "industrial_production_trend": _direction_score(observations.get("industrial_production_trend", "stable")),
        "labor_stress": 1.0 if observations.get("unemployment_trend") == "rising" else 0.0,
        "overtime_trend": _direction_score(observations.get("overtime_trend", "stable")),
        "exports_yoy": observations.get("exports_yoy"),
        "unemployment_claims": observations.get("unemployment_claims"),
        "cci_level": observations.get("cci_total"),
        "pmi": observations.get("pmi"),
        "sahm_rule": observations.get("sahm_rule"),
        "inventory_sales_ratio": _inventory_score(observations.get("inventory_sales_ratio")),
    }
    return mapping.get(metric_id)


def _get_display_format_for_metric(metric_id: str) -> str:
    return "percent" if metric_id == "exports_yoy" else "decimal"


def _get_metric_label(metric_id: str) -> str:
    labels = {
        "leading_index_change": "Leading Index Change",
        "industrial_production_trend": "Industrial Production Trend",
        "labor_stress": "Labor Stress",
        "overtime_trend": "Overtime Trend",
        "exports_yoy": "Exports YoY",
        "unemployment_claims": "Unemployment Claims",
        "cci_level": "CCI",
        "pmi": "PMI",
        "sahm_rule": "Sahm Rule",
        "inventory_sales_ratio": "Inventory/Sales",
    }
    return labels.get(metric_id, metric_id)


def _month_label(observations: dict) -> str:
    month = observations.get("month")
    if month:
        return month
    as_of = observations.get("as_of", "")
    return str(as_of)[:7]


def build_izaax_transposed_bundle(current_observations: dict, history_observations: list[dict], max_months: int = 24) -> IzaaxTransposedBundle:
    all_obs = history_observations[-max_months:] + [current_observations]
    seen = set()
    deduped = []
    for obs in all_obs:
        month = _month_label(obs)
        if month not in seen:
            seen.add(month)
            deduped.append(obs)

    history_rows = []
    previous_phase_for_history = None
    for obs in deduped:
        month = _month_label(obs)
        history_row = build_izaax_history_row(month, obs, previous_phase_for_history)
        history_rows.append(history_row)
        previous_phase_for_history = history_row.phase

    latest_row = history_rows[-1]
    current_phase = latest_row.phase
    next_phase_value = next_phase(current_phase)
    prev_phase_value = previous_phase(current_phase)

    months = [_month_label(obs) for obs in deduped]
    month_columns = [
        {
            "month": row.month,
            "phase": row.phase,
            "phase_label": row.phase_label,
            "transition_keys": list(row.transition_keys),
            "decision_mode": row.decision_mode,
            "decision_summary": row.decision_summary,
            "support_current_phase_signals": list(row.support_current_phase_signals),
            "support_next_phase_signals": list(row.support_next_phase_signals),
            "conflict_signals": list(row.conflict_signals),
            "supporting_signals": list(row.supporting_signals),
            "conflicting_signals": list(row.conflicting_signals),
        }
        for row in history_rows
    ]
    metric_ids = [
        "leading_index_change",
        "industrial_production_trend",
        "labor_stress",
        "overtime_trend",
        "exports_yoy",
        "unemployment_claims",
        "cci_level",
        "pmi",
        "sahm_rule",
        "inventory_sales_ratio",
    ]
    metric_rows = []
    for metric_id in metric_ids:
        display_format = _get_display_format_for_metric(metric_id)
        values = []
        for obs in deduped:
            value = _get_metric_value_for_phase(metric_id, obs)
            values.append(
                {
                    "month": _month_label(obs),
                    "display_value": _format_display_value(value, display_format),
                    "status": "positive" if isinstance(value, (float, int)) and value > 0 else "negative" if isinstance(value, (float, int)) and value < 0 else "neutral",
                }
            )
        metric_rows.append(
            TransposedMetricRow(
                metric_id=metric_id,
                label=_get_metric_label(metric_id),
                display_format=display_format,
                is_transition_key=metric_id in latest_row.transition_keys,
                transition_direction="next" if metric_id in latest_row.transition_keys else "",
                values=values,
            )
        )

    return IzaaxTransposedBundle(
        current_phase=current_phase,
        current_phase_label=PHASE_LABELS[current_phase],
        next_phase=next_phase_value,
        prev_phase=prev_phase_value,
        phase_sequence=PHASE_SEQUENCE,
        transition_keys=list(latest_row.transition_keys),
        metric_rows=metric_rows,
        months=months,
        month_columns=month_columns,
        reasons=list(latest_row.reasons),
    )
