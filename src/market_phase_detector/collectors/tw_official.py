import csv
import io
import re
import zipfile

import requests

from market_phase_detector.collectors.base import HttpCollector


INDICATORS_FILE = "景氣指標與燈號.csv"
SIGNAL_COMPONENTS_FILE = "景氣對策信號構成項目.csv"
LAGGING_FILE = "落後指標構成項目.csv"
LEADING_FILE = "領先指標構成項目.csv"
COINCIDENT_FILE = "同時指標構成項目.csv"

LEADING_INDEX_KEY = "領先指標不含趨勢指數"
COINCIDENT_INDEX_KEY = "同時指標不含趨勢指數"
BUSINESS_SIGNAL_SCORE_KEY = "景氣對策信號綜合分數"
UNEMPLOYMENT_KEY = "失業率(%)"
EXPORT_VALUE_KEY = "海關出口值(十億元)"

# 新增真實指標欄位映射
M1B_KEY = "貨幣總計數M1B(百萬元)"
STOCK_INDEX_KEY = "股價指數(Index1966=100)"
INDUSTRIAL_PRODUCTION_KEY = "工業生產指數(Index2021=100)"
OVERTIME_HOURS_KEY = "工業及服務業加班工時(小時)"
MACHINERY_IMPORT_KEY = "機械及電機設備進口值(十億元)"
MANUFACTURING_SALES_KEY = "製造業銷售量指數(Index2021=100)"
RETAIL_KEY = "批發、零售及餐飲業營業額(十億元)"
INVENTORY_KEY = "製造業存貨價值(千元)"
BANK_LENDING_RATE_KEY = "五大銀行新承做放款平均利率(年息百分比)"
TOTAL_CREDIT_KEY = "全體金融機構放款與投資(十億元)"
UNIT_LABOR_COST_KEY = "製造業單位產出勞動成本指數(2021=100)"


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


def _as_float(row: dict, key: str) -> float | None:
    value = row.get(key, "")
    if value in {"", "-", None}:
        return None
    return float(value)


