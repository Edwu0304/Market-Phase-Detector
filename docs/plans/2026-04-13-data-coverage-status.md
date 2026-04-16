# Data Coverage Status

**Purpose**

This file freezes the current state of the data-acquisition phase so the project can move into table-model refactoring without losing track of what is truly complete and what still remains missing.

---

## Completed Coverage

### Martin Pring / 愛榭克

- Leading indicator direction
- Labor stress proxy
- Production direction proxy
- Export / demand direction
- Inventory-cycle proxy
- Confidence proxy
- Inflation expectation proxy (US)
- Commodity proxy (US)
- Industrial metals proxy (US)
- Breadth / advance-decline (TW)
- Sector participation breadth (TW and US)
- Cross-asset sequencing / intermarket order (US)
- Earnings-growth context proxy indirectly available via current macro stack, but not a core Pring field

### Urakami

- Short-rate proxy
- Long-rate proxy
- Yield-curve spread
- Yield-curve regime label
- Money supply proxy
- Valuation proxy
- Sector rotation / market leadership (TW and US)
- Earnings-growth proxy (US and TW)

### Howard Marks

- Credit spread regime
- Lending standards (US)
- Funding stress (US)
- HY spread
- HY yield
- Distress proxy
- Default-pressure proxy
- Issuance-appetite proxy
- Policy uncertainty proxy
- Margin / leverage proxy
- Breadth / risk-appetite supporting proxies
- Taiwan sector participation context

---

## Remaining Gaps

These are still not truly covered by stable public data in the current implementation:

### Martin Pring / 愛榭克

- Formal breadth/diffusion regime label for US market breadth
- Pring-specific momentum families such as KST / Special K
- Better TW inflation-expectation proxy than plain inflation-related approximations
- Better TW cross-asset bond/equity/commodity sequencing if local bond total-return proxy is added

### Urakami

- Direct aggregate EPS series for Taiwan and US rather than earnings-growth proxy
- Direct bankruptcy / default rate series for Taiwan
- More explicit sector-style leadership taxonomy beyond top/bottom sector

### Howard Marks

- Direct corporate-bond issuance volume time series for Taiwan
- Direct covenant-looseness measure
- Stable public direct default-rate series rather than proxy combination
- Stronger explicit investor-psychology series beyond proxy set

---

## Decision

The project is now at the correct transition point:

1. Stop treating data acquisition as the main blocker
2. Preserve the above remaining gaps as `missing`
3. Refactor the master table model so rows can be rendered as:
   - original
   - proxy
   - missing

That is the next correct step.
