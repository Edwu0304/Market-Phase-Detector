import calendar
from datetime import date
from statistics import mean

from market_phase_detector.collectors.tw_official import extract_ndc_history_metrics
from market_phase_detector.collectors.tw_macro_calculator import compute_sahm_rule, compute_tw_full_metrics


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


def classify_level_trend(current: float | int | None, previous: float | int | None) -> str:
    if current is None or previous is None:
        return "stable"
    if current > previous:
        return "rising"
    if current < previous:
        return "falling"
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

        delta = round(current["value"] - previous["value"], 4)
        history.append(
            {
                "month": month_key,
                "as_of": month_key,
                "leading_index_change": delta,
                "claims_trend": compute_claims_trend(claims_window),
                "coincident_trend": "improving" if delta > 0 else "deteriorating" if delta < 0 else "stable",
                "coincident_direction_score": 1.0 if delta > 0 else -1.0 if delta < 0 else 0.0,
                "sahm_rule": sahm_row["value"],
                "yield_curve": curve_row["value"],
                "hy_spread": hy_row["value"],
            }
        )

    return history[-months:]


def _build_tw_external_latest(external_collector) -> dict:
    extra_data: dict = {}

    try:
        claims_list = external_collector.fetch_mol_claims_annual()
        if claims_list:
            extra_data["unemployment_claims"] = claims_list[-1].get("initial_claims")
            if len(claims_list) >= 2:
                trend = classify_level_trend(claims_list[-1].get("initial_claims"), claims_list[-2].get("initial_claims"))
                extra_data["unemployment_claims_trend"] = "falling" if trend == "falling" else "rising" if trend == "rising" else "stable"
    except Exception:
        pass

    try:
        cci = external_collector.fetch_ncu_cci()
        if cci:
            extra_data["cci_total"] = cci.get("cci_total")
    except Exception:
        pass

    try:
        pmi = external_collector.fetch_latest_cier_pmi()
        if pmi:
            extra_data["pmi"] = pmi.get("pmi")
    except Exception:
        pass

    try:
        m2 = external_collector.fetch_latest_cbc_m2()
        if m2:
            extra_data["m2_yoy"] = m2.get("m2_yoy")
    except Exception:
        pass

    try:
        pe = external_collector.fetch_twse_market_pe()
        if pe:
            extra_data["pe_ratio"] = pe.get("pe_ratio")
    except Exception:
        pass

    try:
        margin = external_collector.fetch_latest_twse_margin()
        if margin:
            extra_data["margin_amount"] = margin.get("margin_amount")
            extra_data["margin_shares"] = margin.get("margin_shares")
            if margin.get("margin_amount") is not None:
                extra_data["margin_trend"] = "excessive" if margin.get("margin_amount", 0) >= 500000000 else "moderate"
    except Exception:
        pass

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

    try:
        expenditure = external_collector.fetch_mof_government_expenditure()
        if expenditure:
            extra_data["government_spending"] = expenditure[-1].get("total_expenditure")
    except Exception:
        pass

    return extra_data


def build_tw_observations(collector, external_collector=None) -> dict:
    metrics = collector.fetch_ndc_zip_metrics(NDC_ZIP_URL)
    full_metrics = compute_tw_full_metrics(metrics)
    extra_data = _build_tw_external_latest(external_collector) if external_collector else {}

    sahm_value = None
    unemp_hist = [v for v in [full_metrics.get("unemployment"), full_metrics.get("unemployment_prev")] if v]
    if len(unemp_hist) >= 3:
        sahm_value = compute_sahm_rule(unemp_hist)

    return {
        "as_of": month_key_from_compact(full_metrics["latest_date"]),
        "business_signal_score": full_metrics["business_signal_score"],
        "leading_index_change": full_metrics["leading_index"] - full_metrics["leading_index_prev"],
        "leading_trend": classify_direction(full_metrics["leading_index"] - full_metrics["leading_index_prev"]),
        "coincident_trend": classify_direction(full_metrics["coincident_index"] - full_metrics["coincident_index_prev"]),
        "coincident_trend_score": full_metrics["coincident_index"] - full_metrics["coincident_index_prev"],
        "unemployment_trend": "rising" if full_metrics["unemployment"] > full_metrics["unemployment_prev"] else "stable",
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
        "bank_lending_rate": full_metrics.get("bank_lending_rate"),
        "bank_lending_rate_change": full_metrics.get("bank_lending_rate_change"),
        "rate_trend": full_metrics.get("rate_trend", "stable"),
        "credit_change": full_metrics.get("credit_change"),
        "credit_trend": full_metrics.get("credit_trend", "stable"),
        "m1b_change": full_metrics.get("m1b_change"),
        "money_supply_trend": full_metrics.get("money_supply_trend", "stable"),
        "stock_index_yoy": full_metrics.get("stock_index_yoy"),
        "stock_trend": full_metrics.get("stock_trend", "neutral"),
        "credit_inventory_ratio": full_metrics.get("credit_inventory_ratio"),
        "unemployment": full_metrics.get("unemployment"),
        "unemployment_prev": full_metrics.get("unemployment_prev"),
        "sahm_rule": sahm_value,
        **extra_data,
    }


