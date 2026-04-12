"""Taiwan external data collectors."""

from __future__ import annotations

import calendar
import html
import io
import json
import re
from datetime import datetime

import pandas as pd
import requests

from market_phase_detector.collectors.base import HttpCollector


TPEX_BOND_BASE_URL = "https://www.tpex.org.tw/storage/bond_zone/tradeinfo/govbond"
MOL_CLAIMS_URL = "https://statdb.mol.gov.tw/html/year/year12/37040.csv"
NCU_CCI_URL = "https://rcted.ncu.edu.tw/"
TWSE_YIELDS_URL = "https://www.twse.com.tw/res/data/zh/home/yields.json"
TWSE_VALUES_URL = "https://www.twse.com.tw/res/data/zh/home/values.json"
CBC_DISCOUNT_RATE_URL = "https://www.cbc.gov.tw/tw/lp-640-1-1-20.html"
CBC_HOME_URL = "https://www.cbc.gov.tw/tw/mp-1.html"
CBC_M2_HISTORY_URL = "https://www.cbc.gov.tw/tw/lp-643-1.html"
CBC_M2_HISTORY_PAGE_TEMPLATE = "https://www.cbc.gov.tw/tw/lp-643-1-{page}-{page_size}.html"
CIER_PMI_CATEGORY_URL = "https://www.cier.edu.tw/eco_cat/pmi-ch/"
CIER_PMI_TREND_URL = "https://www.cier.edu.tw/pmi-trend/"

ZH_M2_TITLE = "\u8ca8\u5e63\u7e3d\u8a08\u6578M2\u5e74\u589e\u7387"
ZH_PMI_TITLE = "\u53f0\u7063\u88fd\u9020\u696d\u63a1\u8cfc\u7d93\u7406\u4eba\u6307\u6578"
ZH_PMI_SHORT = "\u53f0\u7063\u88fd\u9020\u696dPMI"
ZH_CCI = "\u6d88\u8cbb\u8005\u4fe1\u5fc3\u6307\u6578"
ZH_TWSE_TW = "\u81fa\u7063"
ZH_TWSE_TW_ALT = "\u53f0\u7063"


def _strip_tags(value: str) -> str:
    text = re.sub(r"<[^>]+>", "", value)
    return html.unescape(text).replace("\xa0", " ").strip()


def _safe_float(value: str | float | int | None) -> float | None:
    if value is None:
        return None
    if isinstance(value, (float, int)):
        return float(value)

    cleaned = str(value).replace(",", "").replace("%", "").strip()
    if not cleaned or cleaned in {"-", "--"}:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def _month_key(year: int, month: int) -> str:
    return f"{year:04d}-{month:02d}"


def _parse_year_month_label(value: str) -> str | None:
    match = re.search(r"(\d{4})[./-](\d{1,2})", value)
    if not match:
        return None
    return _month_key(int(match.group(1)), int(match.group(2)))


def parse_cbc_discount_rate(html_text: str) -> list[dict]:
    rows: list[dict] = []
    tr_pattern = re.compile(r"<tr[^>]*>(.*?)</tr>", re.DOTALL | re.IGNORECASE)
    td_pattern = re.compile(r"<td[^>]*>(.*?)</td>", re.DOTALL | re.IGNORECASE)

    for tr_match in tr_pattern.finditer(html_text):
        cells = td_pattern.findall(tr_match.group(1))
        if len(cells) < 4:
            continue

        month_key = _parse_year_month_label(_strip_tags(cells[0]))
        discount_rate = _safe_float(_strip_tags(cells[1]))
        if month_key is None or discount_rate is None:
            continue

        rows.append(
            {
                "date": month_key,
                "discount_rate": discount_rate,
                "accommodation_rate": _safe_float(_strip_tags(cells[2])),
                "short_term_rate": _safe_float(_strip_tags(cells[3])),
            }
        )

    return rows


def parse_ncu_cci_from_news(html_text: str) -> dict | None:
    normalized = _strip_tags(html_text)
    match = re.search(
        rf"(\d{{3,4}})\u5e74\s*(\d{{1,2}})\u6708.*?{ZH_CCI}.*?(?:\u7e3d\u6307\u6578)?.*?([\d.]+)",
        normalized,
    )
    if not match:
        return None

    year = int(match.group(1))
    if year < 1911:
        year += 1911
    month = int(match.group(2))
    value = _safe_float(match.group(3))
    if value is None:
        return None

    return {"date": _month_key(year, month), "cci_total": value}