def extract_ndc_history_metrics(dataset: dict[str, list[dict]]) -> list[dict]:
    indicators = dataset[INDICATORS_FILE]
    signal_components = dataset[SIGNAL_COMPONENTS_FILE]
    lagging = dataset[LAGGING_FILE]
    leading = dataset.get(LEADING_FILE, [])
    coincident = dataset.get(COINCIDENT_FILE, [])

    lagging_by_date = {row["Date"]: row for row in lagging}
    signal_by_date = {row["Date"]: row for row in signal_components}
    leading_by_date = {row["Date"]: row for row in leading} if leading else {}
    coincident_by_date = {row["Date"]: row for row in coincident} if coincident else {}
    history: list[dict] = []

    for index in range(1, len(indicators)):
        current = indicators[index]
        previous = indicators[index - 1]
        current_date = current["Date"]
        year_ago_date = f"{int(current_date) - 100}"

        lagging_row = lagging_by_date.get(current_date)
        previous_lagging_row = lagging_by_date.get(previous["Date"])
        signal_row = signal_by_date.get(current_date)
        year_ago_signal_row = signal_by_date.get(year_ago_date)
        leading_row = leading_by_date.get(current_date)
        previous_leading_row = leading_by_date.get(previous["Date"]) if previous["Date"] in leading_by_date else None
        if not all([lagging_row, previous_lagging_row, signal_row, year_ago_signal_row]):
            continue

        leading_index = _as_float(current, LEADING_INDEX_KEY)
        leading_index_prev = _as_float(previous, LEADING_INDEX_KEY)
        coincident_index = _as_float(current, COINCIDENT_INDEX_KEY)
        coincident_index_prev = _as_float(previous, COINCIDENT_INDEX_KEY)
        business_signal_score = _as_float(current, BUSINESS_SIGNAL_SCORE_KEY)
        unemployment = _as_float(lagging_row, UNEMPLOYMENT_KEY)
        unemployment_prev = _as_float(previous_lagging_row, UNEMPLOYMENT_KEY)
        export_value = _as_float(signal_row, EXPORT_VALUE_KEY)
        export_value_year_ago = _as_float(year_ago_signal_row, EXPORT_VALUE_KEY)

        # 新增真實指標
        stock_index = _as_float(signal_row, STOCK_INDEX_KEY)
        stock_index_prev = _as_float(signal_by_date.get(previous["Date"], {}), STOCK_INDEX_KEY)
        industrial_production = _as_float(signal_row, INDUSTRIAL_PRODUCTION_KEY)
        industrial_production_prev = _as_float(signal_by_date.get(previous["Date"], {}), INDUSTRIAL_PRODUCTION_KEY)
        overtime_hours = _as_float(signal_row, OVERTIME_HOURS_KEY)
        overtime_hours_prev = _as_float(signal_by_date.get(previous["Date"], {}), OVERTIME_HOURS_KEY)
        machinery_import_val = _as_float(signal_row, MACHINERY_IMPORT_KEY)
        machinery_import_prev = _as_float(signal_by_date.get(previous["Date"], {}), MACHINERY_IMPORT_KEY)
        manufacturing_sales = _as_float(signal_row, MANUFACTURING_SALES_KEY)
        manufacturing_sales_prev = _as_float(signal_by_date.get(previous["Date"], {}), MANUFACTURING_SALES_KEY)
        retail_sales = _as_float(signal_row, RETAIL_KEY)
        retail_sales_prev = _as_float(signal_by_date.get(previous["Date"], {}), RETAIL_KEY)
        inventory = _as_float(signal_row, INVENTORY_KEY)
        inventory_prev = _as_float(signal_by_date.get(previous["Date"], {}), INVENTORY_KEY)
        bank_lending_rate = _as_float(lagging_row, BANK_LENDING_RATE_KEY)
        bank_lending_rate_prev = _as_float(previous_lagging_row, BANK_LENDING_RATE_KEY)
        total_credit = _as_float(lagging_row, TOTAL_CREDIT_KEY)
        total_credit_prev = _as_float(previous_lagging_row, TOTAL_CREDIT_KEY)
        unit_labor_cost = _as_float(lagging_row, UNIT_LABOR_COST_KEY)
        unit_labor_cost_prev = _as_float(previous_lagging_row, UNIT_LABOR_COST_KEY)
        m1b = _as_float(signal_row, M1B_KEY)
        m1b_prev = _as_float(signal_by_date.get(previous["Date"], {}), M1B_KEY)

        # 基本指標必須存在，真實指標允許 None
        if any(
            value is None
            for value in [
                leading_index,
                leading_index_prev,
                coincident_index,
                coincident_index_prev,
                business_signal_score,
                unemployment,
                unemployment_prev,
                export_value,
                export_value_year_ago,
            ]
        ):
            continue

        history.append(
            {
                "latest_date": current_date,
                # 原始指標
                "business_signal_score": int(business_signal_score),
                "leading_index": leading_index,
                "leading_index_prev": leading_index_prev,
                "coincident_index": coincident_index,
                "coincident_index_prev": coincident_index_prev,
                "unemployment": unemployment,
                "unemployment_prev": unemployment_prev,
                "export_value": export_value,
                "export_value_year_ago": export_value_year_ago,
                # 新增真實指標
                "stock_index": stock_index,
                "stock_index_prev": stock_index_prev,
                "industrial_production": industrial_production,
                "industrial_production_prev": industrial_production_prev,
                "overtime_hours": overtime_hours,
                "overtime_hours_prev": overtime_hours_prev,
                "machinery_import": machinery_import_val,
                "machinery_import_prev": machinery_import_prev,
                "manufacturing_sales": manufacturing_sales,
                "manufacturing_sales_prev": manufacturing_sales_prev,
                "retail_sales": retail_sales,
                "retail_sales_prev": retail_sales_prev,
                "inventory": inventory,
                "inventory_prev": inventory_prev,
                "bank_lending_rate": bank_lending_rate,
                "bank_lending_rate_prev": bank_lending_rate_prev,
                "total_credit": total_credit,
                "total_credit_prev": total_credit_prev,
                "unit_labor_cost": unit_labor_cost,
                "unit_labor_cost_prev": unit_labor_cost_prev,
                "m1b": m1b,
                "m1b_prev": m1b_prev,
            }
        )

    if not history:
        raise ValueError("NDC zip dataset did not contain enough history to derive metrics")

    return history


def extract_latest_ndc_metrics(dataset: dict[str, list[dict]]) -> dict:
    return extract_ndc_history_metrics(dataset)[-1]


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
        dataset = parse_ndc_zip(self.fetch_bytes(url))
        return extract_latest_ndc_metrics(dataset)

    def fetch_ndc_zip_history_metrics(self, url: str) -> list[dict]:
        dataset = parse_ndc_zip(self.fetch_bytes(url))
        return extract_ndc_history_metrics(dataset)
