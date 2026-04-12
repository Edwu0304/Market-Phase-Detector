from market_phase_detector.lenses.metric_sets import LENS_TITLES
from market_phase_detector.models.lenses import (
    IzaaxTransposedBundle,
    LensDecision,
    LensHistoryRow,
    LensMetric,
    TransposedMetricRow,
)
from market_phase_detector.strategy_content import PHASE_LABELS


PHASE_SEQUENCE = ["Recovery", "Growth", "Boom", "Recession"]

TRANSITION_METRICS = {
    "Recovery": {"next": ["leading_index_change", "industrial_production_trend", "pmi"], "prev": ["labor_stress", "unemployment_claims"]},
    "Growth": {"next": ["cci_level", "inventory_sales_ratio", "exports_yoy"], "prev": ["leading_index_change", "pmi"]},
    "Boom": {"next": ["sahm_rule", "unemployment_claims", "inventory_sales_ratio"], "prev": ["cci_level", "leading_index_change"]},
    "Recession": {"next": ["leading_index_change", "pmi", "sahm_rule"], "prev": ["inventory_sales_ratio", "labor_stress"]},
}


def _direction_score(value: str) -> float:
    mapping = {"improving": 1.0, "stable": 0.0, "deteriorating": -1.0, "falling": 1.0, "rising": -1.0}
    return mapping.get(value, 0.0)


def _phase_from_score(score: float, labor_stress: float) -> str:
    if labor_stress >= 1.0 and score <= -0.5:
        return "Recession"
    if score >= 2.4:
        return "Boom"
    if score >= 0.8:
        return "Growth"
    return "Recovery"


def _stance_for_phase(phase: str) -> str:
    return {
        "Recovery": "start building risk",
        "Growth": "hold trend exposure",
        "Boom": "trim risk",
        "Recession": "defend capital",
    }[phase]


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


def _build_narrative(phase: str, previous_phase: str | None) -> str:
    if previous_phase and previous_phase != phase:
        return f"Transitioned from {PHASE_LABELS[previous_phase]} to {PHASE_LABELS[phase]} as leading and cycle data changed."
    return {
        "Recovery": "Leading data is stabilizing after weakness, but conviction is not broad yet.",
        "Growth": "Leading, production, and demand data are improving together.",
        "Boom": "Growth is still positive, but risk of overheating is rising.",
        "Recession": "Labor and demand pressure are strong enough to dominate the cycle signal.",
    }[phase]


def _transition_keys_for_phase(phase: str, previous_phase: str | None) -> list[str]:
    if previous_phase and previous_phase != phase:
        return TRANSITION_METRICS.get(previous_phase, {}).get("next", [])
    return TRANSITION_METRICS.get(phase, {}).get("next", [])


def _phase_votes(observations: dict) -> dict[str, list[str]]:
    votes = {phase: [] for phase in PHASE_SEQUENCE}

    leading = observations.get("leading_index_change", 0.0) or 0.0
    if leading >= 0.6:
        votes["Growth"].append(f"領先指標明顯轉強 ({leading:.2f})")
    elif leading > 0:
        votes["Recovery"].append(f"領先指標回升 ({leading:.2f})")
    elif leading <= -0.2:
        votes["Recession"].append(f"領先指標轉弱 ({leading:.2f})")

    industrial = observations.get("industrial_production_trend", "stable")
    if industrial == "improving":
        votes["Growth"].append("工業生產趨勢改善")
    elif industrial == "deteriorating":
        votes["Recession"].append("工業生產趨勢惡化")

    overtime = observations.get("overtime_trend", "stable")
    if overtime == "rising":
        votes["Growth"].append("加班工時轉強")
    elif overtime == "falling":
        votes["Recession"].append("加班工時轉弱")

    labor_stress = observations.get("unemployment_trend")
    if labor_stress == "rising":
        votes["Recession"].append("失業壓力上升")
    else:
        votes["Recovery"].append("失業壓力未惡化")

    exports_yoy = observations.get("exports_yoy")
    if exports_yoy is not None:
        if exports_yoy >= 5:
            votes["Growth"].append(f"出口年增強勁 ({exports_yoy:.1f}%)")
        elif exports_yoy > 0:
            votes["Recovery"].append(f"出口轉正 ({exports_yoy:.1f}%)")
        else:
            votes["Recession"].append(f"出口轉負 ({exports_yoy:.1f}%)")

    pmi = observations.get("pmi")
    if pmi is not None:
        if pmi >= 54:
            votes["Growth"].append(f"PMI 維持擴張 ({pmi:.1f})")
        elif pmi >= 50:
            votes["Recovery"].append(f"PMI 站回擴張線 ({pmi:.1f})")
        else:
            votes["Recession"].append(f"PMI 跌破擴張線 ({pmi:.1f})")

    cci = observations.get("cci_total")
    if cci is not None:
        if cci > 80:
            votes["Boom"].append(f"信心偏熱 ({cci:.1f})")
        elif cci > 70:
            votes["Growth"].append(f"信心偏強 ({cci:.1f})")

    sahm = observations.get("sahm_rule")
    if sahm is not None and sahm >= 0.5:
        votes["Recession"].append(f"Sahm Rule 偏高 ({sahm:.2f})")

    inventory_score = _inventory_score(observations.get("inventory_sales_ratio"))
    if inventory_score > 0:
        votes["Recovery"].append("庫存循環改善")
    elif inventory_score < 0:
        votes["Recession"].append("庫存訊號偏弱")

    return votes


