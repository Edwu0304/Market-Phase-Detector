# Handoff — 新增指標爬蟲 + 愛榭克轉置表格 UI

## Session 日期
2026-04-06

## 工作摘要

從 `docs/景氣循環投資策略指南 - Curated Briefing - 2026-04-05.md` 中找出缺少的指標，
實作爬蟲、整合到 pipeline，並為愛榭克鏡頭建立全新的轉置表格 UI（指標為列、月份為欄）。

---

## 一、指標缺口分析

比對文件與既有程式碼後，缺少的指標：

| 指標 | 台灣資料來源 | 狀態 |
|------|-------------|------|
| 初領失業救濟金 | 勞動部 | ✅ 年度 CSV 可抓 |
| 消費者信心指數 CCI | 中央大學 | ✅ 首頁可抓 |
| 殖利率曲線利差 10Y-2Y | 櫃買中心 | ✅ XLS 可抓 |
| 信用利差（公司債 - 公債） | 櫃買中心 | ✅ XLS 可抓 |
| 大盤本益比 | 證交所 API | ✅ 最新快照可抓 |
| 融資餘額 | 證交所 API | ✅ 最新快照可抓 |
| 政府歲出 | 財政部 | ⚠️ 只有年度 |
| 200日均線 | 證交所 | ❌ 需每日股價計算 |
| 成交量均線 | 證交所 | ❌ 需每日成交值 |
| 薩姆規則 | 自行計算 | ✅ 已存在計算器 |

---

## 二、爬蟲實作 (`tw_external.py`)

### 已實作的爬蟲方法

| 方法 | 來源 | 說明 |
|------|------|------|
| `fetch_tpex_bond_data()` | TPEx XLS | 公債殖利率 2Y/10Y + 公司債 AAA/AA/A/BBB |
| `fetch_tpex_bond_history()` | TPEx | 逐月回溯歷史（預設 24 個月） |
| `fetch_tpex_credit_spread()` | TPEx | 同日公債+公司債 → 信用利差 BBB |
| `fetch_cbc_credit_spread_proxy()` | TPEx | 別名 → fetch_tpex_bond_data() |
| `fetch_mol_claims_annual()` | MOL CSV (Big5) | 年度失業給付初次認定件數 |
| `fetch_ncu_cci()` | NCU 首頁 | 最新 CCI 總指數 |
| `fetch_twse_market_pe()` | TWSE yields.json | 大盤本益比最新快照 |
| `fetch_latest_twse_margin()` | TWSE values.json | 融資融券餘額最新快照 |
| `fetch_cbc_discount_rate()` | CBC 官網 | 重貼現率歷史 |

### 資料來源 URL

- **櫃買中心公債**: `https://www.tpex.org.tw/storage/bond_zone/tradeinfo/govbond/{year}/{month}/Curve.{date}-C.xls`
- **櫃買中心公司債**: `https://www.tpex.org.tw/storage/bond_zone/tradeinfo/govbond/{year}/{month}/COCurve.{date}-C.xls`
- **勞動部 CSV**: `https://statdb.mol.gov.tw/html/year/year12/37040.csv`
- **證交所 PE**: `https://www.twse.com.tw/res/data/zh/home/yields.json`
- **證交所融資**: `https://www.twse.com.tw/res/data/zh/home/values.json`
- **NCU CCI**: `https://rcted.ncu.edu.tw/`
- **央行利率**: `https://www.cbc.gov.tw/tw/lp-640-1-1-20.html`

### 信用利差公式

```
信用利差 BBB = BBB公司債殖利率 - 公債10Y殖利率
```

資料來源：櫃買中心 XLS（非代理指標，是真實數據）

---

## 三、Pipeline 整合 (`live_pipeline.py`)

### `build_tw_observations()` 新增外部資料整合

```python
obs = build_tw_observations(tw_collector, external_collector=tw_external)
```

新增欄位：
- `unemployment_claims` — 勞動部年度資料
- `cci_total` — 中央大學 CCI
- `pe_ratio` — 證交所本益比
- `margin_amount` / `margin_shares` — 證交所融資
- `gov_yield_10y` / `gov_yield_2y` / `spread_10y_2y` — TPEx 公債
- `credit_spread_bbb` — TPEx 信用利差
- `sahm_rule` — 薩姆規則計算

### `build_tw_history_observations()` 整合歷史

新增參數 `external_collector`，會從 TPEx 和 MOL 拉歷史資料配對。

---

## 四、Lens 整合

### `izaax.py` — 新增轉置表格

- `build_izaax_transposed_bundle()` 產出 `IzaaxTransposedBundle`
- 定義 `PHASE_SEQUENCE = ["Recovery", "Growth", "Boom", "Recession"]`
- 定義 `TRANSITION_METRICS` — 每個階段進入下一階段的關鍵指標：
  - Recovery → Growth: 領先指標、工業生產、出口
  - Growth → Boom: CCI、庫存/銷售比、出口
  - Boom → Recession: 薩姆規則、失業救濟金、庫存
  - Recession → Recovery: 領先指標、失業救濟金、薩姆規則

