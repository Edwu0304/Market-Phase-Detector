from market_phase_detector import cli


def test_generate_payload_uses_live_data_when_available(monkeypatch):
    monkeypatch.setattr(
        cli,
        "fetch_live_dashboard_payload",
        lambda: {"generated_at": "live", "countries": []},
    )

    payload = cli.generate_dashboard_payload()

    assert payload["generated_at"] == "live"


def test_generate_payload_falls_back_to_sample_on_error(monkeypatch):
    monkeypatch.setattr(
        cli,
        "fetch_live_dashboard_payload",
        lambda: (_ for _ in ()).throw(RuntimeError("boom")),
    )

    payload = cli.generate_dashboard_payload()

    assert payload["generated_at"] == "2026-04-05"
    assert payload["meta"]["source"] == "sample_fallback"
    assert "boom" in payload["meta"]["error"]


def test_sample_payload_contains_handbook_content():
    payload = cli.build_sample_payload()

    assert "landing" in payload
    assert "handbook" in payload["countries"][0]
    assert len(payload["countries"][0]["handbook"]["lenses"]) == 3


def test_generate_dashboard_bundle_falls_back_to_sample_on_error(monkeypatch):
    monkeypatch.setattr(
        cli,
        "fetch_live_dashboard_bundle",
        lambda: (_ for _ in ()).throw(RuntimeError("boom")),
    )

    bundle = cli.generate_dashboard_bundle()

    assert bundle["latest"]["meta"]["source"] == "sample_fallback"
    assert bundle["history"] == [bundle["latest"]]
