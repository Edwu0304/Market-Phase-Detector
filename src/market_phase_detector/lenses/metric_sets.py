LENS_TITLES = {
    "izaax": "愛榭克鏡頭",
    "urakami": "浦上邦雄鏡頭",
    "marks": "霍華．馬克斯鏡頭",
}

LENS_METRIC_SETS = {
    "izaax": [
        {
            "id": "leading_index_change",
            "label": "領先指標變動",
            "display_format": "decimal",
            "positive": "improving",
            "negative": "deteriorating",
        },
        {
            "id": "coincident_trend_score",
            "label": "同時指標方向",
            "display_format": "decimal",
            "positive": "improving",
            "negative": "deteriorating",
        },
        {
            "id": "labor_stress",
            "label": "勞動壓力",
            "display_format": "decimal",
            "positive": "cooling",
            "negative": "rising",
        },
        {
            "id": "export_or_production",
            "label": "出口／生產",
            "display_format": "percent",
            "positive": "expanding",
            "negative": "contracting",
        },
    ],
    "urakami": [
        {
            "id": "yield_curve",
            "label": "殖利率曲線",
            "display_format": "spread",
            "positive": "steepening",
            "negative": "inverted",
        },
        {
            "id": "rates_regime",
            "label": "利率環境",
            "display_format": "decimal",
            "positive": "easing",
            "negative": "tight",
        },
        {
            "id": "market_leadership_proxy",
            "label": "市場領導廣度代理",
            "display_format": "decimal",
            "positive": "broadening",
            "negative": "narrow",
        },
    ],
    "marks": [
        {
            "id": "hy_spread",
            "label": "高收益債利差",
            "display_format": "spread",
            "positive": "tightening",
            "negative": "stress",
        },
        {
            "id": "valuation_proxy",
            "label": "估值／風險偏好代理",
            "display_format": "decimal",
            "positive": "reasonable",
            "negative": "stretched",
        },
        {
            "id": "fear_proxy",
            "label": "恐慌／自滿代理",
            "display_format": "decimal",
            "positive": "fearful",
            "negative": "complacent",
        },
    ],
}
