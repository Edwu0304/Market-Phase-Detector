import calendar
from datetime import date
from statistics import mean

from market_phase_detector.collectors.tw_official import extract_ndc_history_metrics
from market_phase_detector.collectors.us_market import USMarketCollector
from market_phase_detector.collectors.tw_macro_calculator import compute_sahm_rule, compute_tw_full_metrics


US_SERIES = {
    "leading_index": "IPMAN",
    "claims": "ICSA",
    "sahm_rule": "SAHMCURRENT",
    "yield_curve": "T10Y2Y",
    "hy_spread": "BAMLH0A0HYM2",
    "inflation_expectation_5y": "T5YIE",
    "funding_stress": "STLFSI4",
    "lending_standards": "DRTSCILM",
    "yield_10y": "DGS10",
    "yield_2y": "DGS2",
    "commodity_index": "PPIACO",
    "industrial_metals_index": "WPU10",
    "policy_uncertainty": "USEPUINDXM",
    "hy_yield": "BAMLH0A0HYM2EY",
    "earnings_growth_proxy": "A3202C0A144NBEA",
    "delinquency_rate": "DRBLACBS",
    "chargeoff_rate": "CORBLACBS",
}

NDC_BUSINESS_INDICATORS_URL = "https://www.ndc.gov.tw/en/Content_List.aspx?n=7FC514B520F97C0D"
NDC_ZIP_URL = "https://ws.ndc.gov.tw/Download.ashx?icon=.zip&n=5pmv5rCj5oyH5qiZ5Y%2BK54eI6JmfLnppcA%3D%3D&u=LzAwMS9hZG1pbmlzdHJhdG9yLzEwL3JlbGZpbGUvNTc4MS82MzkyL2VhMjM1YmQ5LWQwNTItNGE2OS1hYmZjLWQ1Yzc4NWQzZDBlMi56aXA%3D"


def classify_direction(change: float, threshold: float = 0.05) -> str:
    if change > threshold:
        return "improving"
    if change < -threshold:
        return "deteriorating"
    return "stable"


def classify_breadth_regime(ratio: float | None) -> str:
    if ratio is None:
        return "unknown"
    if ratio >= 1.2:
        return "broadening"
    if ratio <= 0.8:
        return "narrowing"
    return "balanced"


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


def compute_year_over_year_change(current: float | None, previous: float | None) -> float | None:
    if current is None or previous in {None, 0}:
        return None
    return round((current / previous - 1) * 100, 2)


def classify_yield_curve_regime(current_10y: float | None, previous_10y: float | None, current_2y: float | None, previous_2y: float | None) -> str:
    if None in {current_10y, previous_10y, current_2y, previous_2y}:
        return "unknown"
    current_spread = current_10y - current_2y
    previous_spread = previous_10y - previous_2y
    if current_spread < 0:
        return "inversion"
    spread_change = current_spread - previous_spread
    long_change = current_10y - previous_10y
    short_change = current_2y - previous_2y
    if spread_change > 0:
        if long_change >= 0 and short_change >= 0:
            return "bear_steepening"
        return "bull_steepening"
    if spread_change < 0:
        return "flattening"
    return "stable"


def compute_distress_proxy(credit_spread: float | None, funding_stress: float | None, lending_standards: float | None) -> float | None:
    if credit_spread is None and funding_stress is None and lending_standards is None:
        return None
    score = 0.0
    if credit_spread is not None:
        score += credit_spread / 2.0
    if funding_stress is not None:
        score += max(funding_stress, 0)
    if lending_standards is not None:
        score += max(lending_standards, 0) / 20.0
    return round(score, 4)


def classify_distress_regime(distress_proxy: float | None) -> str:
    if distress_proxy is None:
        return "unknown"
    if distress_proxy >= 2.5:
        return "high"
    if distress_proxy >= 1.0:
        return "elevated"
    return "contained"


