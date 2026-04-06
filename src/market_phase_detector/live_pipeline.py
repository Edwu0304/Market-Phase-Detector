import calendar
from datetime import date
from statistics import mean

from market_phase_detector.collectors.tw_official import extract_ndc_history_metrics
from market_phase_detector.collectors.tw_macro_calculator import compute_tw_full_metrics, compute_sahm_rule


US_SERIES = {
    "leading_index": "IPMAN",
    "claims": "ICSA",
    "sahm_rule": "SAHMCURRENT",
    "yield_curve": "T10Y2Y",
    "hy_spread": "BAMLH0A0HYM2",
}

NDC_BUSINESS_INDICATORS_URL = "https://www.ndc.gov.tw/en/Content_List.aspx?n=7FC514B520F97C0D"
NDC_ZIP_URL = "https://ws.ndc.gov.tw/Download.ashx?icon=.zip&n=5pmv5rCj5oyH5qiZ5Y%2BK54eI6JmfLnppcA%3D%3D&u=LzAwMS9hZG1pbmlzdHJhdG9yLzEwL3JlbGZpbGUvNTc4MS82MzkyL2VhMjM1YmQ5LWQwNTItNGE2OS1hYmZjLWQ1Yzc4NWQzZDBlMi56aXA%3D"


def classify_direction(change: float, threshold: float = 0.05) -> str:
    if change > threshold:
        return "improving"
    if change < -threshold:
        return "deteriorating"
    return "stable"


def compute_claims_trend(rows: list[dict]) -> str:
    if len(rows) < 8:
        return "stable"

    previous = mean(row["value"] for row in rows[-8:-4])
    recent = mean(row["value"] for row in rows[-4:])

    if recent > previous:
        return "rising"
    if recent < previous:
        return "falling"
    return "stable"


def compute_monthly_change(rows: list[dict]) -> float:
    if len(rows) < 2:
        return 0.0
    return round(rows[-1]["value"] - rows[-2]["value"], 4)


def month_key_from_date(value: str) -> str:
    return value[:7]


def month_key_from_compact(value: str) -> str:
    return f"{value[:4]}-{value[4:6]}"


def _month_end_from_key(month_key: str) -> date:
    year = int(month_key[:4])
    month = int(month_key[5:7])
    day = calendar.monthrange(year, month)[1]
    return date(year, month, day)


def _latest_row_for_month(rows: list[dict], month_key: str) -> dict | None:
    month_rows = [row for row in rows if row["date"].startswith(month_key)]
    if month_rows:
        return month_rows[-1]

    month_end = _month_end_from_key(month_key).isoformat()
    eligible = [row for row in rows if row["date"] <= month_end]
    if not eligible:
        return None
    return eligible[-1]


def build_us_observations(collector) -> dict:
    leading_index = collector.fetch_latest_csv(US_SERIES["leading_index"])
    claims = collector.fetch_latest_csv(US_SERIES["claims"])
    sahm = collector.fetch_latest_csv(US_SERIES["sahm_rule"])
    curve = collector.fetch_latest_csv(US_SERIES["yield_curve"])
    hy = collector.fetch_latest_csv(US_SERIES["hy_spread"])

    return {
        "as_of": month_key_from_date(min(
            leading_index["latest"]["date"],
            sahm["latest"]["date"],
            curve["latest"]["date"],
            hy["latest"]["date"],
        )),
        "leading_index_change": compute_monthly_change(leading_index["rows"]),
        "claims_trend": compute_claims_trend(claims["rows"]),
        "sahm_rule": sahm["latest"]["value"],
        "yield_curve": curve["latest"]["value"],
        "hy_spread": hy["latest"]["value"],
    }


