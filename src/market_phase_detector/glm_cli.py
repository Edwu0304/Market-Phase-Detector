from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import os

import requests


DEFAULT_ENV_FILE = Path(".env.glm.local")
DEFAULT_PROMPT = "Reply with exactly: pong"


@dataclass(frozen=True)
class GLMConfig:
    api_key: str
    base_url: str
    model: str


def load_env_file(env_file: Path) -> GLMConfig:
    values: dict[str, str] = {}
    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return GLMConfig(
        api_key=values.get("API_KEY") or values.get("OPENAI_API_KEY", ""),
        base_url=values.get("BASE_URL") or values.get("OPENAI_BASE_URL", ""),
        model=values.get("MODEL_NAME") or values.get("OPENAI_MODEL", ""),
    )


def load_config(env_file: Path = DEFAULT_ENV_FILE) -> GLMConfig:
    if env_file.exists():
        config = load_env_file(env_file)
    else:
        config = GLMConfig(
            api_key=os.getenv("API_KEY") or os.getenv("OPENAI_API_KEY", ""),
            base_url=os.getenv("BASE_URL") or os.getenv("OPENAI_BASE_URL", ""),
            model=os.getenv("MODEL_NAME") or os.getenv("OPENAI_MODEL", ""),
        )
    missing = [
        name
        for name, value in {
            "api_key": config.api_key,
            "base_url": config.base_url,
            "model": config.model,
        }.items()
        if not value
    ]
    if missing:
        raise ValueError(f"Missing GLM settings: {', '.join(missing)}")
    return config


def build_chat_payload(config: GLMConfig, prompt: str) -> dict:
    return {
        "model": config.model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
    }


def chat_completion(config: GLMConfig, prompt: str, timeout: int = 30) -> dict:
    response = requests.post(
        f"{config.base_url.rstrip('/')}/api/paas/v4/chat/completions",
        headers={
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
        },
        json=build_chat_payload(config, prompt),
        timeout=timeout,
    )
    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        body = response.text.strip()
        detail = f"{exc}"
        if body:
            detail = f"{detail}: {body}"
        raise RuntimeError(detail) from exc
    return response.json()


def extract_text(response_json: dict) -> str:
    choices = response_json.get("choices") or []
    if not choices:
        raise ValueError("GLM response did not include choices")
    message = choices[0].get("message") or {}
    content = message.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        text_parts = [item.get("text", "") for item in content if isinstance(item, dict)]
        return "".join(text_parts).strip()
    raise ValueError("GLM response did not include text content")


def format_result(response_json: dict) -> str:
    return json.dumps(
        {
            "id": response_json.get("id"),
            "model": response_json.get("model"),
            "text": extract_text(response_json),
        },
        ensure_ascii=False,
        indent=2,
    )
