from datetime import date
from pathlib import Path

from market_phase_detector.collectors.tw_official import TaiwanOfficialCollector
from market_phase_detector.collectors.us_fred import FredCollector
from market_phase_detector.engine.state_machine import resolve_transition
from market_phase_detector.engine.tw_rules import derive_tw_candidate
from market_phase_detector.engine.us_rules import derive_us_candidate
from market_phase_detector.exporters.json_exporter import write_dashboard_snapshot
from market_phase_detector.live_pipeline import build_tw_observations, build_us_observations
from market_phase_detector.pipeline import build_country_snapshot
from market_phase_detector.site_builder import build_site


def build_sample_payload() -> dict:
    return {
        "generated_at": "2026-04-05",
        "meta": {
            "source": "sample",
        },
        "countries": [
            build_country_snapshot(
                country="US",
                as_of="2026-03-31",
                observations={
                    "ism": 52.0,
                    "claims_trend": "stable",
                    "sahm_rule": 0.28,
                    "yield_curve": -0.35,
                    "hy_spread": 3.8,
                },
                derived_signals={
                    "macro_direction": "firm",
                    "risk_state": "late_cycle_warning",
                },
                candidate_phase="Boom",
                final_phase="Boom",
                reasons=[
                    "Yield curve inversion is a late-cycle warning",
                    "Manufacturing remains above the expansion threshold",
                ],
                watch="recession_risk",
            ),
            build_country_snapshot(
                country="TW",
                as_of="2026-03-31",
                observations={
                    "business_signal_score": 18,
                    "leading_trend": "improving",
                    "coincident_trend": "stable",
                    "unemployment_trend": "stable",
                    "exports_yoy": -2.5,
                },
                derived_signals={
                    "macro_direction": "improving",
                    "risk_state": "recovery_not_confirmed",
                },
                candidate_phase="Recovery",
                final_phase="Recovery",
                reasons=[
                    "Leading indicators are improving from weak levels",
                    "External demand is stabilizing",
                ],
                watch="recovery_not_confirmed",
            ),
        ],
    }


def fetch_live_dashboard_payload() -> dict:
    us_collector = FredCollector()
    tw_collector = TaiwanOfficialCollector()

    us_observations = build_us_observations(us_collector)
    tw_observations = build_tw_observations(tw_collector)

    us_candidate = derive_us_candidate(
        leading_index_change=us_observations["leading_index_change"],
        claims_trend=us_observations["claims_trend"],
        sahm_rule=us_observations["sahm_rule"],
        yield_curve=us_observations["yield_curve"],
        hy_spread=us_observations["hy_spread"],
    )
    us_transition = resolve_transition(
        previous_phase=us_candidate.phase,
        candidate_phase=us_candidate.phase,
        previous_candidate_phase=us_candidate.phase,
        stress_override=us_candidate.phase == "Recession",
    )

    tw_candidate = derive_tw_candidate(
        business_signal_score=tw_observations["business_signal_score"],
        leading_trend=tw_observations["leading_trend"],
        coincident_trend=tw_observations["coincident_trend"],
        unemployment_trend=tw_observations["unemployment_trend"],
        exports_yoy=tw_observations["exports_yoy"],
        exports_trend="improving" if tw_observations["exports_yoy"] >= 0 else "deteriorating",
    )
    tw_transition = resolve_transition(
        previous_phase=tw_candidate.phase,
        candidate_phase=tw_candidate.phase,
        previous_candidate_phase=tw_candidate.phase,
        stress_override=tw_candidate.phase == "Recession",
    )

    return {
        "generated_at": str(date.today()),
        "meta": {
            "source": "live",
        },
        "countries": [
            build_country_snapshot(
                country="US",
                as_of=us_observations["as_of"],
                observations=us_observations,
                derived_signals={
                    "macro_direction": "improving" if us_observations["leading_index_change"] >= 0 else "softening",
                    "risk_state": us_transition.watch or "none",
                },
                candidate_phase=us_candidate.phase,
                final_phase=us_transition.final_phase,
                reasons=us_candidate.reasons,
                watch=us_transition.watch,
            ),
            build_country_snapshot(
                country="TW",
                as_of=tw_observations["as_of"],
                observations=tw_observations,
                derived_signals={
                    "macro_direction": tw_observations["leading_trend"],
                    "risk_state": tw_transition.watch or "none",
                },
                candidate_phase=tw_candidate.phase,
                final_phase=tw_transition.final_phase,
                reasons=tw_candidate.reasons,
                watch=tw_transition.watch,
            ),
        ],
    }


def generate_dashboard_payload() -> dict:
    try:
        return fetch_live_dashboard_payload()
    except Exception as exc:
        payload = build_sample_payload()
        payload["meta"] = {
            "source": "sample_fallback",
            "error": str(exc),
        }
        return payload


def main() -> None:
    target = Path("data/latest.json")
    write_dashboard_snapshot(generate_dashboard_payload(), target, Path("data/history"))
    build_site("frontend/src", "data", "dist")


if __name__ == "__main__":
    main()
