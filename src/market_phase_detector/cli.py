from datetime import date
from pathlib import Path

from market_phase_detector.collectors.tw_official import TaiwanOfficialCollector
from market_phase_detector.collectors.tw_external import TaiwanExternalCollector
from market_phase_detector.collectors.us_fred import FredCollector
from market_phase_detector.content import build_site_content
from market_phase_detector.engine.state_machine import resolve_transition
from market_phase_detector.engine.tw_rules import derive_tw_candidate
from market_phase_detector.engine.us_rules import derive_us_candidate
from market_phase_detector.exporters.json_exporter import write_dashboard_snapshot, write_site_content
from market_phase_detector.lenses.izaax import (
    build_izaax_history_row,
    build_izaax_lens,
    build_izaax_transposed_bundle,
)
from market_phase_detector.lenses.marks import build_marks_history_row, build_marks_lens
from market_phase_detector.lenses.urakami import build_urakami_history_row, build_urakami_lens
from market_phase_detector.live_pipeline import (
    NDC_ZIP_URL,
    build_tw_history_observations,
    build_tw_observations,
    build_us_history_observations,
    build_us_observations,
)
from market_phase_detector.pipeline import build_country_snapshot
from market_phase_detector.site_builder import build_site
from market_phase_detector.strategy_content import AUTHOR_ORDER, build_country_handbook, build_landing_content


def _build_lens_bundle(observations: dict, history_observations: list[dict]) -> dict:
    izaax_history = []
    urakami_history = []
    marks_history = []
    previous_phases = {"izaax": None, "urakami": None, "marks": None}
    for row in history_observations:
        izaax_row = build_izaax_history_row(row["month"], row, previous_phases["izaax"])
        urakami_row = build_urakami_history_row(row["month"], row, previous_phases["urakami"])
        marks_row = build_marks_history_row(row["month"], row, previous_phases["marks"])
        izaax_history.append(izaax_row.to_dict())
        urakami_history.append(urakami_row.to_dict())
        marks_history.append(marks_row.to_dict())
        previous_phases["izaax"] = izaax_row.phase
        previous_phases["urakami"] = urakami_row.phase
        previous_phases["marks"] = marks_row.phase

    izaax_bundle = {
        **build_izaax_lens(observations).to_dict(),
        "history": izaax_history,
    }
    # Add transposed bundle for Izaax specialized UI
    izaax_bundle["transposed"] = build_izaax_transposed_bundle(observations, history_observations).to_dict()

    return {
        "izaax": izaax_bundle,
        "urakami": {
            **build_urakami_lens(observations).to_dict(),
            "history": urakami_history,
        },
        "marks": {
            **build_marks_lens(observations).to_dict(),
            "history": marks_history,
        },
    }


def build_sample_payload() -> dict:
    tw_history = [
        {
            "month": "2026-01",
            "as_of": "2026-01-31",
            "business_signal_score": 16,
            "leading_index_change": 0.12,
            "leading_trend": "improving",
            "coincident_trend": "stable",
            "unemployment_trend": "stable",
            "exports_yoy": -4.0,
        },
        {
            "month": "2026-02",
            "as_of": "2026-02-28",
            "business_signal_score": 19,
            "leading_index_change": 0.18,
            "leading_trend": "improving",
            "coincident_trend": "stable",
            "unemployment_trend": "stable",
            "exports_yoy": -1.5,
        },
        {
            "month": "2026-03",
            "as_of": "2026-03-31",
            "business_signal_score": 23,
            "leading_index_change": 0.26,
            "leading_trend": "improving",
            "coincident_trend": "improving",
            "unemployment_trend": "stable",
            "exports_yoy": 2.5,
        },
    ]
    us_history = [
        {
            "month": "2026-01",
            "as_of": "2026-01-31",
            "leading_index_change": 0.05,
            "claims_trend": "stable",
            "coincident_trend": "stable",
            "coincident_direction_score": 0.0,
            "sahm_rule": 0.38,
            "yield_curve": -0.20,
            "hy_spread": 4.8,
        },
        {
            "month": "2026-02",
            "as_of": "2026-02-28",
            "leading_index_change": 0.10,
            "claims_trend": "falling",
            "coincident_trend": "stable",
            "coincident_direction_score": 0.0,
            "sahm_rule": 0.33,
            "yield_curve": -0.05,
            "hy_spread": 4.2,
        },
        {
            "month": "2026-03",
            "as_of": "2026-03-31",
            "leading_index_change": 0.20,
            "claims_trend": "falling",
            "coincident_trend": "improving",
            "coincident_direction_score": 1.0,
            "sahm_rule": 0.28,
            "yield_curve": 0.10,
            "hy_spread": 3.8,
        },
    ]
    tw_latest = {
        "as_of": "2026-03-31",
        "business_signal_score": 23,
        "leading_index_change": 0.26,
        "leading_trend": "improving",
        "coincident_trend": "improving",
        "unemployment_trend": "stable",
        "exports_yoy": 2.5,
    }
    us_latest = {
        "as_of": "2026-03-31",
        "leading_index_change": 0.20,
        "claims_trend": "falling",
        "coincident_trend": "improving",
        "coincident_direction_score": 1.0,
        "sahm_rule": 0.28,
        "yield_curve": 0.10,
        "hy_spread": 3.8,
    }

    us_snapshot = build_country_snapshot(
        country="US",
        as_of=us_latest["as_of"],
        observations=us_latest,
        observation_history=us_history,
        derived_signals={"macro_direction": "firm", "risk_state": "none"},
        candidate_phase="Growth",
        final_phase="Growth",
        reasons=["總體與風險訊號同步改善。"],
        watch=None,
        handbook=build_country_handbook("US", "Growth"),
        lenses=_build_lens_bundle(us_latest, us_history),
    )
    tw_snapshot = build_country_snapshot(
        country="TW",
        as_of=tw_latest["as_of"],
        observations=tw_latest,
        observation_history=tw_history,
        derived_signals={"macro_direction": "improving", "risk_state": "none"},
        candidate_phase="Recovery",
        final_phase="Recovery",
        reasons=["領先與出口代理指標同步轉強。"],
        watch=None,
        handbook=build_country_handbook("TW", "Recovery"),
        lenses=_build_lens_bundle(tw_latest, tw_history),
    )
    return {
        "generated_at": "2026-04-05",
        "meta": {"source": "sample"},
        "landing": build_landing_content(),
        "countries": [us_snapshot, tw_snapshot],
    }


