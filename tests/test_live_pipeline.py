from market_phase_detector.live_pipeline import (
    classify_direction,
    compute_claims_trend,
    build_us_observations,
    build_tw_observations,
    build_us_history_observations,
    build_tw_history_observations,
)


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


def test_build_us_observations_uses_fred_series():
    collector = StubFredCollector(
        {
            "IPMAN": {
                "rows": [
                    {"date": "2026-01-01", "value": 0.10},
                    {"date": "2026-02-01", "value": 0.20},
                    {"date": "2026-03-01", "value": 0.30},
                    {"date": "2026-04-01", "value": 0.45},
                ],
                "latest": {"date": "2026-04-01", "value": 0.45},
            },
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
    assert observations["leading_trend"] == "improving"
    assert observations["coincident_trend"] == "improving"
    assert observations["unemployment_trend"] == "rising"
    assert observations["exports_yoy"] > 0


def test_build_us_history_observations_returns_multiple_months():
    collector = StubFredCollector(
        {
            "IPMAN": {
                "rows": [
                    {"date": "2026-01-01", "value": 99.7},
                    {"date": "2026-02-01", "value": 99.8},
                    {"date": "2026-03-01", "value": 100.1},
                    {"date": "2026-04-01", "value": 100.4},
                ],
                "latest": {"date": "2026-04-01", "value": 100.4},
            },
            "ICSA": {
                "rows": [
                    {"date": "2026-01-10", "value": 230000.0},
                    {"date": "2026-01-17", "value": 231000.0},
                    {"date": "2026-01-24", "value": 232000.0},
                    {"date": "2026-01-31", "value": 233000.0},
                    {"date": "2026-02-07", "value": 225000.0},
                    {"date": "2026-02-14", "value": 224000.0},
                    {"date": "2026-02-21", "value": 223000.0},
                    {"date": "2026-02-28", "value": 222000.0},
                    {"date": "2026-03-07", "value": 220000.0},
                    {"date": "2026-03-14", "value": 219000.0},
                    {"date": "2026-03-21", "value": 218000.0},
                    {"date": "2026-03-28", "value": 217000.0},
                    {"date": "2026-04-04", "value": 216000.0},
                    {"date": "2026-04-11", "value": 215000.0},
                    {"date": "2026-04-18", "value": 214000.0},
                    {"date": "2026-04-25", "value": 213000.0},
                ],
                "latest": {"date": "2026-04-25", "value": 213000.0},
            },
            "SAHMCURRENT": {
                "rows": [
                    {"date": "2026-01-01", "value": 0.45},
                    {"date": "2026-02-01", "value": 0.42},
                    {"date": "2026-03-01", "value": 0.35},
                    {"date": "2026-04-01", "value": 0.30},
                ],
                "latest": {"date": "2026-04-01", "value": 0.30},
            },
            "T10Y2Y": {
                "rows": [
                    {"date": "2026-01-30", "value": -0.25},
                    {"date": "2026-02-27", "value": -0.15},
                    {"date": "2026-03-31", "value": 0.10},
                    {"date": "2026-04-30", "value": 0.20},
                ],
                "latest": {"date": "2026-04-30", "value": 0.20},
            },
            "BAMLH0A0HYM2": {
                "rows": [
                    {"date": "2026-01-30", "value": 4.60},
                    {"date": "2026-02-27", "value": 4.20},
                    {"date": "2026-03-31", "value": 3.90},
                    {"date": "2026-04-30", "value": 3.60},
                ],
                "latest": {"date": "2026-04-30", "value": 3.60},
            },
        }
    )

    observations = build_us_history_observations(collector, months=3)

    assert [row["month"] for row in observations] == ["2026-02", "2026-03", "2026-04"]
    assert observations[-1]["claims_trend"] == "falling"
    assert observations[-1]["yield_curve"] == 0.20


def test_build_tw_history_observations_returns_multiple_months():
    dataset = {
        "景氣指標與燈號.csv": [
            {
                "Date": "202501",
                "領先指標不含趨勢指數": "100.0",
                "同時指標不含趨勢指數": "101.0",
                "景氣對策信號綜合分數": "20",
            },
            {
                "Date": "202502",
                "領先指標不含趨勢指數": "100.4",
                "同時指標不含趨勢指數": "101.2",
                "景氣對策信號綜合分數": "24",
            },
            {
                "Date": "202503",
                "領先指標不含趨勢指數": "100.8",
                "同時指標不含趨勢指數": "101.6",
                "景氣對策信號綜合分數": "28",
            },
        ],
        "景氣對策信號構成項目.csv": [
            {"Date": "202403", "海關出口值(十億元)": "1100"},
            {"Date": "202501", "海關出口值(十億元)": "1200"},
            {"Date": "202402", "海關出口值(十億元)": "1080"},
            {"Date": "202502", "海關出口值(十億元)": "1220"},
            {"Date": "202503", "海關出口值(十億元)": "1260"},
            {"Date": "202403", "海關出口值(十億元)": "1100"},
        ],
        "落後指標構成項目.csv": [
            {"Date": "202501", "失業率(%)": "3.40"},
            {"Date": "202502", "失業率(%)": "3.35"},
            {"Date": "202503", "失業率(%)": "3.30"},
        ],
    }

    observations = build_tw_history_observations(dataset, months=2)

    assert [row["month"] for row in observations] == ["2025-02", "2025-03"]
    assert observations[-1]["leading_trend"] == "improving"
    assert observations[-1]["exports_yoy"] > 0
