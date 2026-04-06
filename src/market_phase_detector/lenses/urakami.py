from market_phase_detector.lenses.metric_sets import LENS_TITLES
from market_phase_detector.models.lenses import LensDecision, LensHistoryRow, LensMetric
from market_phase_detector.strategy_content import PHASE_LABELS


def _phase_from_inputs(rate_trend: str, credit_trend: str, money_supply_trend: str) -> str:
    """使用真實利率、信用、貨幣供給判斷相位"""
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


def _rate_trend_label(trend: str) -> str:
    mapping = {"falling": "降息", "stable": "持平", "rising": "升息"}
    return mapping.get(trend, trend)


def build_urakami_lens(observations: dict) -> LensDecision:
    # 使用真實指標
    rate_trend = observations.get("rate_trend", "stable")
    credit_trend = observations.get("credit_trend", "stable")
    money_supply_trend = observations.get("money_supply_trend", "stable")
    bank_lending_rate = observations.get("bank_lending_rate", 0.0)
    credit_change = observations.get("credit_change", 0.0)
    m1b_change = observations.get("m1b_change", 0.0)

    # 新增：本益比
    pe_ratio = observations.get("pe_ratio", None)
    pe_signal = "overvalued" if pe_ratio and pe_ratio > 25 else ("reasonable" if pe_ratio and pe_ratio < 15 else "neutral")

    # 新增：殖利率曲線利差
    yield_spread = observations.get("yield_curve_spread", None)
    yield_inverted = yield_spread is not None and yield_spread < 0

    # 新增：融資餘額趨勢
    margin_amount = observations.get("margin_amount", None)
    margin_trend = observations.get("margin_trend", "stable")

    phase = _phase_from_inputs(rate_trend, credit_trend, money_supply_trend)

    reasons = [
        f"銀行放款利率趨勢 {_rate_trend_label(rate_trend)}（當前 {bank_lending_rate:.3f}%）。",
        "信用擴張中。" if credit_trend == "improving" else "信用收縮中。",
        "貨幣供給成長中。" if money_supply_trend == "improving" else "貨幣供給停滯。",
    ]

    # 新增原因
    if pe_ratio:
        reasons.append(f"大盤本益比 {pe_ratio:.2f}，屬於 {pe_signal} 水準。")
    if yield_inverted:
        reasons.append("殖利率曲線倒掛，注意經濟反轉訊號。")

    metrics = [
        LensMetric("bank_lending_rate", "銀行放款利率", bank_lending_rate if bank_lending_rate is not None else 0.0, "percent", "neutral" if bank_lending_rate is None else ("positive" if rate_trend == "falling" else "negative")),
        LensMetric("credit_change", "信用擴張", credit_change if credit_change is not None else 0.0, "decimal", "neutral" if credit_change is None else ("positive" if credit_change > 0 else "negative")),
        LensMetric("m1b_change", "M1B 貨幣供給", m1b_change if m1b_change is not None else 0.0, "decimal", "neutral" if m1b_change is None else ("positive" if m1b_change > 0 else "negative")),
        # 新增指標
        LensMetric("pe_ratio", "大盤本益比", pe_ratio if pe_ratio is not None else 0.0, "decimal", "neutral" if pe_ratio is None else ("negative" if pe_signal == "overvalued" else "positive")),
        LensMetric("yield_curve", "殖利率曲線利差", yield_spread if yield_spread is not None else 0.0, "spread", "neutral" if yield_spread is None else ("negative" if yield_inverted else "positive")),
        LensMetric("margin_balance", "融資餘額", margin_amount if margin_amount is not None else 0.0, "decimal", "neutral" if margin_amount is None else ("negative" if margin_trend == "excessive" else "positive")),
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
