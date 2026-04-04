from pathlib import Path


def test_monthly_workflow_exists():
    assert Path(".github/workflows/monthly-update.yml").exists()


def test_monthly_workflow_mentions_github_pages():
    workflow = Path(".github/workflows/monthly-update.yml").read_text(encoding="utf-8")

    assert "actions/configure-pages" in workflow
    assert "actions/deploy-pages" in workflow
