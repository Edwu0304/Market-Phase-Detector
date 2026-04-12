from market_phase_detector.strategy_content import (
    AUTHOR_ORDER,
    COUNTRY_LABELS,
    PHASE_LABELS,
    build_author_strategy,
    build_country_handbook,
    build_landing_content,
)


AUTHOR_GUIDES = {
    "izaax": {
        "decision_order": [
            "先看領先動能",
            "再看就業與失業壓力",
            "再看需求與生產是否同步改善",
            "最後用信心與庫存確認轉折",
        ],
        "core_signals": [
            {"label": "領先指標變動", "type": "original"},
            {"label": "失業壓力", "type": "original"},
            {"label": "出口 / 生產方向", "type": "original"},
            {"label": "PMI", "type": "proxy"},
            {"label": "CCI", "type": "proxy"},
        ],
    },
    "urakami": {
        "decision_order": [
            "先看利率方向",
            "再看信用與資金供給",
            "再看市場願不願意承擔風險",
            "最後才看估值是否過熱",
        ],
        "core_signals": [
            {"label": "銀行放款利率", "type": "original"},
            {"label": "信用變化", "type": "original"},
            {"label": "M1B / M2", "type": "proxy"},
            {"label": "殖利率曲線", "type": "proxy"},
            {"label": "本益比 / 融資", "type": "proxy"},
        ],
    },
    "marks": {
        "decision_order": [
            "先看信用有沒有壓力",
            "再看市場情緒是否過熱或恐慌",
            "再看價格是否還有安全邊際",
            "最後決定要防守還是承擔風險",
        ],
        "core_signals": [
            {"label": "信用利差", "type": "original"},
            {"label": "風險偏好", "type": "original"},
            {"label": "CCI", "type": "proxy"},
            {"label": "本益比", "type": "proxy"},
            {"label": "融資餘額", "type": "proxy"},
        ],
    },
}


def build_site_content() -> dict:
    return {
        "home": build_landing_content(),
        "authors": {
            author: {
                **build_author_strategy(author),
                **AUTHOR_GUIDES.get(author, {}),
            }
            for author in AUTHOR_ORDER
        },
        "countries": {
            country: {
                "label": COUNTRY_LABELS[country],
                "strategy_by_phase": {
                    phase: build_country_handbook(country, phase)
                    for phase in PHASE_LABELS
                },
            }
            for country in COUNTRY_LABELS
        },
    }
