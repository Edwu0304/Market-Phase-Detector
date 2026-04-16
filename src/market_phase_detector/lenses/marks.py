from market_phase_detector.lenses.metric_sets import LENS_TITLES
from market_phase_detector.lenses.transition_logic import PHASE_SEQUENCE, pick_phase_from_support, resolve_phase_transition
from market_phase_detector.models.lenses import LensDecision, LensHistoryRow, LensMetric
from market_phase_detector.strategy_content import PHASE_LABELS


TRANSITION_METRICS = {
    "Recovery": ["credit_spread", "stock_index_yoy", "margin_balance"],
    "Growth": ["credit_spread", "cci_level", "margin_balance"],
    "Boom": ["credit_spread", "cci_level", "government_spending"],
    "Recession": ["credit_spread", "stock_index_yoy", "inventory_change"],
}


def _phase_signals(observations: dict) -> dict[str, list[str]]:
    signals = {phase: [] for phase in PHASE_SEQUENCE}

    stock_trend = observations.get("stock_trend", "stable")
    credit_trend = observations.get("credit_trend", "stable")
    inventory_trend = observations.get("inventory_trend", "stable")
    stock_yoy = observations.get("stock_index_yoy")
    credit_spread = observations.get("credit_spread")
    cci_level = observations.get("cci_total")
    margin_amount = observations.get("margin_amount")

    if stock_trend != "deteriorating":
        signals["Recovery"].append("風險偏好不再惡化")
    if credit_trend != "deteriorating":
        signals["Recovery"].append("信用壓力不再惡化")
    if credit_spread is not None and credit_spread < 1.0:
        signals["Recovery"].append(f"信用利差收斂 ({credit_spread:.2f})")

    if stock_trend == "improving":
        signals["Growth"].append("股市趨勢改善")
    if credit_trend == "improving":
        signals["Growth"].append("信用趨勢改善")
    if stock_yoy is not None and stock_yoy > 5:
        signals["Growth"].append(f"股市年增率具建設性 ({stock_yoy:.1f}%)")

    if cci_level is not None and cci_level >= 80:
        signals["Boom"].append(f"景氣與情緒過熱 ({cci_level:.1f})")
    if margin_amount is not None and margin_amount > 500000000:
        signals["Boom"].append("融資餘額過熱")
    if stock_yoy is not None and stock_yoy > 10:
        signals["Boom"].append(f"股市漲幅過熱 ({stock_yoy:.1f}%)")

    if stock_trend == "deteriorating":
        signals["Recession"].append("股市趨勢轉差")
    if credit_trend == "deteriorating":
        signals["Recession"].append("信用趨勢轉差")
    if inventory_trend == "deteriorating":
        signals["Recession"].append("庫存趨勢轉差")
    if credit_spread is not None and credit_spread > 2:
        signals["Recession"].append(f"信用利差明顯擴大 ({credit_spread:.2f})")

    return signals


def _stance_for_phase(phase: str) -> str:
    return {
        "Recovery": "rebuild exposure",
        "Growth": "stay invested",
        "Boom": "reduce crowding risk",
        "Recession": "protect capital",
    }[phase]


def _build_narrative(phase: str, previous_phase: str | None) -> str:
    if previous_phase and previous_phase != phase:
        return f"Transitioned from {PHASE_LABELS[previous_phase]} to {PHASE_LABELS[phase]} as risk appetite and credit conditions changed."
    return {
        "Recovery": "Credit stress is easing before full risk appetite returns.",
        "Growth": "Risk appetite and credit are constructive without obvious extremes.",
        "Boom": "Risk appetite is strong enough that complacency becomes the main risk.",
        "Recession": "Credit and risk appetite are both weak enough to dominate positioning.",
    }[phase]


