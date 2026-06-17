"""Thin wrapper around the NewsData.io API."""

from __future__ import annotations

import os
import time
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

import requests
from tqdm import tqdm

from config import BASE_URL, CATEGORIES, COUNTRY, LANGUAGE, NEWSDATA_API_KEY, PAGE_SIZE


class NewsDataClient:
    def __init__(self) -> None:
        self.api_key = os.getenv("NEWSDATA_API_KEY", NEWSDATA_API_KEY)
        self.base_url = BASE_URL

        if not self.api_key:
            raise ValueError("NEWSDATA_API_KEY is not configured")

    def fetch_latest(self, category: str, page_token: str | None = None) -> dict[str, Any]:
        """Fetch the latest news for a single category."""
        if category not in CATEGORIES:
            raise ValueError(f"Unsupported category: {category}")

        url = f"{self.base_url}/latest"
        params: dict[str, Any] = {
            "apikey": self.api_key,
            "country": COUNTRY,
            "language": LANGUAGE,
            "category": category,
            "size": PAGE_SIZE,
        }
        if page_token:
            params["page"] = page_token

        last_error: Exception | None = None
        for attempt in range(2):
            try:
                response = requests.get(url, params=params, timeout=30)
                if response.status_code == 429:
                    print(f"Rate limit reached for category '{category}'. Skipping.")
                    return {}

                response.raise_for_status()
                return response.json()
            except requests.exceptions.ConnectionError as exc:
                last_error = exc
                if attempt == 0:
                    time.sleep(1)
                    continue
                raise

        if last_error is not None:
            raise last_error
        return {}

    def fetch_all_categories(self) -> list[dict[str, Any]]:
        """Fetch all articles across configured categories."""
        articles: list[dict[str, Any]] = []
        fetched_at = datetime.now(timezone.utc).isoformat()

        for category in tqdm(CATEGORIES, desc="Fetching categories"):
            page_token: str | None = None

            while True:
                payload = self.fetch_latest(category=category, page_token=page_token)
                if not payload:
                    break

                results = payload.get("results", [])
                for article in results:
                    item = deepcopy(article)
                    item["fetched_at"] = fetched_at
                    item["category"] = category
                    articles.append(item)

                page_token = payload.get("nextPage")
                if not page_token:
                    break

        return articles

    def fetch_news(self, category: str, page: int = 1) -> dict[str, Any]:
        """Backward-compatible alias for older callers."""
        page_token = str(page) if page else None
        return self.fetch_latest(category=category, page_token=page_token)
