"""
台灣外部總經指標爬蟲

資料來源：
1. 櫃買中心公債/公司債殖利率：https://www.tpex.org.tw/
2. 勞動部失業給付（年度）：https://statdb.mol.gov.tw/html/year/year12/37040.csv
3. 中央大學 CCI：https://rcted.ncu.edu.tw/
4. 證交所本益比/融資：https://www.twse.com.tw/res/data/zh/home/
5. 央行重貼現率：https://www.cbc.gov.tw/tw/lp-640-1-1-20.html
"""

import io
import re
import calendar
from datetime import datetime

import pandas as pd
import requests

from market_phase_detector.collectors.base import HttpCollector


# =============================================================================
# Parsers
# =============================================================================

def parse_cbc_discount_rate(html: str) -> list[dict]:
    """解析央行重貼現率表格

    Returns:
        [{"date": "2026-03", "discount_rate": 2.0, "accommodation_rate": 2.375, "short_term_rate": 4.25}, ...]
    """
    rows = []
    tr_pattern = re.compile(r'<tr[^>]*>(.*?)</tr>', re.DOTALL)
    td_pattern = re.compile(r'<td[^>]*>(.*?)</td>', re.DOTALL)

    for tr_match in tr_pattern.finditer(html):
        td_matches = td_pattern.findall(tr_match.group(1))
        if len(td_matches) >= 4:
            date_str = re.sub(r'<[^>]+>', '', td_matches[0]).strip()
            discount = re.sub(r'<[^>]+>', '', td_matches[1]).strip()
            accommodation = re.sub(r'<[^>]+>', '', td_matches[2]).strip()
            short_term = re.sub(r'<[^>]+>', '', td_matches[3]).strip()

            try:
                if '/' in date_str:
                    parts = date_str.split('/')
                    year = int(parts[0]) + 1911 if len(parts[0]) <= 3 else int(parts[0])
                    month = int(parts[1])
                    date_key = f"{year}-{month:02d}"
                else:
                    continue

                rows.append({
                    "date": date_key,
                    "discount_rate": float(discount.replace(',', '')) if discount else None,
                    "accommodation_rate": float(accommodation.replace(',', '')) if accommodation else None,
                    "short_term_rate": float(short_term.replace(',', '')) if short_term else None,
                })
            except (ValueError, IndexError):
                continue

    return rows


def parse_ncu_cci_from_news(html: str) -> dict | None:
    """從中央大學新聞稿解析 CCI

    Returns:
        {"date": "2026-03", "cci_total": 62.3} 或 None
    """
    # 尋找 pattern: (\d{3})年(\d{1,2})月...總指數為\s*([\d.]+)\s*點
    cci_match = re.search(r'(\d{3})\s*年\s*(\d{1,2})\s*月.*?總指數為\s*([\d.]+)\s*點', html)
    if cci_match:
        year = int(cci_match.group(1)) + 1911
        month = int(cci_match.group(2))
        return {
            "date": f"{year}-{month:02d}",
            "cci_total": float(cci_match.group(3)),
        }
    return None


def parse_dgbas_cpi(html: str) -> list[dict]:
    """解析主計總處 CPI 資料

    Returns:
        [{"date": "2026-02", "cpi": 110.91, "cpi_yoy": 1.75}, ...]
    """
    rows = []
    pattern = re.compile(r'(\d+)年(\d+)月.*?消費者物價指數.*?([\d.]+).*?(?:年增|較上年|同比).*?([\d.]+)', re.DOTALL)

    for match in pattern.finditer(html):
        year = int(match.group(1)) + 1911
        month = int(match.group(2))
        cpi = float(match.group(3))
        cpi_yoy = float(match.group(4))

        rows.append({
            "date": f"{year}-{month:02d}",
            "cpi": cpi,
            "cpi_yoy": cpi_yoy,
        })

    return rows


# =============================================================================
# Standalone fetcher functions
# =============================================================================

