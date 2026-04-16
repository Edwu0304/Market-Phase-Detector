import datetime as dt
import requests

from market_phase_detector.collectors.base import HttpCollector


YAHOO_SPARK_URL = "https://query1.finance.yahoo.com/v7/finance/spark"

SECTOR_ETFS = {
    "Technology": "XLK",
    "Financials": "XLF",
    "Industrials": "XLI",
    "Consumer Discretionary": "XLY",
    "Consumer Staples": "XLP",
    "Health Care": "XLV",
    "Energy": "XLE",
    "Materials": "XLB",
    "Utilities": "XLU",
    "Real Estate": "XLRE",
    "Communication Services": "XLC",
}

INTERMARKET_ETFS = {
    "Bonds": "TLT",
    "Equities": "SPY",
    "Commodities": "DBC",
}


def parse_yahoo_spark_payload(payload: dict) -> dict[str, list[dict]]:
    result = payload.get("spark", {}).get("result", [])
    if not result:
        raise ValueError("Yahoo spark payload missing result")

    output: dict[str, list[dict]] = {}
    for entry in result:
        symbol = entry.get("symbol")
        response = (entry.get("response") or [{}])[0]
        timestamps = response.get("timestamp", [])
        quote = (response.get("indicators", {}).get("quote") or [{}])[0]
        closes = quote.get("close", [])

        rows = []
        for ts, close in zip(timestamps, closes):
            if close in {None, 0}:
                continue
            date_str = dt.datetime.fromtimestamp(ts, dt.UTC).strftime("%Y-%m-%d")
            rows.append({"date": date_str, "close": float(close)})
        if symbol and rows:
            output[symbol] = rows

    if not output:
        raise ValueError("Yahoo spark payload missing close rows")
    return output


def _month_key(date_str: str) -> str:
    return date_str[:7]


def _three_month_return(rows: list[dict], index: int) -> float | None:
    if index < 3:
        return None
    start = rows[index - 3]["close"]
    end = rows[index]["close"]
    if start == 0:
        return None
    return round((end / start - 1) * 100, 2)


def compute_sector_rotation_snapshot(series_by_sector: dict[str, list[dict]]) -> dict | None:
    ranking: list[tuple[str, float]] = []
    for sector, rows in series_by_sector.items():
        score = _three_month_return(rows, len(rows) - 1)
        if score is None:
            continue
        ranking.append((sector, score))
    if not ranking:
        return None
    leader, leader_return = max(ranking, key=lambda item: item[1])
    laggard, laggard_return = min(ranking, key=lambda item: item[1])
    sector_advance_count = sum(1 for _, score in ranking if score > 0)
    sector_decline_count = sum(1 for _, score in ranking if score < 0)
    sector_breadth_ratio = None
    if sector_decline_count:
        sector_breadth_ratio = round(sector_advance_count / sector_decline_count, 4)
    return {
        "sector_leader": leader,
        "sector_leader_return": leader_return,
        "sector_laggard": laggard,
        "sector_laggard_return": laggard_return,
        "sector_advance_count": sector_advance_count,
        "sector_decline_count": sector_decline_count,
        "sector_breadth_ratio": sector_breadth_ratio,
    }


def compute_sector_rotation_history(series_by_sector: dict[str, list[dict]], months: int = 24) -> list[dict]:
    month_index_map: dict[str, list[tuple[str, float]]] = {}
    for sector, rows in series_by_sector.items():
        for idx in range(len(rows)):
            score = _three_month_return(rows, idx)
            if score is None:
                continue
            month_key = _month_key(rows[idx]["date"])
            month_index_map.setdefault(month_key, []).append((sector, score))

    history = []
    for month_key in sorted(month_index_map)[-months:]:
        ranking = month_index_map[month_key]
        if not ranking:
            continue
        leader, leader_return = max(ranking, key=lambda item: item[1])
        laggard, laggard_return = min(ranking, key=lambda item: item[1])
        sector_advance_count = sum(1 for _, score in ranking if score > 0)
        sector_decline_count = sum(1 for _, score in ranking if score < 0)
        sector_breadth_ratio = None
        if sector_decline_count:
            sector_breadth_ratio = round(sector_advance_count / sector_decline_count, 4)
        history.append(
            {
                "date": month_key,
                "sector_leader": leader,
                "sector_leader_return": leader_return,
                "sector_laggard": laggard,
                "sector_laggard_return": laggard_return,
                "sector_advance_count": sector_advance_count,
                "sector_decline_count": sector_decline_count,
                "sector_breadth_ratio": sector_breadth_ratio,
            }
        )
    return history


