from market_phase_detector.content import build_site_content


def test_build_site_content_contains_home_author_and_country_pages():
    payload = build_site_content()

    assert "home" in payload
    assert "authors" in payload
    assert "countries" in payload
    assert set(payload["authors"]) == {"izaax", "urakami", "marks"}
    assert "TW" in payload["countries"]
    assert "US" in payload["countries"]


def test_country_strategy_content_is_available_by_phase():
    payload = build_site_content()

    handbook = payload["countries"]["TW"]["strategy_by_phase"]["Recovery"]
    assert handbook["country"] == "TW"
    assert len(handbook["authors"]) == 3