def fetch_tpex_bond_data(collector: HttpCollector | None, year: int, month: int) -> dict | None:
    """從櫃買中心取得公債殖利率 + 公司債殖利率，計算信用利差

    URL patterns:
      - Gov bond:    https://www.tpex.org.tw/storage/bond_zone/tradeinfo/govbond/{year}/{month}/Curve.{date}-C.xls
      - Corp bond:   https://www.tpex.org.tw/storage/bond_zone/tradeinfo/govbond/{year}/{month}/COCurve.{date}-C.xls

    Returns:
        {"date": "2026-03-27", "gov_yield_10y": 1.571, "gov_yield_2y": 1.193,
         "spread_10y_2y": 0.378, "corporate_bbb_10y": 2.1506, "credit_spread_bbb": 0.5796}
        或 None
    """
    last_day = calendar.monthrange(year, month)[1]

    for day in range(min(28, last_day), 0, -1):
        try:
            dt = datetime(year, month, day)
            if dt.weekday() >= 5:  # Skip weekends
                continue

            date_str = dt.strftime("%Y%m%d")
            year_str = str(year)
            month_str = f"{year}{month:02d}"

            # Fetch gov bond XLS
            gov_url = f"https://www.tpex.org.tw/storage/bond_zone/tradeinfo/govbond/{year_str}/{month_str}/Curve.{date_str}-C.xls"
            gov_bytes = requests.get(gov_url, timeout=30).content
            if len(gov_bytes) < 1000:
                continue

            gov_df = pd.read_excel(io.BytesIO(gov_bytes), engine='xlrd')

            # Parse gov yields: row[1] = tenor (e.g. "10年(Year)"), row[2] = yield value
            gov_yields = {}
            for _, row in gov_df.iterrows():
                tenor = str(row.iloc[1]) if len(row) > 1 else ""
                rate_val = row.iloc[2] if len(row) > 2 else None
                if rate_val is not None and rate_val != '':
                    try:
                        rate = float(rate_val)
                    except (ValueError, TypeError):
                        continue
                    if "2年" in tenor:
                        gov_yields["2y"] = rate
                    elif "10年" in tenor:
                        gov_yields["10y"] = rate

            # Fetch corporate bond XLS
            corp_url = f"https://www.tpex.org.tw/storage/bond_zone/tradeinfo/govbond/{year_str}/{month_str}/COCurve.{date_str}-C.xls"
            corp_bytes = requests.get(corp_url, timeout=30).content
            if len(corp_bytes) < 1000:
                continue

            # COCurve: row 6 = twBBB, column 13 = 10Y yield (decimal, multiply by 100 for %)
            corp_df = pd.read_excel(io.BytesIO(corp_bytes), engine='xlrd', header=None)
            corporate_bbb_10y = None
            if len(corp_df) > 6:
                bbb_row = corp_df.iloc[6]
                if len(bbb_row) > 13:
                    val = bbb_row.iloc[13]
                    if val is not None and val != '':
                        try:
                            corporate_bbb_10y = float(val) * 100  # Convert decimal to percentage
                        except (ValueError, TypeError):
                            pass

            # Build result
            if gov_yields.get("10y") is not None:
                result = {
                    "date": dt.strftime("%Y-%m-%d"),
                    "gov_yield_10y": gov_yields["10y"],
                    "gov_yield_2y": gov_yields.get("2y"),
                    "spread_10y_2y": gov_yields["10y"] - gov_yields.get("2y", 0),
                }
                if corporate_bbb_10y is not None:
                    result["corporate_bbb_10y"] = corporate_bbb_10y
                    result["credit_spread_bbb"] = round(corporate_bbb_10y - gov_yields["10y"], 4)
                return result

        except Exception:
            continue

    return None


