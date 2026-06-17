"""Central settings for the media_pulse project."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent
SETTINGS_PATH = ROOT_DIR / "config" / "settings.yml"
ENV_PATH = ROOT_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)

DEFAULT_SETTINGS: dict[str, Any] = {
    "newsdata": {
        "base_url": "https://newsdata.io/api/1",
        "country": "id",
        "language": "id,en",
        "page_size": 10,
        "categories": ["politics", "business", "technology", "health"],
    },
    "gemini": {"model": "gemini-2.5-flash"},
    "output": {"csv": "data/news.csv"},
}


def _load_settings() -> dict[str, Any]:
    """Load YAML settings and merge them with defaults."""
    settings = DEFAULT_SETTINGS.copy()
    if not SETTINGS_PATH.exists():
        return settings

    with SETTINGS_PATH.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle) or {}

    if not isinstance(raw, dict):
        return settings

    for section, values in raw.items():
        if isinstance(values, dict) and isinstance(settings.get(section), dict):
            merged = dict(settings[section])
            merged.update(values)
            settings[section] = merged
        else:
            settings[section] = values

    return settings


SETTINGS = _load_settings()

NEWSDATA_SETTINGS = SETTINGS.get("newsdata", {})
GEMINI_SETTINGS = SETTINGS.get("gemini", {})
OUTPUT_SETTINGS = SETTINGS.get("output", {})

BASE_URL = str(NEWSDATA_SETTINGS.get("base_url", DEFAULT_SETTINGS["newsdata"]["base_url"]))
CATEGORIES = list(NEWSDATA_SETTINGS.get("categories", DEFAULT_SETTINGS["newsdata"]["categories"]))
COUNTRY = str(NEWSDATA_SETTINGS.get("country", DEFAULT_SETTINGS["newsdata"]["country"]))
LANGUAGE = str(NEWSDATA_SETTINGS.get("language", DEFAULT_SETTINGS["newsdata"]["language"]))
PAGE_SIZE = int(NEWSDATA_SETTINGS.get("page_size", DEFAULT_SETTINGS["newsdata"]["page_size"]))

NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY", "")
GEMINI_API_KEYS = os.getenv("GEMINI_API_KEYS", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", str(GEMINI_SETTINGS.get("model", DEFAULT_SETTINGS["gemini"]["model"])))
OUTPUT_CSV = str(OUTPUT_SETTINGS.get("csv", DEFAULT_SETTINGS["output"]["csv"]))
