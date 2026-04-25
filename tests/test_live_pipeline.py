from market_phase_detector.live_pipeline import (
    build_tw_history_observations,
    build_tw_observations,
    build_us_history_observations,
    build_us_observations,
    classify_breadth_regime,
    classify_direction,
    classify_distress_regime,
    classify_issuance_appetite,
    compute_claims_trend,
    compute_distress_proxy,
    compute_issuance_appetite_proxy,
    classify_yield_curve_regime,
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


def test_classify_yield_curve_regime_distinguishes_major_states():
    assert classify_yield_curve_regime(4.3, 4.0, 3.7, 3.7) == "bear_steepening"
    assert classify_yield_curve_regime(3.8, 3.9, 3.2, 4.0) == "bull_steepening"
    assert classify_yield_curve_regime(4.0, 4.2, 3.8, 3.6) == "flattening"
    assert classify_yield_curve_regime(4.0, 4.1, 4.4, 4.3) == "inversion"


def test_classify_breadth_regime_maps_ratio_to_state():
    assert classify_breadth_regime(1.35) == "broadening"
    assert classify_breadth_regime(0.65) == "narrowing"
    assert classify_breadth_regime(1.0) == "balanced"


def test_distress_and_issuance_proxies_classify_risk_regimes():
    distress = compute_distress_proxy(4.0, 0.8, 12.0)
    issuance = compute_issuance_appetite_proxy(6.8, 5.3)
    assert distress == 3.4
    assert classify_distress_regime(distress) == "high"
    assert issuance == 12.55
    assert classify_issuance_appetite(issuance) == "selective"
    issuance_selective = compute_issuance_appetite_proxy(6.8, 12.0)
    assert issuance_selective == 9.2
    assert classify_issuance_appetite(issuance_selective) == "selective"


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

    def fetch_cbc_discount_rate(self):
        return [
            {"date": "2026-01", "discount_rate": 1.875, "accommodation_rate": 2.25, "short_term_rate": 0.82},
            {"date": "2026-02", "discount_rate": 1.875, "accommodation_rate": 2.25, "short_term_rate": 0.91},
        ]

    def fetch_latest_twse_market_snapshot(self):
        return {
            "date": "2026-02-28",
            "breadth_ratio": 1.31,
            "advance_decline_spread": 122,
            "sector_advance_count": 20,
            "sector_decline_count": 12,
            "sector_breadth_ratio": 1.6667,
            "sector_leader": "電子零組件類指數",
            "sector_leader_return": 3.01,
            "sector_laggard": "玻璃陶瓷類指數",
            "sector_laggard_return": -2.8,
        }

    def fetch_twse_market_snapshot_history(self, months: int = 24):
        return [
            {
                "date": "2026-01-31",
                "breadth_ratio": 1.05,
                "advance_decline_spread": 18,
                "sector_advance_count": 18,
                "sector_decline_count": 17,
                "sector_breadth_ratio": 1.0588,
                "sector_leader": "光電類指數",
                "sector_leader_return": 3.18,
                "sector_laggard": "居家生活類指數",
                "sector_laggard_return": -2.39,
            }
        ]


class StubUSMarketCollector:
    def fetch_sector_rotation_snapshot(self):
        return {
            "sector_leader": "Technology",
            "sector_leader_return": 12.4,
            "sector_laggard": "Utilities",
            "sector_laggard_return": -3.2,
        }

    def fetch_sector_rotation_history(self, months: int = 24):
        return [
            {
                "date": "2026-01",
                "sector_leader": "Technology",
                "sector_leader_return": 8.2,
                "sector_laggard": "Utilities",
                "sector_laggard_return": -2.1,
            },
            {
                "date": "2026-02",
                "sector_leader": "Technology",
                "sector_leader_return": 12.4,
                "sector_laggard": "Utilities",
                "sector_laggard_return": -3.2,
            },
        ]

    def fetch_intermarket_snapshot(self):
        return {
            "bond_return_3m": 6.4,
            "equity_return_3m": 2.1,
            "commodity_return_3m": -1.3,
            "intermarket_order": "Bonds > Equities > Commodities",
        }

    def fetch_intermarket_history(self, months: int = 24):
        return [
            {
                "date": "2026-01",
                "bond_return_3m": 5.8,
                "equity_return_3m": 1.9,
                "commodity_return_3m": -0.5,
                "intermarket_order": "Bonds > Equities > Commodities",
            },
            {
                "date": "2026-02",
                "bond_return_3m": 6.4,
                "equity_return_3m": 2.1,
                "commodity_return_3m": -1.3,
                "intermarket_order": "Bonds > Equities > Commodities",
            },
        ]


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
            "T5YIE": {"rows": [{"date": "2026-04-01", "value": 2.3}], "latest": {"date": "2026-04-01", "value": 2.3}},
            "STLFSI4": {"rows": [{"date": "2026-04-01", "value": -0.4}], "latest": {"date": "2026-04-01", "value": -0.4}},
            "DRTSCILM": {"rows": [{"date": "2026-04-01", "value": 12.0}], "latest": {"date": "2026-04-01", "value": 12.0}},
            "DGS10": {"rows": [{"date": "2026-03-01", "value": 4.0}, {"date": "2026-04-01", "value": 4.3}], "latest": {"date": "2026-04-01", "value": 4.3}},
            "DGS2": {"rows": [{"date": "2026-03-01", "value": 3.7}, {"date": "2026-04-01", "value": 3.7}], "latest": {"date": "2026-04-01", "value": 3.7}},
            "PPIACO": {"rows": [{"date": "2026-03-01", "value": 220.0}, {"date": "2026-04-01", "value": 223.0}], "latest": {"date": "2026-04-01", "value": 223.0}},
            "WPU10": {"rows": [{"date": "2026-03-01", "value": 188.0}, {"date": "2026-04-01", "value": 191.5}], "latest": {"date": "2026-04-01", "value": 191.5}},
            "USEPUINDXM": {"rows": [{"date": "2026-04-01", "value": 262.0}], "latest": {"date": "2026-04-01", "value": 262.0}},
            "BAMLH0A0HYM2EY": {"rows": [{"date": "2026-04-01", "value": 7.2}], "latest": {"date": "2026-04-01", "value": 7.2}},
            "A3202C0A144NBEA": {"rows": [{"date": "2025-10-01", "value": 3100.0}, {"date": "2026-01-01", "value": 3255.0}], "latest": {"date": "2026-01-01", "value": 3255.0}},
            "DRBLACBS": {"rows": [{"date": "2026-04-01", "value": 1.1}], "latest": {"date": "2026-04-01", "value": 1.1}},
            "CORBLACBS": {"rows": [{"date": "2026-04-01", "value": 0.55}], "latest": {"date": "2026-04-01", "value": 0.55}},
        }
    )
    observations = build_us_observations(collector, market_collector=StubUSMarketCollector())
    assert observations["leading_index_change"] == 0.15
    assert observations["as_of"] == "2026-04"
    assert observations["claims_trend"] == "rising"
    assert observations["yield_curve"] == -0.2
    assert observations["inflation_expectation_5y"] == 2.3
    assert observations["funding_stress"] == -0.4
    assert observations["lending_standards"] == 12.0
    assert observations["yield_curve_regime"] == "bear_steepening"
    assert observations["commodity_index"] == 223.0
    assert observations["commodity_trend"] == "improving"
    assert observations["industrial_metals_index"] == 191.5
    assert observations["industrial_metals_trend"] == "improving"
    assert observations["policy_uncertainty"] == 262.0
    assert observations["hy_yield"] == 7.2
    assert observations["earnings_growth_proxy"] == 5.0
    assert observations["default_pressure_proxy"] == 1.65
    assert observations["default_pressure_regime"] == "elevated"
    assert observations["sector_leader"] == "Technology"
    assert observations["sector_laggard"] == "Utilities"
    assert observations["distress_regime"] == "high"
    assert observations["issuance_appetite_regime"] == "selective"
    assert observations["intermarket_order"] == "Bonds > Equities > Commodities"


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
    assert observations["funding_stress_proxy"] == 0.91
    assert observations["breadth_regime"] == "broadening"


