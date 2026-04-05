"""
台灣新指標採集器

資料來源：
- 央行公債殖利率：https://ws.cb.gov.tw/
- 央行利率：https://rate.cbc.gov.tw/
- 證交所市值/成交值：https://www.twse.com.tw/
"""

import csv
import io
from datetime import datetime

from market_phase_detector.collectors.base import HttpCollector

# 央行公債殖利率 CSV 下載連結
CB_GOV_BOND_YIELD_URL = "https://statdb.cbc.gov.tw/pxweb/Dialog/SBXMenuList.aspx"

# 證交所每月成交值與市值統計
TWSE_MONTHLY_STATS_URL = "https://www.twse.com.tw/rwd/zh/fund/T86?"


def parse_cb_bond_yield_csv(csv_text: str) -> dict:
    """解析央行公債殖利率 CSV
    
    預期欄位：date, 2Y_yield, 5Y_yield, 10Y_yield
    """
    reader = csv.DictReader(io.StringIO(csv_text))
    rows = []
    
    for row in reader:
        try:
            date_str = row.get("date", row.get("統計期", "")).strip()
            if not date_str:
                continue
            
            # 嘗試不同可能的日期格式
            for fmt in ("%Y-%m", "%Y/%m", "%Y%m"):
                try:
                    parsed = datetime.strptime(date_str, fmt)
                    date_key = parsed.strftime("%Y-%m")
                    break
                except ValueError:
                    continue
            else:
                continue
            
            # 解析殖利率
            yield_2y = float(row.get("2年", row.get("2年期", "")).replace("%", "").strip())
            yield_5y = float(row.get("5年", row.get("5年期", "")).replace("%", "").strip())
            yield_10y = float(row.get("10年", row.get("10年期", "")).replace("%", "").strip())
            
            rows.append({
                "date": date_key,
                "yield_2y": yield_2y,
                "yield_5y": yield_5y,
                "yield_10y": yield_10y,
                "spread_10y_2y": yield_10y - yield_2y,
            })
        except (ValueError, KeyError):
            continue
    
    if not rows:
        raise ValueError("CB bond yield CSV did not contain valid data")
    
    return {
        "rows": rows,
        "latest": rows[-1],
    }


def parse_twse_monthly_stats(csv_text: str) -> dict:
    """解析證交所每月市場統計
    
    預期欄位：date, total_cap_value, total_turnover
    """
    reader = csv.DictReader(io.StringIO(csv_text))
    rows = []
    
    for row in reader:
        try:
            date_str = row.get("date", row.get("年月", row.get("月份", ""))).strip()
            if not date_str:
                continue
            
            # 解析日期
            for fmt in ("%Y%m", "%Y-%m", "%Y/%m"):
                try:
                    parsed = datetime.strptime(date_str, fmt)
                    date_key = parsed.strftime("%Y-%m")
                    break
                except ValueError:
                    continue
            else:
                continue
            
            # 解析市值與成交值（單位通常是億元或千元，需視實際資料調整）
            cap_value = float(row.get("總市值", row.get("市值", "0").replace(",", "")))
            turnover = float(row.get("總成交值", row.get("成交值", "0").replace(",", "")))
            
            rows.append({
                "date": date_key,
                "total_cap_value": cap_value,
                "total_turnover": turnover,
                "turnover_ratio": turnover / cap_value if cap_value > 0 else 0.0,
            })
        except (ValueError, KeyError):
            continue
    
    if not rows:
        raise ValueError("TWSE monthly stats CSV did not contain valid data")
    
    return {
        "rows": rows,
        "latest": rows[-1],
    }


class TaiwanBondYieldCollector(HttpCollector):
    """採集台灣公債殖利率資料
    
    資料來源：央行統計資料庫
    """
    
    def fetch_latest(self, url: str) -> dict:
        """取得最新一筆殖利率資料"""
        csv_text = self.get_text(url)
        return parse_cb_bond_yield_csv(csv_text)
    
    def fetch_spread(self, url: str) -> float:
        """取得最新殖利率曲線利差（10Y - 2Y）"""
        data = self.fetch_latest(url)
        return data["latest"]["spread_10y_2y"]


class TaiwanMarketMetricsCollector(HttpCollector):
    """採集台灣證交所市場指標
    
    資料來源：證交所每月統計
    """
    
    def fetch_latest(self, url: str, params: dict | None = None) -> dict:
        """取得最新一筆市場統計資料"""
        csv_text = self.get_text(url, params=params)
        return parse_twse_monthly_stats(csv_text)
    
    def fetch_buffett_indicator(self, url: str) -> float | None:
        """計算巴菲特指標（總市值/名目GDP）
        
        注意：需要配合主計處 GDP 資料，這裡簡化為回傳市值
        """
        data = self.fetch_latest(url)
        return data["latest"]["total_cap_value"]