def fetch_tpex_bond_history(collector: HttpCollector | None, months: int = 24) -> list[dict]:
    """取得櫃買中心公債/公司債殖利率歷史（過去 N 個月）"""
    now = datetime.now()
    results = []

    for i in range(months):
        year = now.year
        month = now.month - i
        while month <= 0:
            month += 12
            year -= 1
        try:
            data = fetch_tpex_bond_data(collector, year, month)
            if data:
                results.append(data)
        except Exception:
            continue

    return results


def fetch_mol_claims_annual(collector: HttpCollector | None) -> list[dict]:
    """取得勞動部失業給付初次認定件數（年度資料）

    URL: https://statdb.mol.gov.tw/html/year/year12/37040.csv
    Encoding: big5
    Skip first 3 header lines
    parts[0] = year (e.g. "92年"), parts[6] = 初次認定核付件數

    Returns:
        [{"date": "2023", "initial_claims": 85534, "year": 2023}, ...]
    """
    url = "https://statdb.mol.gov.tw/html/year/year12/37040.csv"
    try:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        raw_bytes = requests.get(url, timeout=8, verify=False).content
        text = raw_bytes.decode('big5', errors='replace')
    except Exception:
        try:
            raw_bytes = requests.get(url, timeout=8).content
            text = raw_bytes.decode('big5', errors='replace')
        except Exception:
            return []

    lines = text.strip().split('\n')
    # Skip first 3 header lines
    data_lines = lines[3:] if len(lines) > 3 else []

    results = []
    for line in data_lines:
        parts = [p.strip() for p in line.split(',')]
        if len(parts) < 7:
            continue

        # Parse year: e.g. "92年" -> extract number
        year_str = parts[0].replace('年', '').strip()
        try:
            year = int(year_str)
            # Convert ROC year to AD
            if year < 2000:
                year += 1911
        except ValueError:
            continue

        # Parse initial claims (column 6, 0-indexed)
        claims_str = parts[6].replace(',', '').strip() if len(parts) > 6 else ''
        try:
            claims = int(claims_str) if claims_str and claims_str not in ('-', '') else None
        except ValueError:
            claims = None

        results.append({
            "date": f"{year}",
            "initial_claims": claims,
            "year": year,
        })

    return results


def fetch_ncu_cci(collector: HttpCollector | None) -> dict | None:
    """取得中央大學 CCI 最新資料

    URL: https://rcted.ncu.edu.tw/
    Parse pattern: (\\d{3})\\s*年\\s*(\\d{1,2})\\s*月.*?總指數為\\s*([\\d.]+)\\s*點

    Returns:
        {"date": "2026-03", "cci_total": 62.3} 或 None
    """
    url = "https://rcted.ncu.edu.tw/"
    try:
        html = requests.get(url, timeout=30).text
        return parse_ncu_cci_from_news(html)
    except Exception:
        return None


def fetch_twse_market_pe(collector: HttpCollector | None) -> dict | None:
    """取得證交所大盤本益比（最新）

    URL: https://www.twse.com.tw/res/data/zh/home/yields.json
    Parse: data["chart1"]["table2"]["data"] → find item where "台灣" in item[0]

    Returns:
        {"date": "2025/12/31", "pe_ratio": 23.22} 或 None
    """
    url = "https://www.twse.com.tw/res/data/zh/home/yields.json"
    try:
        data = requests.get(url, timeout=30).json()
        chart1 = data.get("chart1", {})
        pe_table = chart1.get("table2", {})
        pe_data = pe_table.get("data", [])

        for item in pe_data:
            if len(item) >= 2 and "台灣" in str(item[0]):
                date_str = chart1.get("table1", {}).get("date", "")
                return {
                    "date": date_str,
                    "pe_ratio": float(item[1]),
                }
    except Exception:
        pass

    return None