def parse_dgbas_cpi(html_text: str) -> list[dict]:
    normalized = _strip_tags(html_text)
    pattern = re.compile(
        r"(\d{3,4})\u5e74\s*(\d{1,2})\u6708.*?CPI.*?([\d.]+).*?(?:\u5e74\u589e\u7387|\u8f03\u4e0a\u5e74\u540c\u6708\u589e\u7387).*?([-\d.]+)"
    )

    rows: list[dict] = []
    for match in pattern.finditer(normalized):
        year = int(match.group(1))
        if year < 1911:
            year += 1911
        month = int(match.group(2))
        cpi = _safe_float(match.group(3))
        cpi_yoy = _safe_float(match.group(4))
        if cpi is None or cpi_yoy is None:
            continue
        rows.append({"date": _month_key(year, month), "cpi": cpi, "cpi_yoy": cpi_yoy})

    return rows


def parse_cbc_m2_from_homepage(html_text: str) -> dict | None:
    pattern = re.compile(
        rf"<a[^>]*title=[\"']{re.escape(ZH_M2_TITLE)}[\"'][^>]*>.*?"
        r"<span[^>]*class=[\"']date[\"'][^>]*>([^<]+)</span>.*?"
        r"<span[^>]*class=[\"']info[\"'][^>]*>\s*<em>([^<]+)</em>",
        re.DOTALL | re.IGNORECASE,
    )
    match = pattern.search(html_text)
    if not match:
        return None

    source_date = _strip_tags(match.group(1))
    month_key = _parse_year_month_label(source_date)
    m2_yoy = _safe_float(_strip_tags(match.group(2)))
    if month_key is None or m2_yoy is None:
        return None

    return {"date": month_key, "m2_yoy": m2_yoy, "source_date": source_date}


def parse_cbc_m2_history_page(html_text: str) -> list[dict]:
    pattern = re.compile(
        r"<tr>\s*<td[^>]*><span>([^<]+)</span></td>\s*<td[^>]*><span>([^<]+)</span></td>\s*</tr>",
        re.DOTALL | re.IGNORECASE,
    )

    rows: list[dict] = []
    for match in pattern.finditer(html_text):
        source_date = _strip_tags(match.group(1))
        month_key = _parse_year_month_label(source_date)
        m2_yoy = _safe_float(_strip_tags(match.group(2)))
        if month_key is None or m2_yoy is None:
            continue
        rows.append({"date": month_key, "m2_yoy": m2_yoy, "source_date": source_date})

    return rows


def parse_cier_pmi_article(html_text: str, source_url: str) -> dict | None:
    normalized = _strip_tags(html_text)
    month_match = re.search(rf"(\d{{4}})\u5e74\s*(\d{{1,2}})\u6708{ZH_PMI_TITLE}", normalized)
    if not month_match:
        return None

    window = normalized[month_match.start() : month_match.start() + 3000]
    value_match = re.search(rf"{ZH_PMI_SHORT}.*?(?:\u81f3|\u70ba)\s*([\d.]+)%", window)
    if not value_match:
        value_match = re.search(r"\bPMI\b.*?(?:\u81f3|\u70ba)\s*([\d.]+)%", window)
    if not value_match:
        return None

    value = _safe_float(value_match.group(1))
    if value is None:
        return None

    year = int(month_match.group(1))
    month = int(month_match.group(2))
    return {"date": _month_key(year, month), "pmi": value, "source_url": source_url}


def parse_cier_pmi_history_page(html_text: str, source_url: str) -> list[dict]:
    attr_match = re.search(r"data-data=(['\"])(.*?)\1", html_text, re.DOTALL | re.IGNORECASE)
    if not attr_match:
        return []

    try:
        table = json.loads(html.unescape(attr_match.group(2)))
    except json.JSONDecodeError:
        return []

    rows: list[dict] = []
    for row in table[1:]:
        if not isinstance(row, list) or len(row) < 2:
            continue
        month_key = _parse_year_month_label(str(row[0]))
        pmi_value = _safe_float(row[1])
        if month_key is None or pmi_value is None:
            continue
        rows.append({"date": month_key, "pmi": pmi_value, "source_url": source_url})

    return rows


