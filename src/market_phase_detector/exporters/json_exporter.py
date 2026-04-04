import json
from pathlib import Path


def write_latest_snapshot(payload: dict, target: str | Path) -> None:
    target_path = Path(target)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _month_key(payload: dict) -> str:
    generated_at = payload.get("generated_at", "")
    if len(generated_at) < 7:
        raise ValueError("payload.generated_at must be an ISO date string")
    return generated_at[:7]


def _build_history_entry(payload: dict) -> dict:
    return {
        "month": _month_key(payload),
        "file": f"{_month_key(payload)}.json",
        "countries": [
            {
                "country": country["country"],
                "phase": country["decision"]["final_phase"],
                "watch": country["decision"].get("watch"),
                "as_of": country["as_of"],
            }
            for country in payload.get("countries", [])
        ],
    }


def write_dashboard_snapshot(payload: dict, latest_target: str | Path, history_dir: str | Path) -> None:
    latest_path = Path(latest_target)
    history_path = Path(history_dir)
    history_path.mkdir(parents=True, exist_ok=True)

    write_latest_snapshot(payload, latest_path)

    month_key = _month_key(payload)
    month_file = history_path / f"{month_key}.json"
    month_file.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    index_path = history_path / "index.json"
    if index_path.exists():
        index = json.loads(index_path.read_text(encoding="utf-8"))
    else:
        index = {"months": []}

    months = [entry for entry in index.get("months", []) if entry.get("month") != month_key]
    months.append(_build_history_entry(payload))
    months.sort(key=lambda entry: entry["month"])

    index_path.write_text(
        json.dumps({"months": months}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
