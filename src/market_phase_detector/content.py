from market_phase_detector.strategy_content import (
    AUTHOR_ORDER,
    COUNTRY_LABELS,
    PHASE_LABELS,
    build_author_strategy,
    build_country_handbook,
    build_landing_content,
)


def build_site_content() -> dict:
    return {
        "home": build_landing_content(),
        "authors": {author: build_author_strategy(author) for author in AUTHOR_ORDER},
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
