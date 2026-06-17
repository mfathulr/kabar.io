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
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OUTPUT_CSV = os.getenv("OUTPUT_CSV", "data/news.csv")
