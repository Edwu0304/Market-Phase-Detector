from market_phase_detector.live_pipeline import (
    build_tw_history_observations,
    build_tw_observations,
    build_us_history_observations,
    build_us_observations,
    classify_direction,
    compute_claims_trend,
)
from market_phase_detector.collectors import tw_official


def test_compute_claims_trend_uses_recent_average():
    rows = [
        {"date": "2026-03-01", "value": 205000.0},
        {"date": "2026-03-08", "value": 206000.0},
        {"date": "2026-03-15", "value": 207000.0},
        {"date": "2026-03-22", "value": 208000.0},
        {"date": "2026-03-29", "value": 220000.0},
        {"date": "2026-04-05", "value": 221000.0},
        {"date": "2026-04-12", "value": 222000.0},
        {"date": "2026-04-19", "value": 223000.0},
    ]
    assert compute_claims_trend(rows) == "rising"


def test_classify_direction_interprets_value_changes():
    assert classify_direction(0.31) == "improving"
    assert classify_direction(-0.12) == "deteriorating"
    assert classify_direction(0.0) == "stable"


class StubFredCollector:
    def __init__(self, payloads):
        self.payloads = payloads

    def fetch_latest_csv(self, series_id: str):
        return self.payloads[series_id]


class StubTaiwanCollector:
    def __init__(self, metrics):
        self.metrics = metrics

    def fetch_ndc_zip_metrics(self, url: str):
        return self.metrics


class StubTaiwanExternalCollector:
    def fetch_mol_claims_annual(self):
        return [
            {"date": "2024", "year": 2024, "initial_claims": 90000},
            {"date": "2025", "year": 2025, "initial_claims": 82000},
        ]

    def fetch_ncu_cci(self):
        return {"date": "2026-02", "cci_total": 71.2}

    def fetch_ncu_cci_history(self, months: int):
        return [{"date": "2026-02", "cci_total": 71.2}]

    def fetch_latest_cier_pmi(self):
        return {"date": "2026-02", "pmi": 55.4}

    def fetch_cier_pmi_history(self, months: int):
        return [{"date": "2026-02", "pmi": 55.4}]

    def fetch_twse_market_pe(self):
        return {"date": "2026-02-28", "pe_ratio": 23.22}

    def fetch_latest_twse_margin(self):
        return {"date": "2026-02-28", "margin_amount": 368046780, "margin_shares": 7872624}

    def fetch_cbc_credit_spread_proxy(self):
        return {
            "date": "2026-02-27",
            "gov_yield_10y": 1.57,
            "gov_yield_2y": 1.19,
            "spread_10y_2y": 0.38,
            "credit_spread_bbb": 0.58,
        }

    def fetch_latest_cbc_m2(self):
        return {"date": "2026-02", "m2_yoy": 5.38}

    def fetch_cbc_m2_history(self, months: int):
        return [{"date": "2026-02", "m2_yoy": 5.38}]


def test_build_us_observations_uses_fred_series():
    collector = StubFredCollector(
        {
            "IPMAN": {"rows": [{"date": "2026-03-01", "value": 0.30}, {"date": "2026-04-01", "value": 0.45}], "latest": {"date": "2026-04-01", "value": 0.45}},
            "ICSA": {
                "rows": [
                    {"date": "2026-03-01", "value": 205000.0},
                    {"date": "2026-03-08", "value": 206000.0},
                    {"date": "2026-03-15", "value": 207000.0},
                    {"date": "2026-03-22", "value": 208000.0},
                    {"date": "2026-03-29", "value": 220000.0},
                    {"date": "2026-04-05", "value": 221000.0},
                    {"date": "2026-04-12", "value": 222000.0},
                    {"date": "2026-04-19", "value": 223000.0},
                ],
                "latest": {"date": "2026-04-19", "value": 223000.0},
            },
            "SAHMCURRENT": {"rows": [{"date": "2026-04-01", "value": 0.31}], "latest": {"date": "2026-04-01", "value": 0.31}},
            "T10Y2Y": {"rows": [{"date": "2026-04-01", "value": -0.2}], "latest": {"date": "2026-04-01", "value": -0.2}},
            "BAMLH0A0HYM2": {"rows": [{"date": "2026-04-01", "value": 4.1}], "latest": {"date": "2026-04-01", "value": 4.1}},
        }
    )
    observations = build_us_observations(collector)
    assert observations["leading_index_change"] == 0.15
    assert observations["as_of"] == "2026-04"
    assert observations["claims_trend"] == "rising"
    assert observations["yield_curve"] == -0.2


