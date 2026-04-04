from datetime import date
from pathlib import Path

from market_phase_detector.collectors.tw_official import TaiwanOfficialCollector
from market_phase_detector.collectors.us_fred import FredCollector
from market_phase_detector.content import build_site_content
from market_phase_detector.engine.state_machine import resolve_transition
from market_phase_detector.engine.tw_rules import derive_tw_candidate
from market_phase_detector.engine.us_rules import derive_us_candidate
from market_phase_detector.exporters.json_exporter import write_dashboard_snapshot, write_site_content
from market_phase_detector.live_pipeline import (
    NDC_ZIP_URL,
    build_tw_history_observations,
    build_tw_observations,
    build_us_history_observations,
    build_us_observations,
)
from market_phase_detector.pipeline import build_country_snapshot
from market_phase_detector.site_builder import build_site
from market_phase_detector.strategy_content import build_country_handbook, build_landing_content


def build_sample_payload() -> dict:
    return {
        "generated_at": "2026-04-05",
        "meta": {
            "source": "sample",
        },
        "landing": build_landing_content(),
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
                handbook=build_country_handbook("US", "Boom"),
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
                handbook=build_country_handbook("TW", "Recovery"),
            ),
        ],
    }


def _build_us_snapshot(observations: dict, previous_phase: str | None, previous_candidate_phase: str | None) -> tuple[dict, str]:
    candidate = derive_us_candidate(
        leading_index_change=observations["leading_index_change"],
        claims_trend=observations["claims_trend"],
        sahm_rule=observations["sahm_rule"],
        yield_curve=observations["yield_curve"],
        hy_spread=observations["hy_spread"],
    )
    transition = resolve_transition(
        previous_phase=previous_phase or candidate.phase,
        candidate_phase=candidate.phase,
        previous_candidate_phase=previous_candidate_phase or candidate.phase,
        stress_override=candidate.phase == "Recession",
    )
    snapshot = build_country_snapshot(
        country="US",
        as_of=observations["as_of"],
        observations=observations,
        derived_signals={
            "macro_direction": "improving" if observations["leading_index_change"] >= 0 else "softening",
            "risk_state": transition.watch or "none",
        },
        candidate_phase=candidate.phase,
        final_phase=transition.final_phase,
        reasons=candidate.reasons,
        watch=transition.watch,
        handbook=build_country_handbook("US", transition.final_phase),
    )
    return snapshot, candidate.phase


def _build_tw_snapshot(observations: dict, previous_phase: str | None, previous_candidate_phase: str | None) -> tuple[dict, str]:
    candidate = derive_tw_candidate(
        business_signal_score=observations["business_signal_score"],
        leading_trend=observations["leading_trend"],
        coincident_trend=observations["coincident_trend"],
        unemployment_trend=observations["unemployment_trend"],
        exports_yoy=observations["exports_yoy"],
        exports_trend="improving" if observations["exports_yoy"] >= 0 else "deteriorating",
    )
    transition = resolve_transition(
        previous_phase=previous_phase or candidate.phase,
        candidate_phase=candidate.phase,
        previous_candidate_phase=previous_candidate_phase or candidate.phase,
        stress_override=candidate.phase == "Recession",
    )
    snapshot = build_country_snapshot(
        country="TW",
        as_of=observations["as_of"],
        observations=observations,
        derived_signals={
            "macro_direction": observations["leading_trend"],
            "risk_state": transition.watch or "none",
        },
        candidate_phase=candidate.phase,
        final_phase=transition.final_phase,
        reasons=candidate.reasons,
        watch=transition.watch,
        handbook=build_country_handbook("TW", transition.final_phase),
    )
    return snapshot, candidate.phase


def _build_latest_payload(us_observations: dict, tw_observations: dict) -> dict:
    us_snapshot, _ = _build_us_snapshot(us_observations, None, None)
    tw_snapshot, _ = _build_tw_snapshot(tw_observations, None, None)

    return {
        "generated_at": str(date.today()),
        "meta": {
            "source": "live",
        },
        "landing": build_landing_content(),
        "countries": [us_snapshot, tw_snapshot],
    }


def _build_history_payloads(us_history: list[dict], tw_history: list[dict]) -> list[dict]:
    us_by_month = {entry["month"]: entry for entry in us_history}
    tw_by_month = {entry["month"]: entry for entry in tw_history}
    months = sorted(set(us_by_month) & set(tw_by_month))

    previous_phases = {"US": None, "TW": None}
    previous_candidates = {"US": None, "TW": None}
    payloads = []
    for month in months:
        us_snapshot, us_candidate = _build_us_snapshot(
            us_by_month[month],
            previous_phases["US"],
            previous_candidates["US"],
        )
        previous_phases["US"] = us_snapshot["decision"]["final_phase"]
        previous_candidates["US"] = us_candidate

        tw_snapshot, tw_candidate = _build_tw_snapshot(
            tw_by_month[month],
            previous_phases["TW"],
            previous_candidates["TW"],
        )
        previous_phases["TW"] = tw_snapshot["decision"]["final_phase"]
        previous_candidates["TW"] = tw_candidate

        payloads.append(
            {
                "generated_at": f"{month}-01",
                "meta": {"source": "live_history"},
                "landing": build_landing_content(),
                "countries": [us_snapshot, tw_snapshot],
            }
        )

    return payloads


def fetch_live_dashboard_payload() -> dict:
    us_collector = FredCollector()
    tw_collector = TaiwanOfficialCollector()
    us_observations = build_us_observations(us_collector)
    tw_observations = build_tw_observations(tw_collector)
    return _build_latest_payload(us_observations, tw_observations)


def fetch_live_dashboard_bundle(months: int = 6) -> dict:
    us_collector = FredCollector()
    tw_collector = TaiwanOfficialCollector()

    us_observations = build_us_observations(us_collector)
    tw_observations = build_tw_observations(tw_collector)
    latest_payload = _build_latest_payload(us_observations, tw_observations)

    us_history = build_us_history_observations(us_collector, months=months)
    tw_history = build_tw_history_observations(
        tw_collector.fetch_ndc_zip_history_metrics(NDC_ZIP_URL),
        months=months,
    )
    history_payloads = _build_history_payloads(us_history, tw_history)
    return {"latest": latest_payload, "history": history_payloads}


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


def generate_dashboard_bundle() -> dict:
    try:
        return fetch_live_dashboard_bundle()
    except Exception as exc:
        payload = build_sample_payload()
        payload["meta"] = {
            "source": "sample_fallback",
            "error": str(exc),
        }
        return {"latest": payload, "history": [payload]}


def main() -> None:
    bundle = generate_dashboard_bundle()
    target = Path("data/latest.json")
    write_dashboard_snapshot(
        bundle["latest"],
        target,
        Path("data/history"),
        history_payloads=bundle["history"],
    )
    write_site_content(build_site_content(), Path("data/site-content.json"))
    build_site("frontend/src", "data", "dist")


if __name__ == "__main__":
    main()