def _build_us_snapshot(observations: dict, history_observations: list[dict], previous_phase: str | None, previous_candidate_phase: str | None) -> tuple[dict, str]:
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
        observation_history=history_observations,
        derived_signals={
            "macro_direction": "improving" if observations["leading_index_change"] >= 0 else "softening",
            "risk_state": transition.watch or "none",
        },
        candidate_phase=candidate.phase,
        final_phase=transition.final_phase,
        reasons=candidate.reasons,
        watch=transition.watch,
        handbook=build_country_handbook("US", transition.final_phase),
        lenses=_build_lens_bundle(observations, history_observations),
    )
    return snapshot, candidate.phase


def _build_tw_snapshot(observations: dict, history_observations: list[dict], previous_phase: str | None, previous_candidate_phase: str | None) -> tuple[dict, str]:
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
        observation_history=history_observations,
        derived_signals={"macro_direction": observations["leading_trend"], "risk_state": transition.watch or "none"},
        candidate_phase=candidate.phase,
        final_phase=transition.final_phase,
        reasons=candidate.reasons,
        watch=transition.watch,
        handbook=build_country_handbook("TW", transition.final_phase),
        lenses=_build_lens_bundle(observations, history_observations),
    )
    return snapshot, candidate.phase


def _build_latest_payload(us_observations: dict, tw_observations: dict, us_history: list[dict], tw_history: list[dict]) -> dict:
    us_snapshot, _ = _build_us_snapshot(us_observations, us_history, None, None)
    tw_snapshot, _ = _build_tw_snapshot(tw_observations, tw_history, None, None)
    return {
        "generated_at": str(date.today()),
        "meta": {"source": "live", "authors": AUTHOR_ORDER},
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
        us_rows = [us_by_month[item] for item in months if item <= month]
        tw_rows = [tw_by_month[item] for item in months if item <= month]
        us_snapshot, us_candidate = _build_us_snapshot(us_by_month[month], us_rows, previous_phases["US"], previous_candidates["US"])
        tw_snapshot, tw_candidate = _build_tw_snapshot(tw_by_month[month], tw_rows, previous_phases["TW"], previous_candidates["TW"])
        previous_phases["US"] = us_snapshot["decision"]["final_phase"]
        previous_phases["TW"] = tw_snapshot["decision"]["final_phase"]
        previous_candidates["US"] = us_candidate
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
    bundle = fetch_live_dashboard_bundle()
    return bundle["latest"]


def fetch_live_dashboard_bundle(months: int = 24) -> dict:
    us_collector = FredCollector()
    tw_collector = TaiwanOfficialCollector()
    tw_external = TaiwanExternalCollector()
    us_history = build_us_history_observations(us_collector, months=months)
    tw_history = build_tw_history_observations(tw_collector.fetch_ndc_zip_history_metrics(NDC_ZIP_URL), external_collector=tw_external, months=months)
    us_observations = build_us_observations(us_collector)
    tw_observations = build_tw_observations(tw_collector, external_collector=tw_external)
    latest_payload = _build_latest_payload(us_observations, tw_observations, us_history, tw_history)
    history_payloads = _build_history_payloads(us_history, tw_history)
    return {"latest": latest_payload, "history": history_payloads}


def generate_dashboard_payload() -> dict:
    try:
        return fetch_live_dashboard_payload()
    except Exception as exc:
        payload = build_sample_payload()
        payload["meta"] = {"source": "sample_fallback", "error": str(exc), "authors": AUTHOR_ORDER}
        return payload


def generate_dashboard_bundle() -> dict:
    try:
        return fetch_live_dashboard_bundle()
    except Exception as exc:
        payload = build_sample_payload()
        payload["meta"] = {"source": "sample_fallback", "error": str(exc), "authors": AUTHOR_ORDER}
        return {"latest": payload, "history": [payload]}


def main() -> None:
    bundle = generate_dashboard_bundle()
    write_dashboard_snapshot(bundle["latest"], Path("data/latest.json"), Path("data/history"), history_payloads=bundle["history"])
    write_site_content(build_site_content(), Path("data/site-content.json"))
    build_site("frontend/src", "data", "dist")


if __name__ == "__main__":
    main()
