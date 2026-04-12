from market_phase_detector.lenses.metric_sets import LENS_TITLES
from market_phase_detector.models.lenses import LensDecision, LensHistoryRow, LensMetric
from market_phase_detector.strategy_content import PHASE_LABELS


TRANSITION_METRICS = {
    "Recovery": ["credit_spread", "stock_index_yoy", "margin_balance"],
    "Growth": ["credit_spread", "cci_level", "margin_balance"],
    "Boom": ["credit_spread", "cci_level", "government_spending"],
    "Recession": ["credit_spread", "stock_index_yoy", "inventory_change"],
}


def _phase_from_risk(stock_trend: str, credit_trend: str, inventory_trend: str) -> str:
    stock_score = 1.0 if stock_trend == "improving" else (-1.0 if stock_trend == "deteriorating" else 0.0)
    credit_score = 1.0 if credit_trend == "improving" else (-1.0 if credit_trend == "deteriorating" else 0.0)
    inventory_penalty = -0.5 if inventory_trend == "deteriorating" else 0.0
    total = stock_score + credit_score + inventory_penalty
    if credit_trend == "deteriorating" and stock_trend == "deteriorating":
        return "Recession"
    if total >= 1.5:
        return "Boom"
    if total >= 0.5:
        return "Growth"
    return "Recovery"


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
    stock_trend = observations.get("stock_trend", "stable")
    credit_trend = observations.get("credit_trend", "stable")
    inventory_trend = observations.get("inventory_trend", "stable")
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

    phase = _phase_from_risk(stock_trend, credit_trend, inventory_trend)
    reasons = [
        f"Stock trend {stock_trend}",
        f"Credit trend {credit_trend}",
        f"Inventory trend {inventory_trend}",
    ]
    if credit_spread is not None:
        reasons.append(f"Credit spread {credit_spread:.2f}")
    if cci_level is not None:
        reasons.append(f"CCI {cci_level:.1f}")
    if margin_amount is not None:
        reasons.append(f"Margin balance {margin_amount:.0f}")

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
        reasons=reasons,
        metrics=metrics,
        transition_keys=TRANSITION_METRICS[phase],
        narrative=_build_narrative(phase, None),
        stance=_stance_for_phase(phase),
    )


def build_marks_history_row(month: str, observations: dict, previous_phase: str | None = None) -> LensHistoryRow:
    current = build_marks_lens(observations)
    transition_keys = TRANSITION_METRICS[previous_phase] if previous_phase and previous_phase != current.phase else TRANSITION_METRICS[current.phase]
    return LensHistoryRow(
        month=month,
        as_of=observations["as_of"],
        phase=current.phase,
        phase_label=current.phase_label,
        reasons=current.reasons,
        metrics=current.metrics,
        previous_phase=previous_phase,
        previous_phase_label=PHASE_LABELS[previous_phase] if previous_phase else None,
        transition_keys=transition_keys,
        narrative=_build_narrative(current.phase, previous_phase),
        stance=_stance_for_phase(current.phase),
    )
