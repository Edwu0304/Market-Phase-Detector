from pathlib import Path


def test_frontend_entrypoint_exists():
    assert Path("frontend/src/index.html").exists()
