from pathlib import Path
import shutil
import time


def build_site(frontend_dir: str | Path, data_dir: str | Path, output_dir: str | Path) -> None:
    frontend_path = Path(frontend_dir)
    data_path = Path(data_dir)
    output_path = Path(output_dir)

    # Clean output directory with retries (Windows file lock issues)
    if output_path.exists():
        for attempt in range(5):
            try:
                shutil.rmtree(output_path)
                time.sleep(0.5)
                break
            except PermissionError:
                time.sleep(2)
            except FileNotFoundError:
                break

    output_path.mkdir(parents=True, exist_ok=True)
    shutil.copytree(frontend_path, output_path, dirs_exist_ok=True)
    shutil.copytree(data_path, output_path / "data", dirs_exist_ok=True)
