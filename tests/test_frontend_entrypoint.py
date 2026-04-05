from pathlib import Path


def test_frontend_entrypoint_exists():
    assert Path("frontend/src/index.html").exists()


def test_country_pages_exist():
    assert Path("frontend/src/tw/index.html").exists()
    assert Path("frontend/src/us/index.html").exists()


def test_frontend_shell_mentions_three_lens_map_and_navigation():
    script = Path("frontend/src/app.js").read_text(encoding="utf-8")
    assert "buildLanding" in script
    assert "首頁" in script
    assert "台灣" in script
    assert "美國" in script
