import csv
import io

from market_phase_detector.collectors.base import HttpCollector


FRED_SERIES_URL = "https://api.stlouisfed.org/fred/series/observations"
FRED_GRAPH_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv"


def parse_fred_payload(payload: dict) -> dict:
    latest = payload["observations"][-1]
    return {
        "date": latest["date"],
        "value": float(latest["value"]),
    }


def parse_fred_csv(csv_text: str) -> dict:
    reader = csv.DictReader(io.StringIO(csv_text))
    rows = []
    headers = reader.fieldnames or []
    if len(headers) < 2:
        raise ValueError("FRED CSV payload must contain date and value columns")

    date_key = headers[0]
    value_key = headers[1]

    for row in reader:
        value = row[value_key]
        if value in {".", "", None}:
            continue
        rows.append(
            {
                "date": row[date_key],
                "value": float(value),
            }
        )

    if not rows:
        raise ValueError("FRED CSV payload did not contain any numeric rows")

    return {
        "rows": rows,
        "latest": rows[-1],
    }


class FredCollector(HttpCollector):
    def fetch_latest(self, series_id: str, api_key: str) -> dict:
        payload = self.get_json(
            FRED_SERIES_URL,
            params={
                "series_id": series_id,
                "api_key": api_key,
                "file_type": "json",
            },
        )
        return parse_fred_payload(payload)

    def fetch_latest_csv(self, series_id: str) -> dict:
        text = self.get_text(
            FRED_GRAPH_URL,
            params={"id": series_id},
        )
        return parse_fred_csv(text)