def build_marks_lens(observations: dict) -> LensDecision:
    phase_signals = _phase_signals(observations)
    phase = pick_phase_from_support(phase_signals)
    stock_yoy = observations.get("stock_index_yoy")
    credit_change = observations.get("credit_change")
    inventory_change = observations.get("inventory_change")
    credit_spread = observations.get("credit_spread")
    cci_level = observations.get("cci_total")
    government_spending = observations.get("government_spending")
    margin_amount = observations.get("margin_amount")
    credit_spread_signal = "wide" if credit_spread is not None and credit_spread > 2 else ("narrow" if credit_spread is not None and credit_spread < 0.5 else "neutral")
    cci_euphoria = bool(cci_level is not None and cci_level > 80)
    margin_excessive = bool(margin_amount is not None and margin_amount > 500000000)

    metrics = [
        LensMetric("stock_index_yoy", "Stock Index YoY", stock_yoy if stock_yoy is not None else 0.0, "percent", "positive" if (stock_yoy or 0) > 0 else "negative" if (stock_yoy or 0) < 0 else "neutral"),
        LensMetric("credit_change", "Credit Change", credit_change if credit_change is not None else 0.0, "decimal", "positive" if (credit_change or 0) > 0 else "negative" if (credit_change or 0) < 0 else "neutral"),
        LensMetric("inventory_change", "Inventory Change", inventory_change if inventory_change is not None else 0.0, "decimal", "negative" if (inventory_change or 0) > 0 else "positive" if (inventory_change or 0) < 0 else "neutral"),
        LensMetric("credit_spread", "Credit Spread", credit_spread if credit_spread is not None else 0.0, "spread", "negative" if credit_spread_signal == "wide" else "positive" if credit_spread_signal == "narrow" else "neutral"),
        LensMetric("cci_level", "CCI", cci_level if cci_level is not None else 50.0, "decimal", "negative" if cci_euphoria else "positive" if cci_level is not None else "neutral", proxy_label="Proxy"),
        LensMetric("government_spending", "Government Spending", government_spending if government_spending is not None else 0.0, "decimal", "neutral", proxy_label="Planned"),
        LensMetric("margin_balance", "Margin Balance", margin_amount if margin_amount is not None else 0.0, "decimal", "negative" if margin_excessive else "positive" if margin_amount is not None else "neutral", proxy_label="Proxy"),
    ]

    return LensDecision(
        lens_id="marks",
        title=LENS_TITLES["marks"],
        phase=phase,
        phase_label=PHASE_LABELS[phase],
        reasons=list(phase_signals.get(phase, [])),
        metrics=metrics,
        transition_keys=TRANSITION_METRICS[phase],
        narrative=_build_narrative(phase, None),
        stance=_stance_for_phase(phase),
    )


def build_marks_history_row(month: str, observations: dict, previous_phase: str | None = None) -> LensHistoryRow:
    current = build_marks_lens(observations)
    phase_signals = _phase_signals(observations)
    resolved = resolve_phase_transition(phase_signals, previous_phase, min_next_support=2)
    phase = resolved["phase"]
    transition_keys = TRANSITION_METRICS[previous_phase] if previous_phase and previous_phase != phase else TRANSITION_METRICS[phase]
    return LensHistoryRow(
        month=month,
        as_of=observations["as_of"],
        phase=phase,
        phase_label=PHASE_LABELS[phase],
        reasons=list(phase_signals.get(phase, [])),
        metrics=current.metrics,
        previous_phase=previous_phase,
        previous_phase_label=PHASE_LABELS[previous_phase] if previous_phase else None,
        transition_keys=transition_keys,
        narrative=_build_narrative(phase, previous_phase),
        stance=_stance_for_phase(phase),
        decision_mode=resolved["decision_mode"],
        decision_summary=resolved["decision_summary"],
        support_current_phase_signals=list(resolved["support_current_phase_signals"]),
        support_next_phase_signals=list(resolved["support_next_phase_signals"]),
        conflict_signals=list(resolved["conflict_signals"]),
        supporting_signals=list(resolved["support_current_phase_signals"]),
        conflicting_signals=list(resolved["conflict_signals"]),
    )
