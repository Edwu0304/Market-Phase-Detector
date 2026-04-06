from market_phase_detector.lenses.metric_sets import LENS_TITLES
from market_phase_detector.models.lenses import LensDecision, LensHistoryRow, LensMetric
from market_phase_detector.strategy_content import PHASE_LABELS


def _phase_from_risk(stock_trend: str, credit_trend: str, inventory_trend: str) -> str:
    """使用股市、信用、庫存判斷風險"""
    stock_score = 1.0 if stock_trend == "improving" else (-1.0 if stock_trend == "deteriorating" else 0.0)
    credit_score = 1.0 if credit_trend == "improving" else (-1.0 if credit_trend == "deteriorating" else 0.0)
    inventory_penalty = -0.5 if inventory_trend == "deteriorating" else 0.0  # 庫存累積 = 負面
    
    total = stock_score + credit_score + inventory_penalty
    
    if credit_trend == "deteriorating" and stock_trend == "deteriorating":
        return "Recession"
    if total >= 1.5:
        return "Boom"
    if total >= 0.5:
        return "Growth"
    return "Recovery"


def build_marks_lens(observations: dict) -> LensDecision:
    # 使用真實指標
    stock_trend = observations.get("stock_trend", "stable")
    credit_trend = observations.get("credit_trend", "stable")
    inventory_trend = observations.get("inventory_trend", "stable")
    stock_yoy = observations.get("stock_index_yoy", 0.0)
    credit_change = observations.get("credit_change", 0.0)
    inventory_change = observations.get("inventory_change", 0.0)

    # 新增：信用利差
    credit_spread = observations.get("credit_spread_proxy", None)
    credit_spread_signal = "wide" if credit_spread and credit_spread > 2 else ("narrow" if credit_spread and credit_spread < 0.5 else "neutral")

    # 新增：消費者信心指數（反向指標）
    cci_level = observations.get("cci_total", None)
    cci_euphoria = cci_level and cci_level > 80

    # 新增：政府支出趨勢
    gov_spending = observations.get("government_spending_trend", None)
    gov_signal = "expanding" if gov_spending and gov_spending > 5 else ("prudent" if gov_spending else "neutral")

    # 新增：融資餘額（市場槓桿指標）
    margin_amount = observations.get("margin_amount", None)
    margin_excessive = margin_amount and margin_amount > 500000000  # 5000億以上視為過高

    phase = _phase_from_risk(stock_trend, credit_trend, inventory_trend)

    reasons = [
        f"股市趨勢 {_direction_label(stock_trend)}（年增 {stock_yoy:.2f}%）。",
        "信用擴張中。" if credit_trend == "improving" else "信用收縮中。",
        "庫存累積中，需留意風險。" if inventory_trend == "deteriorating" else "庫存可控。",
    ]

    # 新增原因
    if credit_spread:
        reasons.append(f"信用利差為 {credit_spread:.2f}%，屬於 {credit_spread_signal} 水準。")
    if cci_euphoria:
        reasons.append(f"消費者信心指數高達 {cci_level:.1f}，市場可能過度樂觀。")
    if margin_excessive:
        reasons.append("融資餘額過高，市場槓桿風險上升。")

    metrics = [
        LensMetric("stock_index_yoy", "股價指數年增", stock_yoy if stock_yoy is not None else 0.0, "percent", "neutral" if stock_yoy is None else ("positive" if stock_yoy > 0 else "negative")),
        LensMetric("credit_change", "信用擴張", credit_change if credit_change is not None else 0.0, "decimal", "neutral" if credit_change is None else ("positive" if credit_change > 0 else "negative")),
        LensMetric("inventory_change", "庫存變動", inventory_change if inventory_change is not None else 0.0, "decimal", "neutral" if inventory_change is None else ("negative" if inventory_change > 0 else "positive")),
        # 新增指標
        LensMetric("credit_spread", "信用利差", credit_spread if credit_spread is not None else 0.0, "spread", "neutral" if credit_spread is None else ("negative" if credit_spread_signal == "wide" else "positive")),
        LensMetric("cci_level", "消費者信心指數", cci_level if cci_level is not None else 50.0, "decimal", "neutral" if cci_level is None else ("negative" if cci_euphoria else "positive")),
        LensMetric("government_spending", "政府支出趨勢", gov_spending if gov_spending is not None else 0.0, "decimal", "neutral" if gov_spending is None else ("negative" if gov_signal == "expanding" else "positive")),
        LensMetric("margin_balance", "融資餘額", margin_amount if margin_amount is not None else 0.0, "decimal", "neutral" if margin_amount is None else ("negative" if margin_excessive else "positive")),
    ]
    return LensDecision(
        lens_id="marks",
        title=LENS_TITLES["marks"],
        phase=phase,
        phase_label=PHASE_LABELS[phase],
        reasons=reasons,
        metrics=metrics,
    )


def _direction_label(value: str) -> str:
    mapping = {"improving": "改善", "stable": "持平", "deteriorating": "惡化"}
    return mapping.get(value, value)


def build_marks_history_row(month: str, observations: dict) -> LensHistoryRow:
    current = build_marks_lens(observations)
    return LensHistoryRow(
        month=month,
        as_of=observations["as_of"],
        phase=current.phase,
        phase_label=current.phase_label,
        reasons=current.reasons,
        metrics=current.metrics,
    )
