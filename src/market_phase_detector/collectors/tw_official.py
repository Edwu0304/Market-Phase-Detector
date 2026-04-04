import re
import csv
import io
import zipfile
import requests

from market_phase_detector.collectors.base import HttpCollector


def parse_tw_series_payload(payload: list[dict]) -> dict:
    latest = payload[-1]
    return {
        "date": latest["date"],
        "value": float(latest["value"]),
    }


def parse_ndc_homepage_metrics(html: str) -> dict:
    date_match = re.search(r"\(([A-Z][a-z]{2}\.\d{4})\)", html)
    signal_match = re.search(r"Monitoring Indicators\s+Monitoring Indicators\s+(\d+)", html)
    leading_match = re.search(r"Leading\s+([+-]?\d+(?:\.\d+)?)%", html)
    coincident_match = re.search(r"Coincident\s+([+-]?\d+(?:\.\d+)?)%", html)

    if not all([date_match, signal_match, leading_match, coincident_match]):
        raise ValueError("Could not parse NDC homepage business indicators block")

    return {
        "date_label": date_match.group(1),
        "business_signal_score": int(signal_match.group(1)),
        "leading_change": float(leading_match.group(1)),
        "coincident_change": float(coincident_match.group(1)),
    }


def parse_ndc_zip(zip_bytes: bytes) -> dict[str, list[dict]]:
    archive = zipfile.ZipFile(io.BytesIO(zip_bytes))
    dataset: dict[str, list[dict]] = {}
    for name in archive.namelist():
        if name == "manifest.csv" or name.startswith("schema-"):
            continue
        text = archive.read(name).decode("utf-8-sig")
        dataset[name] = list(csv.DictReader(io.StringIO(text)))
    return dataset


def extract_latest_ndc_metrics(dataset: dict[str, list[dict]]) -> dict:
    indicators = dataset["景氣指標與燈號.csv"]
    signal_components = dataset["景氣對策信號構成項目.csv"]
    lagging = dataset["落後指標構成項目.csv"]

    latest = indicators[-1]
    previous = indicators[-2]

    lagging_by_date = {row["Date"]: row for row in lagging}
    signal_by_date = {row["Date"]: row for row in signal_components}

    previous_unemployment = lagging_by_date.get(previous["Date"], lagging[-2] if len(lagging) > 1 else lagging[-1])
    year_ago_date = f"{int(latest['Date']) - 100}"

    return {
        "latest_date": latest["Date"],
        "business_signal_score": int(float(latest["景氣對策信號綜合分數"])),
        "leading_index": float(latest["領先指標不含趨勢指數"]),
        "leading_index_prev": float(previous["領先指標不含趨勢指數"]),
        "coincident_index": float(latest["同時指標不含趨勢指數"]),
        "coincident_index_prev": float(previous["同時指標不含趨勢指數"]),
        "unemployment": float(lagging_by_date[latest["Date"]]["失業率(%)"]),
        "unemployment_prev": float(previous_unemployment["失業率(%)"]),
        "export_value": float(signal_by_date[latest["Date"]]["海關出口值(十億元)"]),
        "export_value_year_ago": float(signal_by_date[year_ago_date]["海關出口值(十億元)"]),
    }


class TaiwanOfficialCollector(HttpCollector):
    def fetch_latest(self, url: str, params: dict | None = None) -> dict:
        payload = self.get_json(url, params=params)
        if not isinstance(payload, list):
            raise TypeError("Expected Taiwan official payload to be a list")
        return parse_tw_series_payload(payload)

    def fetch_ndc_homepage_metrics(self, url: str) -> dict:
        html = self.get_text(url)
        return parse_ndc_homepage_metrics(html)

    def fetch_bytes(self, url: str, params: dict | None = None) -> bytes:
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.content

    def fetch_ndc_zip_metrics(self, url: str) -> dict:
        zip_bytes = self.fetch_bytes(url)
        dataset = parse_ndc_zip(zip_bytes)
        return extract_latest_ndc_metrics(dataset)