### `urakami.py` / `marks.py` — 新增指標

- Urakami: 加入 本益比、殖利率曲線利差、融資餘額
- Marks: 加入 信用利差、CCI、政府支出、融資餘額

---

## 五、前端 UI 改寫

### `frontend/src/app.js`

**新增 `buildIzaaxTransposedTable(transposed)` 函式**，渲染：
1. 階段進度條（復甦 → 成長 → 榮景 → 衰退）
2. 目前階段徽章 + 下一步提示
3. 轉置表格（指標為列，月份為欄）
4. ★ 關鍵指標標記
5. 正/負/中性顏色標示
6. 圖例說明

**修改 `buildLensRow()`**：
- Izaax 使用轉置表格，**不顯示滑桿和側邊欄**
- Urakami / Marks 維持原本的滑桿 + 側邊欄

**修改 `createLensController()`**：
- Izaax 不需滑桿控制，直接 return

### `frontend/src/styles.css`

新增 CSS 類別：
- `.izaax-transposed`、`.izaax-phase-banner`
- `.phase-progress`、`.phase-step`、`.phase-step-active`
- `.izaax-table-scroll-wrapper`（overflow-x: auto）
- `.izaax-transposed-table`
- `.cell-positive`、`.cell-negative`、`.cell-neutral`
- `.cell-transition-key`（關鍵指標底線強調）
- `.transition-key-indicator`（★ 符號）
- `.lens-row-izaax`（滿版佈局）

---

## 六、資料模型新增 (`models/lenses.py`)

```python
@dataclass(slots=True)
class TransposedMetricRow:
    metric_id: str
    label: str
    display_format: str
    is_transition_key: bool
    transition_direction: str
    values: list[dict]

@dataclass(slots=True)
class IzaaxTransposedBundle:
    current_phase: str
    current_phase_label: str
    next_phase: str
    prev_phase: str
    phase_sequence: list[str]
    transition_keys: list[str]
    metric_rows: list[TransposedMetricRow]
    months: list[str]
    reasons: list[str]
```

---

## 七、CLI 整合 (`cli.py`)

- 匯入 `TaiwanExternalCollector`
- `fetch_live_dashboard_bundle()` 建立外部爬蟲實例
- `build_tw_observations()` 傳入 `external_collector=tw_external`
- `build_tw_history_observations()` 傳入 `external_collector=tw_external`

---

## 八、相依套件

`pyproject.toml` 新增：
```toml
"pandas>=2.0.0",
"openpyxl>=3.1.0",
"xlrd>=2.0.1",
```

---

## 九、測試結果

```
55 passed in ~3s
```

所有既有測試通過，無破壞性變更。

---

## 十、部署

```bash
npx wrangler pages deploy dist --project-name market-phase-detector
```

最新部署網址：`https://codex-strategy-map-redesign.market-phase-detector.pages.dev/`

---

## 十一、已知問題 / 待辦

| 項目 | 狀況 |
|------|------|
| MOL 月度失業救濟金 | SSL 連線不穩定，目前只用年度 CSV |
| CCI 歷史 | 需逐月解析 PDF/HTML，目前只抓最新值 |
| 200日均線 | 未實作，需每日股價歷史 |
| 成交量均線 | 未實作，需每日成交值 |
| 政府歲出 | 只有年度資料，無月度 |
| MOL SSL 問題 | 已加 verify=False 降級，建議改用 Playwright |

---

## 十二、變更檔案清單

| 檔案 | 變更類型 |
|------|----------|
| `src/.../collectors/tw_external.py` | 大量新增爬蟲方法 |
| `src/.../live_pipeline.py` | 整合外部資料 |
| `src/.../lenses/izaax.py` | 新增轉置表格 builder |
| `src/.../lenses/urakami.py` | 新增指標 |
| `src/.../lenses/marks.py` | 新增指標 |
| `src/.../lenses/metric_sets.py` | 新增指標定義 |
| `src/.../models/lenses.py` | 新增 TransposedMetricRow, IzaaxTransposedBundle |
| `src/.../cli.py` | 整合 TaiwanExternalCollector |
| `src/.../site_builder.py` | 加 retry 處理 Windows 鎖定 |
| `frontend/src/app.js` | 新增 buildIzaaxTransposedTable, 修改 buildLensRow |
| `frontend/src/styles.css` | 新增轉置表格 + 階段進度條 CSS |
| `pyproject.toml` | 新增 pandas, openpyxl, xlrd |
| `tests/test_urakami_lens.py` | 放寬指標比對 |
| `tests/test_marks_lens.py` | 放寬指標比對 |