def _resolve_locked_cycle(raw_phase: str, previous_phase: str | None, votes: dict[str, list[str]]) -> tuple[str, str, list[str], list[str], str]:
    if previous_phase is None:
        supporting = list(votes.get(raw_phase, []))
        return raw_phase, "initial", supporting, [], f"初始月份直接採用 {PHASE_LABELS[raw_phase]}。"

    next_phase = _next_phase(previous_phase)
    previous_support = len(votes.get(previous_phase, []))
    next_support = len(votes.get(next_phase, []))

    if raw_phase == previous_phase:
        return (
            previous_phase,
            "hold",
            list(votes.get(previous_phase, [])),
            list(votes.get(next_phase, [])),
            f"訊號不足以推進到 {PHASE_LABELS[next_phase]}，因此維持 {PHASE_LABELS[previous_phase]}。",
        )

    if raw_phase == next_phase:
        return (
            next_phase,
            "advance" if next_support > previous_support else "ambiguous_advance",
            list(votes.get(next_phase, [])),
            list(votes.get(previous_phase, [])),
            f"核心訊號允許由 {PHASE_LABELS[previous_phase]} 前進到 {PHASE_LABELS[next_phase]}，因此只前進一階。",
        )

    if next_support >= previous_support + 2 and next_support >= 3:
        return (
            next_phase,
            "ambiguous_advance",
            list(votes.get(next_phase, [])),
            list(votes.get(previous_phase, [])) + list(votes.get(raw_phase, [])),
            f"原始訊號有混亂，但推進到 {PHASE_LABELS[next_phase]} 的證據明顯較集中，因此只前進一階。",
        )

    conflicts = []
    for phase, signals in votes.items():
        if phase != previous_phase:
            conflicts.extend(signals)
    return (
        previous_phase,
        "ambiguous_hold",
        list(votes.get(previous_phase, [])),
        conflicts,
        f"訊號彼此衝突或會破壞固定循環順序，因此保守維持 {PHASE_LABELS[previous_phase]}。",
    )


