from market_phase_detector.lenses.metric_sets import LENS_TITLES
from market_phase_detector.models.lenses import LensDecision, LensHistoryRow, LensMetric
from market_phase_detector.strategy_content import PHASE_LABELS


TRANSITION_METRICS = {
    "Recovery": ["bank_lending_rate", "credit_change", "m2_yoy"],
    "Growth": ["yield_curve", "pe_ratio", "margin_balance"],
    "Boom": ["yield_curve", "bank_lending_rate", "margin_balance"],
    "Recession": ["bank_lending_rate", "credit_change", "yield_curve"],
}


def _phase_from_inputs(rate_trend: str, credit_trend: str, money_supply_trend: str) -> str:
    rate_score = 1.0 if rate_trend == "falling" else (-1.0 if rate_trend == "rising" else 0.0)
    credit_score = 1.0 if credit_trend == "improving" else (-1.0 if credit_trend == "deteriorating" else 0.0)
    money_score = 1.0 if money_supply_trend == "improving" else (-1.0 if money_supply_trend == "deteriorating" else 0.0)
    total = rate_score + credit_score + money_score
    if rate_trend == "rising" and credit_trend == "deteriorating":
        return "Recession"
    if total >= 2.0:
        return "Boom"
    if total >= 0.5:
        return "Growth"
    return "Recovery"


def _stance_for_phase(phase: str) -> str:
    return {
        "Recovery": "turn risk back on",
        "Growth": "hold cyclical exposure",
        "Boom": "watch overheating",
        "Recession": "de-risk",
    }[phase]


def _build_narrative(phase: str, previous_phase: str | None) -> str:
    if previous_phase and previous_phase != phase:
        return f"Transitioned from {PHASE_LABELS[previous_phase]} to {PHASE_LABELS[phase]} as rates, credit, and liquidity shifted."
    return {
        "Recovery": "Rates and liquidity are stabilizing, but market confirmation is still early.",
        "Growth": "Rates, credit, and liquidity all support a constructive cycle backdrop.",
        "Boom": "Liquidity is still supportive, but valuation and positioning need more caution.",
        "Recession": "Tight rates and weak credit dominate the market cycle signal.",
    }[phase]


def build_urakami_lens(observations: dict) -> LensDecision:
    rate_trend = observations.get("rate_trend", "stable")
    credit_trend = observations.get("credit_trend", "stable")
    money_supply_trend = observations.get("money_supply_trend", "stable")
    bank_lending_rate = observations.get("bank_lending_rate")
    credit_change = observations.get("credit_change")
    m1b_change = observations.get("m1b_change")
    m2_yoy = observations.get("m2_yoy")
    pe_ratio = observations.get("pe_ratio")
    yield_spread = observations.get("yield_curve_spread")
    margin_amount = observations.get("margin_amount")
    margin_trend = observations.get("margin_trend", "stable")

    phase = _phase_from_inputs(rate_trend, credit_trend, money_supply_trend)
    yield_inverted = yield_spread is not None and yield_spread < 0
    pe_signal = "overvalued" if pe_ratio is not None and pe_ratio > 25 else ("cheap" if pe_ratio is not None and pe_ratio < 15 else "neutral")

    reasons = [
        f"Rate trend {rate_trend}",
        f"Credit trend {credit_trend}",
        f"Money trend {money_supply_trend}",
    ]
    if bank_lending_rate is not None:
        reasons.append(f"Bank lending rate {bank_lending_rate:.3f}%")
    if m2_yoy is not None:
        reasons.append(f"M2 YoY {m2_yoy:.2f}%")
    if pe_ratio is not None:
        reasons.append(f"PE ratio {pe_ratio:.2f}")
    if yield_inverted:
        reasons.append("Yield curve inverted")

    metrics = [
        LensMetric("bank_lending_rate", "Bank Lending Rate", bank_lending_rate if bank_lending_rate is not None else 0.0, "percent", "positive" if rate_trend == "falling" else "negative" if rate_trend == "rising" else "neutral"),
        LensMetric("credit_change", "Credit Change", credit_change if credit_change is not None else 0.0, "decimal", "positive" if (credit_change or 0) > 0 else "negative" if (credit_change or 0) < 0 else "neutral"),
        LensMetric("m1b_change", "M1B Change", m1b_change if m1b_change is not None else 0.0, "decimal", "positive" if (m1b_change or 0) > 0 else "negative" if (m1b_change or 0) < 0 else "neutral"),
        LensMetric("m2_yoy", "M2 YoY", m2_yoy if m2_yoy is not None else 0.0, "percent", "positive" if money_supply_trend == "improving" else "negative" if money_supply_trend == "deteriorating" else "neutral", proxy_label="Proxy"),
        LensMetric("pe_ratio", "PE Ratio", pe_ratio if pe_ratio is not None else 0.0, "decimal", "negative" if pe_signal == "overvalued" else "positive" if pe_signal == "cheap" else "neutral", proxy_label="Proxy"),
        LensMetric("yield_curve", "Yield Curve Spread", yield_spread if yield_spread is not None else 0.0, "spread", "negative" if yield_inverted else "positive" if yield_spread is not None else "neutral", proxy_label="Proxy"),
        LensMetric("margin_balance", "Margin Balance", margin_amount if margin_amount is not None else 0.0, "decimal", "negative" if margin_trend == "excessive" else "positive" if margin_trend == "moderate" else "neutral", proxy_label="Proxy"),
    ]

    return LensDecision(
        lens_id="urakami",
        title=LENS_TITLES["urakami"],
        phase=phase,
        phase_label=PHASE_LABELS[phase],
        reasons=reasons,
        metrics=metrics,
        transition_keys=TRANSITION_METRICS[phase],
        narrative=_build_narrative(phase, None),
        stance=_stance_for_phase(phase),
    )


def build_urakami_history_row(month: str, observations: dict, previous_phase: str | None = None) -> LensHistoryRow:
    current = build_urakami_lens(observations)
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
