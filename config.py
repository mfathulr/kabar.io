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
        "language": "id",
        "page_size": 10,
        "active_category_set": "core_daily",
        "category_sets": {
            "core_daily": ["politics", "business", "technology", "health", "world"],
            "tail_a": ["entertainment", "sports", "domestic", "education"],
            "tail_b": ["crime", "environment", "food", "lifestyle"],
            "tail_c": ["science", "tourism", "top", "other"],
            "core_daily_plus_tail_a": [
                "politics",
                "business",
                "technology",
                "health",
                "world",
                "entertainment",
                "sports",
                "domestic",
                "education",
            ],
            "core_daily_plus_tail_b": [
                "politics",
                "business",
                "technology",
                "health",
                "world",
                "crime",
                "environment",
                "food",
                "lifestyle",
            ],
            "core_daily_plus_tail_c": [
                "politics",
                "business",
                "technology",
                "health",
                "world",
                "science",
                "tourism",
                "top",
                "other",
            ],
            "balanced": ["politics", "business", "technology", "health", "world"],
            "broader": [
                "politics",
                "business",
                "technology",
                "health",
                "world",
                "entertainment",
                "sports",
            ],
            "local": ["domestic", "politics", "education", "crime", "health"],
            "economy": ["business", "technology", "politics", "domestic", "world"],
        },
        "categories": [
            "business",
            "crime",
            "domestic",
            "education",
            "entertainment",
            "environment",
            "food",
            "health",
            "lifestyle",
            "politics",
            "science",
            "sports",
            "technology",
            "top",
            "tourism",
            "world",
            "other",
        ],
        "credit_budget_per_day": 200,
        "credit_buffer": 20,
        "max_pages_per_category": 2,
    },
    "gemini": {
        "model": "gemini-2.5-flash",
        "models": ["gemini-2.5-flash", "gemini-2.5-flash-lite-preview-09-2025"],
    },
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


def _parse_csv_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


SETTINGS = _load_settings()

NEWSDATA_SETTINGS = SETTINGS.get("newsdata", {})
GEMINI_SETTINGS = SETTINGS.get("gemini", {})
OUTPUT_SETTINGS = SETTINGS.get("output", {})

BASE_URL = str(NEWSDATA_SETTINGS.get("base_url", DEFAULT_SETTINGS["newsdata"]["base_url"]))
COUNTRY = str(NEWSDATA_SETTINGS.get("country", DEFAULT_SETTINGS["newsdata"]["country"]))
LANGUAGE = "id"
RAW_PAGE_SIZE = int(NEWSDATA_SETTINGS.get("page_size", DEFAULT_SETTINGS["newsdata"]["page_size"]))
PAGE_SIZE = max(1, min(RAW_PAGE_SIZE, 10))
if RAW_PAGE_SIZE != PAGE_SIZE:
    print(f"Clamped NewsData page_size from {RAW_PAGE_SIZE} to {PAGE_SIZE} for free-tier compatibility.", flush=True)
CATEGORY_OVERRIDE_RAW = os.getenv("NEWSDATA_CATEGORIES", "").strip()
ACTIVE_CATEGORY_SET_ENV = os.getenv("NEWSDATA_ACTIVE_CATEGORY_SET", "").strip()
ACTIVE_CATEGORY_SET = ACTIVE_CATEGORY_SET_ENV or str(
    NEWSDATA_SETTINGS.get("active_category_set", DEFAULT_SETTINGS["newsdata"]["active_category_set"])
)
if CATEGORY_OVERRIDE_RAW and not ACTIVE_CATEGORY_SET_ENV:
    ACTIVE_CATEGORY_SET = "custom"
CATEGORY_SETS = dict(NEWSDATA_SETTINGS.get("category_sets", DEFAULT_SETTINGS["newsdata"]["category_sets"]))
if CATEGORY_OVERRIDE_RAW:
    CATEGORIES = _parse_csv_list(CATEGORY_OVERRIDE_RAW)
elif "active_category_set" in NEWSDATA_SETTINGS:
    CATEGORIES = list(CATEGORY_SETS.get(ACTIVE_CATEGORY_SET, DEFAULT_SETTINGS["newsdata"]["categories"]))
else:
    raw_categories = NEWSDATA_SETTINGS.get("categories")
    if isinstance(raw_categories, list) and raw_categories:
        CATEGORIES = list(raw_categories)
    else:
        CATEGORIES = list(CATEGORY_SETS.get(ACTIVE_CATEGORY_SET, DEFAULT_SETTINGS["newsdata"]["categories"]))
if not CATEGORIES:
    CATEGORIES = list(DEFAULT_SETTINGS["newsdata"]["categories"])
MAX_PAGES_PER_CATEGORY = int(
    NEWSDATA_SETTINGS.get("max_pages_per_category", DEFAULT_SETTINGS["newsdata"]["max_pages_per_category"])
)
NEWSDATA_CREDIT_BUDGET_PER_DAY = int(
    NEWSDATA_SETTINGS.get("credit_budget_per_day", DEFAULT_SETTINGS["newsdata"]["credit_budget_per_day"])
)
NEWSDATA_CREDIT_BUFFER = int(
    NEWSDATA_SETTINGS.get("credit_buffer", DEFAULT_SETTINGS["newsdata"]["credit_buffer"])
)

NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY", "")
GEMINI_API_KEYS = os.getenv("GEMINI_API_KEYS", "")
_GEMINI_MODELS_RAW = os.getenv("GEMINI_MODELS", "").strip()
if _GEMINI_MODELS_RAW:
    GEMINI_MODELS = [model.strip() for model in _GEMINI_MODELS_RAW.split(",") if model.strip()]
else:
    raw_models = GEMINI_SETTINGS.get("models")
    if isinstance(raw_models, list) and raw_models:
        GEMINI_MODELS = [str(model).strip() for model in raw_models if str(model).strip()]
    else:
        GEMINI_MODELS = []

GEMINI_MODEL = os.getenv("GEMINI_MODEL", str(GEMINI_SETTINGS.get("model", DEFAULT_SETTINGS["gemini"]["model"])))
if not GEMINI_MODELS:
    GEMINI_MODELS = [GEMINI_MODEL]
else:
    seen: set[str] = set()
    GEMINI_MODELS = [model for model in GEMINI_MODELS if not (model in seen or seen.add(model))]
OUTPUT_CSV = str(OUTPUT_SETTINGS.get("csv", DEFAULT_SETTINGS["output"]["csv"]))