def compute_issuance_appetite_proxy(hy_yield: float | None, lending_standards: float | None) -> float | None:
    if hy_yield is None and lending_standards is None:
        return None
    hy_component = 0.0 if hy_yield is None else max(0.0, 10.0 - hy_yield)
    lending_component = 0.0 if lending_standards is None else max(0.0, 12.0 - lending_standards / 2.0)
    return round(hy_component + lending_component, 4)


def classify_issuance_appetite(issuance_proxy: float | None) -> str:
    if issuance_proxy is None:
        return "unknown"
    if issuance_proxy >= 14:
        return "open"
    if issuance_proxy >= 8:
        return "selective"
    return "tight"


def compute_default_pressure_proxy(delinquency_rate: float | None, chargeoff_rate: float | None) -> float | None:
    if delinquency_rate is None and chargeoff_rate is None:
        return None
    return round((delinquency_rate or 0.0) + (chargeoff_rate or 0.0), 4)


def classify_default_pressure(default_pressure_proxy: float | None) -> str:
    if default_pressure_proxy is None:
        return "unknown"
    if default_pressure_proxy >= 2.5:
        return "high"
    if default_pressure_proxy >= 1.0:
        return "elevated"
    return "contained"


def month_key_from_date(value: str) -> str:
    return value[:7]


def month_key_from_compact(value: str) -> str:
    return f"{value[:4]}-{value[4:6]}"


def _latest_dated_row(rows: list[dict], month_key: str | None = None) -> dict | None:
    dated_rows = [row for row in rows if row.get("date")]
    if month_key is not None:
        dated_rows = [row for row in dated_rows if (_row_month_key(row.get("date"), month_key) or "9999-99") <= month_key]
    if not dated_rows:
        return None
    return max(dated_rows, key=lambda row: _row_month_key(row.get("date"), month_key) or str(row["date"]))


def _row_month_key(date_value, reference_month_key: str | None = None) -> str | None:
    if not date_value:
        return None
    value = str(date_value)
    if len(value) >= 7 and value[4] == "-":
        return value[:7]
    if len(value) == 4 and value.isdigit():
        return f"{value}-12"
    month_day = value.split("/")
    if len(month_day) == 2 and all(part.isdigit() for part in month_day) and reference_month_key:
        return f"{reference_month_key[:4]}-{int(month_day[0]):02d}"
    return None


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


