from pathlib import Path
import shutil


def build_site(frontend_dir: str | Path, data_dir: str | Path, output_dir: str | Path) -> None:
    frontend_path = Path(frontend_dir)
    data_path = Path(data_dir)
    output_path = Path(output_dir)

    if output_path.exists():
        shutil.rmtree(output_path)

    shutil.copytree(frontend_path, output_path)
    shutil.copytree(data_path, output_path / "data")
