# 指標與 API 資料來源

本文件整理目前專案所有有用到的外部資料來源、實際抓取網址、欄位用途，以及在專案內被轉成什麼指標。

## 1. 美國資料來源

美國資料全部來自 FRED。

程式位置：

- [us_fred.py](/D:/repo/python/Market%20Phase%20Detector/.worktrees/strategy-map-redesign/src/market_phase_detector/collectors/us_fred.py)
- [live_pipeline.py](/D:/repo/python/Market%20Phase%20Detector/.worktrees/strategy-map-redesign/src/market_phase_detector/live_pipeline.py)

### 實際抓取端點

- CSV 圖表端點：`https://fred.stlouisfed.org/graph/fredgraph.csv?id=<SERIES_ID>`
- JSON 端點：`https://api.stlouisfed.org/fred/series/observations`

專案目前實際使用的是 CSV 端點。

### 美國序列對照表

| 專案內部代碼 | FRED 序列 ID | 用途 | 官方頁面 |
|---|---|---|---|
| `leading_index` | `IPMAN` | 製造業工業生產，拿來看景氣與工業活動方向 | [IPMAN](https://fred.stlouisfed.org/series/IPMAN) |
| `claims` | `ICSA` | 初領失業救濟金，拿來看勞動市場壓力方向 | [ICSA](https://fred.stlouisfed.org/series/ICSA) |
| `sahm_rule` | `SAHMCURRENT` | Sahm Rule，拿來確認衰退風險 | [SAHMCURRENT](https://fred.stlouisfed.org/series/SAHMCURRENT) |
| `yield_curve` | `T10Y2Y` | 10 年期減 2 年期殖利率差，拿來看殖利率曲線斜率 | [T10Y2Y](https://fred.stlouisfed.org/series/T10Y2Y) |
| `hy_spread` | `BAMLH0A0HYM2` | 高收益債利差，拿來看信用風險與風險偏好 | [BAMLH0A0HYM2](https://fred.stlouisfed.org/series/BAMLH0A0HYM2) |

### 專案內部轉換方式

#### `leading_index_change`

- 來源：`IPMAN`
- 轉換：最近兩期差值
- 用途：
  - 美國網站總相位
  - 愛榭克鏡頭
  - 浦上邦雄鏡頭
  - 霍華．馬克斯鏡頭的估值／風險偏好代理

#### `claims_trend`

- 來源：`ICSA`
- 轉換：最近 8 週資料切成前 4 週與後 4 週，做平均比較
- 結果：`rising`、`falling`、`stable`
- 用途：
  - 美國網站總相位
  - 愛榭克鏡頭的勞動壓力代理
  - 霍華．馬克斯鏡頭的恐慌代理

#### `sahm_rule`

- 來源：`SAHMCURRENT`
- 轉換：直接使用最新值
- 用途：
  - 美國網站總相位的衰退確認

#### `yield_curve`

- 來源：`T10Y2Y`
- 轉換：直接使用最新值
- 用途：
  - 美國網站總相位
  - 浦上邦雄鏡頭
  - 霍華．馬克斯鏡頭的估值代理補充

#### `hy_spread`

- 來源：`BAMLH0A0HYM2`
- 轉換：直接使用最新值
- 用途：
  - 美國網站總相位
  - 霍華．馬克斯鏡頭核心信用代理

## 2. 台灣資料來源

台灣資料主要來自國發會的景氣指標 ZIP 資料。

程式位置：

- [tw_official.py](/D:/repo/python/Market%20Phase%20Detector/.worktrees/strategy-map-redesign/src/market_phase_detector/collectors/tw_official.py)
- [live_pipeline.py](/D:/repo/python/Market%20Phase%20Detector/.worktrees/strategy-map-redesign/src/market_phase_detector/live_pipeline.py)

### 實際抓取端點

- 國發會景氣指標說明頁：
  [https://www.ndc.gov.tw/en/Content_List.aspx?n=7FC514B520F97C0D](https://www.ndc.gov.tw/en/Content_List.aspx?n=7FC514B520F97C0D)
- 專案目前直接抓的 ZIP：
  `https://ws.ndc.gov.tw/Download.ashx?icon=.zip&n=5pmv5rCj5oyH5qiZ5Y%2BK54eI6JmfLnppcA%3D%3D&u=LzAwMS9hZG1pbmlzdHJhdG9yLzEwL3JlbGZpbGUvNTc4MS82MzkyL2VhMjM1YmQ5LWQwNTItNGE2OS1hYmZjLWQ1Yzc4NWQzZDBlMi56aXA%3D`

### 國發會方法說明參考

- 景氣對策信號簡介：
  [https://www.ndc.gov.tw/nc_335_2236](https://www.ndc.gov.tw/nc_335_2236)
- 景氣對策信號如何編製：
  [https://www.ndc.gov.tw/nc_336_25586](https://www.ndc.gov.tw/nc_336_25586)

### ZIP 內部目前使用的欄位概念

程式會從 ZIP 解出多個 CSV，並抽取下列概念欄位：

- 景氣對策信號分數
- 領先指標
- 同時指標
- 失業率
- 出口值

### 專案內部轉換方式

#### `business_signal_score`

- 來源：國發會景氣對策信號分數
- 轉換：直接使用
- 用途：
  - 台灣網站總相位

#### `leading_trend`

- 來源：領先指標與前期差值
- 轉換：大於門檻為 `improving`，小於負門檻為 `deteriorating`，否則 `stable`
- 用途：
  - 台灣網站總相位
  - 愛榭克鏡頭

#### `coincident_trend`

- 來源：同時指標與前期差值
- 轉換：同上
- 用途：
  - 台灣網站總相位
  - 愛榭克鏡頭
  - 浦上邦雄鏡頭的市場廣度代理

#### `unemployment_trend`

- 來源：失業率與前期比較
- 轉換：若上升則 `rising`，否則目前程式記為 `stable`
- 用途：
  - 台灣網站總相位
  - 愛榭克鏡頭勞動壓力代理
  - 霍華．馬克斯鏡頭恐慌代理

#### `exports_yoy`

- 來源：當月出口值與去年同期比較
- 轉換：年增率百分比
- 用途：
  - 台灣網站總相位
  - 愛榭克鏡頭出口／生產代理

## 3. 站點文字內容來源

這不是外部 API，但也是前端顯示的重要來源。

程式位置：

- [strategy_content.py](/D:/repo/python/Market%20Phase%20Detector/.worktrees/strategy-map-redesign/src/market_phase_detector/strategy_content.py)
- [content.py](/D:/repo/python/Market%20Phase%20Detector/.worktrees/strategy-map-redesign/src/market_phase_detector/content.py)

它負責：

- 三位作者理論說明
- 各相位文案
- 首頁方法說明
- 資料原則說明

## 4. 指標到畫面的對應

### 首頁

- 讀取 `data/latest.json`
- 顯示台灣與美國的網站總相位

### 國別頁上方摘要

- 顯示該國網站總相位
- 顯示最新觀測值 `observations`

### 三個鏡頭

- 每個鏡頭讀自己的 `lenses.<author>`
- 顯示：
  - 目前相位
  - 理由
  - 指標表格
  - 歷史月份拉桿

## 5. 維運注意事項

### 不要私下替換資料源

因為目前整個系統的判斷邏輯、測試與 UI 欄位，都是依這批來源設計。

如果你要換資料源，至少要同步檢查：

- `collectors/`
- `live_pipeline.py`
- `engine/`
- `lenses/`
- `tests/`
- 維運文件

### 台美歷史月份必須共同對齊

這個專案不是各顯各的最新月份，而是只顯示台美都可對齊的共同月份。

因此：

- 美國資料比較快更新，不代表畫面就要先跳新月份
- 台灣若尚未更新，歷史時間軸就應停在共同月份