def build_us_observations(collector, market_collector=None) -> dict:
    leading_index = collector.fetch_latest_csv(US_SERIES["leading_index"])
    claims = collector.fetch_latest_csv(US_SERIES["claims"])
    sahm = collector.fetch_latest_csv(US_SERIES["sahm_rule"])
    curve = collector.fetch_latest_csv(US_SERIES["yield_curve"])
    hy = collector.fetch_latest_csv(US_SERIES["hy_spread"])
    inflation = collector.fetch_latest_csv(US_SERIES["inflation_expectation_5y"])
    funding = collector.fetch_latest_csv(US_SERIES["funding_stress"])
    lending = collector.fetch_latest_csv(US_SERIES["lending_standards"])
    yield_10y = collector.fetch_latest_csv(US_SERIES["yield_10y"])
    yield_2y = collector.fetch_latest_csv(US_SERIES["yield_2y"])
    commodity = collector.fetch_latest_csv(US_SERIES["commodity_index"])
    metals = collector.fetch_latest_csv(US_SERIES["industrial_metals_index"])
    policy_uncertainty = collector.fetch_latest_csv(US_SERIES["policy_uncertainty"])
    hy_yield = collector.fetch_latest_csv(US_SERIES["hy_yield"])
    earnings = collector.fetch_latest_csv(US_SERIES["earnings_growth_proxy"])
    delinquency = collector.fetch_latest_csv(US_SERIES["delinquency_rate"])
    chargeoff = collector.fetch_latest_csv(US_SERIES["chargeoff_rate"])
    as_of_month = month_key_from_date(min(
        leading_index["latest"]["date"],
        sahm["latest"]["date"],
        curve["latest"]["date"],
        hy["latest"]["date"],
        inflation["latest"]["date"],
        funding["latest"]["date"],
        lending["latest"]["date"],
        commodity["latest"]["date"],
        metals["latest"]["date"],
        policy_uncertainty["latest"]["date"],
        hy_yield["latest"]["date"],
    ))
    sector_rotation_snapshot = market_collector.fetch_sector_rotation_snapshot() if market_collector else None
    intermarket_snapshot = market_collector.fetch_intermarket_snapshot() if market_collector else None
    sector_rotation_history = market_collector.fetch_sector_rotation_history(months=24) if market_collector else []
    intermarket_history = market_collector.fetch_intermarket_history(months=24) if market_collector else []
    sector_rotation_map = {row["date"]: row for row in sector_rotation_history}
    intermarket_map = {row["date"]: row for row in intermarket_history}

    sahm_row = _latest_row_for_month(sahm["rows"], as_of_month)
    curve_row = _latest_row_for_month(curve["rows"], as_of_month)
    hy_row = _latest_row_for_month(hy["rows"], as_of_month)
    inflation_row = _latest_row_for_month(inflation["rows"], as_of_month)
    funding_row = _latest_row_for_month(funding["rows"], as_of_month)
    lending_row = _latest_row_for_month(lending["rows"], as_of_month)
    yield_10y_row = _latest_row_for_month(yield_10y["rows"], as_of_month)
    yield_2y_row = _latest_row_for_month(yield_2y["rows"], as_of_month)
    commodity_row = _latest_row_for_month(commodity["rows"], as_of_month)
    metals_row = _latest_row_for_month(metals["rows"], as_of_month)
    policy_uncertainty_row = _latest_row_for_month(policy_uncertainty["rows"], as_of_month)
    hy_yield_row = _latest_row_for_month(hy_yield["rows"], as_of_month)
    earnings_row = _latest_row_for_month(earnings["rows"], as_of_month)
    delinquency_row = _latest_row_for_month(delinquency["rows"], as_of_month)
    chargeoff_row = _latest_row_for_month(chargeoff["rows"], as_of_month)
    previous_month_key = f"{int(as_of_month[:4]) - 1}-{as_of_month[5:7]}" if as_of_month.endswith("-01") else None
    sector_rotation = sector_rotation_map.get(as_of_month) or sector_rotation_snapshot
    intermarket = intermarket_map.get(as_of_month) or intermarket_snapshot
    yield_curve_regime = classify_yield_curve_regime(
        None if yield_10y_row is None else yield_10y_row["value"],
        yield_10y["rows"][-2]["value"] if len(yield_10y["rows"]) >= 2 else None,
        None if yield_2y_row is None else yield_2y_row["value"],
        yield_2y["rows"][-2]["value"] if len(yield_2y["rows"]) >= 2 else None,
    )
    distress_proxy = compute_distress_proxy(None if hy_row is None else hy_row["value"], None if funding_row is None else funding_row["value"], None if lending_row is None else lending_row["value"])
    issuance_appetite_proxy = compute_issuance_appetite_proxy(None if hy_yield_row is None else hy_yield_row["value"], None if lending_row is None else lending_row["value"])
    earnings_growth_proxy = compute_year_over_year_change(
        None if earnings_row is None else earnings_row["value"],
        earnings["rows"][-2]["value"] if len(earnings["rows"]) >= 2 else None,
    )
    default_pressure_proxy = compute_default_pressure_proxy(
        None if delinquency_row is None else delinquency_row["value"],
        None if chargeoff_row is None else chargeoff_row["value"],
    )

    return {
        "as_of": as_of_month,
        "leading_index_change": compute_monthly_change(leading_index["rows"]),
        "claims_trend": compute_claims_trend(claims["rows"]),
        "sahm_rule": None if sahm_row is None else sahm_row["value"],
        "yield_curve": None if curve_row is None else curve_row["value"],
        "hy_spread": None if hy_row is None else hy_row["value"],
        "inflation_expectation_5y": None if inflation_row is None else inflation_row["value"],
        "funding_stress": None if funding_row is None else funding_row["value"],
        "lending_standards": None if lending_row is None else lending_row["value"],
        "yield_10y": None if yield_10y_row is None else yield_10y_row["value"],
        "yield_2y": None if yield_2y_row is None else yield_2y_row["value"],
        "yield_curve_regime": yield_curve_regime,
        "commodity_index": None if commodity_row is None else commodity_row["value"],
        "commodity_trend": classify_direction(compute_monthly_change(commodity["rows"])),
        "industrial_metals_index": None if metals_row is None else metals_row["value"],
        "industrial_metals_trend": classify_direction(compute_monthly_change(metals["rows"])),
        "policy_uncertainty": None if policy_uncertainty_row is None else policy_uncertainty_row["value"],
        "hy_yield": None if hy_yield_row is None else hy_yield_row["value"],
        "earnings_growth_proxy": earnings_growth_proxy,
        "delinquency_rate": None if delinquency_row is None else delinquency_row["value"],
        "chargeoff_rate": None if chargeoff_row is None else chargeoff_row["value"],
        "default_pressure_proxy": default_pressure_proxy,
        "default_pressure_regime": classify_default_pressure(default_pressure_proxy),
        "distress_proxy": distress_proxy,
        "distress_regime": classify_distress_regime(distress_proxy),
        "issuance_appetite_proxy": issuance_appetite_proxy,
        "issuance_appetite_regime": classify_issuance_appetite(issuance_appetite_proxy),
        "sector_leader": None if sector_rotation is None else sector_rotation.get("sector_leader"),
        "sector_leader_return": None if sector_rotation is None else sector_rotation.get("sector_leader_return"),
        "sector_laggard": None if sector_rotation is None else sector_rotation.get("sector_laggard"),
        "sector_laggard_return": None if sector_rotation is None else sector_rotation.get("sector_laggard_return"),
        "sector_advance_count": None if sector_rotation is None else sector_rotation.get("sector_advance_count"),
        "sector_decline_count": None if sector_rotation is None else sector_rotation.get("sector_decline_count"),
        "sector_breadth_ratio": None if sector_rotation is None else sector_rotation.get("sector_breadth_ratio"),
        "bond_return_3m": None if intermarket is None else intermarket.get("bond_return_3m"),
        "equity_return_3m": None if intermarket is None else intermarket.get("equity_return_3m"),
        "commodity_return_3m": None if intermarket is None else intermarket.get("commodity_return_3m"),
        "intermarket_order": None if intermarket is None else intermarket.get("intermarket_order"),
    }


