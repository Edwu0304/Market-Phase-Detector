from market_phase_detector.strategy_content import (
    COUNTRY_LABELS,
    PHASE_LABELS,
    build_country_handbook,
    build_landing_content,
)


def build_site_content() -> dict:
    return {
        "home": build_landing_content(),
        "countries": {
            country: {
                "label": COUNTRY_LABELS[country],
                "handbook_by_phase": {
                    phase: build_country_handbook(country, phase)
                    for phase in PHASE_LABELS
                },
            }
            for country in COUNTRY_LABELS
        },
    }
