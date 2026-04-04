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