def build_us_history_observations(collector, months: int = 12) -> list[dict]:
    series = {name: collector.fetch_latest_csv(series_id) for name, series_id in US_SERIES.items()}
    leading_rows = series["leading_index"]["rows"]
    claims_rows = series["claims"]["rows"]
    sahm_rows = series["sahm_rule"]["rows"]
    curve_rows = series["yield_curve"]["rows"]
    hy_rows = series["hy_spread"]["rows"]

    history: list[dict] = []
    for index in range(1, len(leading_rows)):
        current = leading_rows[index]
        previous = leading_rows[index - 1]
        month_key = month_key_from_date(current["date"])
        month_end = _month_end_from_key(month_key).isoformat()
        claims_window = [row for row in claims_rows if row["date"] <= month_end][-8:]
        sahm_row = _latest_row_for_month(sahm_rows, month_key)
        curve_row = _latest_row_for_month(curve_rows, month_key)
        hy_row = _latest_row_for_month(hy_rows, month_key)

        if len(claims_window) < 8 or not all([sahm_row, curve_row, hy_row]):
            continue

        history.append(
            {
                "month": month_key,
                "as_of": month_key,
                "leading_index_change": round(current["value"] - previous["value"], 4),
                "claims_trend": compute_claims_trend(claims_window),
                "coincident_trend": "improving" if round(current["value"] - previous["value"], 4) > 0 else "deteriorating" if round(current["value"] - previous["value"], 4) < 0 else "stable",
                "coincident_direction_score": 1.0 if round(current["value"] - previous["value"], 4) > 0 else -1.0 if round(current["value"] - previous["value"], 4) < 0 else 0.0,
                "sahm_rule": sahm_row["value"],
                "yield_curve": curve_row["value"],
                "hy_spread": hy_row["value"],
            }
        )

    return history[-months:]


def build_tw_observations(collector, external_collector=None) -> dict:
    """建立台灣完整觀測值（包含三位大師需要的所有真實指標）

    Args:
        collector: NDC 資料爬蟲
        external_collector: 外部資料爬蟲（勞動部、證交所、央行等）
    """
    metrics = collector.fetch_ndc_zip_metrics(NDC_ZIP_URL)
    full_metrics = compute_tw_full_metrics(metrics)

    # ===== 整合外部資料 =====
    extra_data = {}
    if external_collector:
        # 勞動部 — 初領失業救濟金
        try:
            claims_list = external_collector.fetch_mol_claims_annual()
            if claims_list:
                extra_data["unemployment_claims"] = claims_list[-1].get("initial_claims")
        except Exception:
            pass

        # 中央大學 — CCI
        try:
            cci = external_collector.fetch_ncu_cci()
            if cci:
                extra_data["cci_total"] = cci.get("cci_total")
        except Exception:
            pass

        # 證交所 — 本益比
        try:
            pe = external_collector.fetch_twse_market_pe()
            if pe:
                extra_data["pe_ratio"] = pe.get("pe_ratio")
        except Exception:
            pass

        # 證交所 — 融資餘額
        try:
            margin = external_collector.fetch_latest_twse_margin()
            if margin:
                extra_data["margin_amount"] = margin.get("margin_amount")
                extra_data["margin_shares"] = margin.get("margin_shares")
        except Exception:
            pass

        # 櫃買中心 — 公債殖利率 + 信用利差 (BBB - 公債10Y)
        try:
            bond = external_collector.fetch_cbc_credit_spread_proxy()
            if bond:
                extra_data["gov_yield_10y"] = bond.get("gov_yield_10y")
                extra_data["gov_yield_2y"] = bond.get("gov_yield_2y")
                extra_data["yield_curve_spread"] = bond.get("spread_10y_2y")
                extra_data["credit_spread_bbb"] = bond.get("credit_spread_bbb")
                extra_data["credit_spread"] = bond.get("credit_spread_bbb")
        except Exception:
            pass

        # 財政部 — 政府歲出
        try:
            expenditure = external_collector.fetch_mof_government_expenditure()
            if expenditure:
                extra_data["government_spending"] = expenditure[-1].get("total_expenditure")
        except Exception:
            pass

    # 計算薩姆規則
    sahm_value = None
    unemp_hist = [v for v in [full_metrics.get("unemployment"), full_metrics.get("unemployment_prev")] if v]
    if len(unemp_hist) >= 3:
        sahm_value = compute_sahm_rule(unemp_hist)

    return {
        "as_of": month_key_from_compact(full_metrics["latest_date"]),
        # ===== 原始 NDC 指標 =====
        "business_signal_score": full_metrics["business_signal_score"],
        "leading_index_change": full_metrics["leading_index"] - full_metrics["leading_index_prev"],
        "leading_trend": classify_direction(full_metrics["leading_index"] - full_metrics["leading_index_prev"]),
        "coincident_trend": classify_direction(full_metrics["coincident_index"] - full_metrics["coincident_index_prev"]),
        "coincident_trend_score": full_metrics["coincident_index"] - full_metrics["coincident_index_prev"],
        "unemployment_trend": "rising" if full_metrics["unemployment"] > full_metrics["unemployment_prev"] else "stable",
        # ===== 愛榭克真實指標 =====
        "industrial_production_change": full_metrics.get("industrial_production_change"),
        "industrial_production_trend": full_metrics.get("industrial_production_trend", "stable"),
        "overtime_hours_change": full_metrics.get("overtime_hours_change"),
        "overtime_trend": full_metrics.get("overtime_trend", "stable"),
        "machinery_import_yoy": full_metrics.get("machinery_import_yoy"),
        "investment_trend": full_metrics.get("investment_trend", "stable"),
        "retail_sales_change": full_metrics.get("retail_sales_change"),
        "consumption_trend": full_metrics.get("consumption_trend", "stable"),
        "inventory_change": full_metrics.get("inventory_change"),
        "inventory_trend": full_metrics.get("inventory_trend", "stable"),
        "inventory_sales_ratio": full_metrics.get("inventory_sales_ratio"),
        "exports_yoy": full_metrics.get("exports_yoy"),
        "export_trend": full_metrics.get("export_trend", "stable"),
        "mfg_sales_change": full_metrics.get("manufacturing_sales_change"),
        "mfg_sales_trend": full_metrics.get("mfg_sales_trend", "stable"),
        # ===== 浦上邦雄真實指標 =====
        "bank_lending_rate": full_metrics.get("bank_lending_rate"),
        "bank_lending_rate_change": full_metrics.get("bank_lending_rate_change"),
        "rate_trend": full_metrics.get("rate_trend", "stable"),
        "credit_change": full_metrics.get("credit_change"),
        "credit_trend": full_metrics.get("credit_trend", "stable"),
        "m1b_change": full_metrics.get("m1b_change"),
        "money_supply_trend": full_metrics.get("money_supply_trend", "stable"),
        "stock_index_yoy": full_metrics.get("stock_index_yoy"),
        "stock_trend": full_metrics.get("stock_trend", "neutral"),
        # ===== 馬克斯真實指標 =====
        "credit_inventory_ratio": full_metrics.get("credit_inventory_ratio"),
        "unemployment": full_metrics.get("unemployment"),
        "unemployment_prev": full_metrics.get("unemployment_prev"),
        # ===== 新增外部指標 =====
        "sahm_rule": sahm_value,
        **extra_data,
    }


