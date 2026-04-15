from market_phase_detector.cli import build_sample_payload


def test_sample_payload_exposes_three_lens_bundles():
    payload = build_sample_payload()
    country = payload["countries"][0]

    assert "lenses" in country
    assert set(country["lenses"]) == {"izaax", "urakami", "marks"}
    assert country["lenses"]["izaax"]["history"]
    assert country["lenses"]["marks"]["metrics"]
    izaax_row = country["lenses"]["izaax"]["history"][-1]
    assert "support_current_phase_signals" in izaax_row
    assert "support_next_phase_signals" in izaax_row
    assert "conflict_signals" in izaax_row
