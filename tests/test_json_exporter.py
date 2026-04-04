import json

from market_phase_detector.exporters.json_exporter import write_latest_snapshot


def test_write_latest_snapshot_creates_json_file(tmp_path):
    target = tmp_path / "latest.json"

    write_latest_snapshot({"countries": []}, target)

    assert target.exists()
    assert json.loads(target.read_text(encoding="utf-8")) == {"countries": []}
