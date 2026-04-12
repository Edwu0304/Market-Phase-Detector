LENS_TITLES = {
    "izaax": "Izaax Lens",
    "urakami": "Urakami Lens",
    "marks": "Marks Lens",
}

LENS_METRIC_SETS = {
    "izaax": [
        {"id": "leading_index_change", "label": "Leading Index Change", "display_format": "decimal", "positive": "improving", "negative": "deteriorating"},
        {"id": "coincident_trend_score", "label": "Coincident Trend Score", "display_format": "decimal", "positive": "improving", "negative": "deteriorating"},
        {"id": "labor_stress", "label": "Labor Stress", "display_format": "decimal", "positive": "cooling", "negative": "rising"},
        {"id": "export_or_production", "label": "Export or Production Proxy", "display_format": "percent", "positive": "expanding", "negative": "contracting"},
        {"id": "unemployment_claims", "label": "Unemployment Claims", "display_format": "decimal", "positive": "declining", "negative": "rising"},
        {"id": "cci_level", "label": "CCI", "display_format": "decimal", "positive": "optimistic", "negative": "pessimistic"},
        {"id": "pmi", "label": "PMI", "display_format": "decimal", "positive": "expanding", "negative": "contracting"},
        {"id": "sahm_rule", "label": "Sahm Rule", "display_format": "decimal", "positive": "no_recession", "negative": "recession_signal"},
        {"id": "inventory_sales_ratio", "label": "Inventory / Sales", "display_format": "decimal", "positive": "healthy", "negative": "accumulating"},
    ],
    "urakami": [
        {"id": "yield_curve", "label": "Yield Curve", "display_format": "spread", "positive": "steepening", "negative": "inverted"},
        {"id": "rates_regime", "label": "Rates Regime", "display_format": "decimal", "positive": "easing", "negative": "tight"},
        {"id": "market_leadership_proxy", "label": "Market Leadership Proxy", "display_format": "decimal", "positive": "broadening", "negative": "narrow"},
        {"id": "bank_lending_rate", "label": "Bank Lending Rate", "display_format": "percent", "positive": "falling", "negative": "rising"},
        {"id": "credit_change", "label": "Credit Change", "display_format": "decimal", "positive": "improving", "negative": "deteriorating"},
        {"id": "m1b_change", "label": "M1B Change", "display_format": "decimal", "positive": "improving", "negative": "deteriorating"},
        {"id": "m2_yoy", "label": "M2 YoY", "display_format": "percent", "positive": "improving", "negative": "deteriorating"},
        {"id": "pe_ratio", "label": "PE Ratio", "display_format": "decimal", "positive": "reasonable", "negative": "overvalued"},
        {"id": "ma_200day", "label": "200D MA", "display_format": "percent", "positive": "above", "negative": "below"},
        {"id": "volume_ma", "label": "Volume MA", "display_format": "decimal", "positive": "confirming", "negative": "diverging"},
        {"id": "margin_balance", "label": "Margin Balance", "display_format": "decimal", "positive": "moderate", "negative": "excessive"},
    ],
    "marks": [
        {"id": "hy_spread", "label": "HY Spread", "display_format": "spread", "positive": "tightening", "negative": "stress"},
        {"id": "valuation_proxy", "label": "Valuation Proxy", "display_format": "decimal", "positive": "reasonable", "negative": "stretched"},
        {"id": "fear_proxy", "label": "Fear Proxy", "display_format": "decimal", "positive": "fearful", "negative": "complacent"},
        {"id": "credit_spread", "label": "Credit Spread", "display_format": "spread", "positive": "narrow", "negative": "wide"},
        {"id": "cci_level", "label": "CCI", "display_format": "decimal", "positive": "calm", "negative": "euphoric"},
        {"id": "margin_balance", "label": "Margin Balance", "display_format": "decimal", "positive": "moderate", "negative": "excessive"},
        {"id": "government_spending", "label": "Government Spending", "display_format": "decimal", "positive": "prudent", "negative": "expanding"},
    ],
}
