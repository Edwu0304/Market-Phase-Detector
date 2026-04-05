import json
from pathlib import Path


def _normalize_month_token(value: str) -> str:
    if len(value) >= 7 and value[4] == "-":
        return value[:7]
    if len(value) >= 6 and value[:6].isdigit():
        return f"{value[:4]}-{value[4:6]}"
    raise ValueError(f"Unsupported month token: {value}")


def write_latest_snapshot(payload: dict, target: str | Path) -> None:
    target_path = Path(target)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _month_key(payload: dict) -> str:
    countries = payload.get("countries", [])
    if countries:
        normalized = {_normalize_month_token(country["as_of"]) for country in countries if country.get("as_of")}
        if len(normalized) == 1:
            return next(iter(normalized))
    generated_at = payload.get("generated_at", "")
    if generated_at:
        return _normalize_month_token(generated_at)
    raise ValueError("payload must contain countries.as_of or generated_at")


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
                "lenses": {
                    lens_id: {
                        "phase": lens_bundle["phase"],
                        "as_of": lens_bundle["history"][-1]["as_of"] if lens_bundle.get("history") else country["as_of"],
                    }
                    for lens_id, lens_bundle in country.get("lenses", {}).items()
                },
            }
            for country in payload.get("countries", [])
        ],
    }


def write_dashboard_snapshot(
    payload: dict,
    latest_target: str | Path,
    history_dir: str | Path,
    history_payloads: list[dict] | None = None,
) -> None:
    latest_path = Path(latest_target)
    history_path = Path(history_dir)
    history_path.mkdir(parents=True, exist_ok=True)

    write_latest_snapshot(payload, latest_path)

    payloads = history_payloads or [payload]
    for existing_file in history_path.glob("*.json"):
        existing_file.unlink()
    new_entries = []
    for history_payload in payloads:
        month_key = _month_key(history_payload)
        month_file = history_path / f"{month_key}.json"
        month_file.write_text(
            json.dumps(history_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        new_entries.append(_build_history_entry(history_payload))

    index_path = history_path / "index.json"
    months = list(new_entries)
    months.sort(key=lambda entry: entry["month"])

    index_path.write_text(
        json.dumps({"months": months}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def write_site_content(payload: dict, target: str | Path) -> None:
    target_path = Path(target)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
