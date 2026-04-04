from pathlib import Path


def test_monthly_workflow_exists():
    assert Path(".github/workflows/monthly-update.yml").exists()