def compute_intermarket_snapshot(series_by_asset: dict[str, list[dict]]) -> dict | None:
    ranking: list[tuple[str, float]] = []
    for asset, rows in series_by_asset.items():
        score = _three_month_return(rows, len(rows) - 1)
        if score is None:
            continue
        ranking.append((asset, score))
    if len(ranking) < 3:
        return None
    ranking.sort(key=lambda item: item[1], reverse=True)
    return {
        "bond_return_3m": next(score for asset, score in ranking if asset == "Bonds"),
        "equity_return_3m": next(score for asset, score in ranking if asset == "Equities"),
        "commodity_return_3m": next(score for asset, score in ranking if asset == "Commodities"),
        "intermarket_order": " > ".join(asset for asset, _ in ranking),
    }


def compute_intermarket_history(series_by_asset: dict[str, list[dict]], months: int = 24) -> list[dict]:
    month_index_map: dict[str, list[tuple[str, float]]] = {}
    for asset, rows in series_by_asset.items():
        for idx in range(len(rows)):
            score = _three_month_return(rows, idx)
            if score is None:
                continue
            month_key = _month_key(rows[idx]["date"])
            month_index_map.setdefault(month_key, []).append((asset, score))

    history = []
    for month_key in sorted(month_index_map)[-months:]:
        ranking = month_index_map[month_key]
        if len(ranking) < 3:
            continue
        ranking.sort(key=lambda item: item[1], reverse=True)
        history.append(
            {
                "date": month_key,
                "bond_return_3m": next(score for asset, score in ranking if asset == "Bonds"),
                "equity_return_3m": next(score for asset, score in ranking if asset == "Equities"),
                "commodity_return_3m": next(score for asset, score in ranking if asset == "Commodities"),
                "intermarket_order": " > ".join(asset for asset, _ in ranking),
            }
        )
    return history


class USMarketCollector(HttpCollector):
    def fetch_sector_histories(self, range_: str = "5y", interval: str = "1mo") -> dict[str, list[dict]]:
        response = requests.get(
            YAHOO_SPARK_URL,
            params={"symbols": ",".join(SECTOR_ETFS.values()), "range": range_, "interval": interval},
            headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json,text/plain,*/*"},
            timeout=self.timeout,
        )
        response.raise_for_status()
        payload = response.json()
        raw = parse_yahoo_spark_payload(payload)
        return {
            sector: raw[symbol]
            for sector, symbol in SECTOR_ETFS.items()
            if symbol in raw
        }

    def fetch_sector_rotation_snapshot(self) -> dict | None:
        series_by_sector = self.fetch_sector_histories()
        return compute_sector_rotation_snapshot(series_by_sector)

    def fetch_sector_rotation_history(self, months: int = 24) -> list[dict]:
        series_by_sector = self.fetch_sector_histories()
        return compute_sector_rotation_history(series_by_sector, months=months)

    def fetch_intermarket_histories(self, range_: str = "5y", interval: str = "1mo") -> dict[str, list[dict]]:
        response = requests.get(
            YAHOO_SPARK_URL,
            params={"symbols": ",".join(INTERMARKET_ETFS.values()), "range": range_, "interval": interval},
            headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json,text/plain,*/*"},
            timeout=self.timeout,
        )
        response.raise_for_status()
        payload = response.json()
        raw = parse_yahoo_spark_payload(payload)
        return {
            asset: raw[symbol]
            for asset, symbol in INTERMARKET_ETFS.items()
            if symbol in raw
        }

    def fetch_intermarket_snapshot(self) -> dict | None:
        series_by_asset = self.fetch_intermarket_histories()
        return compute_intermarket_snapshot(series_by_asset)

    def fetch_intermarket_history(self, months: int = 24) -> list[dict]:
        series_by_asset = self.fetch_intermarket_histories()
        return compute_intermarket_history(series_by_asset, months=months)
