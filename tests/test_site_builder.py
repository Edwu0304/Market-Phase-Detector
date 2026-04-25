from pathlib import Path

from market_phase_detector.site_builder import build_site


def test_build_site_copies_frontend_and_data(tmp_path):
    frontend_dir = tmp_path / "frontend"
    data_dir = tmp_path / "data"
    output_dir = tmp_path / "dist"

    frontend_dir.mkdir()
    data_dir.mkdir()

    (frontend_dir / "index.html").write_text("<html></html>", encoding="utf-8")
    (data_dir / "latest.json").write_text("{}", encoding="utf-8")

    build_site(frontend_dir, data_dir, output_dir)

    assert (output_dir / "index.html").exists()
    assert (output_dir / "data" / "latest.json").exists()


def test_build_site_ignores_nested_git_metadata(tmp_path):
    frontend_dir = tmp_path / "frontend"
    data_dir = tmp_path / "data"
    output_dir = tmp_path / "dist"

    frontend_dir.mkdir()
    (frontend_dir / "index.html").write_text("<html></html>", encoding="utf-8")
    (data_dir / ".git" / "objects").mkdir(parents=True)
    (data_dir / "latest.json").write_text("{}", encoding="utf-8")
    (data_dir / ".git" / "objects" / "pack.pack").write_text("ignored", encoding="utf-8")

    build_site(frontend_dir, data_dir, output_dir)

    assert (output_dir / "data" / "latest.json").exists()
    assert not (output_dir / "data" / ".git").exists()