def _build_tw_external_history(external_collector, months: int) -> dict:
    external_history: dict = {}
    if not external_collector:
        return external_history

    try:
        claims_hist = external_collector.fetch_mol_claims_annual()
        if claims_hist:
            external_history["unemployment_claims"] = {str(r["year"]): r for r in claims_hist}
            external_history["unemployment_claims_rows"] = claims_hist
    except Exception:
        pass

    try:
        bond_hist = external_collector.fetch_tpex_bond_history(months)
        if bond_hist:
            external_history["bond"] = {r["date"][:7]: r for r in bond_hist}
    except Exception:
        pass

    try:
        cci_hist = external_collector.fetch_ncu_cci_history(months)
        if cci_hist:
            external_history["cci"] = {r["date"]: r for r in cci_hist}
    except Exception:
        pass

    try:
        pmi_hist = external_collector.fetch_cier_pmi_history(months)
        if pmi_hist:
            external_history["pmi"] = {r["date"]: r for r in pmi_hist}
    except Exception:
        pass

    try:
        m2_hist = external_collector.fetch_cbc_m2_history(months)
        if m2_hist:
            external_history["m2"] = {r["date"]: r for r in m2_hist}
    except Exception:
        pass

    return external_history


def build_tw_history_observations(
    history_metrics: list[dict] | dict[str, list[dict]],
    external_collector=None,
    months: int = 24,
) -> list[dict]:
    metrics_rows = extract_ndc_history_metrics(history_metrics) if isinstance(history_metrics, dict) else history_metrics
    external_history = _build_tw_external_history(external_collector, months)

    history = []
    for metrics in metrics_rows[-months:]:
        full_metrics = compute_tw_full_metrics(metrics)
        month_key = month_key_from_compact(full_metrics["latest_date"])

        sahm_value = None
        unemp_hist = [v for v in [full_metrics.get("unemployment"), full_metrics.get("unemployment_prev")] if v]
        if len(unemp_hist) >= 3:
            sahm_value = compute_sahm_rule(unemp_hist)

        extra_data = {}
        year_str = month_key[:4]

        if external_history.get("unemployment_claims") and year_str in external_history["unemployment_claims"]:
            claims = external_history["unemployment_claims"][year_str]
            extra_data["unemployment_claims"] = claims.get("initial_claims")
            claims_rows = external_history.get("unemployment_claims_rows", [])
            current_index = next((idx for idx, row in enumerate(claims_rows) if str(row.get("year")) == year_str), None)
            if current_index is not None and current_index > 0:
                previous_claims = claims_rows[current_index - 1]
                trend = classify_level_trend(claims.get("initial_claims"), previous_claims.get("initial_claims"))
                extra_data["unemployment_claims_trend"] = "falling" if trend == "falling" else "rising" if trend == "rising" else "stable"

        if external_history.get("bond") and month_key in external_history["bond"]:
            bond = external_history["bond"][month_key]
            extra_data["gov_yield_10y"] = bond.get("gov_yield_10y")
            extra_data["gov_yield_2y"] = bond.get("gov_yield_2y")
            extra_data["yield_curve_spread"] = bond.get("spread_10y_2y")
            extra_data["credit_spread_bbb"] = bond.get("credit_spread_bbb")
            extra_data["credit_spread"] = bond.get("credit_spread_bbb")

        if external_history.get("cci") and month_key in external_history["cci"]:
            extra_data["cci_total"] = external_history["cci"][month_key].get("cci_total")

        if external_history.get("pmi") and month_key in external_history["pmi"]:
            extra_data["pmi"] = external_history["pmi"][month_key].get("pmi")

        if external_history.get("m2") and month_key in external_history["m2"]:
            extra_data["m2_yoy"] = external_history["m2"][month_key].get("m2_yoy")

        history.append(
            {
                "month": month_key,
                "as_of": month_key,
                "business_signal_score": full_metrics["business_signal_score"],
                "leading_index_change": full_metrics["leading_index"] - full_metrics["leading_index_prev"],
                "leading_trend": classify_direction(full_metrics["leading_index"] - full_metrics["leading_index_prev"]),
                "coincident_trend": classify_direction(full_metrics["coincident_index"] - full_metrics["coincident_index_prev"]),
                "coincident_trend_score": full_metrics["coincident_index"] - full_metrics["coincident_index_prev"],
                "unemployment_trend": "rising" if full_metrics["unemployment"] > full_metrics["unemployment_prev"] else "stable",
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
                "bank_lending_rate": full_metrics.get("bank_lending_rate"),
                "bank_lending_rate_change": full_metrics.get("bank_lending_rate_change"),
                "rate_trend": full_metrics.get("rate_trend", "stable"),
                "credit_change": full_metrics.get("credit_change"),
                "credit_trend": full_metrics.get("credit_trend", "stable"),
                "m1b_change": full_metrics.get("m1b_change"),
                "money_supply_trend": full_metrics.get("money_supply_trend", "stable"),
                "stock_index_yoy": full_metrics.get("stock_index_yoy"),
                "stock_trend": full_metrics.get("stock_trend", "neutral"),
                "credit_inventory_ratio": full_metrics.get("credit_inventory_ratio"),
                "unemployment": full_metrics.get("unemployment"),
                "unemployment_prev": full_metrics.get("unemployment_prev"),
                "sahm_rule": sahm_value,
                **extra_data,
            }
        )

    return history[-months:]
