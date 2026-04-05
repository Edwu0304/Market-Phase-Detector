"""
台灣新指標採集器

資料來源策略：
由於台灣許多指標（如 PMI、CCI、信用利差）沒有像美國 FRED 那樣統一的 API，
我們採取以下策略：

1. 優先使用現有國發會 NDC 資料（已在 tw_official.py 實作）
2. 使用 FRED 間接取得台灣相關指標（如台股估值、利差等）
3. 對於無法自動取得的指標，使用 Proxy 或簡化計算

參考資料來源：
- 國發會 NDC：景氣指標、失業率、出口
- FRED：台灣 PMI (從中經院)、台股本益比等
- 證交所 OpenAPI：市值、成交值（需手動更新或爬蟲）
"""

from market_phase_detector.collectors.base import HttpCollector

# FRED 上的台灣相關指標
FRED_TAIWAN_PMI = "TBSCOMP"  # 台灣 PMI（中經院，如果有的話）
FRED_TAIWAN_STOCK_PE = ""  # 台股本益比（FRED 上可能沒有，需其他來源）


class TaiwanProxyCollector(HttpCollector):
    """採集台灣代理指標
    
    用於補充國發會資料不足的部分
    """
    
    def fetch_taiwan_pmi_from_fred(self, series_id: str = "TBSCOMP") -> dict | None:
        """嘗試從 FRED 取得台灣 PMI 資料
        
        注意：FRED 可能沒有直接的台灣 PMI，需確認系列 ID
        """
        try:
            url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
            csv_text = self.get_text(url)
            # 解析邏輯同 us_fred.py
            return self._parse_fred_csv(csv_text)
        except Exception:
            return None
    
    def _parse_fred_csv(self, csv_text: str) -> dict:
        import csv
        import io
        
        reader = csv.DictReader(io.StringIO(csv_text))
        rows = []
        headers = reader.fieldnames or []
        
        if len(headers) < 2:
            raise ValueError("CSV must contain date and value columns")
        
        date_key = headers[0]
        value_key = headers[1]
        
        for row in reader:
            value = row[value_key]
            if value in {".", "", None}:
                continue
            rows.append({
                "date": row[date_key],
                "value": float(value),
            })
        
        if not rows:
            raise ValueError("No valid data rows found")
        
        return {
            "rows": rows,
            "latest": rows[-1],
        }