def test_build_tw_observations_uses_ndc_metrics():
    collector = StubTaiwanCollector(
        {
            "latest_date": "202602",
            "business_signal_score": 29,
            "leading_index": 103.5,
            "leading_index_prev": 103.1,
            "coincident_index": 106.4,
            "coincident_index_prev": 106.1,
            "unemployment": 3.32,
            "unemployment_prev": 3.29,
            "export_value": 1367.0,
            "export_value_year_ago": 1200.0,
        }
    )
    observations = build_tw_observations(collector)
    assert observations["business_signal_score"] == 29
    assert observations["as_of"] == "2026-02"
    assert observations["leading_trend"] == "improving"
    assert observations["coincident_trend"] == "improving"
    assert observations["unemployment_trend"] == "rising"
    assert observations["exports_yoy"] > 0


def test_build_tw_observations_wires_existing_external_fields():
    collector = StubTaiwanCollector(
        {
            "latest_date": "202602",
            "business_signal_score": 29,
            "leading_index": 103.5,
            "leading_index_prev": 103.1,
            "coincident_index": 106.4,
            "coincident_index_prev": 106.1,
            "unemployment": 3.32,
            "unemployment_prev": 3.29,
            "export_value": 1367.0,
            "export_value_year_ago": 1200.0,
        }
    )
    observations = build_tw_observations(collector, external_collector=StubTaiwanExternalCollector())
    assert observations["unemployment_claims"] == 82000
    assert observations["unemployment_claims_trend"] == "falling"
    assert observations["pmi"] == 55.4
    assert observations["m2_yoy"] == 5.38
    assert observations["credit_spread"] == 0.58
    assert observations["margin_trend"] == "moderate"


def test_build_us_history_observations_can_backfill_twelve_months():
    leading_rows = []
    claims_rows = []
    sahm_rows = []
    curve_rows = []
    hy_rows = []
    for month in range(1, 14):
        year = 2025 if month <= 12 else 2026
        display_month = month if month <= 12 else 1
        month_text = f"{year}-{display_month:02d}"
        leading_rows.append({"date": f"{month_text}-01", "value": 99.0 + month * 0.2})
        sahm_rows.append({"date": f"{month_text}-01", "value": max(0.2, 0.6 - month * 0.02)})
        curve_rows.append({"date": f"{month_text}-28", "value": -0.2 + month * 0.05})
        hy_rows.append({"date": f"{month_text}-28", "value": 5.0 - month * 0.1})
        for week in range(4):
            claims_rows.append({"date": f"{month_text}-{7 + week * 7:02d}", "value": 240000.0 - month * 1500 - week * 100})

    collector = StubFredCollector(
        {
            "IPMAN": {"rows": leading_rows, "latest": leading_rows[-1]},
            "ICSA": {"rows": claims_rows, "latest": claims_rows[-1]},
            "SAHMCURRENT": {"rows": sahm_rows, "latest": sahm_rows[-1]},
            "T10Y2Y": {"rows": curve_rows, "latest": curve_rows[-1]},
            "BAMLH0A0HYM2": {"rows": hy_rows, "latest": hy_rows[-1]},
        }
    )
    observations = build_us_history_observations(collector, months=12)
    assert len(observations) == 12
    assert observations[-1]["as_of"] == observations[-1]["month"]
    assert observations[-1]["coincident_direction_score"] in {-1.0, 0.0, 1.0}


def test_build_tw_history_observations_include_lens_ready_metrics():
    indicator_rows = []
    signal_rows = []
    lagging_rows = []
    for month in range(1, 14):
        compact = f"2025{month:02d}"
        year = 2025 if month <= 12 else 2026
        display_month = month if month <= 12 else 1
        compact = f"{year}{display_month:02d}"
        indicator_rows.append(
            {
                "Date": compact,
                tw_official.LEADING_INDEX_KEY: f"{100 + month * 0.3:.1f}",
                tw_official.COINCIDENT_INDEX_KEY: f"{101 + month * 0.3:.1f}",
                tw_official.BUSINESS_SIGNAL_SCORE_KEY: f"{18 + month}",
            }
        )
        signal_rows.append({"Date": compact, tw_official.EXPORT_VALUE_KEY: f"{1200 + month * 15}"})
        signal_rows.append({"Date": f"{int(compact) - 100}", tw_official.EXPORT_VALUE_KEY: f"{1100 + month * 10}"})
        lagging_rows.append({"Date": compact, tw_official.UNEMPLOYMENT_KEY: f"{3.5 - month * 0.01:.2f}"})

    dataset = {
        tw_official.INDICATORS_FILE: indicator_rows,
        tw_official.SIGNAL_COMPONENTS_FILE: signal_rows,
        tw_official.LAGGING_FILE: lagging_rows,
    }
    observations = build_tw_history_observations(dataset, months=12)
    assert len(observations) == 12
    assert observations[-1]["as_of"] == observations[-1]["month"]
    assert "leading_index_change" in observations[-1]
    assert "exports_yoy" in observations[-1]
