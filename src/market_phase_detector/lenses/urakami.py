from market_phase_detector.lenses.metric_sets import LENS_TITLES
from market_phase_detector.lenses.transition_logic import PHASE_SEQUENCE, next_phase, pick_phase_from_support, resolve_phase_transition
from market_phase_detector.models.lenses import LensDecision, LensHistoryRow, LensMetric, SemanticLensRow
from market_phase_detector.strategy_content import PHASE_LABELS


TRANSITION_METRICS = {
    "Recovery": ["bank_lending_rate", "credit_change", "m2_yoy"],
    "Growth": ["yield_curve", "pe_ratio", "margin_balance"],
    "Boom": ["yield_curve", "bank_lending_rate", "margin_balance"],
    "Recession": ["bank_lending_rate", "credit_change", "yield_curve"],
}

URAKAMI_SEMANTIC_ROW_SPECS = [
    {
        "row_id": "urakami-rate-direction",
        "master_category": "政策與短率方向",
        "master_description": "判斷金融相場是否啟動的第一層利率觀察。",
        "site_metric_label": "銀行放款利率 / rate trend",
        "source_type": "proxy",
        "metric_ids": ["bank_lending_rate"],
        "transition_role": "advance",
    },
    {
        "row_id": "urakami-credit-liquidity",
        "master_category": "信用與流動性",
        "master_description": "觀察信用擴張與貨幣供給是否支撐市場向上。",
        "site_metric_label": "credit change / M2 YoY / M1B",
        "source_type": "proxy",
        "metric_ids": ["credit_change", "m2_yoy", "m1b_change"],
        "transition_role": "advance",
    },
    {
        "row_id": "urakami-yield-curve",
        "master_category": "殖利率曲線",
        "master_description": "觀察陡峭化、平坦化與倒掛所代表的景氣轉折。",
        "site_metric_label": "Yield Curve Spread",
        "source_type": "proxy",
        "metric_ids": ["yield_curve"],
        "transition_role": "risk",
    },
    {
        "row_id": "urakami-valuation",
        "master_category": "估值與過熱",
        "master_description": "觀察 PER 是否從金融相場走向過熱。",
        "site_metric_label": "PE Ratio",
        "source_type": "proxy",
        "metric_ids": ["pe_ratio"],
        "transition_role": "risk",
    },
    {
        "row_id": "urakami-leverage",
        "master_category": "市場槓桿與擁擠",
        "master_description": "觀察融資餘額與擁擠交易是否升溫。",
        "site_metric_label": "Margin Balance",
        "source_type": "proxy",
        "metric_ids": ["margin_balance"],
        "transition_role": "risk",
    },
]


def _phase_signals(observations: dict) -> dict[str, list[str]]:
    signals = {phase: [] for phase in PHASE_SEQUENCE}

    rate_trend = observations.get("rate_trend", "stable")
    credit_trend = observations.get("credit_trend", "stable")
    money_trend = observations.get("money_supply_trend", "stable")
    bank_lending_rate = observations.get("bank_lending_rate")
    m2_yoy = observations.get("m2_yoy")
    pe_ratio = observations.get("pe_ratio")
    yield_spread = observations.get("yield_curve_spread")
    margin_trend = observations.get("margin_trend", "stable")
    margin_amount = observations.get("margin_amount")

    if rate_trend != "rising":
      signals["Recovery"].append("利率不再持續緊縮")
    if credit_trend != "deteriorating":
      signals["Recovery"].append("信用環境止穩")
    if money_trend != "deteriorating":
      signals["Recovery"].append("流動性不再收縮")

    if rate_trend == "falling":
        signals["Growth"].append("利率開始走寬鬆")
    if credit_trend == "improving":
        signals["Growth"].append("信用擴張改善")
    if money_trend == "improving":
        signals["Growth"].append("貨幣供給轉為擴張")
    if bank_lending_rate is not None and bank_lending_rate <= 2.2:
        signals["Growth"].append(f"放款利率仍具支撐 ({bank_lending_rate:.3f}%)")

    if pe_ratio is not None and pe_ratio >= 25:
        signals["Boom"].append(f"估值偏高 ({pe_ratio:.2f})")
    if margin_trend == "excessive" or (margin_amount is not None and margin_amount > 500000000):
        signals["Boom"].append("槓桿部位過熱")
    if yield_spread is not None and yield_spread >= 0.8:
        signals["Boom"].append(f"殖利率曲線仍偏熱 ({yield_spread:.2f})")

    if rate_trend == "rising":
        signals["Recession"].append("利率重新偏緊")
    if credit_trend == "deteriorating":
        signals["Recession"].append("信用條件惡化")
    if money_trend == "deteriorating":
        signals["Recession"].append("貨幣供給收縮")
    if yield_spread is not None and yield_spread < 0:
        signals["Recession"].append(f"殖利率曲線倒掛 ({yield_spread:.2f})")

    if m2_yoy is not None and m2_yoy >= 6.0:
        signals["Growth"].append(f"M2 維持支撐 ({m2_yoy:.2f}%)")

    return signals


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


