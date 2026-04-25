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
    assert "warning_state" in izaax_row
    assert "warning_reasons" in izaax_row
    semantic_row = country["lenses"]["izaax"]["transposed"]["semantic_rows"][0]
    assert "master_category" in semantic_row
    assert "site_metric_label" in semantic_row
    assert "source_type" in semantic_row
    assert "warning_state" in country["lenses"]["izaax"]["transposed"]
    assert country["lenses"]["urakami"]["history"][-1]["semantic_rows"]
    assert country["lenses"]["marks"]["history"][-1]["semantic_rows"]
