from market_phase_detector.collectors.tw_official import (
    extract_latest_ndc_metrics,
    parse_tw_series_payload,
)


def test_parse_tw_series_payload_extracts_latest_entry():
    payload = [
        {"date": "2026-01", "value": "17"},
        {"date": "2026-02", "value": "19"},
    ]

    result = parse_tw_series_payload(payload)

    assert result["date"] == "2026-02"
    assert result["value"] == 19.0


def test_extract_latest_ndc_metrics_combines_zip_tables():
    dataset = {
        "景氣指標與燈號.csv": [
            {
                "Date": "202601",
                "領先指標不含趨勢指數": "103.4",
                "同時指標不含趨勢指數": "106.1",
                "景氣對策信號綜合分數": "27",
                "景氣對策信號": "黃紅燈",
            },
            {
                "Date": "202602",
                "領先指標不含趨勢指數": "103.8",
                "同時指標不含趨勢指數": "106.4",
                "景氣對策信號綜合分數": "29",
                "景氣對策信號": "黃紅燈",
            },
        ],
        "景氣對策信號構成項目.csv": [
            {"Date": "202502", "海關出口值(十億元)": "1200.0"},
            {"Date": "202602", "海關出口值(十億元)": "1367.0"},
        ],
        "落後指標構成項目.csv": [
            {"Date": "202601", "失業率(%)": "3.29"},
            {"Date": "202602", "失業率(%)": "3.32"},
        ],
    }

    result = extract_latest_ndc_metrics(dataset)

    assert result["latest_date"] == "202602"
    assert result["business_signal_score"] == 29
    assert result["leading_index"] == 103.8
    assert result["leading_index_prev"] == 103.4
    assert result["coincident_index"] == 106.4
    assert result["unemployment"] == 3.32
