from market_phase_detector.collectors.us_market import (
    compute_intermarket_history,
    compute_intermarket_snapshot,
    compute_sector_rotation_history,
    compute_sector_rotation_snapshot,
    parse_yahoo_spark_payload,
)


def test_parse_yahoo_spark_payload_extracts_close_rows():
    payload = {
        "spark": {
            "result": [
                {
                    "symbol": "XLK",
                    "response": [{"timestamp": [1704067200, 1706745600], "indicators": {"quote": [{"close": [100.0, 103.5]}]}}],
                }
            ]
        }
    }

    rows = parse_yahoo_spark_payload(payload)

    assert rows == {
        "XLK": [
            {"date": "2024-01-01", "close": 100.0},
            {"date": "2024-02-01", "close": 103.5},
        ]
    }


def test_compute_sector_rotation_snapshot_ranks_three_month_returns():
    series = {
        "Technology": [
            {"date": "2025-10-01", "close": 100.0},
            {"date": "2025-11-01", "close": 102.0},
            {"date": "2025-12-01", "close": 108.0},
            {"date": "2026-01-01", "close": 115.0},
        ],
        "Utilities": [
            {"date": "2025-10-01", "close": 100.0},
            {"date": "2025-11-01", "close": 98.0},
            {"date": "2025-12-01", "close": 96.0},
            {"date": "2026-01-01", "close": 94.0},
        ],
    }

    record = compute_sector_rotation_snapshot(series)

    assert record == {
        "sector_leader": "Technology",
        "sector_leader_return": 15.0,
        "sector_laggard": "Utilities",
        "sector_laggard_return": -6.0,
        "sector_advance_count": 1,
        "sector_decline_count": 1,
        "sector_breadth_ratio": 1.0,
    }


def test_compute_sector_rotation_history_returns_monthly_rankings():
    series = {
        "Technology": [
            {"date": "2025-09-01", "close": 100.0},
            {"date": "2025-10-01", "close": 102.0},
            {"date": "2025-11-01", "close": 105.0},
            {"date": "2025-12-01", "close": 109.0},
            {"date": "2026-01-01", "close": 112.0},
        ],
        "Financials": [
            {"date": "2025-09-01", "close": 100.0},
            {"date": "2025-10-01", "close": 99.0},
            {"date": "2025-11-01", "close": 98.0},
            {"date": "2025-12-01", "close": 97.0},
            {"date": "2026-01-01", "close": 96.0},
        ],
    }

    records = compute_sector_rotation_history(series, months=3)

    assert records[-1] == {
        "date": "2026-01",
        "sector_leader": "Technology",
        "sector_leader_return": 9.8,
        "sector_laggard": "Financials",
        "sector_laggard_return": -3.03,
        "sector_advance_count": 1,
        "sector_decline_count": 1,
        "sector_breadth_ratio": 1.0,
    }


def test_compute_intermarket_snapshot_returns_rank_order():
    series = {
        "Bonds": [
            {"date": "2025-10-01", "close": 100.0},
            {"date": "2025-11-01", "close": 102.0},
            {"date": "2025-12-01", "close": 105.0},
            {"date": "2026-01-01", "close": 109.0},
        ],
        "Equities": [
            {"date": "2025-10-01", "close": 100.0},
            {"date": "2025-11-01", "close": 101.0},
            {"date": "2025-12-01", "close": 103.0},
            {"date": "2026-01-01", "close": 106.0},
        ],
        "Commodities": [
            {"date": "2025-10-01", "close": 100.0},
            {"date": "2025-11-01", "close": 99.0},
            {"date": "2025-12-01", "close": 98.0},
            {"date": "2026-01-01", "close": 97.0},
        ],
    }

    record = compute_intermarket_snapshot(series)

    assert record == {
        "bond_return_3m": 9.0,
        "equity_return_3m": 6.0,
        "commodity_return_3m": -3.0,
        "intermarket_order": "Bonds > Equities > Commodities",
    }


def test_compute_intermarket_history_returns_monthly_orders():
    series = {
        "Bonds": [
            {"date": "2025-09-01", "close": 100.0},
            {"date": "2025-10-01", "close": 102.0},
            {"date": "2025-11-01", "close": 104.0},
            {"date": "2025-12-01", "close": 109.0},
            {"date": "2026-01-01", "close": 111.0},
        ],
        "Equities": [
            {"date": "2025-09-01", "close": 100.0},
            {"date": "2025-10-01", "close": 101.0},
            {"date": "2025-11-01", "close": 103.0},
            {"date": "2025-12-01", "close": 105.0},
            {"date": "2026-01-01", "close": 108.0},
        ],
        "Commodities": [
            {"date": "2025-09-01", "close": 100.0},
            {"date": "2025-10-01", "close": 100.0},
            {"date": "2025-11-01", "close": 99.0},
            {"date": "2025-12-01", "close": 98.0},
            {"date": "2026-01-01", "close": 97.0},
        ],
    }

    records = compute_intermarket_history(series, months=2)

    assert records[-1] == {
        "date": "2026-01",
        "bond_return_3m": 8.82,
        "equity_return_3m": 6.93,
        "commodity_return_3m": -3.0,
        "intermarket_order": "Bonds > Equities > Commodities",
    }
