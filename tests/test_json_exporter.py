import json

from market_phase_detector.exporters.json_exporter import write_dashboard_snapshot, write_latest_snapshot


def test_write_latest_snapshot_creates_json_file(tmp_path):
    target = tmp_path / "latest.json"

    write_latest_snapshot({"countries": []}, target)

    assert target.exists()
    assert json.loads(target.read_text(encoding="utf-8")) == {"countries": []}


def test_write_dashboard_snapshot_creates_history_artifacts(tmp_path):
    latest_target = tmp_path / "latest.json"
    history_dir = tmp_path / "history"
    payload = {
        "generated_at": "2026-04-05",
        "meta": {"source": "live"},
        "countries": [
            {
                "country": "US",
                "as_of": "2026-04-01",
                "decision": {"final_phase": "Growth"},
            }
        ],
    }

    write_dashboard_snapshot(payload, latest_target, history_dir)

    history_file = history_dir / "2026-04.json"
    index_file = history_dir / "index.json"

    assert latest_target.exists()
    assert history_file.exists()
    assert index_file.exists()
    index = json.loads(index_file.read_text(encoding="utf-8"))
    assert index["months"][-1]["month"] == "2026-04"
    assert index["months"][-1]["countries"][0]["phase"] == "Growth"


def test_write_dashboard_snapshot_can_backfill_multiple_months(tmp_path):
    latest_target = tmp_path / "latest.json"
    history_dir = tmp_path / "history"
    march_payload = {
        "generated_at": "2026-03-05",
        "meta": {"source": "live"},
        "countries": [
            {
                "country": "US",
                "as_of": "2026-03-01",
                "decision": {"final_phase": "Recovery", "watch": None},
            },
            {
                "country": "TW",
                "as_of": "2026-03-31",
                "decision": {"final_phase": "Growth", "watch": None},
            },
        ],
    }
    april_payload = {
        "generated_at": "2026-04-05",
        "meta": {"source": "live"},
        "countries": [
            {
                "country": "US",
                "as_of": "2026-04-01",
                "decision": {"final_phase": "Growth", "watch": None},
            },
            {
                "country": "TW",
                "as_of": "2026-04-30",
                "decision": {"final_phase": "Boom", "watch": "insufficient_confirmation"},
            },
        ],
    }

    write_dashboard_snapshot(
        april_payload,
        latest_target,
        history_dir,
        history_payloads=[march_payload, april_payload],
    )

    assert (history_dir / "2026-03.json").exists()
    assert (history_dir / "2026-04.json").exists()

    index = json.loads((history_dir / "index.json").read_text(encoding="utf-8"))
    assert [entry["month"] for entry in index["months"]] == ["2026-03", "2026-04"]
    assert index["months"][0]["countries"][0]["phase"] == "Recovery"
