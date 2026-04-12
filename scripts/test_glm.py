from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from market_phase_detector.glm_cli import (
    DEFAULT_ENV_FILE,
    DEFAULT_PROMPT,
    chat_completion,
    format_result,
    load_config,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Minimal GLM smoke test")
    parser.add_argument(
        "--env-file",
        type=Path,
        default=DEFAULT_ENV_FILE,
        help="Path to the local GLM env file",
    )
    parser.add_argument(
        "--prompt",
        default=DEFAULT_PROMPT,
        help="Prompt sent to the model",
    )
    args = parser.parse_args()

    config = load_config(args.env_file)
    response_json = chat_completion(config, args.prompt)
    print(format_result(response_json))


if __name__ == "__main__":
    main()