def test_build_tw_observations_prefers_latest_discount_rate_by_date():
    class ReverseOrderedExternalCollector(StubTaiwanExternalCollector):
        def fetch_cbc_discount_rate(self):
            return [
                {"date": "2026-02", "discount_rate": 1.875, "accommodation_rate": 2.25, "short_term_rate": 0.91},
                {"date": "2026-01", "discount_rate": 1.875, "accommodation_rate": 2.25, "short_term_rate": 0.82},
            ]

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

    observations = build_tw_observations(collector, external_collector=ReverseOrderedExternalCollector())

    assert observations["funding_stress_proxy"] == 0.91


def test_build_tw_observations_uses_bond_data_for_observation_month():
    class MonthAwareExternalCollector(StubTaiwanExternalCollector):
        def fetch_tpex_bond_data(self, year: int, month: int):
            assert (year, month) == (2026, 2)
            return {
                "date": "2026-02-26",
                "gov_yield_10y": 1.415,
                "gov_yield_2y": 1.569,
                "spread_10y_2y": -0.154,
                "credit_spread_bbb": 0.7358,
            }

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

    observations = build_tw_observations(collector, external_collector=MonthAwareExternalCollector())

    assert observations["gov_yield_10y"] == 1.415
    assert observations["gov_yield_2y"] == 1.569
    assert observations["yield_curve_spread"] == -0.154
    assert observations["credit_spread_bbb"] == 0.7358


