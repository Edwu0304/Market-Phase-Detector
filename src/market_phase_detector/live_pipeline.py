import calendar
from datetime import date
from statistics import mean

from market_phase_detector.collectors.tw_official import extract_ndc_history_metrics


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


def build_tw_observations(collector) -> dict:
    metrics = collector.fetch_ndc_zip_metrics(NDC_ZIP_URL)

    return {
        "as_of": month_key_from_compact(metrics["latest_date"]),
        "business_signal_score": metrics["business_signal_score"],
        "leading_trend": classify_direction(metrics["leading_index"] - metrics["leading_index_prev"]),
        "coincident_trend": classify_direction(metrics["coincident_index"] - metrics["coincident_index_prev"]),
        "unemployment_trend": "rising" if metrics["unemployment"] > metrics["unemployment_prev"] else "stable",
        "exports_yoy": ((metrics["export_value"] - metrics["export_value_year_ago"]) / metrics["export_value_year_ago"]) * 100,
    }


def build_tw_history_observations(history_metrics: list[dict] | dict[str, list[dict]], months: int = 12) -> list[dict]:
    metrics_rows = extract_ndc_history_metrics(history_metrics) if isinstance(history_metrics, dict) else history_metrics

    history = []
    for metrics in metrics_rows:
        history.append(
            {
                "month": month_key_from_compact(metrics["latest_date"]),
                "as_of": month_key_from_compact(metrics["latest_date"]),
                "business_signal_score": metrics["business_signal_score"],
                "leading_index_change": metrics["leading_index"] - metrics["leading_index_prev"],
                "leading_trend": classify_direction(metrics["leading_index"] - metrics["leading_index_prev"]),
                "coincident_trend": classify_direction(metrics["coincident_index"] - metrics["coincident_index_prev"]),
                "unemployment_trend": "rising" if metrics["unemployment"] > metrics["unemployment_prev"] else "stable",
                "exports_yoy": ((metrics["export_value"] - metrics["export_value_year_ago"]) / metrics["export_value_year_ago"]) * 100,
            }
        )

    return history[-months:]