def _build_semantic_rows(metrics: list[LensMetric], transition_keys: list[str]) -> list[SemanticLensRow]:
    metric_map = {metric.metric_id: metric for metric in metrics}
    rows = []
    for spec in URAKAMI_SEMANTIC_ROW_SPECS:
        current_values = []
        for metric_id in spec["metric_ids"]:
            metric = metric_map.get(metric_id)
            if metric is None:
                continue
            metric_dict = metric.to_dict()
            current_values.append(
                {
                    "metric_id": metric_id,
                    "label": metric_dict["label"],
                    "display_value": metric_dict["display_value"],
                    "status": metric_dict["status"],
                }
            )
        rows.append(
            SemanticLensRow(
                row_id=spec["row_id"],
                master_category=spec["master_category"],
                master_description=spec["master_description"],
                site_metric_label=spec["site_metric_label"],
                source_type=spec["source_type"],
                metric_ids=list(spec["metric_ids"]),
                current_values=current_values,
                transition_role=spec["transition_role"],
                is_transition_driver=any(metric_id in transition_keys for metric_id in spec["metric_ids"]),
            )
        )
    return rows


def build_urakami_lens(observations: dict) -> LensDecision:
    phase_signals = _phase_signals(observations)
    phase = pick_phase_from_support(phase_signals)
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
    yield_inverted = yield_spread is not None and yield_spread < 0
    pe_signal = "overvalued" if pe_ratio is not None and pe_ratio > 25 else ("cheap" if pe_ratio is not None and pe_ratio < 15 else "neutral")

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
        reasons=list(phase_signals.get(phase, [])),
        metrics=metrics,
        semantic_rows=_build_semantic_rows(metrics, TRANSITION_METRICS[phase]),
        transition_keys=TRANSITION_METRICS[phase],
        narrative=_build_narrative(phase, None),
        stance=_stance_for_phase(phase),
    )


def build_urakami_history_row(month: str, observations: dict, previous_phase: str | None = None) -> LensHistoryRow:
    current = build_urakami_lens(observations)
    phase_signals = _phase_signals(observations)
    resolved = resolve_phase_transition(phase_signals, previous_phase, min_next_support=2)
    if previous_phase and resolved["decision_mode"] == "override":
        resolved["phase"] = previous_phase
        resolved["decision_mode"] = "hold"
        resolved["decision_summary"] = f"Hold {PHASE_LABELS[previous_phase]}; conflicting signals are noted but not strong enough for a regime change."
    phase = resolved["phase"]
    transition_keys = TRANSITION_METRICS[previous_phase] if previous_phase and previous_phase != phase else TRANSITION_METRICS[phase]
    return LensHistoryRow(
        month=month,
        as_of=observations["as_of"],
        phase=phase,
        phase_label=PHASE_LABELS[phase],
        reasons=list(phase_signals.get(phase, [])),
        metrics=current.metrics,
        semantic_rows=_build_semantic_rows(current.metrics, transition_keys),
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