def build_tw_history_observations(
    history_metrics: list[dict] | dict[str, list[dict]],
    external_collector=None,
    months: int = 24,
) -> list[dict]:
    """建立台灣歷史觀測值（預設 24 個月）

    Args:
        history_metrics: NDC 歷史指標資料
        external_collector: 外部資料爬蟲（可選）
        months: 要回傳的月數
    """
    metrics_rows = extract_ndc_history_metrics(history_metrics) if isinstance(history_metrics, dict) else history_metrics

    # ===== 取得外部歷史資料（如果有的話）=====
    external_history = {}
    if external_collector:
        try:
            # 勞動部 — 失業救濟金年度
            claims_hist = external_collector.fetch_mol_claims_annual()
            if claims_hist:
                external_history["unemployment_claims"] = {str(r["year"]): r for r in claims_hist}
        except Exception:
            pass

        try:
            # 櫃買中心 — 公債殖利率 + 信用利差歷史
            bond_hist = external_collector.fetch_tpex_bond_history(months)
            if bond_hist:
                external_history["bond"] = {r["date"][:7]: r for r in bond_hist}
        except Exception:
            pass

        try:
            # 中央大學 — CCI 歷史
            cci_hist = external_collector.fetch_ncu_cci_history(months)
            if cci_hist:
                external_history["cci"] = {r["date"]: r for r in cci_hist}
        except Exception:
            pass

    history = []
    for metrics in metrics_rows[-months:]:
        full_metrics = compute_tw_full_metrics(metrics)
        month_key = month_key_from_compact(full_metrics["latest_date"])

        # 計算薩姆規則（需要失業率歷史）
        sahm_value = None
        unemp_hist = [v for v in [full_metrics.get("unemployment"), full_metrics.get("unemployment_prev")] if v]
        if len(unemp_hist) >= 3:
            sahm_value = compute_sahm_rule(unemp_hist)

        # 整合外部歷史資料
        extra_data = {}
        year_str = month_key[:4]
        if external_history.get("unemployment_claims") and year_str in external_history["unemployment_claims"]:
            claims = external_history["unemployment_claims"][year_str]
            extra_data["unemployment_claims"] = claims.get("initial_claims")

        if external_history.get("bond") and month_key in external_history["bond"]:
            bond = external_history["bond"][month_key]
            extra_data["gov_yield_10y"] = bond.get("gov_yield_10y")
            extra_data["gov_yield_2y"] = bond.get("gov_yield_2y")
            extra_data["yield_curve_spread"] = bond.get("spread_10y_2y")
            extra_data["credit_spread_bbb"] = bond.get("credit_spread_bbb")
            extra_data["credit_spread"] = bond.get("credit_spread_bbb")

        if external_history.get("cci") and month_key in external_history["cci"]:
            cci = external_history["cci"][month_key]
            extra_data["cci_total"] = cci.get("cci_total")

        history.append(
            {
                "month": month_key,
                "as_of": month_key,
                # ===== 原始 NDC 指標 =====
                "business_signal_score": full_metrics["business_signal_score"],
                "leading_index_change": full_metrics["leading_index"] - full_metrics["leading_index_prev"],
                "leading_trend": classify_direction(full_metrics["leading_index"] - full_metrics["leading_index_prev"]),
                "coincident_trend": classify_direction(full_metrics["coincident_index"] - full_metrics["coincident_index_prev"]),
                "coincident_trend_score": full_metrics["coincident_index"] - full_metrics["coincident_index_prev"],
                "unemployment_trend": "rising" if full_metrics["unemployment"] > full_metrics["unemployment_prev"] else "stable",
                # ===== 愛榭克真實指標 =====
                "industrial_production_change": full_metrics.get("industrial_production_change"),
                "industrial_production_trend": full_metrics.get("industrial_production_trend", "stable"),
                "overtime_hours_change": full_metrics.get("overtime_hours_change"),
                "overtime_trend": full_metrics.get("overtime_trend", "stable"),
                "machinery_import_yoy": full_metrics.get("machinery_import_yoy"),
                "investment_trend": full_metrics.get("investment_trend", "stable"),
                "retail_sales_change": full_metrics.get("retail_sales_change"),
                "consumption_trend": full_metrics.get("consumption_trend", "stable"),
                "inventory_change": full_metrics.get("inventory_change"),
                "inventory_trend": full_metrics.get("inventory_trend", "stable"),
                "inventory_sales_ratio": full_metrics.get("inventory_sales_ratio"),
                "exports_yoy": full_metrics.get("exports_yoy"),
                "export_trend": full_metrics.get("export_trend", "stable"),
                "mfg_sales_change": full_metrics.get("manufacturing_sales_change"),
                "mfg_sales_trend": full_metrics.get("mfg_sales_trend", "stable"),
                # ===== 浦上邦雄真實指標 =====
                "bank_lending_rate": full_metrics.get("bank_lending_rate"),
                "bank_lending_rate_change": full_metrics.get("bank_lending_rate_change"),
                "rate_trend": full_metrics.get("rate_trend", "stable"),
                "credit_change": full_metrics.get("credit_change"),
                "credit_trend": full_metrics.get("credit_trend", "stable"),
                "m1b_change": full_metrics.get("m1b_change"),
                "money_supply_trend": full_metrics.get("money_supply_trend", "stable"),
                "stock_index_yoy": full_metrics.get("stock_index_yoy"),
                "stock_trend": full_metrics.get("stock_trend", "neutral"),
                # ===== 馬克斯真實指標 =====
                "credit_inventory_ratio": full_metrics.get("credit_inventory_ratio"),
                "unemployment": full_metrics.get("unemployment"),
                "unemployment_prev": full_metrics.get("unemployment_prev"),
                # ===== 新增外部歷史指標 =====
                "sahm_rule": sahm_value,
                **extra_data,
            }
        )

    return history[-months:]
