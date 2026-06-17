"""Central settings for the media_pulse project."""

from __future__ import annotations

import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://newsdata.io/api/1"
CATEGORIES = ["politics", "business", "technology", "health"]
COUNTRY = "id"
LANGUAGE = "id,en"
PAGE_SIZE = 10

NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY", "")
GEMINI_API_KEYS = os.getenv("GEMINI_API_KEYS", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
OUTPUT_CSV = os.getenv("OUTPUT_CSV", "data/news.csv")
