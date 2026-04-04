from pathlib import Path


def test_frontend_entrypoint_exists():
    assert Path("frontend/src/index.html").exists()


def test_country_pages_exist():
    assert Path("frontend/src/tw/index.html").exists()
    assert Path("frontend/src/us/index.html").exists()


def test_country_pages_exist():
    assert Path("frontend/src/tw/index.html").exists()
    assert Path("frontend/src/us/index.html").exists()