def fetch_tpex_bond_data(collector: HttpCollector | None, year: int, month: int) -> dict | None:
    last_day = calendar.monthrange(year, month)[1]
    timeout = collector.timeout if collector else 30

    for day in range(min(28, last_day), 0, -1):
        try:
            dt = datetime(year, month, day)
            if dt.weekday() >= 5:
                continue

            date_str = dt.strftime("%Y%m%d")
            month_key = f"{year}{month:02d}"

            gov_url = f"{TPEX_BOND_BASE_URL}/{year}/{month_key}/Curve.{date_str}-C.xls"
            gov_response = requests.get(gov_url, timeout=timeout)
            if gov_response.status_code != 200 or len(gov_response.content) < 1000:
                continue

            gov_df = pd.read_excel(io.BytesIO(gov_response.content), engine="xlrd")
            gov_yields: dict[str, float] = {}
            for _, row in gov_df.iterrows():
                tenor = str(row.iloc[1]) if len(row) > 1 else ""
                rate = _safe_float(row.iloc[2] if len(row) > 2 else None)
                if rate is None:
                    continue
                if "2" in tenor and "Year" in tenor:
                    gov_yields["2y"] = rate
                elif "10" in tenor and "Year" in tenor:
                    gov_yields["10y"] = rate

            if "10y" not in gov_yields:
                continue

            corp_url = f"{TPEX_BOND_BASE_URL}/{year}/{month_key}/COCurve.{date_str}-C.xls"
            corp_response = requests.get(corp_url, timeout=timeout)
            corporate_bbb_10y = None
            if corp_response.status_code == 200 and len(corp_response.content) >= 1000:
                corp_df = pd.read_excel(io.BytesIO(corp_response.content), engine="xlrd", header=None)
                if len(corp_df) > 6 and len(corp_df.iloc[6]) > 13:
                    raw_value = _safe_float(corp_df.iloc[6].iloc[13])
                    if raw_value is not None:
                        corporate_bbb_10y = raw_value * 100

            result = {
                "date": dt.strftime("%Y-%m-%d"),
                "gov_yield_10y": gov_yields["10y"],
                "gov_yield_2y": gov_yields.get("2y"),
                "spread_10y_2y": None if gov_yields.get("2y") is None else gov_yields["10y"] - gov_yields["2y"],
            }
            if corporate_bbb_10y is not None:
                result["corporate_bbb_10y"] = corporate_bbb_10y
                result["credit_spread_bbb"] = round(corporate_bbb_10y - gov_yields["10y"], 4)
            return result
        except Exception:
            continue

    return None


def fetch_tpex_bond_history(collector: HttpCollector | None, months: int = 24) -> list[dict]:
    now = datetime.now()
    rows: list[dict] = []
    for offset in range(months):
        year = now.year
        month = now.month - offset
        while month <= 0:
            month += 12
            year -= 1
        item = fetch_tpex_bond_data(collector, year, month)
        if item:
            rows.append(item)
    return sorted(rows, key=lambda row: row["date"])


def fetch_mol_claims_annual(collector: HttpCollector | None) -> list[dict]:
    timeout = collector.timeout if collector else 30
    response = requests.get(MOL_CLAIMS_URL, timeout=timeout, verify=False)
    response.raise_for_status()
    text = response.content.decode("big5", errors="replace")

    rows: list[dict] = []
    for line in text.strip().splitlines()[3:]:
        parts = [part.strip() for part in line.split(",")]
        if len(parts) < 7:
            continue

        year_match = re.search(r"(\d+)", parts[0])
        if not year_match:
            continue
        year = int(year_match.group(1))
        if year < 1911:
            year += 1911

        claims = _safe_float(parts[6])
        rows.append({"date": str(year), "initial_claims": int(claims) if claims is not None else None, "year": year})

    return rows


def fetch_ncu_cci(collector: HttpCollector | None) -> dict | None:
    timeout = collector.timeout if collector else 30
    html_text = requests.get(NCU_CCI_URL, timeout=timeout).text
    return parse_ncu_cci_from_news(html_text)


def fetch_twse_market_pe(collector: HttpCollector | None) -> dict | None:
    timeout = collector.timeout if collector else 30
    data = requests.get(TWSE_YIELDS_URL, timeout=timeout).json()
    chart1 = data.get("chart1", {})
    pe_data = chart1.get("table2", {}).get("data", [])

    for item in pe_data:
        if len(item) < 2:
            continue
        label = str(item[0])
        if label in {ZH_TWSE_TW, ZH_TWSE_TW_ALT}:
            pe_ratio = _safe_float(item[1])
            if pe_ratio is not None:
                return {"date": chart1.get("table1", {}).get("date", ""), "pe_ratio": pe_ratio}

    return None


