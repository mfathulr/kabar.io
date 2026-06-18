"""Thin wrapper around the NewsData.io API."""

from __future__ import annotations

import os
import time
from copy import deepcopy
from datetime import datetime, timezone
from math import ceil
from typing import Any

import requests
from tqdm import tqdm

from config import (
    ACTIVE_CATEGORY_SET,
    BASE_URL,
    CATEGORIES,
    COUNTRY,
    LANGUAGE,
    MAX_PAGES_PER_CATEGORY,
    NEWSDATA_API_KEY,
    NEWSDATA_CREDIT_BUFFER,
    NEWSDATA_CREDIT_BUDGET_PER_DAY,
    PAGE_SIZE,
)


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

    @staticmethod
    def _estimate_page_credit_cost(page_size: int) -> int:
        """Estimate how many NewsData credits a single request can use."""
        return max(1, ceil(max(page_size, 1) / 10))

    def fetch_all_categories(self) -> list[dict[str, Any]]:
        """Fetch all articles across configured categories in round-robin order."""
        articles: list[dict[str, Any]] = []
        fetched_at = datetime.now(timezone.utc).isoformat()

        categories = list(CATEGORIES)
        if not categories:
            return articles

        max_credits = max(1, NEWSDATA_CREDIT_BUDGET_PER_DAY - NEWSDATA_CREDIT_BUFFER)
        page_credit_cost = self._estimate_page_credit_cost(PAGE_SIZE)
        page_tokens: dict[str, str | None] = {category: None for category in categories}
        page_counts: dict[str, int] = {category: 0 for category in categories}
        completed_categories: set[str] = set()
        credits_used = 0
        progress = tqdm(total=len(categories), desc="Category rounds")

        print(
            "NewsData category mix: "
            f"{ACTIVE_CATEGORY_SET} -> {', '.join(categories)}",
            flush=True,
        )
        print(
            "NewsData credit guard: "
            f"budget={NEWSDATA_CREDIT_BUDGET_PER_DAY}/day, buffer={NEWSDATA_CREDIT_BUFFER}, "
            f"max_for_this_run={max_credits}, page_cost={page_credit_cost}",
            flush=True,
        )

        try:
            while len(completed_categories) < len(categories):
                made_progress = False
                for category in categories:
                    if category in completed_categories:
                        continue
                    if page_counts[category] >= MAX_PAGES_PER_CATEGORY:
                        print(
                            f"Reached max_pages_per_category={MAX_PAGES_PER_CATEGORY} for '{category}'.",
                            flush=True,
                        )
                        completed_categories.add(category)
                        progress.update(1)
                        continue
                    if credits_used >= max_credits:
                        print(
                            "Stopping fetch because the daily credit guard was reached.",
                            flush=True,
                        )
                        return articles
                    if credits_used + page_credit_cost > max_credits:
                        print(
                            f"Stopping before fetching '{category}' page {page_counts[category] + 1} "
                            "to preserve the daily credit buffer.",
                            flush=True,
                        )
                        return articles

                    payload = self.fetch_latest(category=category, page_token=page_tokens[category])
                    made_progress = True
                    if not payload:
                        completed_categories.add(category)
                        progress.update(1)
                        continue

                    results = payload.get("results", [])
                    for article in results:
                        item = deepcopy(article)
                        item["fetched_at"] = fetched_at
                        item["category"] = category
                        articles.append(item)
                    credits_used += page_credit_cost

                    page_counts[category] += 1
                    page_tokens[category] = payload.get("nextPage")

                    if not page_tokens[category]:
                        completed_categories.add(category)
                        progress.update(1)
                    elif page_counts[category] >= MAX_PAGES_PER_CATEGORY:
                        print(
                            f"Reached max_pages_per_category={MAX_PAGES_PER_CATEGORY} for '{category}'.",
                            flush=True,
                        )
                        completed_categories.add(category)
                        progress.update(1)

                if not made_progress:
                    break
        finally:
            progress.close()

        return articles

    def fetch_news(self, category: str, page: int = 1) -> dict[str, Any]:
        """Backward-compatible alias for older callers."""
        page_token = str(page) if page else None
        return self.fetch_latest(category=category, page_token=page_token)
