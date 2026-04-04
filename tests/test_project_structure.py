from pathlib import Path


def test_project_structure_exists():
    assert Path("src/market_phase_detector/engine").exists()