def build_us_history_observations(collector, market_collector=None, months: int = 12) -> list[dict]:
    series = {name: collector.fetch_latest_csv(series_id) for name, series_id in US_SERIES.items()}
    sector_rotation_history = market_collector.fetch_sector_rotation_history(months=months) if market_collector else []
    sector_rotation_map = {row["date"]: row for row in sector_rotation_history}
    intermarket_history = market_collector.fetch_intermarket_history(months=months) if market_collector else []
    intermarket_map = {row["date"]: row for row in intermarket_history}
    leading_rows = series["leading_index"]["rows"]
    claims_rows = series["claims"]["rows"]
    sahm_rows = series["sahm_rule"]["rows"]
    curve_rows = series["yield_curve"]["rows"]
    hy_rows = series["hy_spread"]["rows"]
    inflation_rows = series["inflation_expectation_5y"]["rows"]
    funding_rows = series["funding_stress"]["rows"]
    lending_rows = series["lending_standards"]["rows"]
    yield_10y_rows = series["yield_10y"]["rows"]
    yield_2y_rows = series["yield_2y"]["rows"]
    commodity_rows = series["commodity_index"]["rows"]
    metals_rows = series["industrial_metals_index"]["rows"]
    policy_uncertainty_rows = series["policy_uncertainty"]["rows"]
    hy_yield_rows = series["hy_yield"]["rows"]
    earnings_rows = series["earnings_growth_proxy"]["rows"]
    delinquency_rows = series["delinquency_rate"]["rows"]
    chargeoff_rows = series["chargeoff_rate"]["rows"]

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
        inflation_row = _latest_row_for_month(inflation_rows, month_key)
        funding_row = _latest_row_for_month(funding_rows, month_key)
        lending_row = _latest_row_for_month(lending_rows, month_key)
        yield_10y_row = _latest_row_for_month(yield_10y_rows, month_key)
        yield_2y_row = _latest_row_for_month(yield_2y_rows, month_key)
        commodity_row = _latest_row_for_month(commodity_rows, month_key)
        metals_row = _latest_row_for_month(metals_rows, month_key)
        policy_uncertainty_row = _latest_row_for_month(policy_uncertainty_rows, month_key)
        hy_yield_row = _latest_row_for_month(hy_yield_rows, month_key)
        earnings_row = _latest_row_for_month(earnings_rows, month_key)
        delinquency_row = _latest_row_for_month(delinquency_rows, month_key)
        chargeoff_row = _latest_row_for_month(chargeoff_rows, month_key)
        previous_month_key = month_key_from_date(previous["date"])
        prev_yield_10y_row = _latest_row_for_month(yield_10y_rows, previous_month_key)
        prev_yield_2y_row = _latest_row_for_month(yield_2y_rows, previous_month_key)
        prev_commodity_row = _latest_row_for_month(commodity_rows, previous_month_key)
        prev_metals_row = _latest_row_for_month(metals_rows, previous_month_key)
        prev_year_month_key = f"{int(month_key[:4]) - 1}-{month_key[5:7]}"
        prev_earnings_row = _latest_row_for_month(earnings_rows, prev_year_month_key)

        if len(claims_window) < 8 or not all([sahm_row, curve_row, hy_row, inflation_row, funding_row, lending_row, yield_10y_row, yield_2y_row, commodity_row, metals_row, policy_uncertainty_row, hy_yield_row]):
            continue

        delta = round(current["value"] - previous["value"], 4)
        distress_proxy = compute_distress_proxy(hy_row["value"], funding_row["value"], lending_row["value"])
        issuance_appetite_proxy = compute_issuance_appetite_proxy(hy_yield_row["value"], lending_row["value"])
        default_pressure_proxy = compute_default_pressure_proxy(
            delinquency_row["value"] if delinquency_row else None,
            chargeoff_row["value"] if chargeoff_row else None,
        )
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
                "inflation_expectation_5y": inflation_row["value"],
                "funding_stress": funding_row["value"],
                "lending_standards": lending_row["value"],
                "yield_10y": yield_10y_row["value"],
                "yield_2y": yield_2y_row["value"],
                "yield_curve_regime": classify_yield_curve_regime(
                    yield_10y_row["value"],
                    prev_yield_10y_row["value"] if prev_yield_10y_row else None,
                    yield_2y_row["value"],
                    prev_yield_2y_row["value"] if prev_yield_2y_row else None,
                ),
                "commodity_index": commodity_row["value"],
                "commodity_trend": classify_direction(
                    0.0 if prev_commodity_row is None else commodity_row["value"] - prev_commodity_row["value"]
                ),
                "industrial_metals_index": metals_row["value"],
                "industrial_metals_trend": classify_direction(
                    0.0 if prev_metals_row is None else metals_row["value"] - prev_metals_row["value"]
                ),
                "policy_uncertainty": policy_uncertainty_row["value"],
                "hy_yield": hy_yield_row["value"],
                "earnings_growth_proxy": compute_year_over_year_change(
                    earnings_row["value"] if earnings_row else None,
                    prev_earnings_row["value"] if prev_earnings_row else None,
                ),
                "delinquency_rate": None if delinquency_row is None else delinquency_row["value"],
                "chargeoff_rate": None if chargeoff_row is None else chargeoff_row["value"],
                "default_pressure_proxy": default_pressure_proxy,
                "default_pressure_regime": classify_default_pressure(default_pressure_proxy),
                "distress_proxy": distress_proxy,
                "distress_regime": classify_distress_regime(distress_proxy),
                "issuance_appetite_proxy": issuance_appetite_proxy,
                "issuance_appetite_regime": classify_issuance_appetite(issuance_appetite_proxy),
                "sector_leader": None if month_key not in sector_rotation_map else sector_rotation_map[month_key].get("sector_leader"),
                "sector_leader_return": None if month_key not in sector_rotation_map else sector_rotation_map[month_key].get("sector_leader_return"),
                "sector_laggard": None if month_key not in sector_rotation_map else sector_rotation_map[month_key].get("sector_laggard"),
                "sector_laggard_return": None if month_key not in sector_rotation_map else sector_rotation_map[month_key].get("sector_laggard_return"),
                "sector_advance_count": None if month_key not in sector_rotation_map else sector_rotation_map[month_key].get("sector_advance_count"),
                "sector_decline_count": None if month_key not in sector_rotation_map else sector_rotation_map[month_key].get("sector_decline_count"),
                "sector_breadth_ratio": None if month_key not in sector_rotation_map else sector_rotation_map[month_key].get("sector_breadth_ratio"),
                "bond_return_3m": None if month_key not in intermarket_map else intermarket_map[month_key].get("bond_return_3m"),
                "equity_return_3m": None if month_key not in intermarket_map else intermarket_map[month_key].get("equity_return_3m"),
                "commodity_return_3m": None if month_key not in intermarket_map else intermarket_map[month_key].get("commodity_return_3m"),
                "intermarket_order": None if month_key not in intermarket_map else intermarket_map[month_key].get("intermarket_order"),
            }
        )

    return history[-months:]