def build_izaax_lens(observations: dict) -> LensDecision:
    leading_score = observations.get("leading_index_change", 0.0) or 0.0
    industrial_trend = observations.get("industrial_production_trend", "stable")
    industrial_score = _direction_score(industrial_trend)
    overtime_trend = observations.get("overtime_trend", "stable")
    overtime_score = _direction_score(overtime_trend)
    labor_stress = 1.0 if observations.get("unemployment_trend") == "rising" else 0.0
    claims_trend = observations.get("unemployment_claims_trend", "stable")
    claims_score = _direction_score(claims_trend)
    exports_yoy = observations.get("exports_yoy", 0.0) or 0.0
    export_score = 0.6 if exports_yoy > 0 else (-0.6 if exports_yoy < 0 else 0.0)
    pmi = observations.get("pmi")
    pmi_score = 0.8 if pmi is not None and pmi >= 50 else (-0.8 if pmi is not None else 0.0)
    cci_level = observations.get("cci_total")
    cci_signal = "euphoria" if cci_level is not None and cci_level > 80 else ("warm" if cci_level is not None and cci_level > 70 else "neutral")
    sahm_value = observations.get("sahm_rule")
    inventory_score = _inventory_score(observations.get("inventory_sales_ratio"))

    score = leading_score + industrial_score + overtime_score + claims_score * 0.5 + export_score + pmi_score + inventory_score * 0.3 - labor_stress
    phase = _phase_from_score(score, labor_stress)

    reasons = [
        f"Leading index change {leading_score:.2f}",
        f"Industrial trend {industrial_trend}",
        f"Overtime trend {overtime_trend}",
        f"Exports YoY {exports_yoy:.1f}%",
    ]
    if observations.get("unemployment_claims") is not None:
        reasons.append(f"Claims trend {claims_trend}")
    if pmi is not None:
        reasons.append(f"PMI {pmi:.1f}")
    if cci_level is not None:
        reasons.append(f"CCI {cci_level:.1f}")
    if sahm_value is not None and sahm_value >= 0.5:
        reasons.append(f"Sahm rule {sahm_value:.2f}")

    metrics = [
        LensMetric("leading_index_change", "Leading Index Change", leading_score, "decimal", _metric_status(leading_score)),
        LensMetric("industrial_production_trend", "Industrial Production Trend", industrial_score, "decimal", _metric_status(industrial_score)),
        LensMetric("labor_stress", "Labor Stress", labor_stress, "decimal", "negative" if labor_stress else "positive"),
        LensMetric("overtime_trend", "Overtime Trend", overtime_score, "decimal", _metric_status(overtime_score)),
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
        stance=_stance_for_phase(phase),
    )


def build_izaax_history_row(month: str, observations: dict, previous_phase: str | None = None) -> LensHistoryRow:
    current = build_izaax_lens(observations)
    votes = _phase_votes(observations)
    resolved_phase, decision_mode, supporting_signals, conflicting_signals, decision_summary = _resolve_locked_cycle(
        current.phase,
        previous_phase,
        votes,
    )
    transition_keys = TRANSITION_METRICS.get(previous_phase, {}).get("next", []) if previous_phase and resolved_phase != previous_phase else []
    return LensHistoryRow(
        month=month,
        as_of=observations["as_of"],
        phase=resolved_phase,
        phase_label=PHASE_LABELS[resolved_phase],
        reasons=current.reasons,
        metrics=current.metrics,
        previous_phase=previous_phase,
        previous_phase_label=PHASE_LABELS[previous_phase] if previous_phase else None,
        transition_keys=transition_keys,
        narrative=_build_narrative(resolved_phase, previous_phase),
        stance=_stance_for_phase(resolved_phase),
        decision_mode=decision_mode,
        decision_summary=decision_summary,
        supporting_signals=supporting_signals,
        conflicting_signals=conflicting_signals,
    )


def _phase_index(phase: str) -> int:
    try:
        return PHASE_SEQUENCE.index(phase)
    except ValueError:
        return 0


def _next_phase(phase: str) -> str:
    idx = _phase_index(phase)
    return PHASE_SEQUENCE[(idx + 1) % len(PHASE_SEQUENCE)]


def _prev_phase(phase: str) -> str:
    idx = _phase_index(phase)
    return PHASE_SEQUENCE[(idx - 1) % len(PHASE_SEQUENCE)]


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
    next_phase = _next_phase(current_phase)
    prev_phase = _prev_phase(current_phase)

    months = [_month_label(obs) for obs in deduped]
    month_columns = [
        {
            "month": row.month,
            "phase": row.phase,
            "phase_label": row.phase_label,
            "transition_keys": list(row.transition_keys),
            "decision_mode": row.decision_mode,
            "decision_summary": row.decision_summary,
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
        next_phase=next_phase,
        prev_phase=prev_phase,
        phase_sequence=PHASE_SEQUENCE,
        transition_keys=list(latest_row.transition_keys),
        metric_rows=metric_rows,
        months=months,
        month_columns=month_columns,
        reasons=list(latest_row.reasons),
    )
