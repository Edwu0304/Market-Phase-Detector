from market_phase_detector.collectors.us_fred import parse_fred_csv, parse_fred_payload


def test_parse_fred_payload_extracts_latest_value():
    payload = {
        "observations": [
            {"date": "2026-02-01", "value": "50.2"},
            {"date": "2026-03-01", "value": "49.8"},
        ]
    }

    result = parse_fred_payload(payload)

    assert result["date"] == "2026-03-01"
    assert result["value"] == 49.8


def test_parse_fred_csv_extracts_rows_and_latest_value():
    csv_text = "DATE,VALUE\n2026-03-01,51.2\n2026-04-01,52.0\n"

    result = parse_fred_csv(csv_text)

    assert result["latest"]["date"] == "2026-04-01"
    assert result["latest"]["value"] == 52.0
    assert len(result["rows"]) == 2


def test_parse_fred_csv_handles_series_named_value_column():
    csv_text = "observation_date,USSLIND\n2026-03-01,0.30\n2026-04-01,0.45\n"

    result = parse_fred_csv(csv_text)

    assert result["latest"]["date"] == "2026-04-01"
    assert result["latest"]["value"] == 0.45


def test_parse_fred_csv_skips_blank_rows():
    csv_text = "observation_date,T10Y2Y\n2026-03-01,-0.20\n2026-04-01,\n"

    result = parse_fred_csv(csv_text)

    assert result["latest"]["date"] == "2026-03-01"
    assert result["latest"]["value"] == -0.2