def _build_tw_external_latest(external_collector, month_key: str) -> dict:
    extra_data: dict = {}

    try:
        claims_list = external_collector.fetch_mol_claims_annual()
        claims_cutoff = [row for row in claims_list if str(row.get("year", "")) <= month_key[:4]] if claims_list else []
        if claims_cutoff:
            extra_data["unemployment_claims"] = claims_cutoff[-1].get("initial_claims")
            if len(claims_cutoff) >= 2:
                trend = classify_level_trend(claims_cutoff[-1].get("initial_claims"), claims_cutoff[-2].get("initial_claims"))
                extra_data["unemployment_claims_trend"] = "falling" if trend == "falling" else "rising" if trend == "rising" else "stable"
    except Exception:
        pass

    try:
        cci_hist = external_collector.fetch_ncu_cci_history(24)
        cci = _latest_dated_row(cci_hist, month_key)
        if cci:
            extra_data["cci_total"] = cci.get("cci_total")
    except Exception:
        pass

    try:
        pmi_hist = external_collector.fetch_cier_pmi_history(24)
        pmi = _latest_dated_row(pmi_hist, month_key)
        if pmi:
            extra_data["pmi"] = pmi.get("pmi")
    except Exception:
        pass

    try:
        m2_hist = external_collector.fetch_cbc_m2_history(24)
        m2 = _latest_dated_row(m2_hist, month_key)
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
        if margin and (_row_month_key(margin.get("date"), month_key) or "9999-99") <= month_key:
            extra_data["margin_amount"] = margin.get("margin_amount")
            extra_data["margin_shares"] = margin.get("margin_shares")
            if margin.get("margin_amount") is not None:
                extra_data["margin_trend"] = "excessive" if margin.get("margin_amount", 0) >= 500000000 else "moderate"
    except Exception:
        pass

    try:
        market_hist = external_collector.fetch_twse_market_snapshot_history(24)
        market_snapshot = _latest_dated_row(market_hist, month_key)
        latest_market_snapshot = external_collector.fetch_latest_twse_market_snapshot()
        if latest_market_snapshot and (_row_month_key(latest_market_snapshot.get("date"), month_key) or "9999-99") <= month_key:
            if market_snapshot is None or (_row_month_key(latest_market_snapshot.get("date"), month_key) or "") > (_row_month_key(market_snapshot.get("date"), month_key) or ""):
                market_snapshot = latest_market_snapshot
        if market_snapshot:
            extra_data["breadth_ratio"] = market_snapshot.get("breadth_ratio")
            extra_data["advance_decline_spread"] = market_snapshot.get("advance_decline_spread")
            extra_data["sector_advance_count"] = market_snapshot.get("sector_advance_count")
            extra_data["sector_decline_count"] = market_snapshot.get("sector_decline_count")
            extra_data["sector_breadth_ratio"] = market_snapshot.get("sector_breadth_ratio")
            extra_data["sector_leader"] = market_snapshot.get("sector_leader")
            extra_data["sector_leader_return"] = market_snapshot.get("sector_leader_return")
            extra_data["sector_laggard"] = market_snapshot.get("sector_laggard")
            extra_data["sector_laggard_return"] = market_snapshot.get("sector_laggard_return")
            extra_data["breadth_regime"] = classify_breadth_regime(market_snapshot.get("breadth_ratio"))
    except Exception:
        pass

    try:
        revenue_snapshot = external_collector.fetch_latest_tw_revenue_snapshot()
        if revenue_snapshot and (_row_month_key(revenue_snapshot.get("date"), month_key) or "9999-99") <= month_key:
            extra_data["earnings_growth_proxy"] = revenue_snapshot.get("revenue_yoy")
            extra_data["revenue_current_total"] = revenue_snapshot.get("revenue_current_total")
            extra_data["revenue_year_ago_total"] = revenue_snapshot.get("revenue_year_ago_total")
    except Exception:
        pass

    try:
        bond_year = int(month_key[:4])
        bond_month = int(month_key[5:7])
        if hasattr(external_collector, "fetch_tpex_bond_data"):
            bond = external_collector.fetch_tpex_bond_data(bond_year, bond_month)
        else:
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
        discount_rows = external_collector.fetch_cbc_discount_rate()
        latest_discount_row = _latest_dated_row(discount_rows, month_key)
        if latest_discount_row:
            extra_data["funding_stress_proxy"] = latest_discount_row.get("short_term_rate")
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
    as_of_month = month_key_from_compact(full_metrics["latest_date"])
    extra_data = _build_tw_external_latest(external_collector, as_of_month) if external_collector else {}

    sahm_value = None
    unemp_hist = [v for v in [full_metrics.get("unemployment"), full_metrics.get("unemployment_prev")] if v]
    if len(unemp_hist) >= 3:
        sahm_value = compute_sahm_rule(unemp_hist)

    return {
        "as_of": as_of_month,
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

    try:
        market_hist = external_collector.fetch_twse_market_snapshot_history(months)
        if market_hist:
            external_history["market_snapshot"] = {r["date"][:7]: r for r in market_hist}
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

        if external_history.get("market_snapshot") and month_key in external_history["market_snapshot"]:
            market_snapshot = external_history["market_snapshot"][month_key]
            extra_data["breadth_ratio"] = market_snapshot.get("breadth_ratio")
            extra_data["advance_decline_spread"] = market_snapshot.get("advance_decline_spread")
            extra_data["sector_advance_count"] = market_snapshot.get("sector_advance_count")
            extra_data["sector_decline_count"] = market_snapshot.get("sector_decline_count")
            extra_data["sector_breadth_ratio"] = market_snapshot.get("sector_breadth_ratio")
            extra_data["sector_leader"] = market_snapshot.get("sector_leader")
            extra_data["sector_leader_return"] = market_snapshot.get("sector_leader_return")
            extra_data["sector_laggard"] = market_snapshot.get("sector_laggard")
            extra_data["sector_laggard_return"] = market_snapshot.get("sector_laggard_return")
            extra_data["breadth_regime"] = classify_breadth_regime(market_snapshot.get("breadth_ratio"))

        try:
            discount_rows = external_collector.fetch_cbc_discount_rate()
            rate_map = {row["date"]: row for row in discount_rows}
            if month_key in rate_map:
                extra_data["funding_stress_proxy"] = rate_map[month_key].get("short_term_rate")
        except Exception:
            pass

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
