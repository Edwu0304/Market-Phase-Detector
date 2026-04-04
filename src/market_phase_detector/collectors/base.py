from dataclasses import dataclass

import requests


@dataclass(slots=True)
class HttpCollector:
    timeout: int = 30

    def get_json(self, url: str, params: dict | None = None) -> dict | list:
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def get_text(self, url: str, params: dict | None = None) -> str:
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        response.encoding = response.encoding or "utf-8"
        return response.text
