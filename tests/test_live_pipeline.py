from market_phase_detector.live_pipeline import (
    classify_direction,
    compute_claims_trend,
    build_us_observations,
    build_tw_observations,
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