def test_build_tw_observations_cuts_external_data_to_phase_month():
    class FutureBiasedExternalCollector(StubTaiwanExternalCollector):
        def fetch_ncu_cci(self):
            return {"date": "2026-03", "cci_total": 62.3}

        def fetch_ncu_cci_history(self, months: int):
            return [
                {"date": "2026-02", "cci_total": 66.58},
                {"date": "2026-03", "cci_total": 62.3},
            ]

        def fetch_latest_cier_pmi(self):
            return {"date": "2026-03", "pmi": 55.4}

        def fetch_cier_pmi_history(self, months: int):
            return [
                {"date": "2026-02", "pmi": 58.5},
                {"date": "2026-03", "pmi": 55.4},
            ]

        def fetch_latest_cbc_m2(self):
            return {"date": "2026-03", "m2_yoy": 5.38}

        def fetch_cbc_m2_history(self, months: int):
            return [
                {"date": "2026-02", "m2_yoy": 5.16},
                {"date": "2026-03", "m2_yoy": 5.38},
            ]

        def fetch_latest_twse_market_snapshot(self):
            return {
                "date": "2026-04-17",
                "breadth_ratio": 1.0061,
                "advance_decline_spread": 3,
                "sector_advance_count": 20,
                "sector_decline_count": 17,
                "sector_breadth_ratio": 1.1765,
                "sector_leader": "玻璃陶瓷類指數",
                "sector_leader_return": 5.75,
                "sector_laggard": "塑膠類指數",
                "sector_laggard_return": -2.55,
            }

        def fetch_twse_market_snapshot_history(self, months: int = 24):
            return [
                {
                    "date": "2026-02-28",
                    "breadth_ratio": 1.31,
                    "advance_decline_spread": 122,
                    "sector_advance_count": 20,
                    "sector_decline_count": 12,
                    "sector_breadth_ratio": 1.6667,
                    "sector_leader": "航運類指數",
                    "sector_leader_return": 3.01,
                    "sector_laggard": "金融保險類指數",
                    "sector_laggard_return": -2.8,
                }
            ]

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

    observations = build_tw_observations(collector, external_collector=FutureBiasedExternalCollector())

    assert observations["cci_total"] == 66.58
    assert observations["pmi"] == 58.5
    assert observations["m2_yoy"] == 5.16
    assert observations["breadth_ratio"] == 1.31


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
            "T5YIE": {"rows": [{"date": row["date"], "value": 2.0 + i * 0.02} for i, row in enumerate(sahm_rows)], "latest": {"date": sahm_rows[-1]["date"], "value": 2.24}},
            "STLFSI4": {"rows": [{"date": row["date"], "value": -0.5 + i * 0.05} for i, row in enumerate(sahm_rows)], "latest": {"date": sahm_rows[-1]["date"], "value": 0.1}},
            "DRTSCILM": {"rows": [{"date": row["date"], "value": 5.0 + i} for i, row in enumerate(sahm_rows)], "latest": {"date": sahm_rows[-1]["date"], "value": 17.0}},
            "DGS10": {"rows": [{"date": row["date"], "value": 3.5 + i * 0.05} for i, row in enumerate(sahm_rows)], "latest": {"date": sahm_rows[-1]["date"], "value": 4.1}},
            "DGS2": {"rows": [{"date": row["date"], "value": 3.2 + i * 0.04} for i, row in enumerate(sahm_rows)], "latest": {"date": sahm_rows[-1]["date"], "value": 3.68}},
            "PPIACO": {"rows": [{"date": row["date"], "value": 200 + i * 1.5} for i, row in enumerate(sahm_rows)], "latest": {"date": sahm_rows[-1]["date"], "value": 218.0}},
            "WPU10": {"rows": [{"date": row["date"], "value": 180 + i * 1.2} for i, row in enumerate(sahm_rows)], "latest": {"date": sahm_rows[-1]["date"], "value": 194.4}},
            "USEPUINDXM": {"rows": [{"date": row["date"], "value": 110 + i * 5.0} for i, row in enumerate(sahm_rows)], "latest": {"date": sahm_rows[-1]["date"], "value": 170.0}},
            "BAMLH0A0HYM2EY": {"rows": [{"date": row["date"], "value": 6.0 + i * 0.1} for i, row in enumerate(sahm_rows)], "latest": {"date": sahm_rows[-1]["date"], "value": 8.4}},
            "A3202C0A144NBEA": {"rows": [{"date": "2025-01-01", "value": 3000.0}, {"date": "2025-04-01", "value": 3060.0}, {"date": "2025-07-01", "value": 3120.0}, {"date": "2025-10-01", "value": 3210.0}, {"date": "2026-01-01", "value": 3300.0}], "latest": {"date": "2026-01-01", "value": 3300.0}},
            "DRBLACBS": {"rows": [{"date": row["date"], "value": 0.8 + i * 0.03} for i, row in enumerate(sahm_rows)], "latest": {"date": sahm_rows[-1]["date"], "value": 1.52}},
            "CORBLACBS": {"rows": [{"date": row["date"], "value": 0.4 + i * 0.02} for i, row in enumerate(sahm_rows)], "latest": {"date": sahm_rows[-1]["date"], "value": 0.88}},
        }
    )
    observations = build_us_history_observations(collector, market_collector=StubUSMarketCollector(), months=12)
    assert len(observations) == 12
    assert observations[-1]["as_of"] == observations[-1]["month"]
    assert observations[-1]["coincident_direction_score"] in {-1.0, 0.0, 1.0}
    assert "yield_curve_regime" in observations[-1]
    assert "inflation_expectation_5y" in observations[-1]
    assert "lending_standards" in observations[-1]
    assert "commodity_index" in observations[-1]
    assert "industrial_metals_index" in observations[-1]
    assert "policy_uncertainty" in observations[-1]
    assert "hy_yield" in observations[-1]
    assert "earnings_growth_proxy" in observations[-1]
    assert "default_pressure_proxy" in observations[-1]
    assert observations[-1]["sector_leader"] == "Technology"
    assert observations[-1]["distress_regime"] in {"contained", "elevated", "high"}
    assert observations[-1]["issuance_appetite_regime"] in {"tight", "selective", "open"}
    assert observations[-1]["intermarket_order"] == "Bonds > Equities > Commodities"


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
    observations = build_tw_history_observations(dataset, external_collector=StubTaiwanExternalCollector(), months=12)
    assert len(observations) == 12
    assert observations[-1]["as_of"] == observations[-1]["month"]
    assert "leading_index_change" in observations[-1]
    assert "exports_yoy" in observations[-1]
    assert "breadth_regime" in observations[-1]
