from market_phase_detector.models.phases import DecisionRecord


def test_decision_record_has_phase_and_reasons():
    record = DecisionRecord(
        country="US",
        as_of="2026-03-31",
        candidate_phase="Boom",
        final_phase="Boom",
        watch="recession_risk",
        reasons=["Yield curve inverted"],
    )

    assert record.final_phase == "Boom"
    assert record.reasons == ["Yield curve inverted"]
