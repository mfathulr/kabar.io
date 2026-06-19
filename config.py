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
        "active_category_set": "balanced",
        "category_sets": {
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
        "categories": ["politics", "business", "technology", "health", "world"],
        "credit_budget_per_day": 200,
        "credit_buffer": 20,
        "max_pages_per_category": 5,
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
ACTIVE_CATEGORY_SET = str(
    NEWSDATA_SETTINGS.get("active_category_set", DEFAULT_SETTINGS["newsdata"]["active_category_set"])
)
CATEGORY_SETS = dict(NEWSDATA_SETTINGS.get("category_sets", DEFAULT_SETTINGS["newsdata"]["category_sets"]))
RAW_CATEGORIES = NEWSDATA_SETTINGS.get("categories")
if "active_category_set" in NEWSDATA_SETTINGS:
    CATEGORIES = list(CATEGORY_SETS.get(ACTIVE_CATEGORY_SET, DEFAULT_SETTINGS["newsdata"]["categories"]))
elif isinstance(RAW_CATEGORIES, list) and RAW_CATEGORIES:
    CATEGORIES = list(RAW_CATEGORIES)
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