def fetch_latest_twse_margin(collector: HttpCollector | None) -> dict | None:
    """取得證交所最新融資融券餘額

    URL: https://www.twse.com.tw/res/data/zh/home/values.json
    Parse: data["chart"]["margin"] → last row = [date, margin_shares, margin_amount, short_shares]

    Returns:
        {"date": "4/2", "margin_shares": 8081563, "margin_amount": 385200709, "short_shares": 170164}
        或 None
    """
    url = "https://www.twse.com.tw/res/data/zh/home/values.json"
    try:
        data = requests.get(url, timeout=30).json()
        margin_data = data.get("chart", {}).get("margin", [])
        if margin_data and len(margin_data) > 0:
            last_row = margin_data[-1]
            if len(last_row) >= 4:
                return {
                    "date": str(last_row[0]),
                    "margin_shares": int(last_row[1]),
                    "margin_amount": int(last_row[2]),
                    "short_shares": int(last_row[3]),
                }
    except Exception:
        pass

    return None


def fetch_cbc_discount_rate(collector: HttpCollector | None) -> list[dict]:
    """取得央行重貼現率歷史資料

    URL: https://www.cbc.gov.tw/tw/lp-640-1-1-20.html

    Returns:
        [{"date": "2026-03", "discount_rate": 2.0, ...}, ...]
    """
    url = "https://www.cbc.gov.tw/tw/lp-640-1-1-20.html"
    try:
        html = requests.get(url, timeout=30).text
        return parse_cbc_discount_rate(html)
    except Exception:
        return []


# =============================================================================
# TaiwanExternalCollector class
# =============================================================================

class TaiwanExternalCollector(HttpCollector):
    """採集台灣外部總經指標（非 NDC 來源）"""

    # ------------------------------------------------------------------
    # TPEx Bond Data
    # ------------------------------------------------------------------

    def fetch_tpex_bond_data(self, year: int, month: int) -> dict | None:
        """取得櫃買中心公債+公司債殖利率（指定年月）

        Returns:
            {"date": "2026-03-27", "gov_yield_10y": 1.571, "gov_yield_2y": 1.193,
             "spread_10y_2y": 0.378, "corporate_bbb_10y": 2.1506, "credit_spread_bbb": 0.5796}
        """
        return fetch_tpex_bond_data(self, year, month)

    def fetch_tpex_bond_history(self, months: int = 24) -> list[dict]:
        """取得櫃買中心公債/公司債殖利率歷史（過去 N 個月）"""
        return fetch_tpex_bond_history(self, months)

    # ------------------------------------------------------------------
    # MOL Unemployment Claims
    # ------------------------------------------------------------------

    def fetch_mol_claims_annual(self) -> list[dict]:
        """取得勞動部失業給付初次認定件數（年度）"""
        return fetch_mol_claims_annual(self)

    # ------------------------------------------------------------------
    # NCU CCI
    # ------------------------------------------------------------------

    def fetch_ncu_cci(self) -> dict | None:
        """取得中央大學 CCI 最新資料"""
        return fetch_ncu_cci(self)

    # ------------------------------------------------------------------
    # TWSE PE Ratio
    # ------------------------------------------------------------------

    def fetch_twse_market_pe(self) -> dict | None:
        """取得證交所大盤本益比（最新）"""
        return fetch_twse_market_pe(self)

    # ------------------------------------------------------------------
    # TWSE Margin
    # ------------------------------------------------------------------

    def fetch_latest_twse_margin(self) -> dict | None:
        """取得證交所最新融資融券餘額"""
        return fetch_latest_twse_margin(self)

    # ------------------------------------------------------------------
    # CBC Discount Rate
    # ------------------------------------------------------------------

    def fetch_cbc_discount_rate(self) -> list[dict]:
        """取得央行重貼現率歷史資料"""
        return fetch_cbc_discount_rate(self)

    # ------------------------------------------------------------------
    # CBC Credit Spread Proxy (alias to TPEx bond data for current month)
    # ------------------------------------------------------------------

    def fetch_cbc_credit_spread_proxy(self) -> dict | None:
        """取得信用利差（代理，使用櫃買中心當月資料）

        等價於 fetch_tpex_bond_data(current_year, current_month)。
        """
        now = datetime.now()
        return self.fetch_tpex_bond_data(now.year, now.month)
