import json

from market_phase_detector.exporters.json_exporter import write_dashboard_snapshot, write_latest_snapshot


def test_write_latest_snapshot_creates_json_file(tmp_path):
    target = tmp_path / "latest.json"

    write_latest_snapshot({"countries": []}, target)

    assert target.exists()
    assert json.loads(target.read_text(encoding="utf-8")) == {"countries": []}


def test_write_dashboard_snapshot_creates_history_artifacts_with_lenses(tmp_path):
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
                "lenses": {
                    "izaax": {
                        "phase": "Growth",
                        "metrics": [{"id": "leading_index_change", "value": 0.1}],
                        "history": [{"month": "2026-04", "as_of": "2026-04-01", "phase": "Growth"}],
                    }
                },
            }
        ],
    }

    write_dashboard_snapshot(payload, latest_target, history_dir)

    history_file = history_dir / "2026-04.json"
    index_file = history_dir / "index.json"
    assert history_file.exists()
    assert index_file.exists()
    index = json.loads(index_file.read_text(encoding="utf-8"))
    assert index["months"][-1]["countries"][0]["lenses"]["izaax"]["phase"] == "Growth"


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
                "lenses": {"marks": {"phase": "Recovery", "history": [{"month": "2026-03", "as_of": "2026-03-01", "phase": "Recovery"}]}},
            }
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
                "lenses": {"marks": {"phase": "Growth", "history": [{"month": "2026-04", "as_of": "2026-04-01", "phase": "Growth"}]}},
            }
        ],
    }
    write_dashboard_snapshot(april_payload, latest_target, history_dir, history_payloads=[march_payload, april_payload])
    index = json.loads((history_dir / "index.json").read_text(encoding="utf-8"))
    assert [entry["month"] for entry in index["months"]] == ["2026-03", "2026-04"]
    assert index["months"][1]["countries"][0]["lenses"]["marks"]["phase"] == "Growth"


def test_write_dashboard_snapshot_rebuilds_index_without_stale_months(tmp_path):
    latest_target = tmp_path / "latest.json"
    history_dir = tmp_path / "history"
    history_dir.mkdir()
    (history_dir / "2026-04.json").write_text("{}", encoding="utf-8")
    (history_dir / "index.json").write_text(
        json.dumps({"months": [{"month": "2026-04", "file": "2026-04.json", "countries": []}]}, ensure_ascii=False),
        encoding="utf-8",
    )
    payload = {
        "generated_at": "2026-04-05",
        "countries": [
            {
                "country": "US",
                "as_of": "2026-02",
                "decision": {"final_phase": "Growth", "watch": None},
                "lenses": {},
            }
        ],
    }
    write_dashboard_snapshot(payload, latest_target, history_dir, history_payloads=[payload])
    index = json.loads((history_dir / "index.json").read_text(encoding="utf-8"))
    assert [entry["month"] for entry in index["months"]] == ["2026-02"]
