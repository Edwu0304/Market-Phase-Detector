# Missing Indicator Source Matrix

**Purpose**

This is the execution-facing source matrix for the missing indicators identified in the three-masters inventory.

For each missing or under-modeled indicator family:

- define the intended master signal
- identify the best available source
- classify whether the source is direct or proxy
- note country coverage
- note ingestion feasibility

---

## 1. Martin Pring / 愛榭克

| Master signal | Preferred source | TW | US | Type | Feasibility | Notes |
|---|---|---|---|---|---|---|
| Bond trend | CBC / TPEx government bond yield history | yes | no | proxy | high | TW can infer direction from yield history or bond total-return proxy |
| Bond trend | FRED Treasury yield series | no | yes | proxy | high | Already partially available through FRED collector |
| Equity trend | TWSE index history | yes | no | direct-ish | high | Can compute rolling trend from TAIEX |
| Equity trend | Yahoo Finance / FRED market index proxies | no | yes | direct-ish | medium | Already operationally simple |
| Commodity index | FRED commodity index series | no | yes/global | direct-ish | high | Good US/global proxy for Pring intermarket work |
| Industrial metals | FRED industrial commodity / metals proxies | no | yes/global | proxy | medium | Better than scraping LME first |
| Market breadth / diffusion | TWSE advancing/declining issues, sector rise/fall counts | yes | no | proxy | medium | Need derived breadth series from daily stats |
| Market breadth / diffusion | FRED/market breadth not native; use NYSE/NASDAQ breadth via public feeds if available | no | partial | proxy | low-medium | Might require separate public source or derived dataset |
| Inflation expectations | CBC CPI / TW inflation data | yes | no | proxy | medium | True expectation series likely not public; use inflation proxy |
| Inflation expectations | FRED breakeven inflation (`T5YIE`, `T10YIE`) | no | yes | direct-ish | high | Best current US fit |
| Cross-asset sequencing | Derived from bond trend + equity trend + commodity trend | yes | yes | derived | high | No single external source; compute in pipeline |
| Market breadth diffusion regime | Derived from issue counts or sector participation | yes | yes | derived | medium | Should be computed internally once source exists |

### Immediate Pring priorities

1. Completed: FRED inflation expectation series
2. Completed: TWSE breadth derivation
3. Completed: commodity/metals global proxies
4. Completed: cross-asset sequencing logic after the raw series exist
5. Remaining: formal breadth/diffusion regime label for the U.S.

---

## 2. Urakami

| Master signal | Preferred source | TW | US | Type | Feasibility | Notes |
|---|---|---|---|---|---|---|
| Short-rate direction | CBC policy / discount rate history | yes | no | direct-ish | high | Existing collection already close |
| Short-rate direction | FRED policy rate / fed funds | no | yes | direct | high | Easy via existing FRED path |
| Long-rate direction | TPEx government bond curve | yes | no | direct-ish | high | Existing bond collector already supports this |
| Long-rate direction | FRED / Treasury yield series | no | yes | direct | high | Easy |
| Yield-curve regime labels | Derived from short and long rates | yes | yes | derived | high | Need regime transformation, not new scraping |
| EPS growth | TWSE/TPEX financial statements, monthly revenue, earnings disclosures | yes | no | direct-ish | medium | Requires aggregation logic, not a single clean API |
| EPS growth | S&P 500 EPS aggregate source | no | yes | direct-ish | medium | Public partial; likely proxy if not licensed |
| Bankruptcy / default pressure | Judicial / FSC distress data | yes | no | proxy | medium-low | Feasible but likely messy |
| Bankruptcy / default pressure | Moody's / S&P default studies or public default proxies | no | yes | proxy | low-medium | Public direct series limited |
| Sector rotation / market leadership | TWSE sector indices and relative strength | yes | no | direct-ish | high | Best local route |
| Sector rotation / market leadership | S&P sector indices / ETF relative strength | no | yes | direct-ish | high | Can derive from sector ETFs or public indices |
| Stock response vs earnings phase | Derived from price trend + EPS growth | yes | yes | derived | medium | Requires EPS input first |

### Immediate Urakami priorities

1. Completed: sector rotation metrics for TW and US
2. Completed: yield-curve regime labels from existing rates
3. Completed: earnings-growth proxy / aggregation
4. Remaining: direct bankruptcy/default series unless a stable public source is confirmed

---

## 3. Howard Marks

| Master signal | Preferred source | TW | US | Type | Feasibility | Notes |
|---|---|---|---|---|---|---|
| Credit spread regime | TPEx corporate-vs-government spread | yes | no | direct-ish | high | Already in project |
| Credit spread regime | FRED HY / BBB spread series | no | yes | direct-ish | high | Already partly in project |
| High-yield market activity / issuance | TPEx corporate bond issuance / trading stats | yes | no | proxy | medium | Better local proxy than none |
| High-yield market activity / issuance | FRED / ICE BofA HY spread + issuance proxy from public market stats | no | yes | proxy | medium | Spread exists; issuance may need supplemental public source |
| Lending standards | CBC/FSC bank credit conditions proxies | yes | no | proxy | low-medium | Likely only proxy-level coverage |
| Lending standards | Fed Senior Loan Officer Opinion Survey | no | yes | direct-ish | high | Strong fit for Marks financing conditions |
| Distress / default pressure | Taiwan court/FSC distress proxies | yes | no | proxy | low-medium | Likely weak but possible |
| Distress / default pressure | Moody's default rate proxy or public recession/default indicators | no | yes | proxy | medium | Direct ratings data may be paywalled |
| Liquidity / funding stress | Taiwan money market spread proxies | yes | no | proxy | low-medium | Need source validation |
| Liquidity / funding stress | FRED funding stress series / TED / FRA-OIS style proxies | no | yes | direct-ish | high | Good Marks-compatible signal |
| Investor sentiment / risk appetite | CCI, margin, valuation, turnover | yes | yes | proxy | high | Current project already leans here |
| Covenant looseness | no clean public TW source | no | limited | missing | low | Likely out of scope for first pass |

### Immediate Marks priorities

1. Completed: US lending-standards survey
2. Completed: US funding-stress series
3. Completed in proxy form: distress/default-pressure and issuance-appetite
4. Remaining: TW issuance / corporate bond activity proxy
5. Remaining: covenant-looseness only if a robust public source appears

---

## 4. Recommended Build Order

The most practical next ingestion wave is:

1. **Pring**
   - completed: US inflation expectations from FRED
   - completed: TW breadth from TWSE issue counts
   - completed: commodity/metals proxy series
   - completed: intermarket sequencing
2. **Urakami**
   - completed: yield-curve regime derivation
   - completed: sector rotation metrics for TW and US
   - completed: earnings-growth aggregation/proxy
3. **Marks**
   - completed: US lending standards
   - completed: US funding stress
   - remaining: TW bond issuance / activity proxy

---

## 5. What Not To Block On

These are real gaps, but they should not block the next implementation wave:

- Pring exact LME institutional metals feeds
- Urakami clean public default-rate series for Taiwan
- Marks covenant-looseness direct datasets

These can be represented as `missing` in the master table until a stable source is confirmed.