def fetch_latest_twse_margin(collector: HttpCollector | None) -> dict | None:
    timeout = collector.timeout if collector else 30
    data = requests.get(TWSE_VALUES_URL, timeout=timeout).json()
    margin_rows = data.get("chart", {}).get("margin", [])
    if not margin_rows:
        return None

    last_row = margin_rows[-1]
    if len(last_row) < 4:
        return None

    return {
        "date": str(last_row[0]),
        "margin_shares": int(last_row[1]),
        "margin_amount": int(last_row[2]),
        "short_shares": int(last_row[3]),
    }


def fetch_cbc_discount_rate(collector: HttpCollector | None) -> list[dict]:
    timeout = collector.timeout if collector else 30
    html_text = requests.get(CBC_DISCOUNT_RATE_URL, timeout=timeout).text
    return parse_cbc_discount_rate(html_text)


def fetch_latest_cbc_m2(collector: HttpCollector | None) -> dict | None:
    timeout = collector.timeout if collector else 30
    html_text = requests.get(CBC_HOME_URL, timeout=timeout).text
    return parse_cbc_m2_from_homepage(html_text)


def fetch_cbc_m2_history(collector: HttpCollector | None, months: int = 24) -> list[dict]:
    timeout = collector.timeout if collector else 30
    page_size = max(40, months)
    html_text = requests.get(CBC_M2_HISTORY_PAGE_TEMPLATE.format(page=1, page_size=page_size), timeout=timeout).text
    rows = sorted(parse_cbc_m2_history_page(html_text), key=lambda row: row["date"])

    if len(rows) >= months:
        return rows[-months:]

    fallback_html = requests.get(CBC_M2_HISTORY_URL, timeout=timeout).text
    fallback_rows = sorted(parse_cbc_m2_history_page(fallback_html), key=lambda row: row["date"])
    return fallback_rows[-months:]


def fetch_latest_cier_pmi(collector: HttpCollector | None) -> dict | None:
    timeout = collector.timeout if collector else 30
    html_text = requests.get(CIER_PMI_CATEGORY_URL, timeout=timeout).text
    return parse_cier_pmi_article(html_text, CIER_PMI_CATEGORY_URL)


def fetch_cier_pmi_history(collector: HttpCollector | None, months: int = 24) -> list[dict]:
    timeout = collector.timeout if collector else 30
    html_text = requests.get(CIER_PMI_TREND_URL, timeout=timeout).text
    rows = parse_cier_pmi_history_page(html_text, CIER_PMI_TREND_URL)
    return rows[-months:]


class TaiwanExternalCollector(HttpCollector):
    def fetch_tpex_bond_data(self, year: int, month: int) -> dict | None:
        return fetch_tpex_bond_data(self, year, month)

    def fetch_tpex_bond_history(self, months: int = 24) -> list[dict]:
        return fetch_tpex_bond_history(self, months)

    def fetch_mol_claims_annual(self) -> list[dict]:
        return fetch_mol_claims_annual(self)

    def fetch_ncu_cci(self) -> dict | None:
        return fetch_ncu_cci(self)

    def fetch_twse_market_pe(self) -> dict | None:
        return fetch_twse_market_pe(self)

    def fetch_latest_twse_margin(self) -> dict | None:
        return fetch_latest_twse_margin(self)

    def fetch_cbc_discount_rate(self) -> list[dict]:
        return fetch_cbc_discount_rate(self)

    def fetch_latest_cbc_m2(self) -> dict | None:
        return fetch_latest_cbc_m2(self)

    def fetch_cbc_m2_history(self, months: int = 24) -> list[dict]:
        return fetch_cbc_m2_history(self, months)

    def fetch_latest_cier_pmi(self) -> dict | None:
        return fetch_latest_cier_pmi(self)

    def fetch_cier_pmi_history(self, months: int = 24) -> list[dict]:
        return fetch_cier_pmi_history(self, months)

    def fetch_cbc_credit_spread_proxy(self) -> dict | None:
        now = datetime.now()
        return self.fetch_tpex_bond_data(now.year, now.month)
