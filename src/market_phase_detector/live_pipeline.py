from statistics import mean


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


def build_us_observations(collector) -> dict:
    leading_index = collector.fetch_latest_csv(US_SERIES["leading_index"])
    claims = collector.fetch_latest_csv(US_SERIES["claims"])
    sahm = collector.fetch_latest_csv(US_SERIES["sahm_rule"])
    curve = collector.fetch_latest_csv(US_SERIES["yield_curve"])
    hy = collector.fetch_latest_csv(US_SERIES["hy_spread"])

    return {
        "as_of": min(
            leading_index["latest"]["date"],
            sahm["latest"]["date"],
            curve["latest"]["date"],
            hy["latest"]["date"],
        ),
        "leading_index_change": compute_monthly_change(leading_index["rows"]),
        "claims_trend": compute_claims_trend(claims["rows"]),
        "sahm_rule": sahm["latest"]["value"],
        "yield_curve": curve["latest"]["value"],
        "hy_spread": hy["latest"]["value"],
    }


def build_tw_observations(collector) -> dict:
    metrics = collector.fetch_ndc_zip_metrics(NDC_ZIP_URL)

    return {
        "as_of": metrics["latest_date"],
        "business_signal_score": metrics["business_signal_score"],
        "leading_trend": classify_direction(metrics["leading_index"] - metrics["leading_index_prev"]),
        "coincident_trend": classify_direction(metrics["coincident_index"] - metrics["coincident_index_prev"]),
        "unemployment_trend": "rising" if metrics["unemployment"] > metrics["unemployment_prev"] else "stable",
        "exports_yoy": ((metrics["export_value"] - metrics["export_value_year_ago"]) / metrics["export_value_year_ago"]) * 100,
    }
